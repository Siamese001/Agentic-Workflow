#!/usr/bin/env python3
"""Absorb current mv_trace_replay_eval_gaps into trace_replay_eval ratchet baseline."""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE = REPO_ROOT / "artifacts" / "adg" / "ci_ratchets" / "trace_replay_eval_baseline.json"


def _gap_key(layer: str, file: str | None, gap_type: str) -> str:
    return f"{layer}:{file or '<unknown>'}:{gap_type}"


def _resolve_snapshot() -> Path:
    import os

    override = os.environ.get("ADG_SNAPSHOT", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415

    snap = latest_sqlite()
    if snap is None:
        raise FileNotFoundError("no adg_indexed_*.sqlite under artifacts/adg")
    return snap


def main() -> int:
    snapshot = _resolve_snapshot()
    if not snapshot.is_file():
        print(f"missing snapshot: {snapshot}", file=sys.stderr)
        return 2
    gaps: dict[str, bool] = {}
    coverage: dict[str, dict[str, float]] = {}
    with sqlite3.connect(str(snapshot)) as conn:
        for _node_id, file, layer, _ht, _hr, _he, gap_type in conn.execute(
            """
            SELECT node_id, file, layer, has_trace, has_replay_link, has_eval, gap_type
            FROM mv_trace_replay_eval_gaps
            WHERE gap_type != 'ok'
            """
        ):
            gaps[_gap_key(layer, file, gap_type)] = True
        try:
            for layer, action_node_count, eval_covered_count in conn.execute(
                """
                SELECT layer,
                       COUNT(*) AS action_node_count,
                       SUM(CASE WHEN has_eval = 1 THEN 1 ELSE 0 END) AS eval_covered_count
                FROM mv_trace_replay_eval_gaps
                GROUP BY layer
                """
            ):
                pct = (100.0 * eval_covered_count / action_node_count) if action_node_count else 100.0
                coverage[layer] = {
                    "action_node_count": action_node_count,
                    "eval_covered_count": eval_covered_count,
                    "coverage_pct": pct,
                }
        except sqlite3.Error:
            pass
    payload = {
        "gaps": gaps,
        "coverage": coverage,
        "absorbed_at": datetime.now(timezone.utc).isoformat(),
        "snapshot": snapshot.name,
        "gap_count": len(gaps),
    }
    BASELINE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"[trace_replay] wrote {len(gaps)} gap keys to {BASELINE.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
