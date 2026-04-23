"""Probe the shape of 'imports' edges in ADG — symbol-level vs module-level."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import importlib  # noqa: E402

_gate_base = importlib.import_module("ops_scripts.ci._adg_wiring_gate_base")
connect_snapshot = _gate_base.connect_snapshot
latest_snapshot = _gate_base.latest_snapshot


def main() -> int:
    conn = connect_snapshot(latest_snapshot())

    print("== edge_kinds for relation_type='imports' ==")
    for row in conn.execute(
        "SELECT edge_kind, COUNT(*) FROM edges WHERE relation_type='imports' "
        "GROUP BY edge_kind ORDER BY 2 DESC"
    ):
        print(f"  {row[0]:30s} {row[1]}")

    print()
    print("== sample imports edges targeting hybrid_recall_stage.py (any node) ==")
    for row in conn.execute(
        """
        SELECT e.edge_kind, e.symbol, dst.entity_type, dst.adg_name
        FROM edges e
        JOIN nodes dst ON dst.id = e.dst_id
        WHERE e.relation_type = 'imports'
          AND dst.resolved_path = 'agentic_core/knowledge/retrieval/hybrid_recall_stage.py'
        LIMIT 10
        """
    ):
        print(f"  {row}")

    print()
    print("== fan-in counts (module vs any-node in module) for C0 stages ==")
    targets = [
        "agentic_core/knowledge/retrieval/retrieval_plan.py",
        "agentic_core/knowledge/gates/preretrieval_gate.py",
        "agentic_core/knowledge/retrieval/hybrid_recall_stage.py",
        "agentic_core/knowledge/retrieval/senior_librarian_reranker.py",
        "agentic_core/knowledge/retrieval/evidence_contract_builder.py",
        "agentic_core/L0_routing/config/path_constants.py",
    ]
    for t in targets:
        n_mod = conn.execute(
            "SELECT COUNT(*) FROM edges e JOIN nodes dst ON dst.id=e.dst_id "
            "WHERE e.relation_type='imports' AND dst.entity_type='module' "
            "AND dst.resolved_path=?",
            (t,),
        ).fetchone()[0]
        n_any = conn.execute(
            "SELECT COUNT(*) FROM edges e JOIN nodes dst ON dst.id=e.dst_id "
            "WHERE e.relation_type='imports' AND dst.resolved_path=?",
            (t,),
        ).fetchone()[0]
        caller_layers_any = conn.execute(
            "SELECT DISTINCT src.layer FROM edges e "
            "JOIN nodes dst ON dst.id=e.dst_id "
            "JOIN nodes src ON src.id=e.src_id "
            "WHERE e.relation_type='imports' AND dst.resolved_path=? AND src.layer IS NOT NULL",
            (t,),
        ).fetchall()
        layers = sorted({r[0] for r in caller_layers_any if r[0]})
        print(f"  {t:65s}  mod_fanin={n_mod:4d}  any_fanin={n_any:4d}  caller_layers={layers}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
