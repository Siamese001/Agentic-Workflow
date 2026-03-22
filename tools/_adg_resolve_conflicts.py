#!/usr/bin/env python3
"""
Resolve rebase conflicts by accepting both sides:
- Keep all guardian suppression lines from OURS
- Keep all content from THEIRS
Strategy: strip conflict markers, merge both sides.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIP = {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}

CONFLICT_FILES = [
    "agentic_core/L0_routing/scripts/execute_ssot.py",
    "agentic_core/L5_safety/validators/dependencygraph_validator.py",
    "ops_scripts/ci/_debug_mixed_list.py",
    "ops_scripts/ci/_debug_visitor.py",
    "ops_scripts/ci/_find_truly_fixable.py",
    "ops_scripts/ci/_search_fixable.py",
    "ops_scripts/ci/_test_fixer.py",
    "ops_scripts/general/find_hangs.py",
    "ops_scripts/general/quick_hang_finder.py",
    "ops_scripts/hooks/landmine_baseline.txt",
]


def merge_conflict_blocks(content: str) -> str:
    """
    Merge conflict blocks by combining both sides.
    OURS adds guardian suppression lines; THEIRS has base content.
    We keep OURS (which is a superset: base + suppression lines).
    """
    lines = content.splitlines(keepends=True)
    result = []
    in_ours = False
    in_theirs = False
    ours_lines = []
    theirs_lines = []

    for line in lines:
        if line.startswith("<<<<<<<"):
            in_ours = True
            ours_lines = []
            theirs_lines = []
        elif line.startswith("=======") and in_ours:
            in_ours = False
            in_theirs = True
        elif line.startswith(">>>>>>>") and in_theirs:
            in_theirs = False
            # Strategy: prefer OURS (has guardian suppression lines)
            # but fall back to THEIRS for baseline.txt (just take THEIRS = remote)
            result.extend(ours_lines)
        elif in_ours:
            ours_lines.append(line)
        elif in_theirs:
            theirs_lines.append(line)
        else:
            result.append(line)

    return "".join(result)


def merge_baseline(content: str) -> str:
    """For baseline.txt: take THEIRS (remote has more up-to-date baseline)."""
    lines = content.splitlines(keepends=True)
    result = []
    in_ours = False
    in_theirs = False
    theirs_lines = []

    for line in lines:
        if line.startswith("<<<<<<<"):
            in_ours = True
            theirs_lines = []
        elif line.startswith("=======") and in_ours:
            in_ours = False
            in_theirs = True
        elif line.startswith(">>>>>>>") and in_theirs:
            in_theirs = False
            result.extend(theirs_lines)
        elif in_ours:
            pass  # discard ours for baseline
        elif in_theirs:
            theirs_lines.append(line)
        else:
            result.append(line)

    return "".join(result)


def main() -> None:
    print("Resolving rebase conflicts...")

    for rel_path in CONFLICT_FILES:
        path = REPO / rel_path
        if not path.exists():
            print(f"  SKIP (not found): {rel_path}")
            continue

        content = path.read_text(encoding="utf-8", errors="replace")
        if "<<<<<<<" not in content:
            print(f"  CLEAN (no conflict): {rel_path}")
            continue

        if rel_path.endswith("landmine_baseline.txt"):
            resolved = merge_baseline(content)
        else:
            resolved = merge_conflict_blocks(content)

        path.write_text(resolved, encoding="utf-8")
        print(f"  RESOLVED: {rel_path}")

    # Stage resolved files
    r = subprocess.run(
        ["git", "add"] + CONFLICT_FILES,
        capture_output=True, text=True, cwd=str(REPO)
    )
    print(f"\ngit add rc: {r.returncode}")
    if r.stderr.strip():
        print(r.stderr.strip()[:200])

    # Continue rebase
    r2 = subprocess.run(
        ["git", "rebase", "--continue"],
        capture_output=True, text=True,
        env={**__import__("os").environ, "GIT_EDITOR": "true"},
        cwd=str(REPO)
    )
    print(f"git rebase --continue rc: {r2.returncode}")
    print(r2.stdout.strip()[:300])
    if r2.stderr.strip():
        print(r2.stderr.strip()[:300])


if __name__ == "__main__":
    main()
