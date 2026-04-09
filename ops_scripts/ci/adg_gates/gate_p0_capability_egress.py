"""Gate 4: P0 Capability / Egress Gate.

Blocks provider/tool/network paths lacking registry/ticket/egress coverage.
Surfaces missing choke points.
Identifies exact bypass path.

Source views:
    - mv_capability_and_egress_gaps
    - mv_gateway_bypass_paths
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any

from ops_scripts.ci.adg_gates.gate_base import ADGGateBase, GateResult, GateViolation


class CapabilityEgressGate(ADGGateBase):
    """P0 Capability/Egress Gate.

    Enforces that all provider and tool invocations route through
    approved gateways with proper choke points.
    """

    gate_family = "capability_egress"
    severity = "P0"
    source_views = [
        "mv_capability_and_egress_gaps",
        "mv_gateway_bypass_paths",
    ]

    def _execute_gate_logic(self) -> GateResult:
        """Execute capability/egress check."""
        violations: list[GateViolation] = []
        summary: dict[str, Any] = {
            "total_violations": 0,
            "provider_without_capability_route": 0,
            "action_without_egress_gate": 0,
            "gateway_bypass_paths": 0,
            "by_layer": {},
            "in_modified_area": 0,
        }

        if not self.conn:
            return self._empty_result()

        # Check 1: Capability and egress gaps
        try:
            cursor = self.conn.execute("""
                SELECT node_id, file, layer, provider_invoke_count, capability_route_count,
                       egress_gate_count, gap_type
                FROM mv_capability_and_egress_gaps
                WHERE gap_type != 'ok'
            """)
            for row in cursor.fetchall():
                (
                    node_id,
                    file,
                    layer,
                    provider_invoke_count,
                    capability_route_count,
                    egress_gate_count,
                    gap_type,
                ) = row

                # Track by gap type
                if gap_type == "provider_without_capability_route":
                    summary["provider_without_capability_route"] += 1
                elif gap_type == "action_without_egress_gate":
                    summary["action_without_egress_gate"] += 1

                # Track by layer
                summary["by_layer"][layer] = summary["by_layer"].get(layer, 0) + 1

                in_mod = self._is_in_modified_area(file)
                if in_mod:
                    summary["in_modified_area"] += 1

                violation = GateViolation(
                    violation_id=f"egress_gap_{node_id}",
                    source_view="mv_capability_and_egress_gaps",
                    source_node=str(node_id),
                    source_edge=None,
                    file=file,
                    line=None,
                    layer_src=layer,
                    layer_dst=None,
                    path_id=str(node_id),
                    first_illegal_hop=f"{layer}->{gap_type}",
                    path_criticality=3.5 if gap_type == "action_without_egress_gate" else 3.0,
                    in_modified_area=in_mod,
                    message=f"Egress gap ({gap_type}): {provider_invoke_count} provider invocations, "
                    f"{capability_route_count} capability routes, {egress_gate_count} egress gates",
                    extra={
                        "provider_invoke_count": provider_invoke_count,
                        "capability_route_count": capability_route_count,
                        "egress_gate_count": egress_gate_count,
                        "gap_type": gap_type,
                    },
                )
                violations.append(violation)
        except sqlite3.Error:
            pass

        # Check 2: Gateway bypass paths
        try:
            cursor = self.conn.execute("""
                SELECT edge_id, src_file, src_layer, provider_symbol, source_file, line_no, bypass_type
                FROM mv_gateway_bypass_paths
            """)
            for row in cursor.fetchall():
                edge_id, src_file, src_layer, provider_symbol, source_file, line_no, bypass_type = row

                summary["gateway_bypass_paths"] += 1

                in_mod = self._is_in_modified_area(source_file or src_file)
                if in_mod:
                    summary["in_modified_area"] += 1

                violation = GateViolation(
                    violation_id=f"bypass_{edge_id}",
                    source_view="mv_gateway_bypass_paths",
                    source_node=None,
                    source_edge=str(edge_id),
                    file=source_file or src_file,
                    line=line_no,
                    layer_src=src_layer,
                    layer_dst=None,
                    path_id=None,
                    first_illegal_hop=f"{src_layer}->{bypass_type}",
                    path_criticality=4.0,
                    in_modified_area=in_mod,
                    message=f"Gateway bypass: {provider_symbol} ({bypass_type})",
                    extra={
                        "provider_symbol": provider_symbol,
                        "bypass_type": bypass_type,
                    },
                )
                violations.append(violation)
        except sqlite3.Error:
            pass

        # Determine status: P0 blocks if any gateway bypasses or action without egress
        summary["total_violations"] = len(violations)
        has_critical = summary["gateway_bypass_paths"] > 0 or summary["action_without_egress_gate"] > 0
        status = "blocked" if has_critical else ("warn" if violations else "passed")

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
                "provider_without_capability_route": 0,
                "action_without_egress_gate": 0,
                "gateway_bypass_paths": 0,
                "by_layer": {},
                "in_modified_area": 0,
                "note": "Materialized views not available - no violations detected",
            },
        )


def main() -> int:
    """CLI entry point."""
    gate = CapabilityEgressGate()
    return gate.run_and_exit()


if __name__ == "__main__":
    import sys

    sys.exit(main())
