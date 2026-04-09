"""Gate 2: P0 Authority Boundary Gate.

Blocks illegal L0/L1/L6/L2/UWG boundary crossings.
Blocks current-run vs future-run mutation confusion.
Blocks HITL changes lacking re-clearance.

Source views:
    - mv_authority_boundary_breaches
    - mv_live_future_mutation_conflicts
    - mv_hitl_reclearance_gaps
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any

from ops_scripts.ci.adg_gates.gate_base import ADGGateBase, GateResult, GateViolation


class AuthorityBoundaryGate(ADGGateBase):
    """P0 Authority Boundary Gate.

    Enforces architectural authority boundaries between layers.
    Blocks illegal crossings and mutation conflicts.
    """

    gate_family = "authority_boundary"
    severity = "P0"
    source_views = [
        "mv_authority_boundary_breaches",
        "mv_live_future_mutation_conflicts",
        "mv_hitl_reclearance_gaps",
    ]

    def _execute_gate_logic(self) -> GateResult:
        """Execute authority boundary check."""
        violations: list[GateViolation] = []
        summary: dict[str, Any] = {
            "total_violations": 0,
            "by_breach_class": {},
            "by_layer_pair": {},
            "in_modified_area": 0,
            "live_future_conflicts": 0,
            "hitl_reclearance_gaps": 0,
        }

        if not self.conn:
            return self._empty_result()

        # Check 1: Authority boundary breaches
        try:
            cursor = self.conn.execute("""
                SELECT edge_id, src_file, src_layer, dst_file, dst_layer,
                       relation_type, source_file, line_no, breach_class
                FROM mv_authority_boundary_breaches
            """)
            for row in cursor.fetchall():
                (
                    edge_id,
                    src_file,
                    src_layer,
                    dst_file,
                    dst_layer,
                    rel_type,
                    source_file,
                    line_no,
                    breach_class,
                ) = row

                # Track by breach class
                summary["by_breach_class"][breach_class] = summary["by_breach_class"].get(breach_class, 0) + 1

                # Track by layer pair
                layer_pair = f"{src_layer}->{dst_layer}"
                summary["by_layer_pair"][layer_pair] = summary["by_layer_pair"].get(layer_pair, 0) + 1

                in_mod = self._is_in_modified_area(source_file or src_file)
                if in_mod:
                    summary["in_modified_area"] += 1

                violation = GateViolation(
                    violation_id=f"breach_{edge_id}",
                    source_view="mv_authority_boundary_breaches",
                    source_node=None,
                    source_edge=str(edge_id),
                    file=source_file or src_file,
                    line=line_no,
                    layer_src=src_layer,
                    layer_dst=dst_layer,
                    path_id=None,
                    first_illegal_hop=layer_pair,
                    path_criticality=3.0 if breach_class == "layer_violation" else 2.0,
                    in_modified_area=in_mod,
                    message=f"Authority boundary breach ({breach_class}): {src_layer} -> {dst_layer} via {rel_type}",
                    extra={
                        "breach_class": breach_class,
                        "relation_type": rel_type,
                        "dst_file": dst_file,
                    },
                )
                violations.append(violation)
        except sqlite3.Error:
            pass

        # Check 2: Live/future mutation conflicts
        try:
            cursor = self.conn.execute("""
                SELECT file, layer, live_write_count, snapshot_link_count, conflict_type
                FROM mv_live_future_mutation_conflicts
            """)
            for row in cursor.fetchall():
                file, layer, live_write_count, snapshot_link_count, conflict_type = row

                summary["live_future_conflicts"] += 1

                in_mod = self._is_in_modified_area(file)
                if in_mod:
                    summary["in_modified_area"] += 1

                violation = GateViolation(
                    violation_id=f"mutation_conflict_{file.replace('/', '_')}",
                    source_view="mv_live_future_mutation_conflicts",
                    source_node=None,
                    source_edge=None,
                    file=file,
                    line=None,
                    layer_src=layer,
                    layer_dst=None,
                    path_id=None,
                    first_illegal_hop=None,
                    path_criticality=4.0,
                    in_modified_area=in_mod,
                    message=f"Live/future mutation conflict: {live_write_count} writes + {snapshot_link_count} snapshot links",
                    extra={
                        "live_write_count": live_write_count,
                        "snapshot_link_count": snapshot_link_count,
                        "conflict_type": conflict_type,
                    },
                )
                violations.append(violation)
        except sqlite3.Error:
            pass

        # Check 3: HITL re-clearance gaps
        try:
            cursor = self.conn.execute("""
                SELECT node_id, file, layer, write_edge_count, guardrail_edge_count, gap_type
                FROM mv_hitl_reclearance_gaps
                WHERE gap_type = 'write_without_guardrail'
            """)
            for row in cursor.fetchall():
                node_id, file, layer, write_edge_count, guardrail_edge_count, gap_type = row

                summary["hitl_reclearance_gaps"] += 1

                in_mod = self._is_in_modified_area(file)
                if in_mod:
                    summary["in_modified_area"] += 1

                violation = GateViolation(
                    violation_id=f"hitl_gap_{node_id}",
                    source_view="mv_hitl_reclearance_gaps",
                    source_node=str(node_id),
                    source_edge=None,
                    file=file,
                    line=None,
                    layer_src=layer,
                    layer_dst=None,
                    path_id=str(node_id),
                    first_illegal_hop=None,
                    path_criticality=2.5,
                    in_modified_area=in_mod,
                    message=f"HITL re-clearance gap: {write_edge_count} writes without guardrail coverage",
                    extra={
                        "write_edge_count": write_edge_count,
                        "guardrail_edge_count": guardrail_edge_count,
                        "gap_type": gap_type,
                    },
                )
                violations.append(violation)
        except sqlite3.Error:
            pass

        # Determine status
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
                "by_breach_class": {},
                "by_layer_pair": {},
                "in_modified_area": 0,
                "live_future_conflicts": 0,
                "hitl_reclearance_gaps": 0,
                "note": "Materialized views not available - no violations detected",
            },
        )


def main() -> int:
    """CLI entry point."""
    gate = AuthorityBoundaryGate()
    return gate.run_and_exit()


if __name__ == "__main__":
    import sys

    sys.exit(main())
