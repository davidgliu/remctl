"""Each count must equal its ceiling in .agent/ratchet-state.json.

Above the ceiling fails; below it fails too, so a fix lowers the ceiling in the same change.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".venv", ".mypy_cache", ".pytest_cache", ".ruff_cache", "dist", "build"}
HANDOFF = re.compile(r"handoff", re.IGNORECASE)


def ceiling(name: str) -> int:
    data = json.loads((ROOT / ".agent" / "ratchet-state.json").read_text())
    value = data["ceilings"][name]
    assert isinstance(value, int)
    return value


def repo_files() -> list[Path]:
    return [
        p
        for p in ROOT.rglob("*")
        if p.is_file() and not SKIP_DIRS.intersection(p.relative_to(ROOT).parts[:-1])
    ]


def test_adrs_have_measured_evidence() -> None:
    adr_dir = ROOT / "docs" / "adr"
    missing = sorted(
        p.name
        for p in adr_dir.glob("[0-9]*.md")
        if not re.search(r"^## Measured evidence\s*$", p.read_text(), re.MULTILINE)
    )
    assert len(missing) == ceiling("adr-missing-measured-evidence"), missing


def test_no_handoff_docs() -> None:
    found = sorted(
        str(p.relative_to(ROOT))
        for p in repo_files()
        if p.suffix == ".md" and HANDOFF.search(p.name)
    )
    assert len(found) == ceiling("handoff-docs"), found
