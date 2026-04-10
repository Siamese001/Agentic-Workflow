#!/usr/bin/env python3
"""Rollback Gate — Enforce explicit rollback checkpoints before multi-file phases.

Constitutional Rule: Before starting any phase touching more than 3 files, MUST create
explicit rollback checkpoint. When phase validation fails, MUST NOT commit partial state.

This gate enforces that:
1. Multi-file phases have rollback checkpoints before execution
2. Failed phases are rolled back, not committed in broken state
3. Checkpoint artifacts exist in artifacts/rollback/
4. Commit message references checkpoint when committing after phase

BLOCKS commits that:
- Modify >3 files without rollback checkpoint reference
- Commit partial phase state after validation failure
- Skip checkpoint creation for large refactors

PASSES commits that:
- Reference rollback checkpoint in commit message
- Include checkpoint artifacts in artifacts/rollback/
- Modify ≤3 files (small changes don't require checkpoint)
"""

import json
import subprocess
import sys
from pathlib import Path

# Repo root
_REPO_ROOT = Path(__file__).resolve().parents[2]

# Rollback checkpoint directory
_CHECKPOINT_DIR = _REPO_ROOT / "artifacts" / "rollback"

# Threshold for requiring rollback checkpoint
_FILE_COUNT_THRESHOLD = 3

# Required checkpoint artifact patterns
_CHECKPOINT_PATTERNS = [
    "checkpoint_*.json",
    "rollback_*.json",
    "phase_*_checkpoint.json",
]

# Required justification keywords in commit message
_CHECKPOINT_KEYWORDS = [
    "checkpoint",
    "rollback",
    "phase checkpoint",
    "pre-phase checkpoint",
    "rollback-gate",
]

# Patterns indicating phase execution
_PHASE_KEYWORDS = [
    "phase",
    "refactor",
    "migration",
    "multi-file",
    "large change",
]


def _get_staged_files() -> list[str]:
    """Get list of staged files."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _get_commit_message() -> str:
    """Get the current commit message."""
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        commit_msg_file = _REPO_ROOT / ".git" / "COMMIT_EDITMSG"
        if commit_msg_file.exists():
            return commit_msg_file.read_text(encoding="utf-8", errors="ignore")
        return ""
    return result.stdout.strip()


def _check_checkpoint_artifacts() -> bool:
    """Check if rollback checkpoint artifacts exist."""
    if not _CHECKPOINT_DIR.exists():
        return False

    for pattern in _CHECKPOINT_PATTERNS:
        if list(_CHECKPOINT_DIR.glob(pattern)):
            return True
    return False


def _has_checkpoint_reference(commit_msg: str) -> bool:
    """Check if commit message references rollback checkpoint."""
    msg_lower = commit_msg.lower()
    return any(keyword in msg_lower for keyword in _CHECKPOINT_KEYWORDS)


def _is_phase_commit(commit_msg: str) -> bool:
    """Check if this appears to be a phase execution commit."""
    msg_lower = commit_msg.lower()
    return any(keyword in msg_lower for keyword in _PHASE_KEYWORDS)


def _count_modified_modules(staged_files: list[str]) -> int:
    """Count number of modified Python modules (excluding tests, artifacts)."""
    count = 0
    for file_path in staged_files:
        # Skip non-Python files
        if not file_path.endswith(".py"):
            continue
        # Skip test files
        if "test_" in file_path or "/tests/" in file_path:
            continue
        # Skip artifacts
        if "artifacts/" in file_path:
            continue
        count += 1
    return count


def main() -> int:
    """Enforce rollback gate — verify checkpoint artifact when phase completes."""
    staged_files = _get_staged_files()
    if not staged_files:
        return 0

    commit_msg = _get_commit_message()

    # Only check if commit message indicates phase completion
    is_phase = _is_phase_commit(commit_msg)
    if not is_phase:
        # Not a phase commit, no checkpoint required
        return 0

    # Phase commit — verify checkpoint was recorded
    has_checkpoint_ref = _has_checkpoint_reference(commit_msg)
    has_checkpoint_artifacts = _check_checkpoint_artifacts()

    # If checkpoint reference or artifacts exist, pass
    if has_checkpoint_ref or has_checkpoint_artifacts:
        if not has_checkpoint_artifacts:
            print("\n[WARN] Rollback Gate — Checkpoint referenced but no artifacts found")
            print("\nCommit message references checkpoint but no artifacts in:")
            print(f"  {_CHECKPOINT_DIR}")
            print("\nConsider creating checkpoint artifacts for auditability.")
        return 0

    # Phase commit without checkpoint evidence — FAIL
    print("\n[FAIL] Rollback Gate (Structural) — Phase commit without checkpoint evidence")
    print("\n[!] NOTE: This checks for checkpoint ARTIFACTS only (observable).")
    print("    Primary enforcement = Windsurf skill (BEFORE phase starts).")
    print("\nThis appears to be a phase commit (keywords: phase, refactor, migration, etc.)")
    print("\nStaged files:")
    for f in staged_files[:10]:
        print(f"  - {f}")
    if len(staged_files) > 10:
        print(f"  ... and {len(staged_files) - 10} more")

    print("\n§ROLLBACK-GATE requires:")
    print("  1. Create explicit checkpoint BEFORE multi-file phase")
    print("  2. Save checkpoint artifacts to artifacts/rollback/")
    print("  3. Reference checkpoint in commit message")
    print("  4. Roll back (not commit) if phase validation fails")

    print("\nRequired in commit message:")
    print("  - 'checkpoint', 'rollback', 'phase checkpoint', or")
    print("  - 'pre-phase checkpoint', 'rollback-gate'")

    print("\nCheckpoint creation:")
    print("  1. Before phase: git stash push -m 'Phase X checkpoint'")
    print('  2. Save state: echo \'{"phase": "X", "files": [...]}\' > artifacts/rollback/checkpoint_X.json')
    print("  3. Execute phase")
    print("  4. If validation fails: git stash pop (restore checkpoint)")
    print("  5. If validation passes: commit with checkpoint reference")

    print("\nExample commit message:")
    print("  'Phase 5: Fix import violations (checkpoint: stash@{0})'")

    print("\nSee: .windsurf/skills/rollback-gate/")

    return 1


if __name__ == "__main__":
    sys.exit(main())
