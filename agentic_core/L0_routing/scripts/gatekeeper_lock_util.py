"""
Gatekeeper Lock - Pre-commit Security Hook

Protects critical infrastructure files from unauthorized modifications.
ArchivalGatekeeper.py is a PROTECTED file that requires explicit override.

USAGE:
    # As pre-commit hook (checks staged files)
    python scripts/security/gatekeeper_lock_util.py

    # With commit message file (for commit-msg stage)
    python scripts/security/gatekeeper_lock_util.py --commit-msg-filename .git/COMMIT_EDITMSG

BYPASS METHODS:
    1. Include '[SECURITY-OVERRIDE]' in commit message
    2. Set environment variable: GATEKEEPER_BYPASS=1
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)
from agentic_core.utils.ast_fuzzy_util import normalize_path

PROTECTED_FILES = ["agentic_core/L5_safety/enforcement/ArchivalGatekeeper.py"]
OVERRIDE_TOKEN = "[SECURITY-OVERRIDE]"
BYPASS_ENV_VAR = "GATEKEEPER_BYPASS"


def get_staged_files() -> list[str]:
    """Get list of staged files from git."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_staged_files", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_staged_files", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "get_staged_files")
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True
        )
        return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except subprocess.CalledProcessError:
        return []


def get_commit_message(commit_msg_file: str | None) -> str:
    """Read commit message from file if provided."""
    if commit_msg_file and Path(commit_msg_file).exists():
        return Path(commit_msg_file).read_text(encoding="utf-8")
    return ""


def check_env_bypass() -> bool:
    """Check if bypass environment variable is set."""
    return os.environ.get(BYPASS_ENV_VAR, "").lower() in ("1", "true", "yes")


def check_commit_message_override(commit_message: str) -> bool:
    """Check if commit message contains override token."""
    return OVERRIDE_TOKEN in commit_message


def main() -> int:
    """TODO: Add documentation for main."""
    parser = argparse.ArgumentParser(description="Gatekeeper Lock - Protect critical files")
    parser.add_argument("--commit-msg-filename", help="Path to commit message file (for commit-msg stage)")
    args = parser.parse_args()
    if check_env_bypass():
        return 0
    staged_files = get_staged_files()
    if not staged_files:
        return 0
    staged_normalized = [normalize_path(f) for f in staged_files]
    protected_normalized = [normalize_path(f) for f in PROTECTED_FILES]
    protected_modified = []
    for protected in protected_normalized:
        for staged in staged_normalized:
            if staged == protected or staged.endswith(protected):
                protected_modified.append(protected)
                break
    if not protected_modified:
        return 0
    commit_message = get_commit_message(args.commit_msg_filename)
    if check_commit_message_override(commit_message):
        for _f in protected_modified:
            pass
        return 0
    for _f in protected_modified:
        pass
    return 1


if __name__ == "__main__":
    sys.exit(main())
