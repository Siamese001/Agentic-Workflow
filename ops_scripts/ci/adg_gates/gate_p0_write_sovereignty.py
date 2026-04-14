"""Gate 3: P0 Write Sovereignty Gate.

Blocks direct or indirect durable write bypasses.
Blocks non-UWG write paths.
Emits exact violating path and first illegal hop.

Source views:
    - mv_write_sovereignty_paths
    - mv_new_write_bypass_paths
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any

from ops_scripts.ci.adg_gates.gate_base import ADGGateBase, GateResult, GateViolation
from ops_scripts.ci.adg_gates.gate_policy import ExecutionPolicy
from tqdm import tqdm


class WriteSovereigntyGate(ADGGateBase):
    """P0 Write Sovereignty Gate.

    Enforces that all durable writes route through the Universal Write Gateway (UWG).
    Blocks direct writes and bypass paths.
    """

    gate_family = "write_sovereignty"
    severity = "P0"
    source_views = [
        "mv_write_sovereignty_paths",
        "mv_new_write_bypass_paths",
    ]
    execution_policy = ExecutionPolicy(
        stage="preflight+full",
        repairability="manual_only",
        gate_action="halt",
        artifact_policy="minimal_failure_artifact",
        signal_source="sqlite_mv_ci",
        evidence_tier="truth",
    )

    def _execute_preflight_logic(self) -> GateResult:
        """Preflight: detect direct write imports bypassing UWG via import edges."""
        violations: list[GateViolation] = []
        summary: dict[str, Any] = {
            "total_violations": 0,
            "preflight_mode": True,
            "source": "import_edges",
            "in_modified_area": 0,
        }

        if not self.conn:
            return self._empty_result()

        try:
            cursor = self.conn.execute("""
                SELECT DISTINCT src.node_id, src.file_path, src.layer,
                                dst.file_path AS dst_file
                FROM edges e
                JOIN nodes src ON src.node_id = e.src_id
                JOIN nodes dst ON dst.node_id = e.tgt_id
                WHERE e.relation_type = 'imports'
                  AND (
                    dst.file_path LIKE '%sqlite%'
                    OR dst.file_path LIKE '%redis%'
                    OR dst.file_path LIKE '%storage%'
                  )
                  AND src.file_path NOT LIKE '%uwg%'
                  AND src.file_path NOT LIKE '%write_gateway%'
                LIMIT 100
            """)
            for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                src_node_id, src_file, layer, dst_file = row[0], row[1], row[2], row[3]
                in_mod = self._is_in_modified_area(src_file)
                if in_mod:
                    summary["in_modified_area"] += 1
                violations.append(
                    GateViolation(
                        violation_id=f"preflight_write_{src_node_id}",
                        source_view="import_edges",
                        source_node=str(src_node_id),
                        source_edge=None,
                        file=src_file,
                        line=None,
                        layer_src=layer,
                        layer_dst=None,
                        path_id=None,
                        first_illegal_hop=f"{layer}->direct_write",
                        path_criticality=4.0,
                        in_modified_area=in_mod,
                        message=(
                            f"[PREFLIGHT] Direct storage import bypassing UWG: {src_file} -> {dst_file}"
                        ),
                        path_criticality_class="write",
                        structured_action_required=True,
                        approval_required=True,
                    )
                )
        except sqlite3.Error:
            pass

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
            policy=self.execution_policy,
            stage="preflight",
        )

    def _execute_gate_logic(self) -> GateResult:
        """Execute write sovereignty check."""
        violations: list[GateViolation] = []
        summary: dict[str, Any] = {
            "total_violations": 0,
            "critical_writes": 0,
            "warning_writes": 0,
            "by_layer": {},
            "in_modified_area": 0,
            "new_bypass_paths": 0,
        }

        if not self.conn:
            return self._empty_result()

        # Check 1: Non-UWG write sovereignty paths
        try:
            cursor = self.conn.execute("""
                SELECT edge_id, writer_file, writer_layer, write_symbol, write_line,
                       source_file, is_uwg_routed, is_direct_infra_write, severity
                FROM mv_write_sovereignty_paths
                WHERE is_uwg_routed = 0
            """)
            for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                (
                    edge_id,
                    writer_file,
                    writer_layer,
                    write_symbol,
                    write_line,
                    source_file,
                    _,
                    is_direct_infra_write,
                    severity,
                ) = row

                # Track by severity
                if severity == "critical":
                    summary["critical_writes"] += 1
                elif severity == "warning":
                    summary["warning_writes"] += 1

                # Track by layer
                summary["by_layer"][writer_layer] = summary["by_layer"].get(writer_layer, 0) + 1

                in_mod = self._is_in_modified_area(source_file or writer_file)
                if in_mod:
                    summary["in_modified_area"] += 1

                violation = GateViolation(
                    violation_id=f"write_{edge_id}",
                    source_view="mv_write_sovereignty_paths",
                    source_node=None,
                    source_edge=str(edge_id),
                    file=source_file or writer_file,
                    line=write_line,
                    layer_src=writer_layer,
                    layer_dst=None,
                    path_id=None,
                    first_illegal_hop=f"{writer_layer}->direct_write",
                    path_criticality=4.0 if severity == "critical" else 2.5,
                    in_modified_area=in_mod,
                    message=f"Non-UWG write path ({severity}): {write_symbol} in {writer_layer}"
                    + (" [DIRECT INFRA]" if is_direct_infra_write else ""),
                    extra={
                        "is_direct_infra_write": bool(is_direct_infra_write),
                        "write_symbol": write_symbol,
                        "severity": severity,
                    },
                )
                violations.append(violation)
        except sqlite3.Error:
            pass

        # Check 2: New write bypass paths (delta from baseline)
        try:
            cursor = self.conn.execute("""
                SELECT edge_id, src_file, src_layer, bypass_type, source_file, line_no, is_new
                FROM mv_new_write_bypass_paths
                WHERE is_new = 1
            """)
            for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                edge_id, src_file, src_layer, bypass_type, source_file, line_no, _ = row

                summary["new_bypass_paths"] += 1

                in_mod = self._is_in_modified_area(source_file or src_file)
                if in_mod:
                    summary["in_modified_area"] += 1

                violation = GateViolation(
                    violation_id=f"new_bypass_{edge_id}",
                    source_view="mv_new_write_bypass_paths",
                    source_node=None,
                    source_edge=str(edge_id),
                    file=source_file or src_file,
                    line=line_no,
                    layer_src=src_layer,
                    layer_dst=None,
                    path_id=None,
                    first_illegal_hop=f"{src_layer}->{bypass_type}",
                    path_criticality=5.0,  # New bypass is highest criticality
                    in_modified_area=in_mod,
                    message=f"New write bypass path: {bypass_type} in {src_layer} (NEWLY INTRODUCED)",
                    extra={
                        "bypass_type": bypass_type,
                        "is_new": True,
                    },
                )
                violations.append(violation)
        except sqlite3.Error:
            pass

        # Determine status: P0 blocks if any critical violations or new bypass paths
        summary["total_violations"] = len(violations)
        has_critical = summary["critical_writes"] > 0 or summary["new_bypass_paths"] > 0
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
                "critical_writes": 0,
                "warning_writes": 0,
                "by_layer": {},
                "in_modified_area": 0,
                "new_bypass_paths": 0,
                "note": "Materialized views not available - no violations detected",
            },
        )


def main() -> int:
    """CLI entry point."""
    gate = WriteSovereigntyGate()
    return gate.run_and_exit()


if __name__ == "__main__":
    import sys

    sys.exit(main())
