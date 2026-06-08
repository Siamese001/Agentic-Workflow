#!/usr/bin/env python3
"""
post_agent_plan_supersession_retire.py — auto-retire superseded predecessor
plans in Notion (Status->Retired + Summary note + posted comment).

Runs in the post-agent governance chain (dispatched from
after_agent_governance_dispatch.py via post_agent_dispatch.py). After each agent
response it:

  1. scans plan files for ``## Supersedes`` / ``supersedes:`` declarations,
  2. for each named predecessor still in a non-terminal Notion status,
  3. patches it to ``Retired``, appends a dated Summary note, and posts a
     supersession comment linking the successor.

Fail policy: OPEN — always exits 0; any error is logged, never raised into the
turn. No-op when ``NOTION_TOKEN`` is absent (the CI sweep gate
``check_plan_supersession_consistency.py`` covers offline/cross-session cases).

Flags / env:
  --dry-run                       : report intended actions, no writes
  --execute                       : force writes (default when NOTION_TOKEN set)
  PLAN_SUPERSESSION_RETIRE_BYPASS=1 : disable entirely (exit 0)

Audit log: artifacts/governance/plan_supersession_audit.jsonl
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import _plan_supersession as sup  # noqa: E402


def _drain_stdin() -> None:
    # Post-agent scripts are fed the response on stdin. We don't need the text
    # (the engine scans plan files), but draining keeps the dispatch contract.
    try:
        if not sys.stdin.isatty():
            sys.stdin.read()
    except (OSError, ValueError):
        pass


def main() -> int:
    if os.environ.get("PLAN_SUPERSESSION_RETIRE_BYPASS") == "1":
        return 0

    _drain_stdin()

    # CLI override; otherwise execute only when a token is available.
    argv = sys.argv[1:]
    if "--dry-run" in argv:
        execute = False
    elif "--execute" in argv:
        execute = True
    else:
        execute = bool(sup.load_token())

    try:
        declarations = sup.discover_declarations()
        if not declarations:
            return 0
        if not execute and not sup.load_token():
            # Nothing to verify against; stay silent (sweep gate owns offline).
            return 0
        result = sup.reconcile(execute=execute, declarations=declarations)
    except Exception as err:  # guardian: allow-broad-exception -- post-agent fail-soft; must never break the turn
        print(f"[plan_supersession_retire] skipped: {err}", file=sys.stderr)
        return 0

    retired = result.retired
    if retired:
        verb = "retired" if execute else "would retire"
        for a in retired:
            print(
                f"[plan_supersession_retire] {verb} predecessor '{a.predecessor}' "
                f"superseded by '{a.successor}' ({a.detail})",
                file=sys.stderr,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
