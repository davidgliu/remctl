#!/usr/bin/env python3
"""Compare the local checkout with the installed CLI, signed host, and plugins."""

from __future__ import annotations

import argparse
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from build_capability_archive import SOURCE_MANIFEST, _verify_source_manifest


def sealed_archive(executable: Path) -> bytes:
    """Read the Python archive from the signed host's Mach-O section."""
    binary = executable.read_bytes()
    if struct.unpack_from("<I", binary)[0] != 0xFEEDFACF:
        raise ValueError("Expected a 64-bit Mach-O Capability Host")
    commands = struct.unpack_from("<I", binary, 16)[0]
    offset = 32
    for _ in range(commands):
        command, size = struct.unpack_from("<II", binary, offset)
        if command == 0x19:
            sections = struct.unpack_from("<I", binary, offset + 64)[0]
            for index in range(sections):
                section = offset + 72 + index * 80
                name = binary[section:section + 16].rstrip(b"\0")
                if name == b"__rctl_pyz":
                    length = struct.unpack_from("<Q", binary, section + 40)[0]
                    start = struct.unpack_from("<I", binary, section + 48)[0]
                    return binary[start:start + length]
        offset += size
    raise ValueError("Capability Host has no sealed Python archive")


def verify(root: Path, app: Path, client: Path, codex_cache: Path, claude_cache: Path) -> dict:
    _verify_source_manifest(root)
    checks = {}

    def compare(label: str, source: Path, destination: Path) -> None:
        checks[label] = destination.is_file() and source.read_bytes() == destination.read_bytes()

    for name in [*SOURCE_MANIFEST.values(), "remctl_workspace.html", "remctl_mcp_widget.html"]:
        compare("cli:" + name, root / name, client / name)
    resources = app / "Contents/Resources"
    for folder in ["plugins", ".agents/plugins"]:
        for source in sorted((root / folder).rglob("*")):
            if source.is_file():
                relative = source.relative_to(root)
                compare("host:" + str(relative), source, resources / relative)
    missing_plugins = []
    for folder, cache in [("plugins/remctl", codex_cache), ("plugins/claude-code", claude_cache)]:
        if not cache.exists():
            missing_plugins.append(str(cache))
            continue
        for source in sorted((root / folder).rglob("*")):
            if source.is_file():
                compare("cache:" + str(source.relative_to(root)), source, cache / source.relative_to(root / folder))

    python = (resources / "remctl-capability-python-path").read_text().strip()
    executable = app / "Contents/MacOS/RemCTL Capability Host"
    with tempfile.TemporaryDirectory(prefix="remctl-surface-parity-") as directory:
        expected = Path(directory) / "capability.pyz"
        subprocess.run([python, str(root / "scripts/build_capability_archive.py"),
                        "--source-root", str(root), "--output", str(expected)], check=True)
        checks["sealed_archive"] = sealed_archive(executable) == expected.read_bytes()
    signature = subprocess.run(["codesign", "--verify", "--deep", "--strict", str(app)],
                               capture_output=True, text=True)
    checks["signature"] = signature.returncode == 0
    return {"ok": all(checks.values()), "checks": checks, "unavailablePluginCaches": missing_plugins,
            "mismatches": [name for name, passed in checks.items() if not passed]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--app", type=Path, default=Path.home() / "Applications/RemCTL Capability Host.app")
    parser.add_argument("--client", type=Path, default=Path.home() / "bin")
    parser.add_argument("--codex-cache", type=Path)
    parser.add_argument("--claude-cache", type=Path)
    args = parser.parse_args()
    try:
        root = args.source_root.resolve()
        codex_version = json.loads((root / "plugins/remctl/plugin.json").read_text())["version"]
        claude_version = json.loads((root / "plugins/claude-code/.claude-plugin/plugin.json").read_text())["version"]
        codex_cache = args.codex_cache or Path.home() / ".codex/plugins/cache/remctl-local/remctl" / codex_version
        claude_cache = args.claude_cache or Path.home() / ".claude/plugins/cache/remctl/remctl" / claude_version
        report = verify(root, args.app, args.client, codex_cache, claude_cache)
    except (OSError, ValueError, struct.error, subprocess.CalledProcessError) as error:
        report = {"ok": False, "error": str(error)}
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
