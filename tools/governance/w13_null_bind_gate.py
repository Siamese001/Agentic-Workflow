#!/usr/bin/env python3
"""W1.3 read-only null/unknown/no-bind audit for high-churn decision types.

Plan: author-gate-feedback-loop-d4e8f1 phase W1.3.

Inspects ``refactor_decision_ledger.sqlite`` **without mutating** it. Emits JSON
containing counts and a verdict for operator/analytics use. **Advisory only** —
does not change Author-Gate, HITL, or CI behavior.

High-churn definition: ``decision_type`` values with at least ``--churn-min``
total decision rows (default: 5).

``high_churn_null_bind_count``: among decisions in those types, rows where the
outcome indicates missing or weak bind signal for learning hygiene:
  - no ``decision_outcomes`` row, OR
  - ``bind_confidence`` IS NULL and ``outcome_bind_tier`` NULL/empty, OR
  - ``outcome_bind_tier`` in (``unknown_bind``, ``no_bind``)

``disputed_bind`` rows are counted separately and **excluded** from
``high_churn_null_bind_count`` (distinct hygiene dimension).

Usage::
    python tools/governance/w13_null_bind_gate.py
    python tools/governance/w13_null_bind_gate.py --out artifacts/governance/author_gate_feedback_loop/custom.json
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.refactor_decisions.ledger_paths import REFACTOR_DECISION_LEDGER_DB  # noqa: E402

PLAN_ID = "author-gate-feedback-loop-d4e8f1"
WAVE = "W1.3"


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (name,)
    ).fetchone()
    return row is not None


def _outcome_columns(conn: sqlite3.Connection) -> set[str]:
    try:
        return {r[1] for r in conn.execute("PRAGMA table_info(decision_outcomes)").fetchall()}
    except sqlite3.Error:
        return set()


def run_audit(
    db_path: Path,
    *,
    churn_min: int,
    fail_over: int,
    warn_over: int,
) -> dict[str, Any]:
    checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    base: dict[str, Any] = {
        "plan_id": PLAN_ID,
        "wave": WAVE,
        "ledger_path": str(db_path.resolve()),
        "checked_at_utc": checked_at,
        "advisory_only": True,
        "no_author_gate_weakening": True,
        "threshold": {
            "churn_min_rows_per_type": churn_min,
            "fail_high_churn_null_bind_over": fail_over,
            "warn_high_churn_null_bind_over": warn_over,
        },
    }

    if not db_path.exists():
        base.update(
            {
                "total_decisions": 0,
                "null_bind_count": 0,
                "disputed_bind_count": 0,
                "unknown_bind_count": 0,
                "no_bind_count": 0,
                "high_churn_null_bind_count": 0,
                "high_churn_types": [],
                "verdict": "PASS",
                "note": "ledger_missing — no rows to audit",
            }
        )
        return base

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=10)
    try:
        conn.row_factory = sqlite3.Row
        if not _table_exists(conn, "decisions"):
            raise RuntimeError("decisions table missing")

        total = int(conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0])  # type: ignore[index]

        if not _table_exists(conn, "decision_outcomes"):
            base.update(
                {
                    "total_decisions": total,
                    "null_bind_count": total,
                    "disputed_bind_count": 0,
                    "unknown_bind_count": 0,
                    "no_bind_count": 0,
                    "high_churn_null_bind_count": total,
                    "high_churn_types": [],
                    "verdict": "WARN",
                    "note": "decision_outcomes table missing — all decisions treated as unbound",
                }
            )
            return base

        ocols = _outcome_columns(conn)
        has_tier = "outcome_bind_tier" in ocols
        has_bind_conf = "bind_confidence" in ocols
        has_disputed = "bind_disputed" in ocols

        type_rows = conn.execute(
            "SELECT decision_type, COUNT(*) AS c FROM decisions "
            "WHERE decision_type IS NOT NULL AND TRIM(decision_type) != '' "
            "GROUP BY decision_type"
        ).fetchall()
        hot_types = {str(r[0]) for r in type_rows if int(r[1]) >= churn_min}
        hot_list = sorted(hot_types)

        disputed_bind_count = 0
        unknown_bind_count = 0
        no_bind_count = 0
        null_bind_count = 0
        high_churn_null_bind_count = 0

        q = """
            SELECT d.decision_id, d.decision_type,
                   o.decision_id AS outcome_decision_id
        """
        if has_bind_conf:
            q += ", o.bind_confidence"
        else:
            q += ", NULL AS bind_confidence"
        if has_tier:
            q += ", o.outcome_bind_tier"
        else:
            q += ", NULL AS outcome_bind_tier"
        if has_disputed:
            q += ", o.bind_disputed"
        else:
            q += ", 0 AS bind_disputed"

        q += """
            FROM decisions d
            LEFT JOIN decision_outcomes o ON o.decision_id = d.decision_id
        """
        for row in conn.execute(q).fetchall():
            dt = row["decision_type"] or ""
            tier_raw = (row["outcome_bind_tier"] or "").strip().lower() if has_tier else ""
            bdis = int(row["bind_disputed"] or 0) if has_disputed else 0
            bconf = row["bind_confidence"]
            outcome_missing = row["outcome_decision_id"] is None

            is_disputed = bdis == 1 or tier_raw == "disputed_bind"
            if is_disputed:
                disputed_bind_count += 1

            is_unknown = tier_raw == "unknown_bind"
            if is_unknown:
                unknown_bind_count += 1

            is_no = tier_raw == "no_bind"
            if is_no:
                no_bind_count += 1

            tier_empty = not tier_raw
            conf_null = bconf is None or (isinstance(bconf, str) and not str(bconf).strip())
            is_null_bind = outcome_missing or (conf_null and tier_empty and not is_disputed)

            if is_null_bind:
                null_bind_count += 1

            weak_signal = (
                outcome_missing
                or (tier_empty and conf_null)
                or tier_raw in ("unknown_bind", "no_bind")
            )
            if dt in hot_types and weak_signal and not is_disputed:
                high_churn_null_bind_count += 1

        if high_churn_null_bind_count > fail_over:
            verdict = "FAIL"
        elif high_churn_null_bind_count > warn_over:
            verdict = "WARN"
        else:
            verdict = "PASS"

        base.update(
            {
                "total_decisions": total,
                "null_bind_count": null_bind_count,
                "disputed_bind_count": disputed_bind_count,
                "unknown_bind_count": unknown_bind_count,
                "no_bind_count": no_bind_count,
                "high_churn_null_bind_count": high_churn_null_bind_count,
                "high_churn_types": hot_list,
                "verdict": verdict,
            }
        )
        return base
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--db", type=Path, default=REFACTOR_DECISION_LEDGER_DB)
    parser.add_argument("--churn-min", type=int, default=5)
    parser.add_argument("--warn-over", type=int, default=0, help="WARN if high_churn_null_bind_count > this")
    parser.add_argument("--fail-over", type=int, default=25)
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write JSON to this path (default: artifacts/.../<stamp>_w13_null_bind_gate.json)",
    )
    args = parser.parse_args()

    out_dir = REPO_ROOT / "artifacts" / "governance" / "author_gate_feedback_loop"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = args.out or (out_dir / f"{stamp}_w13_null_bind_gate.json")

    payload = run_audit(
        args.db.resolve() if args.db.is_absolute() else (REPO_ROOT / args.db).resolve(),
        churn_min=max(1, args.churn_min),
        fail_over=max(0, args.fail_over),
        warn_over=max(-1, args.warn_over),
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(str(out_path.relative_to(REPO_ROOT.resolve())), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
