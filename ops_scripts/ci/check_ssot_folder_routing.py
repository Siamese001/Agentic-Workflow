#!/usr/bin/env python3
"""
check_ssot_folder_routing.py — pre-commit gate for SSOT folder routing (§30).

Reads staged Python files from git index. For each file ADDED in this commit
(status 'A'), runs the canonical SSOT routing helper. Fails the commit
(exit 1) on any violation, prints the canonical target suggestion.

Pre-existing files (status 'M', 'R', 'D') are never checked — the rule
applies to NEW files only, matching the Windsurf hook behavior.

Bypass: SSOT_FOLDER_BYPASS=1 (logged to stderr).

SSOT logic: ``.claude/governance/scripts/_ssot_folder_check.py``. Both this gate and
the Windsurf hook ``pre_write_gate.py`` import from the same helper to
prevent drift.

Constitutional tie-in: §31 (see ``.claude/rules/ssot-folder-enforcement.md``).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    """Locate repo root by walking up to the .git directory."""
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / ".git").exists():
            return parent
    return Path.cwd()


def _import_helper(repo: Path):
    """Import the canonical SSOT helper from .claude/governance/scripts/."""
    helper_dir = repo / ".claude" / "governance/scripts"
    sys.path.insert(0, str(helper_dir))
    try:
        import _ssot_folder_check  # type: ignore[import-not-found]
    except ImportError as exc:
        print(
            f"[check_ssot_folder_routing] FATAL: cannot import "
            f"_ssot_folder_check from {helper_dir}: {exc}",
            file=sys.stderr,
        )
        sys.exit(2)
    return _ssot_folder_check


def _staged_added_files(repo: Path) -> list[str]:
    """Return repo-relative POSIX paths of files ADDED in this commit."""
    try:
        proc = subprocess.run(
            ["git", "diff", "--cached", "--name-status", "--diff-filter=A"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"[check_ssot_folder_routing] FATAL: git diff failed: {exc}", file=sys.stderr)
        sys.exit(2)
    if proc.returncode != 0:
        # No git index (e.g., running outside a commit) — pass.
        return []
    files: list[str] = []
    for line in proc.stdout.splitlines():
        # Format: "A\tpath/to/file.py"
        parts = line.split("\t", 1)
        if len(parts) == 2 and parts[0].strip() == "A":
            files.append(parts[1].strip().replace("\\", "/"))
    return files


def main() -> int:
    repo = _repo_root()
    helper = _import_helper(repo)

    bypass = os.environ.get("SSOT_FOLDER_BYPASS") == "1"

    added = _staged_added_files(repo)
    if not added:
        return 0

    violations = []
    for rel in added:
        if not rel.endswith(".py"):
            continue
        # The CI gate sees ADDED files — by definition not on disk before
        # this commit. Pass exists=False to mirror the new-file semantics.
        v = helper.decide(rel, exists=False)
        if v is not None:
            violations.append(v)

    if not violations:
        return 0

    if bypass:
        print(
            f"[check_ssot_folder_routing] BYPASSED ({len(violations)} violation(s)) "
            f"— SSOT_FOLDER_BYPASS=1 set. Logged for review.",
            file=sys.stderr,
        )
        for v in violations:
            print(f"  - {v.path} -> suggested: {v.suggested}", file=sys.stderr)
        return 0

    print(
        f"[check_ssot_folder_routing] BLOCKED — {len(violations)} new file(s) "
        f"violate SSOT folder routing (constitutional §31).",
        file=sys.stderr,
    )
    for v in violations:
        print(f"\n  ✗ {v.path}", file=sys.stderr)
        print(f"    forbidden: {v.forbidden}", file=sys.stderr)
        print(f"    suggested: {v.suggested}", file=sys.stderr)
        print(f"    reason:    {v.message}", file=sys.stderr)
    print(
        "\nFix: move the new file(s) to the suggested SSOT folder, "
        "or set SSOT_FOLDER_BYPASS=1 if the violation is intentional. "
        "Rule: .claude/rules/ssot-folder-enforcement.md",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
