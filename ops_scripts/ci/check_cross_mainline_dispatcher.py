#!/usr/bin/env python3
"""Gate AUDIT-4 — cross-mainline dispatcher ratchet.

Flags modules that dispatch (via ``imports``/``calls``/``flows_to``/
``controls_flow``) to **three or more distinct MAINLINE layers**
(``L0..L5``) excluding the module's own layer. Such modules concentrate
architectural blast radius — a swallowed failure inside one of them
poisons multiple cognitive/execution/state planes simultaneously.

Distinct from ``check_layer_skip`` which examines single edges; this
gate examines aggregate dispatch patterns. Distinct from
``check_graph_layer_evidence`` which validates plan documents.

Tier R (ratchet). Out of scope: utility-layer callees
(``L_SHARED``/``L_RUNTIME``/``L_TOOLS``/``L_OPS``/``L_APP``/``L_PG``/
``L_SL``/``L_TEST``) are NOT counted toward the threshold — only true
mainline cross-cutting matters.
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .cursor/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    Violation,
    WiringGate,
    cli_exit,
    connect_snapshot,
    latest_snapshot,
)

MAINLINE_LAYERS = ("L0", "L1", "L2", "L3", "L4", "L5")
DISPATCH_RELATIONS = ("imports", "calls", "flows_to", "controls_flow")
THRESHOLD_DISTINCT_MAINLINE = 3


class CrossMainlineDispatcherGate(WiringGate):
    gate_id = "AUDIT_4_cross_mainline_dispatcher"
    tier = "R"
    baseline_filename = "audit_cross_mainline_dispatcher.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        cur = conn.cursor()
        rel_placeholders = ",".join("?" * len(DISPATCH_RELATIONS))
        mainline_placeholders = ",".join("?" * len(MAINLINE_LAYERS))
        cur.execute(
            f"""
            SELECT src_n.resolved_path, src_n.layer,
                   GROUP_CONCAT(DISTINCT dst_n.layer) AS callee_layers,
                   COUNT(*) AS edge_count
            FROM edges e
            JOIN nodes src_n ON src_n.id = e.src_id
            JOIN nodes dst_n ON dst_n.id = e.dst_id
            WHERE e.relation_type IN ({rel_placeholders})
              AND src_n.entity_type = 'module'
              AND src_n.layer IN ({mainline_placeholders})
              AND dst_n.layer IN ({mainline_placeholders})
              AND dst_n.layer != src_n.layer
              AND src_n.resolved_path NOT LIKE 'tests/%'
              AND src_n.resolved_path NOT LIKE 'archives/%'
            GROUP BY src_n.resolved_path, src_n.layer
            HAVING COUNT(DISTINCT dst_n.layer) >= ?
            ORDER BY COUNT(DISTINCT dst_n.layer) DESC, edge_count DESC
            """,
            (*DISPATCH_RELATIONS, *MAINLINE_LAYERS, *MAINLINE_LAYERS, THRESHOLD_DISTINCT_MAINLINE),
        )
        violations: list[Violation] = []
        for path, src_layer, callee_layers_csv, edge_count in cur.fetchall():
            distinct = sorted(set((callee_layers_csv or "").split(",")) - {""})
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=path,
                    rule="dispatches_to_3_or_more_mainline_layers",
                    detail=f"src_layer={src_layer} mainline_callees={distinct} edges={edge_count}",
                    extra={
                        "src_layer": src_layer,
                        "mainline_callee_layers": distinct,
                        "mainline_callee_count": len(distinct),
                        "edge_count": edge_count,
                        "threshold": THRESHOLD_DISTINCT_MAINLINE,
                    },
                )
            )
        return violations


def main() -> int:
    gate = CrossMainlineDispatcherGate()
    if "--seed" in sys.argv:
        conn = connect_snapshot(latest_snapshot())
        try:
            raw = gate.run(conn)
        finally:
            conn.close()
        gate.seed_baseline(len(raw))
        print(f"[{gate.gate_id}] baseline seeded: count={len(raw)}")
        return 0
    result = gate.execute()
    if result.baseline_count is not None:
        print(f"[{gate.gate_id}] current={len(result.violations)} baseline={result.baseline_count}")
    return cli_exit(result)


if __name__ == "__main__":
    sys.exit(main())
