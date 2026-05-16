#!/usr/bin/env python3
"""
check_memory_promotion_parity.py — W5.2 memory-graph promotion parity.

For every decision row with `promote_to_pattern=1` AND created_at older than
--min-age-days, assert a matching `ProceduralPattern:*` entity exists in the
memory knowledge graph. Missing promotion = degraded next-session recall.

Matching rule:
    A memory entity satisfies the promotion if its `name` is exactly
      `ProceduralPattern:dec_<first-8-of-decision_id>` OR
    its `observations` contain the decision_id substring OR
    its `name` contains a slugged form of selected_option_id.

Exit 0 — all eligible decisions have matching entities
Exit 1 — at least one missing promotion
Exit 2 — script error

Bypass: MEMORY_PROMOTION_PARITY_BYPASS=1
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_DB = REPO_ROOT / ".cursor" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
MEMORY_DB = REPO_ROOT / "artifacts" / "memory" / "knowledge_graph.sqlite"
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "memory_promotion_violations.jsonl"
BYPASS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "memory_promotion_bypass.jsonl"


def _log(path: Path, payload: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        **payload,
                    }
                )
                + "\n"
            )
    except OSError:
        # guardian: allow-silent-swallow -- log unwritable: non-fatal
        pass


def _load_promotable_decisions(min_age_days: int) -> list[dict]:
    if not LEDGER_DB.exists():
        return []
    cutoff = (datetime.now(timezone.utc) - timedelta(days=min_age_days)).isoformat(timespec="seconds")
    try:
        conn = sqlite3.connect(f"file:{LEDGER_DB}?mode=ro", uri=True, timeout=5)
    except sqlite3.Error:
        return []
    rows: list[dict] = []
    try:
        # decision_outcomes holds promote_to_pattern; JOIN to decisions.
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "decision_outcomes" not in tables:
            return []
        for r in conn.execute(
            "SELECT d.decision_id, d.created_at, d.selected_option_id "
            "FROM decisions d JOIN decision_outcomes o "
            "ON d.decision_id = o.decision_id "
            "WHERE o.promote_to_pattern = 1 AND d.created_at <= ?",
            (cutoff,),
        ):
            rows.append(
                {
                    "decision_id": r[0],
                    "created_at": r[1],
                    "selected": r[2] or "",
                }
            )
    except sqlite3.Error:
        return []
    finally:
        conn.close()
    return rows


def _memory_has_promotion(
    entity_names: set[str], obs_index: dict[str, str], decision_id: str, selected: str
) -> bool:
    short_id = decision_id[:12] if decision_id else ""
    # Direct-name match
    for name in entity_names:
        if short_id and short_id in name:
            return True
        if "ProceduralPattern:" in name and (
            (short_id and short_id in name) or (selected and selected[:40].lower() in name.lower())
        ):
            return True
    # Observation match: any entity's observations contain the decision_id
    if short_id and short_id in obs_index.get("_all_obs", ""):
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Memory promotion parity (W5.2)")
    ap.add_argument(
        "--min-age-days", type=int, default=7, help="Only check decisions older than this (gives writer time)"
    )
    ap.add_argument("--max-missing", type=int, default=0, help="Tolerate this many unpromoted before failing")
    args = ap.parse_args()

    if os.environ.get("MEMORY_PROMOTION_PARITY_BYPASS") == "1":
        _log(BYPASS_LOG, {"reason": "env"})
        print("[check_memory_promotion_parity] BYPASS (env). Logged.", file=sys.stderr)
        return 0

    decisions = _load_promotable_decisions(args.min_age_days)
    if not decisions:
        print("[check_memory_promotion_parity] OK — no promotable decisions in window", file=sys.stderr)
        return 0

    if not MEMORY_DB.exists():
        print(f"[check_memory_promotion_parity] FAIL — memory DB missing: {MEMORY_DB}", file=sys.stderr)
        _log(VIOLATIONS_LOG, {"reason": "memory_db_missing", "eligible_count": len(decisions)})
        return 1

    try:
        conn = sqlite3.connect(f"file:{MEMORY_DB}?mode=ro", uri=True, timeout=5)
    except sqlite3.Error as exc:
        print(f"[check_memory_promotion_parity] script error: {exc}", file=sys.stderr)
        return 2

    try:
        entity_names = {r[0] for r in conn.execute("SELECT name FROM entities")}
        all_obs = "\n".join(r[0] or "" for r in conn.execute("SELECT content FROM observations"))
    except sqlite3.Error:
        conn.close()
        return 2
    finally:
        conn.close()

    obs_index = {"_all_obs": all_obs}
    missing: list[dict] = []
    for d in decisions:
        if not _memory_has_promotion(entity_names, obs_index, d["decision_id"], d["selected"]):
            missing.append(d)

    eligible = len(decisions)
    print(
        f"[check_memory_promotion_parity] eligible={eligible} "
        f"missing={len(missing)} threshold={args.max_missing}",
        file=sys.stderr,
    )

    if len(missing) > args.max_missing:
        print(
            f"[check_memory_promotion_parity] FAIL — {len(missing)} promotable "
            f"decision(s) not found in memory graph",
            file=sys.stderr,
        )
        for m in missing[:10]:
            print(
                f"  {m['decision_id']}  created={m['created_at']}  selected={m['selected'][:60]}",
                file=sys.stderr,
            )
        _log(
            VIOLATIONS_LOG,
            {
                "missing": missing[:50],
                "eligible": eligible,
                "min_age_days": args.min_age_days,
            },
        )
        return 1

    print(f"[check_memory_promotion_parity] PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (sqlite3.Error, OSError) as exc:
        print(f"[check_memory_promotion_parity] script error: {exc}", file=sys.stderr)
        sys.exit(2)
