#!/usr/bin/env python3
"""
check_ledger_integrity.py — CI gate: Author-Gate ledger hash chain is unbroken.

Wraps author_gate_ledger_integrity.verify_chain and emits the canonical CI
format ( PASS / FAIL + forensic reason ).

Exit codes:
    0 = chain verifies end-to-end (or ledger is absent — fresh checkout)
    1 = chain broken at a specific row_id — forensic reason printed to stderr
    2 = integrity library import failure (installation error)

CONSTITUTIONAL
    - No subprocess, pure library call
    - UTF-8 stdio
    - Specific exceptions (ImportError, sqlite3.Error already handled inside lib)
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / ".claude" / "governance/scripts"))

try:
    from author_gate_ledger_integrity import DB_PATH, verify_chain
except ImportError as exc:
    print(f"[check_ledger_integrity] Integrity library import failed: {exc}", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    res = verify_chain(DB_PATH)
    if res.ok:
        if res.total_rows == 0:
            print("[check_ledger_integrity] PASS — ledger absent (fresh state).")
        elif res.total_rows > res.verified_rows:
            # Unsealed rows — advisory only (CI still passes; backfill is local)
            unsealed = res.total_rows - res.verified_rows
            print(
                f"[check_ledger_integrity] PASS — {res.verified_rows}/{res.total_rows} sealed; "
                f"{unsealed} unsealed row(s). Run: python .claude/governance/scripts/"
                f"author_gate_ledger_integrity.py --backfill"
            )
        else:
            print(
                f"[check_ledger_integrity] PASS — {res.verified_rows}/{res.total_rows} "
                f"rows verified, chain intact."
            )
        return 0

    print(
        f"[check_ledger_integrity] FAIL — chain broken at {res.first_broken_id} "
        f"after {res.verified_rows} verified row(s) of {res.total_rows}.",
        file=sys.stderr,
    )
    if res.reason:
        print(f"  reason: {res.reason}", file=sys.stderr)
    print(
        "  Remediation: inspect recent writes. If tamper is ruled out, the row may "
        "have been mutated by a buggy capture or manual edit. Re-run "
        "`--backfill` will NOT fix a broken chain — it only seals NULL-hash rows.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
