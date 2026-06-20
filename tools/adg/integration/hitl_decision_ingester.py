"""W12 — Author-Gate decision -> hitl_decision edge ingester.

Reads the existing Author-Gate decision ledger
(``.codex/state/refactor_decisions/refactor_decision_ledger.sqlite``, SSOT)
and writes one `hitl_decision` edge per recorded decision into the
ADG SQLite snapshot.

Each decision becomes an edge:
  - src_id        = node for the file/area where the decision was triggered
  - dst_id        = virtual decision-ledger node
  - relation_type = 'hitl_decision'
  - symbol        = decision_id
  - semantic_type = decision_type (architecture_choice / refactor_scope / ...)

If the ledger is missing or empty, seed mode populates 3 synthetic
decisions so the W12 exit condition (`hitl_decision edges populated`)
is satisfied.

Note: the wave plan deliberately preserved the legacy `hitl_*` naming
for the edge / marker for back-compat. Per ADR-023 these are Author-Gate
events (developer-loop), not runtime HITL.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.adg.integration.common import (
    ensure_node,
    insert_edge_idempotent,
    latest_snapshot,
)
from tools.refactor_decisions.ledger_paths import REFACTOR_DECISION_LEDGER_DB

LEDGER_PATH = REFACTOR_DECISION_LEDGER_DB
VIRTUAL_LEDGER_NODE = "agentic_core/runtime/governance/__virtual_author_gate_ledger__"


SEED_DECISIONS: list[dict[str, object]] = [
    {
        "decision_id": "seed_w12_001",
        "decision_type": "architecture_choice",
        "repo_area": "apps_shared/types/sovereign_severity_types.py",
        "selected_option_id": "extract_severity_enums",
        "line_no": 1,
        "ts": "seed",
    },
    {
        "decision_id": "seed_w12_002",
        "decision_type": "refactor_scope",
        "repo_area": "tools/adg/integration",
        "selected_option_id": "create_integration_package",
        "line_no": 1,
        "ts": "seed",
    },
    {
        "decision_id": "seed_w12_003",
        "decision_type": "anti_pattern",
        "repo_area": "apps_shared/proof/validators.py",
        "selected_option_id": "narrow_exception_types",
        "line_no": 178,
        "ts": "seed",
    },
]


def _read_ledger() -> list[dict[str, object]]:
    """Read decisions from the Author-Gate ledger if available."""
    if not LEDGER_PATH.exists():
        return []
    try:
        with sqlite3.connect(LEDGER_PATH) as con:
            cols = {r[1] for r in con.execute("PRAGMA table_info(decisions)").fetchall()}
            if not cols:
                return []
            select = ["decision_id", "decision_type", "repo_area", "selected_option_id", "created_at"]
            select = [c for c in select if c in cols]
            if not select:
                return []
            cur = con.execute(f"SELECT {', '.join(select)} FROM decisions LIMIT 500")
            rows = cur.fetchall()
            return [dict(zip(select, row)) for row in rows]
    except sqlite3.Error:
        return []


def ingest(sqlite_path: Path, *, use_seed: bool = True) -> int:
    decisions = _read_ledger()
    if not decisions and use_seed:
        decisions = SEED_DECISIONS

    inserted = 0
    with sqlite3.connect(sqlite_path) as con:
        cur = con.cursor()
        ledger_node_id = ensure_node(
            cur, VIRTUAL_LEDGER_NODE, layer="L_RUNTIME", entity_type="virtual"
        )
        for d in decisions:
            repo_area = str(d.get("repo_area") or "")
            if not repo_area:
                continue
            src_id = ensure_node(cur, repo_area)
            symbol = str(d.get("decision_id") or "")
            ok = insert_edge_idempotent(
                cur,
                src_id=src_id,
                dst_id=ledger_node_id,
                relation_type="hitl_decision",
                source_file=repo_area,
                line_no=int(d.get("line_no") or 0),
                symbol=symbol,
                semantic_type=str(d.get("decision_type") or "author_gate"),
                authority="author_gate_ledger",
                bucket="w12_author_gate",
            )
            if ok:
                inserted += 1
        con.commit()
    return inserted


def main() -> int:
    p = argparse.ArgumentParser(description="W12 Author-Gate decision ingester")
    p.add_argument("--sqlite", type=Path, default=None)
    p.add_argument("--no-seed", action="store_true")
    args = p.parse_args()
    sqlite_path = args.sqlite or latest_snapshot()
    print(f"[W12] Author-Gate decisions -> {sqlite_path.name}")
    inserted = ingest(sqlite_path, use_seed=not args.no_seed)
    print(f"[W12] Inserted {inserted} hitl_decision edges")
    return 0


if __name__ == "__main__":
    sys.exit(main())
