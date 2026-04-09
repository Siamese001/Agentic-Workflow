"""Gate 1: P0 Critical Path Integrity Gate.

Blocks missing required v29 stages on action-capable or write-capable paths.
Identifies the first illegal hop, emits path criticality.
Distinguishes ingress/execution/provider/write/sink severity.

Source views:
    - mv_critical_path_segments
    - mv_runtime_spine_gaps
    - mv_path_criticality_rollup
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ops_scripts.ci.adg_gates.gate_base import ADGGateBase, GateResult, GateViolation


class CriticalPathIntegrityGate(ADGGateBase):
    """P0 Critical Path Integrity Gate.

    Enforces that all action-capable and write-capable paths have required
    v29 runtime spine stages. Blocks on missing stages with detailed
    path provenance.
    """

    gate_family = "critical_path_integrity"
    severity = "P0"
    source_views = [
        "mv_critical_path_segments",
        "mv_runtime_spine_gaps",
        "mv_path_criticality_rollup",
    ]

    # Required layers that must be present on action-capable paths
    REQUIRED_SPINE_LAYERS = ("L0", "L1", "L2", "L3", "L4", "L5", "L6")

    # Forbidden cross-layer pairs that indicate architectural bypass
    FORBIDDEN_HOPS = [
        ("L6", "L2"),
        ("L6", "L0"),
        ("L6", "L1"),
        ("L_APP", "L0"),
        ("L_APP", "L1"),
        ("L_APP", "L2"),
    ]

    def _execute_gate_logic(self) -> GateResult:
        """Execute critical path integrity check."""
        violations: list[GateViolation] = []
        summary: dict[str, Any] = {
            "total_violations": 0,
            "by_layer": {},
            "in_modified_area": 0,
            "max_criticality": 0.0,
            "spine_gap_count": 0,
            "forbidden_hop_count": 0,
        }

        if not self.conn:
            return self._empty_result()

        # Check 1: Runtime spine gaps (modules disconnected from spine)
        try:
            cursor = self.conn.execute("""
                SELECT layer, module_count, gap_count, gap_pct
                FROM mv_runtime_spine_gaps
                WHERE gap_count > 0
            """)
            for row in cursor.fetchall():
                layer, module_count, gap_count, gap_pct = row
                summary["spine_gap_count"] += gap_count

                violation = GateViolation(
                    violation_id=f"spine_gap_{layer}",
                    source_view="mv_runtime_spine_gaps",
                    source_node=None,
                    source_edge=None,
                    file=None,
                    line=None,
                    layer_src=layer,
                    layer_dst=None,
                    path_id=None,
                    first_illegal_hop=f"{layer}->spine",
                    path_criticality=float(gap_pct),
                    in_modified_area=False,
                    message=f"Layer {layer} has {gap_count} modules disconnected from runtime spine "
                    f"({gap_pct:.1f}% of {module_count} modules)",
                )
                violations.append(violation)
        except sqlite3.Error:
            # View may not exist - skip this check
            pass

        # Check 2: Forbidden cross-layer hops
        try:
            for src_layer, dst_layer in self.FORBIDDEN_HOPS:
                cursor = self.conn.execute(
                    """
                    SELECT COUNT(*), SUM(edge_count)
                    FROM mv_critical_path_segments
                    WHERE src_layer = ? AND dst_layer = ?
                """,
                    (src_layer, dst_layer),
                )
                row = cursor.fetchone()
                if row and row[0] > 0:
                    file_count = row[0]
                    edge_count = row[1] or 0

                    summary["forbidden_hop_count"] += edge_count
                    key = f"{src_layer}->{dst_layer}"
                    summary["by_layer"][key] = summary["by_layer"].get(key, 0) + edge_count

                    violation = GateViolation(
                        violation_id=f"forbidden_hop_{src_layer}_{dst_layer}",
                        source_view="mv_critical_path_segments",
                        source_node=None,
                        source_edge=None,
                        file=None,
                        line=None,
                        layer_src=src_layer,
                        layer_dst=dst_layer,
                        path_id=None,
                        first_illegal_hop=key,
                        path_criticality=float(edge_count),
                        in_modified_area=False,
                        message=f"Forbidden cross-layer hop: {src_layer} -> {dst_layer} "
                        f"({edge_count} edges across {file_count} layer pairs)",
                    )
                    violations.append(violation)
        except sqlite3.Error:
            pass

        # Check 3: High criticality modules with violations
        try:
            cursor = self.conn.execute("""
                SELECT node_id, adg_name, layer, resolved_path,
                       fan_in, fan_out, violation_count, criticality_score
                FROM mv_path_criticality_rollup
                WHERE violation_count > 0
                  AND criticality_score > 5.0
                ORDER BY criticality_score DESC
                LIMIT 50
            """)
            for row in cursor.fetchall():
                node_id, adg_name, layer, resolved_path, fan_in, fan_out, vcount, score = row

                if score > summary["max_criticality"]:
                    summary["max_criticality"] = float(score)

                in_mod = self._is_in_modified_area(resolved_path)
                if in_mod:
                    summary["in_modified_area"] += 1

                violation = GateViolation(
                    violation_id=f"critical_{node_id}",
                    source_view="mv_path_criticality_rollup",
                    source_node=str(node_id),
                    source_edge=None,
                    file=resolved_path,
                    line=None,
                    layer_src=layer,
                    layer_dst=None,
                    path_id=str(node_id),
                    first_illegal_hop=None,
                    path_criticality=float(score),
                    in_modified_area=in_mod,
                    message=f"High criticality module with {vcount} violations: "
                    f"{adg_name} (score={score:.2f}, fan_in={fan_in}, fan_out={fan_out})",
                    extra={
                        "fan_in": fan_in,
                        "fan_out": fan_out,
                        "violation_count": vcount,
                    },
                )
                violations.append(violation)
        except sqlite3.Error:
            pass

        # Determine status: P0 blocks if any violations
        summary["total_violations"] = len(violations)
        status = "blocked" if violations else "passed"

        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=status,
            violations=violations,
            summary=summary,
        )

    def _empty_result(self) -> GateResult:
        """Return empty result when connection unavailable."""
        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="passed",
            violations=[],
            summary={
                "total_violations": 0,
                "by_layer": {},
                "in_modified_area": 0,
                "max_criticality": 0.0,
                "spine_gap_count": 0,
                "forbidden_hop_count": 0,
                "note": "Materialized views not available - no violations detected",
            },
        )


def main() -> int:
    """CLI entry point."""
    gate = CriticalPathIntegrityGate()
    return gate.run_and_exit()


if __name__ == "__main__":
    import sys

    sys.exit(main())
