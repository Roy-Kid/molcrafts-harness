#!/usr/bin/env python3
"""Bump the marketplace version across every plugin + marketplace manifest.

This is the deterministic half of the project-local ``release-bump`` skill
(``/mol:release`` delegates version bumping to it via ``mol_project.release``).
It discovers targets dynamically so it survives plugin add/remove:

- ``.claude-plugin/marketplace.json``            → every ``.plugins[].version``
- ``plugins/*/.claude-plugin/plugin.json``       → ``.version``
- ``plugins/*/.codex-plugin/plugin.json``        → ``.version``

``.agents/plugins/marketplace.json`` has no version field and is left alone.

Every version field must currently agree; the tool refuses to bump a
mismatched tree. It preserves file formatting exactly by replacing only the
``"version": "<old>"`` token, matching the hand-edit done for past releases.

Stdlib only. Usage:

    python3 scripts/bump_version.py <patch|minor|major>   # bump + rewrite
    python3 scripts/bump_version.py --check                # verify agreement only
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

_SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def target_files() -> list[Path]:
    files = [REPO_ROOT / ".claude-plugin" / "marketplace.json"]
    files += sorted((REPO_ROOT / "plugins").glob("*/.claude-plugin/plugin.json"))
    files += sorted((REPO_ROOT / "plugins").glob("*/.codex-plugin/plugin.json"))
    return [f for f in files if f.is_file()]


def versions_in(path: Path) -> list[str]:
    """Every ``version`` value carried in this JSON file, order-independent."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    found: list[str] = []
    if isinstance(payload, dict):
        if isinstance(payload.get("version"), str):  # plugin.json
            found.append(payload["version"])
        for entry in payload.get("plugins", []):  # marketplace.json
            if isinstance(entry, dict) and isinstance(entry.get("version"), str):
                found.append(entry["version"])
    return found


def collect() -> tuple[dict[Path, list[str]], set[str]]:
    per_file: dict[Path, list[str]] = {}
    seen: set[str] = set()
    for path in target_files():
        vs = versions_in(path)
        if vs:
            per_file[path] = vs
            seen.update(vs)
    return per_file, seen


def bump(old: str, part: str) -> str:
    m = _SEMVER.match(old)
    if not m:
        raise SystemExit(f"current version {old!r} is not semver X.Y.Z")
    major, minor, patch = (int(g) for g in m.groups())
    if part == "major":
        major, minor, patch = major + 1, 0, 0
    elif part == "minor":
        minor, patch = minor + 1, 0
    elif part == "patch":
        patch += 1
    else:
        raise SystemExit(f"unknown bump part {part!r} (expected patch|minor|major)")
    return f"{major}.{minor}.{patch}"


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("part", nargs="?", choices=["patch", "minor", "major"])
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify all version fields agree and print the current value; no write.",
    )
    args = parser.parse_args()

    per_file, seen = collect()
    if not per_file:
        raise SystemExit("no version fields found under plugins/ or marketplace.json")
    if len(seen) != 1:
        offenders = ", ".join(
            f"{rel(p)}={vs}" for p, vs in sorted(per_file.items(), key=lambda kv: rel(kv[0]))
        )
        raise SystemExit(f"version fields disagree; refusing to bump: {offenders}")

    (old,) = tuple(seen)

    if args.check or args.part is None:
        print(f"current={old}")
        if args.part is None and not args.check:
            print("no bump part given; use patch|minor|major to rewrite", file=sys.stderr)
            return 2
        return 0

    new = bump(old, args.part)
    token_old = f'"version": "{old}"'
    token_new = f'"version": "{new}"'
    total = 0
    for path in sorted(per_file, key=rel):
        text = path.read_text(encoding="utf-8")
        count = text.count(token_old)
        path.write_text(text.replace(token_old, token_new), encoding="utf-8")
        total += count
        print(f"  {rel(path)}: {count} field(s)")
    print(f"old={old} new={new} fields={total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
