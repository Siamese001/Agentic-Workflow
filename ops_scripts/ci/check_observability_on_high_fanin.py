#!/usr/bin/env python3
"""Gate AUDIT-2 — observability on high-fan-in modules ratchet.

Modules with ``fan_in >= 50`` (per ``mv_hotspot_centrality``) MUST emit
at least one outgoing edge to an observability target — either a node
on layer L6 or a symbol whose name matches a tracing/metric/audit
pattern (``trace``, ``logger``, ``logging``, ``metric``, ``audit``,
``observ``, ``otel``, ``span``, ``emit``, ``MetricsEmission``).

Modules failing this rule are *blind hotspots* — every failure they
swallow propagates to many callers without a forensic trail.

Tier R (ratchet). Baseline locks current count.
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .windsurf/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
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

FANIN_THRESHOLD = 50
MAINLINE_LAYERS = ("L0", "L1", "L2", "L3", "L4", "L5")


class ObservabilityHighFaninGate(WiringGate):
    gate_id = "AUDIT_2_observability_on_high_fanin"
    tier = "R"
    baseline_filename = "audit_observability_high_fanin.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        cur = conn.cursor()
        cur.execute(
            f"""
            SELECT n.id, n.adg_name, n.layer, n.resolved_path,
                   h.fan_in, h.fan_out
            FROM nodes n
            JOIN mv_hotspot_centrality h ON h.node_id = n.id
            WHERE n.entity_type = 'module'
              AND h.fan_in >= ?
              AND n.layer IN ({",".join("?" * len(MAINLINE_LAYERS))})
              AND n.resolved_path NOT LIKE 'tests/%'
              AND n.resolved_path NOT LIKE 'archives/%'
              AND n.resolved_path NOT LIKE '.windsurf/%'
              -- Exclude smoke-test helpers (test scaffolding in production paths)
              AND n.resolved_path NOT LIKE '%/_smoke.py'
              AND n.resolved_path NOT LIKE '%_smoke.py'
              -- Exclude config/registry modules (mostly static data, observability
              -- belongs at the call sites that consume them, not at the module itself)
              AND n.resolved_path NOT LIKE '%/config/%'
              AND n.resolved_path NOT LIKE '%_config.py'
              AND n.resolved_path NOT LIKE '%_registry.py'
              AND n.resolved_path NOT LIKE '%/structure_blueprint/%'
              AND n.id NOT IN (
                  SELECT DISTINCT e.src_id FROM edges e
                  JOIN nodes dst ON dst.id = e.dst_id
                  WHERE dst.layer = 'L6'
                     OR dst.adg_name LIKE '%trace%'
                     OR dst.adg_name LIKE '%logger%'
                     OR dst.adg_name LIKE '%logging%'
                     OR dst.adg_name LIKE '%metric%'
                     OR dst.adg_name LIKE '%audit%'
                     OR dst.adg_name LIKE '%observ%'
                     OR dst.adg_name LIKE '%otel%'
                     OR dst.adg_name LIKE '%span%'
                     OR dst.adg_name LIKE '%emit%'
                     OR dst.adg_name LIKE '%MetricsEmission%'
              )
            ORDER BY h.fan_in DESC
            """,
            (FANIN_THRESHOLD, *MAINLINE_LAYERS),
        )
        violations: list[Violation] = []
        for nid, adg_name, layer, path, fan_in, fan_out in cur.fetchall():
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=path or adg_name,
                    rule="high_fanin_module_has_no_observability_edge",
                    detail=f"layer={layer} fan_in={fan_in} fan_out={fan_out}",
                    extra={
                        "node_id": nid,
                        "layer": layer,
                        "fan_in": fan_in,
                        "fan_out": fan_out,
                        "threshold": FANIN_THRESHOLD,
                    },
                )
            )
        return violations


def main() -> int:
    gate = ObservabilityHighFaninGate()
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
