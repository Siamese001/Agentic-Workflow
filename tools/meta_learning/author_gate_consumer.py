#!/usr/bin/env python3
"""author_gate_consumer.py — Meta-learning consumer for the Author-Gate ledger.

Plan: `.windsurf/plans/author-gate-hardening-a3b8f2.md` W4.P4.1.

Mirrors the runtime HITL consumer (`tools/meta_learning/run_hitl_consumer.py`)
for the author-loop Author-Gate surface. Reads
`refactor_decision_ledger.sqlite`, joins decisions ↔ outcomes, updates a
per-class Thompson bandit (cell key = (decision_type, reason_code)), and
persists bandit state to
`.windsurf/state/refactor_decisions/bandit_state.json` so
`precedent_injector.py` can read the prior on the next packet emit.

Bandit cell posterior: Beta(α, β)
    α starts at 1 (prior success)
    β starts at 1 (prior failure)
    For each (decision_type, reason_code) pair, every closed outcome updates:
        α += 1 if outcome.success == 1
        β += 1 otherwise
    success := promote_to_pattern=1 AND rollback_required=0 AND regression_found=0.

The bandit_prior surfaced back to the packet builder is
    mean = α / (α + β)
    ci_width = 2 × sqrt(mean × (1 - mean) / (α + β))   # ~95% normal approx

Usage:
    python tools/meta_learning/author_gate_consumer.py --dry-run
    python tools/meta_learning/author_gate_consumer.py --apply
"""

from __future__ import annotations

import argparse
import json
import math
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / ".windsurf" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
STATE_PATH = REPO_ROOT / ".windsurf" / "state" / "refactor_decisions" / "bandit_state.json"


def _success(row: sqlite3.Row) -> bool:
    return bool(row["promote_to_pattern"] and not row["rollback_required"] and not row["regression_found"])


def update_bandit(conn: sqlite3.Connection) -> dict[str, dict[str, float]]:
    """Re-fit the bandit from scratch over all closed outcomes.

    Rebuilding from zero each run is O(n) in #outcomes and removes any risk
    of double-counting when the consumer re-runs. For the expected scale
    (≤10k outcomes over the ledger lifetime) this is trivial.
    """
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """SELECT d.decision_type,
                  COALESCE(d.reason_code, '') AS reason_code,
                  COALESCE(o.promote_to_pattern, 0) AS promote_to_pattern,
                  COALESCE(o.rollback_required, 0)  AS rollback_required,
                  COALESCE(o.regression_found, 0)   AS regression_found
             FROM decisions d
             JOIN decision_outcomes o USING (decision_id)
            WHERE d.decision_type IS NOT NULL"""
    ).fetchall()

    state: dict[str, dict[str, float]] = {}
    for r in rows:
        key = f"{r['decision_type']}|{r['reason_code'] or 'unknown'}"
        cell = state.setdefault(key, {"alpha": 1.0, "beta": 1.0, "n": 0.0})
        cell["n"] += 1
        if _success(r):
            cell["alpha"] += 1
        else:
            cell["beta"] += 1
    # Derive summary stats per cell
    for cell in state.values():
        alpha = cell["alpha"]
        beta = cell["beta"]
        mean = alpha / (alpha + beta)
        cell["mean"] = round(mean, 4)
        if mean in (0.0, 1.0):
            cell["ci95_width"] = 0.0
        else:
            cell["ci95_width"] = round(
                2.0 * math.sqrt(mean * (1.0 - mean) / (alpha + beta)),
                4,
            )
    return state


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--db", default=str(DB_PATH))
    p.add_argument("--state", default=str(STATE_PATH))
    p.add_argument("--apply", action="store_true", help="Persist bandit state; without this, dry-run")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)

    db = Path(args.db)
    if not db.exists():
        print(f"[author_gate_consumer] ledger not found: {db}", file=sys.stderr)
        return 2

    conn = sqlite3.connect(str(db), timeout=10)
    try:
        state = update_bandit(conn)
    finally:
        conn.close()

    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cells": state,
        "cell_count": len(state),
    }
    if args.apply and not args.dry_run:
        state_path = Path(args.state)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps({"state_path": str(state_path), "cells": len(state)}))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
