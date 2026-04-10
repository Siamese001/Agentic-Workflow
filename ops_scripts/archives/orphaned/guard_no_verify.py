#!/usr/bin/env python3
"""
Guard against unauthorized --no-verify bypasses.

Enforcement:
- Blocks commits made with --no-verify unless explicitly authorized
- Requires bypass justification in commit message
- Logs all bypass attempts for audit trail

Constitutional Authority: .windsurfrules §1.4 (zero-tolerance for test skipping)
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "guard_no_verify", "uwg_governed_write")
_emit_writes_through("p1", "guard_no_verify", "uwg_governed_write_2")
_emit_pulls_context("p1", "guard_no_verify", "context_retrieval")
_emit_pulls_context("p1", "guard_no_verify", "context_retrieval_2")
emit_determinism_digest("trace_guard_no_verify", "guard_no_verify_dispatch")
emit_determinism_digest("trace_guard_no_verify", "guard_no_verify_complete")
_emit_validated_by_safety_plane("p1", "guard_no_verify", "safety_validation")

# Minimum justification length (characters)
MIN_JUSTIFICATION_LENGTH = 20

# Test result artifact path
TEST_RESULT_ARTIFACT = Path("artifacts/adg_ci_lane_gate_result.json")

# Bypass audit log
BYPASS_AUDIT_LOG = Path("artifacts/bypass_audit.jsonl")


def check_bypass_authorization(commit_msg_file: str) -> bool:
    """
    Check if --no-verify bypass is authorized.

    Returns:
        True if authorized or not a bypass, False if unauthorized bypass detected
    """
    # Read commit message
    commit_msg_path = Path(commit_msg_file)
    if not commit_msg_path.exists():
        return True  # Not a commit, allow

    commit_msg = commit_msg_path.read_text(encoding="utf-8")

    # Check for bypass authorization marker
    bypass_pattern = r"BYPASS-AUTHORIZED:\s*(.+)"
    match = re.search(bypass_pattern, commit_msg, re.MULTILINE)

    if match:
        justification = match.group(1).strip()
        if len(justification) < MIN_JUSTIFICATION_LENGTH:
            print(f"❌ BYPASS-AUTHORIZED justification too short (min {MIN_JUSTIFICATION_LENGTH} chars)")
            print(f"   Got ({len(justification)} chars): {justification}")
            return False

        # Log the authorized bypass
        log_bypass(commit_msg, justification, authorized=True)
        print(f"✅ Bypass authorized: {justification[:60]}...")
        return True

    # Check if this appears to be a bypass attempt
    if is_bypass_attempt():
        print("❌ CRITICAL: Commit appears to bypass pre-commit hooks")
        print()
        print("   If you used --no-verify, you must include:")
        print("   BYPASS-AUTHORIZED: <detailed justification>")
        print("   in your commit message.")
        print()
        print("   Example:")
        print("   fix: Emergency hotfix for production outage")
        print()
        print("   BYPASS-AUTHORIZED: Production is down, pre-commit hook has a bug")
        print("   that blocks all commits. This commit fixes the hook itself.")
        print("   Post-commit validation will run in CI. Ticket: INCIDENT-1234")
        print()

        # Log the unauthorized bypass attempt
        log_bypass(commit_msg, "UNAUTHORIZED", authorized=False)
        return False

    return True


def is_bypass_attempt() -> bool:
    """
    Heuristically detect if this commit bypassed pre-commit hooks.

    Checks:
    1. Are there Python files in the commit?
    2. Was the test result artifact updated recently?
    """
    # Check if there are Python files being committed
    if not has_python_files_staged():
        return False  # No Python files, bypass detection not applicable

    # Check if test results were updated recently (within last 60 seconds)
    if tests_were_run_recently():
        return False  # Tests ran, not a bypass

    # Python files staged but tests didn't run = likely bypass
    return True


def has_python_files_staged() -> bool:
    """Check if any Python files are staged for commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        staged_files = result.stdout.splitlines()
        return any(f.endswith(".py") for f in staged_files)
    except subprocess.CalledProcessError:
        return False


def tests_were_run_recently() -> bool:
    """Check if test artifacts were updated in the last 60 seconds."""
    if not TEST_RESULT_ARTIFACT.exists():
        return False

    # Check if file was modified in last 60 seconds
    import time

    mtime = TEST_RESULT_ARTIFACT.stat().st_mtime
    age_seconds = time.time() - mtime
    return age_seconds < 60


def log_bypass(commit_msg: str, justification: str, authorized: bool) -> None:
    """Log bypass attempt for audit trail."""
    BYPASS_AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "authorized": authorized,
        "justification": justification,
        "commit_msg_preview": commit_msg[:200],
        "user": os.environ.get("USER") or os.environ.get("USERNAME") or "unknown",
    }

    with open(BYPASS_AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: guard_no_verify.py <commit-msg-file>", file=sys.stderr)
        return 1

    commit_msg_file = sys.argv[1]

    if check_bypass_authorization(commit_msg_file):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
