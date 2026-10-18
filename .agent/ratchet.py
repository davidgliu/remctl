#!/usr/bin/env python3
"""Fail when a suppression or ceiling total rises, or a guard config changes, without a trailer.

Compares the merge base of --base and --head with --head.
Exit 0: no unexplained change, adoption, or no base ref locally. Exit 1: unexplained.
Exit 2: git or parse error (fail closed).
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import math
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from typing import Any

STATE_FILES = (".agent/ratchet-state.json", "eslint-suppressions.json")
ANSWERS_FILE = ".copier-answers.yml"
SELF = ".agent/ratchet.py"

GUARD_FILES = (
    ".agent/test-gate",
    SELF,
    ".agent/tools.txt",
    ".github/workflows/ratchet.yml",
    "tests/test_repo_shape.py",
    ".agent/swift_scan.py",
    "tools/design/color.py",
    "tools/design/contrast.py",
    "tools/design/tokens.py",
)
# Every path is guard config except code, docs and assets: a lockfile, package manifest, .npmrc
# or pnpm-workspace.yaml override can swap a checker as surely as its own config file can.
FREE_SUFFIXES = (
    *(".py", ".pyi", ".sh", ".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs", ".json", ".swift"),
    *(".md", ".css", ".html", ".svg", ".png"),
)
# Tool config hides behind free suffixes: dotfiles (.pnpmfile.cjs, .prettierrc.json), *.config.*
# (ESLint resolves one from each linted file's directory), manifests and tsconfigs.
GUARD_BASENAMES = (".*", "*.config.*", "package.json", "tsconfig*.json")
PYPROJECT_GUARD_TABLES = ("ruff", "mypy", "pytest")

DIRECTIVE_PREFIX = re.compile(r"(?:ruff|flake8|mypy|pyright|pylint|shellcheck)\b", re.I)
DIRECTIVE_ANYWHERE = re.compile(r"noqa|type\s*:\s*ignore", re.I)
PREFILTER = "noqa|ignore|ruff|flake8|mypy|pyright|pylint|shellcheck"

RAISE_TRAILER = re.compile(r"^Ratchet-raised:\s*(\S+)\s+(\S+)\s*->\s*(\S+)\s+because\s+(.+)$", re.M)
CONFIG_TRAILER = re.compile(r"^Guard-config:\s*(\S+)\s+because\s+(.+)$", re.M)
MIN_REASON_WORDS = 5


class RatchetError(Exception):
    pass


@dataclass(frozen=True)
class Raise:
    rule: str
    base: float
    head: float

    def trailer(self) -> str:
        return f"Ratchet-raised: {self.rule} {fmt(self.base)} -> {fmt(self.head)} because <why, 5+ words>"


@dataclass(frozen=True)
class Ok:
    explained: list[Raise] = field(default_factory=list)


@dataclass(frozen=True)
class Adoption:
    state_files: list[str]


@dataclass(frozen=True)
class Unexplained:
    raises: list[Raise]
    configs: list[str]


Verdict = Ok | Adoption | Unexplained


def fmt(n: float) -> str:
    return "inf" if math.isinf(n) else str(int(n))


def git(*args: str, ok_codes: tuple[int, ...] = (0,)) -> str:
    proc = subprocess.run(["git", *args], capture_output=True, text=True)
    if proc.returncode not in ok_codes:
        raise RatchetError(f"git {' '.join(args)}: {proc.stderr.strip() or proc.returncode}")
    return proc.stdout


def exists(ref: str, path: str) -> bool:
    return subprocess.run(["git", "cat-file", "-e", f"{ref}:{path}"], capture_output=True).returncode == 0


def show(ref: str, path: str) -> str | None:
    return git("show", f"{ref}:{path}") if exists(ref, path) else None


def grep(ref: str, pattern: str) -> list[str]:
    out = git(
        "grep", "-h", "--text", "-i", "-E", pattern, ref, "--", ":/", f":(top,exclude){SELF}",
        ok_codes=(0, 1),
    )
    return out.splitlines()


def line_rules(line: str) -> list[str]:
    comments = (c.strip() for c in line.split("#")[1:])
    return [
        re.sub(r"\s+", "", c.lower())
        for c in comments
        if DIRECTIVE_PREFIX.match(c) or DIRECTIVE_ANYWHERE.search(c)
    ]


def comment_counts(ref: str) -> dict[str, int]:
    total: dict[str, int] = {}
    for line in grep(ref, PREFILTER):
        for rule in line_rules(line):
            total[rule] = total.get(rule, 0) + 1
    return total


def parse_ratchet_state(path: str, text: str) -> dict[str, int]:
    try:
        data: Any = json.loads(text)
    except json.JSONDecodeError as e:
        raise RatchetError(f"{path}: invalid JSON: {e}") from e
    ceilings = data.get("ceilings") if isinstance(data, dict) else None
    if not isinstance(ceilings, dict) or not ceilings:
        raise RatchetError(f"{path}: no ceilings parsed (a known state file must yield entries)")
    out: dict[str, int] = {}
    for name, value in ceilings.items():
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise RatchetError(f"{path}: ceiling {name!r} is not a non-negative integer")
        out[f"state:{name}"] = value
    return out


def parse_eslint_suppressions(path: str, text: str) -> dict[str, int]:
    try:
        data: Any = json.loads(text)
    except json.JSONDecodeError as e:
        raise RatchetError(f"{path}: invalid JSON: {e}") from e
    if not isinstance(data, dict):
        raise RatchetError(f"{path}: expected an object of files")
    out: dict[str, int] = {}
    for file, rules in data.items():
        if not isinstance(rules, dict) or not rules:
            raise RatchetError(f"{path}: {file!r} must map rules to counts")
        for rule, entry in rules.items():
            n = entry.get("count") if isinstance(entry, dict) else None
            if not isinstance(n, int) or isinstance(n, bool) or n < 0:
                raise RatchetError(f"{path}: {file!r} {rule!r} has no non-negative integer count")
            out[f"eslint:{rule}"] = out.get(f"eslint:{rule}", 0) + n
    return out


STATE_PARSERS = {
    ".agent/ratchet-state.json": parse_ratchet_state,
    "eslint-suppressions.json": parse_eslint_suppressions,
}


def counts(ref: str) -> dict[str, float]:
    total: dict[str, float] = dict(comment_counts(ref))
    for path in STATE_FILES:
        text = show(ref, path)
        if text is not None:
            total.update(STATE_PARSERS[path](path, text))
    return total


def raises(base: dict[str, float], head: dict[str, float]) -> list[Raise]:
    return [
        Raise(rule, base.get(rule, 0), head[rule])
        for rule in sorted(head)
        if head[rule] > base.get(rule, 0)
    ]


def state_file_raises(base: str, head: str) -> list[Raise]:
    out = []
    for path in STATE_FILES:
        at_base, at_head = exists(base, path), exists(head, path)
        if at_base and not at_head:
            out.append(Raise(f"file:{path}", 1, math.inf))
        elif at_head and not at_base:
            out.append(Raise(f"file:{path}", 0, 1))
    return out


def adopted_state_files(base: str, head: str) -> list[str]:
    if exists(base, ANSWERS_FILE) or not exists(head, ANSWERS_FILE):
        return []
    return [p for p in STATE_FILES if exists(head, p) and not exists(base, p)]


def pyproject_guard_tables(text: str | None, path: str) -> dict[str, Any]:
    if text is None:
        return {}
    try:
        tool = tomllib.loads(text).get("tool", {})
    except tomllib.TOMLDecodeError as e:
        raise RatchetError(f"{path}: invalid TOML: {e}") from e
    return {k: tool[k] for k in PYPROJECT_GUARD_TABLES if k in tool}


def is_guard_path(path: str) -> bool:
    # macOS file systems are case-insensitive, so ESLint loads Eslint.config.mjs too.
    # A copier template guards whatever it renders to.
    path = path.lower().removesuffix(".jinja")
    name = path.rsplit("/", 1)[-1]
    if path in {f.lower() for f in GUARD_FILES} or any(fnmatch.fnmatchcase(name, g) for g in GUARD_BASENAMES):
        return True
    return path not in STATE_FILES and name != "pyproject.toml" and not name.endswith(FREE_SUFFIXES)


def guard_config_changed(base: str, head: str) -> list[str]:
    # -z keeps non-ASCII names verbatim; git would otherwise quote them and hide their suffix.
    changed = git("diff", "-z", "--name-only", "--no-renames", base, head).split("\0")[:-1]
    out = []
    for path in changed:
        if is_guard_path(path):
            out.append(path)
        elif path.rsplit("/", 1)[-1] == "pyproject.toml":
            if pyproject_guard_tables(show(base, path), path) != pyproject_guard_tables(show(head, path), path):
                out.append(path)
    return out


def explained(r: Raise, bodies: str) -> bool:
    return any(
        (rule, old, new) == (r.rule, fmt(r.base), fmt(r.head)) and len(reason.split()) >= MIN_REASON_WORDS
        for rule, old, new, reason in RAISE_TRAILER.findall(bodies)
    )


def config_explained(path: str, bodies: str) -> bool:
    return any(p == path and len(reason.split()) >= MIN_REASON_WORDS for p, reason in CONFIG_TRAILER.findall(bodies))


def verdict(base: str, head: str) -> Verdict:
    mb = git("merge-base", base, head).strip()
    adopted = adopted_state_files(mb, head)
    if adopted:
        return Adoption(adopted)
    all_raises = raises(counts(mb), counts(head)) + state_file_raises(mb, head)
    configs = guard_config_changed(mb, head)
    bodies = git("log", "--format=%(trailers:only,unfold)", f"{mb}..{head}")
    bad_raises = [r for r in all_raises if not explained(r, bodies)]
    bad_configs = [p for p in configs if not config_explained(p, bodies)]
    if bad_raises or bad_configs:
        return Unexplained(bad_raises, bad_configs)
    return Ok(all_raises)


def default_base() -> str | None:
    if "origin" not in git("remote").split():
        return None
    head_ref = subprocess.run(
        ["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], capture_output=True, text=True
    ).stdout.strip()
    candidates = [head_ref.removeprefix("origin/")] if head_ref else ["main", "master"]
    for branch in candidates:
        subprocess.run(["git", "fetch", "-q", "origin", branch], capture_output=True)
        if subprocess.run(["git", "rev-parse", "-q", "--verify", f"origin/{branch}"], capture_output=True).returncode == 0:
            return f"origin/{branch}"
    return None


def report(v: Verdict) -> int:
    match v:
        case Adoption(state_files):
            print(f"ratchet: adoption ({', '.join(state_files)} added with {ANSWERS_FILE})")
            return 0
        case Ok(explained_raises):
            for r in explained_raises:
                print(f"ratchet: {r.rule} {fmt(r.base)} -> {fmt(r.head)} (explained by trailer)")
            print("ratchet ok")
            return 0
        case Unexplained(bad_raises, bad_configs):
            for r in bad_raises:
                print(f"ratchet: {r.rule} rose {fmt(r.base)} -> {fmt(r.head)}")
            for p in bad_configs:
                print(f"ratchet: guard config changed: {p}")
            print("\nFix the rise, or add these trailers to the final trailer block of a commit message in the range:")
            for r in bad_raises:
                print(r.trailer())
            for p in bad_configs:
                print(f"Guard-config: {p} because <why, 5+ words>")
            return 1
    raise AssertionError(v)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", help="base ref; default: origin's default branch (skips when absent)")
    ap.add_argument("--head", default="HEAD", help="head commit; default HEAD")
    args = ap.parse_args(argv)
    try:
        base = args.base or default_base()
        if base is None:
            print("ratchet skipped: no base ref")
            return 0
        head = git("rev-parse", "--verify", f"{args.head}^{{commit}}").strip()
        return report(verdict(base, head))
    except RatchetError as e:
        print(f"ratchet error (failing closed): {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
