#!/usr/bin/env python3
"""Unified ADG Gate - ADG snapshot freshness check (pre-commit mode).

Default mode (--snapshot-only):
  1. Find latest ADG snapshot in artifacts/adg/
  2. If fresh (< 30 min) → pass silently
  3. If stale or missing → warn, exit 0 (never blocks commits)
  To refresh: python tools/generate_full_adg.py

Legacy mode (no flag, or --force-adg):
  Runs full ADG generation + source-code checks. Use manually or in CI only.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADG_DIR = REPO_ROOT / "artifacts" / "adg"
SNAPSHOT_MAX_AGE_SECONDS = 1800  # 30 minutes

# ADG-relevant file patterns
ADG_RELEVANT_PATTERNS = [
    "agentic_core/**/*.py",
    "tools/generate/**/*.py",
    "tools/adg/**/*.py",
    "config/**/*.yaml",
]


def _check_adg_files_changed() -> bool:
    """Check if ADG-relevant files changed in this commit.

    Returns:
        True if ADG-relevant files changed, False otherwise
    """
    try:
        # Get staged files
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            check=False,  # Don't raise on non-zero exit
        )

        staged_files = result.stdout.strip().split("\n") if result.stdout.strip() else []

        if not staged_files:
            return False

        # Check if any staged files match ADG-relevant patterns
        for pattern in ADG_RELEVANT_PATTERNS:
            for staged_file in staged_files:
                # Simple pattern matching
                if pattern.startswith("agentic_core/") and staged_file.startswith("agentic_core/"):
                    if staged_file.endswith(".py"):
                        return True
                elif pattern.startswith("tools/generate/") and staged_file.startswith("tools/generate/"):
                    if staged_file.endswith(".py"):
                        return True
                elif pattern.startswith("tools/adg/") and staged_file.startswith("tools/adg/"):
                    if staged_file.endswith(".py"):
                        return True
                elif pattern.startswith("config/") and staged_file.startswith("config/"):
                    if staged_file.endswith(".yaml"):
                        return True

        return False

    except OSError as e:
        print(f"[ADG-UNIFIED] Warning: Could not check for ADG file changes: {e}", file=sys.stderr)
        # Default to False (don't generate ADG) on error
        return False


def _run_adg_generation() -> int:
    """Run full ADG generation.

    Returns:
        Exit code from generate_full_adg.py
    """
    print("[ADG-UNIFIED] ADG-relevant files changed. Running full ADG generation...")
    print("[ADG-UNIFIED] This will take ~95 seconds...")

    # Set ADG_SKIP_GIT to prevent auto-commit during pre-commit hook
    # The pre-commit hook will commit the artifacts itself
    import os

    os.environ["ADG_SKIP_GIT"] = "1"

    result = subprocess.run(
        [sys.executable, "tools/generate/generate_full_adg.py"],
        cwd=REPO_ROOT,
        check=False,
    )

    if result.returncode == 0:
        print("[ADG-UNIFIED] ADG generation completed successfully")
    else:
        print("[ADG-UNIFIED] ERROR: ADG generation failed", file=sys.stderr)

    return result.returncode


def _run_python_grep_ban() -> int:
    """Run Python grep ban gate.

    Returns:
        Exit code from adg_python_ban_gate.py
    """
    print("[ADG-UNIFIED] Running Python grep ban check...")

    result = subprocess.run(
        [sys.executable, "ops_scripts/ci/adg_python_ban_gate.py", "--staged"],
        cwd=REPO_ROOT,
        check=False,
    )

    return result.returncode


def _run_yaml_grep_ban() -> int:
    """Run YAML grep ban gate.

    Returns:
        Exit code from adg_yaml_grep_ban_gate.py
    """
    print("[ADG-UNIFIED] Running YAML grep ban check...")

    result = subprocess.run(
        [sys.executable, "ops_scripts/ci/adg_yaml_grep_ban_gate.py", "--staged"],
        cwd=REPO_ROOT,
        check=False,
    )

    return result.returncode


def _run_skip_file_ratchet() -> int:
    """Run skip-file ratchet.

    Returns:
        Exit code from adg_skip_file_ratchet.py
    """
    print("[ADG-UNIFIED] Running skip-file ratchet check...")

    result = subprocess.run(
        [sys.executable, "ops_scripts/ci/adg_skip_file_ratchet.py"],
        cwd=REPO_ROOT,
        check=False,
    )

    return result.returncode


def _check_snapshot_freshness() -> int:
    """Check ADG snapshot age. Warns if stale, never blocks.

    Returns:
        0 always (warn-only)
    """
    if not ADG_DIR.exists():
        print(
            "[ADG-UNIFIED] WARNING: artifacts/adg/ not found — no ADG snapshot exists.",
            file=sys.stderr,
        )
        print("[ADG-UNIFIED] Run: python tools/generate_full_adg.py", file=sys.stderr)
        return 0

    snapshots = sorted(ADG_DIR.glob("adg_snapshot_*.json"))
    if not snapshots:
        print("[ADG-UNIFIED] WARNING: No ADG snapshot found in artifacts/adg/", file=sys.stderr)
        print("[ADG-UNIFIED] Run: python tools/generate_full_adg.py", file=sys.stderr)
        return 0

    latest = snapshots[-1]
    age_seconds = time.time() - latest.stat().st_mtime
    age_minutes = age_seconds / 60

    if age_seconds > SNAPSHOT_MAX_AGE_SECONDS:
        print(
            f"[ADG-UNIFIED] WARNING: ADG snapshot is {age_minutes:.0f}m old (>{SNAPSHOT_MAX_AGE_SECONDS // 60}m threshold).",
            file=sys.stderr,
        )
        print("[ADG-UNIFIED] Run: python tools/generate_full_adg.py", file=sys.stderr)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Unified ADG Gate")
    parser.add_argument(
        "--snapshot-only",
        action="store_true",
        help="Check ADG snapshot freshness only — no generation, no source-code checks",
    )
    parser.add_argument(
        "--force-adg",
        action="store_true",
        help="Force ADG generation even if no ADG files changed",
    )
    args = parser.parse_args()

    if args.snapshot_only:
        return _check_snapshot_freshness()

    print("[ADG-UNIFIED] === Unified ADG Gate ===")

    # Step 1: Check if ADG generation needed
    adg_files_changed = _check_adg_files_changed()
    force_adg = args.force_adg

    if adg_files_changed or force_adg:
        reason = "forced" if force_adg else "ADG-relevant files changed"
        print(f"[ADG-UNIFIED] Reason for ADG generation: {reason}")

        # Run ADG generation
        exit_code = _run_adg_generation()
        if exit_code != 0:
            print("[ADG-UNIFIED] ERROR: ADG generation failed, aborting", file=sys.stderr)
            return exit_code
    else:
        print("[ADG-UNIFIED] No ADG-relevant files changed, skipping ADG generation")
        print("[ADG-UNIFIED] Using existing ADG if available")

    # Step 2: Run source-code checks (NOT done by generate_full_adg.py)
    print("[ADG-UNIFIED] Running source-code checks...")

    # Python grep ban
    exit_code = _run_python_grep_ban()
    if exit_code != 0:
        print("[ADG-UNIFIED] ERROR: Python grep ban check failed", file=sys.stderr)
        return exit_code

    # YAML grep ban
    exit_code = _run_yaml_grep_ban()
    if exit_code != 0:
        print("[ADG-UNIFIED] ERROR: YAML grep ban check failed", file=sys.stderr)
        return exit_code

    # Skip-file ratchet
    exit_code = _run_skip_file_ratchet()
    if exit_code != 0:
        print("[ADG-UNIFIED] ERROR: Skip-file ratchet check failed", file=sys.stderr)
        return exit_code

    print("[ADG-UNIFIED] [OK] All checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
