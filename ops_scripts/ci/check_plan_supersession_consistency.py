#!/usr/bin/env python3
"""
check_plan_supersession_consistency.py — CI sweep gate (PLAN-SUPERSEDE).

Backstop for the live post-agent hook. The hook can only act on plans visible
in the session that ran it; this sweep re-derives the full picture from every
plan file on disk and checks it against Notion, catching the cross-session /
cross-worktree / Notion-only cases the hook structurally cannot observe (the
exact failure mode in the originating RCA).

Behavior:
  * Scan all plan files for ``## Supersedes`` / ``supersedes:`` declarations.
  * For each named predecessor still in a NON-terminal Notion status, report it
    as an inconsistency (declared-superseded but not Retired).
  * ``--execute`` retires them (Status->Retired + Summary note + comment) via the
    shared engine; default is report-only (dry-run).

Exit policy:
  * No NOTION_TOKEN  -> advisory INFO, exit 0 (cannot verify offline).
  * Inconsistencies found, advisory mode (default) -> exit 0 with WARNING list.
  * Inconsistencies found, PLAN_SUPERSESSION_GATE_FAIL_CLOSED=1 -> exit 1.
  * Bypass entirely: PLAN_SUPERSESSION_GATE_BYPASS=1 -> exit 0.

Run:
  python ops_scripts/ci/check_plan_supersession_consistency.py            # report
  python ops_scripts/ci/check_plan_supersession_consistency.py --execute  # fix
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / ".claude" / "governance" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import _plan_supersession as sup  # noqa: E402


def main() -> int:
    if os.environ.get("PLAN_SUPERSESSION_GATE_BYPASS") == "1":
        print("[PLAN-SUPERSEDE] bypassed via PLAN_SUPERSESSION_GATE_BYPASS=1")
        return 0

    execute = "--execute" in sys.argv[1:]
    declarations = sup.discover_declarations()
    if not declarations:
        print("[PLAN-SUPERSEDE] no '## Supersedes' declarations found — clean.")
        return 0

    decl_count = sum(len(v) for v in declarations.values())
    print(
        f"[PLAN-SUPERSEDE] {len(declarations)} plan(s) declare supersession "
        f"over {decl_count} predecessor(s)."
    )

    if not sup.load_token():
        print(
            "[PLAN-SUPERSEDE] INFO: NOTION_TOKEN not set — cannot verify predecessor "
            "status; skipping (advisory). Set NOTION_TOKEN to enforce."
        )
        return 0

    result = sup.reconcile(execute=execute, declarations=declarations)

    pending = [a for a in result.actions if a.outcome == "would_retire"]
    fixed = [a for a in result.actions if a.outcome == "retired"]
    errors = [a for a in result.actions if a.outcome == "error"]

    for a in fixed:
        print(f"[PLAN-SUPERSEDE] retired '{a.predecessor}' (superseded by '{a.successor}')")
    for a in errors:
        print(f"[PLAN-SUPERSEDE] ERROR on '{a.predecessor}': {a.detail}", file=sys.stderr)

    if not pending and not errors:
        print("[PLAN-SUPERSEDE] consistent — every declared predecessor is terminal.")
        return 0

    for a in pending:
        print(
            f"[PLAN-SUPERSEDE] WARNING: '{a.predecessor}' is declared superseded by "
            f"'{a.successor}' but is still non-terminal ({a.detail}). "
            f"Run with --execute to retire.",
            file=sys.stderr,
        )

    fail_closed = os.environ.get("PLAN_SUPERSESSION_GATE_FAIL_CLOSED") == "1"
    if (pending or errors) and fail_closed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
