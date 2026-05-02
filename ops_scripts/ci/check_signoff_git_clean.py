"""CI gate: refuse Fort Knox signoff compile when the working tree is dirty.

Fort Knox constitutional §32 + plan fortknox-100pct-static-runtime-gap-9a3d4f.md
§GAP-4: a signed report must be reproducible from `git_commit`; a dirty
tree means `git_commit` alone cannot reconstruct the exact inputs that
were signed.

This gate reads `artifacts/certification/final_requirement_signoff_report.json`
and fails closed when `git_dirty == True`, unless
`FORTKNOX_DEV_MODE=1` is set (which acknowledges developer loop).

Exit codes:
    0 — git_dirty=False (or dev mode); safe to promote trust_level >= SIGNED_PROOF
    2 — git_dirty=True (fail-closed)
    3 — HARNESS_ERROR (report missing / unreadable)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = REPO_ROOT / "artifacts" / "certification" / "final_requirement_signoff_report.json"


def main() -> int:
    if os.environ.get("FORTKNOX_DEV_MODE") == "1":
        print("[check_signoff_git_clean] FORTKNOX_DEV_MODE=1 — bypass (dev loop)")
        return 0
    if not REPORT.exists():
        print(f"[check_signoff_git_clean] HARNESS_ERROR: report missing at {REPORT}",
              file=sys.stderr)
        return 3
    try:
        d = json.loads(REPORT.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[check_signoff_git_clean] HARNESS_ERROR: {exc}", file=sys.stderr)
        return 3
    dirty = d.get("git_dirty")
    commit = d.get("git_commit")
    if dirty is None:
        print("[check_signoff_git_clean] HARNESS_ERROR: git_dirty field absent",
              file=sys.stderr)
        return 3
    if dirty is True:
        print(
            f"[check_signoff_git_clean] FAIL_CLOSED: git_dirty=True at compile time "
            f"(git_commit={commit}). Trust-level promotion to SIGNED_PROOF or "
            f"FINAL_SIGNED_CERTIFICATION blocked. Commit all changes, re-run "
            f"`python scripts/compile_requirement_signoff.py`, then re-run this gate. "
            f"To bypass for dev-loop work, set FORTKNOX_DEV_MODE=1.",
            file=sys.stderr,
        )
        return 2
    print(f"[check_signoff_git_clean] PASS: git_commit={commit} git_dirty=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
