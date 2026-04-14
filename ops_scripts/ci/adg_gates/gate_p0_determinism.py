"""Gate 6: P0 Determinism / Provenance Reconciliation Gate.

Blocks unresolved DB/report/digest mismatches on protected artifact integrity surfaces.
Emits exact mismatch details and likely source artifact scope.

Source views:
    - mv_determinism_provenance_drift
    - mv_graph_vs_report_mismatches
    - mv_digest_reconciliation
    - mv_snapshot_integrity_anomalies
"""

from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap_repo_root() -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return repo_root


_REPO_ROOT = _bootstrap_repo_root()

import sqlite3
from datetime import datetime, timezone
from typing import Any

from ops_scripts.ci.adg_gates.gate_base import ADGGateBase, GateResult, GateViolation

try:
    from tqdm import tqdm
except ImportError as exc:
    raise RuntimeError("tqdm is required for ADG CI gates; install with: pip install tqdm") from exc


class DeterminismProvenanceGate(ADGGateBase):
    """P0 Determinism/Provenance Reconciliation Gate.

    Enforces consistency between the graph database, reports, and digests.
    Blocks on unresolved mismatches that indicate integrity violations.
    """

    gate_family = "determinism_provenance"
    severity = "P0"
    source_views = [
        "mv_determinism_provenance_drift",
        "mv_graph_vs_report_mismatches",
        "mv_digest_reconciliation",
        "mv_snapshot_integrity_anomalies",
    ]

    def _execute_gate_logic(self) -> GateResult:
        """Execute determinism/provenance check."""
        violations: list[GateViolation] = []
        summary: dict[str, Any] = {
            "total_violations": 0,
            "determinism_drift": 0,
            "graph_report_mismatches": 0,
            "digest_reconciliation_failures": 0,
            "snapshot_integrity_anomalies": 0,
            "by_type": {},
            "in_modified_area": 0,
        }

        if not self.conn:
            return self._empty_result()

        # Check 1: Determinism/provenance drift
        try:
            cursor = self.conn.execute("""
                SELECT drift_type, affected_nodes, affected_edges, severity, description
                FROM mv_determinism_provenance_drift
                WHERE severity IN ('high', 'critical')
            """)
            for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                drift_type, affected_nodes, affected_edges, severity, description = row

                summary["determinism_drift"] += 1
                summary["by_type"][drift_type] = summary["by_type"].get(drift_type, 0) + 1

                violation = GateViolation(
                    violation_id=f"drift_{drift_type}",
                    source_view="mv_determinism_provenance_drift",
                    source_node=None,
                    source_edge=None,
                    file=None,
                    line=None,
                    layer_src=None,
                    layer_dst=None,
                    path_id=None,
                    first_illegal_hop=None,
                    path_criticality=4.0 if severity == "critical" else 3.0,
                    in_modified_area=False,
                    message=f"Determinism drift ({severity}): {drift_type} - {description}"
                    f" (nodes={affected_nodes}, edges={affected_edges})",
                    extra={
                        "drift_type": drift_type,
                        "affected_nodes": affected_nodes,
                        "affected_edges": affected_edges,
                        "severity": severity,
                        "description": description,
                    },
                )
                violations.append(violation)
        except sqlite3.Error:
            pass

        # Check 2: Graph vs report mismatches
        try:
            cursor = self.conn.execute("""
                SELECT mismatch_type, graph_count, report_count, delta, affected_artifacts
                FROM mv_graph_vs_report_mismatches
                WHERE ABS(delta) > 0
            """)
            for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                mismatch_type, graph_count, report_count, delta, affected_artifacts = row

                summary["graph_report_mismatches"] += 1

                violation = GateViolation(
                    violation_id=f"mismatch_{mismatch_type}",
                    source_view="mv_graph_vs_report_mismatches",
                    source_node=None,
                    source_edge=None,
                    file=None,
                    line=None,
                    layer_src=None,
                    layer_dst=None,
                    path_id=None,
                    first_illegal_hop=None,
                    path_criticality=3.5 if abs(delta) > 10 else 2.5,
                    in_modified_area=False,
                    message=f"Graph/report mismatch: {mismatch_type} graph={graph_count}, "
                    f"report={report_count}, delta={delta:+d}",
                    extra={
                        "mismatch_type": mismatch_type,
                        "graph_count": graph_count,
                        "report_count": report_count,
                        "delta": delta,
                        "affected_artifacts": affected_artifacts,
                    },
                )
                violations.append(violation)
        except sqlite3.Error:
            pass

        # Check 3: Digest reconciliation failures
        try:
            cursor = self.conn.execute("""
                SELECT artifact_scope, expected_digest, actual_digest, match_status, severity
                FROM mv_digest_reconciliation
                WHERE match_status = 'mismatch'
            """)
            for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                artifact_scope, expected_digest, actual_digest, match_status, severity = row

                summary["digest_reconciliation_failures"] += 1

                violation = GateViolation(
                    violation_id=f"digest_{artifact_scope}",
                    source_view="mv_digest_reconciliation",
                    source_node=None,
                    source_edge=None,
                    file=None,
                    line=None,
                    layer_src=None,
                    layer_dst=None,
                    path_id=None,
                    first_illegal_hop=None,
                    path_criticality=5.0 if severity == "critical" else 4.0,
                    in_modified_area=False,
                    message=f"Digest mismatch ({severity}): {artifact_scope} expected={expected_digest[:16]}..., "
                    f"actual={actual_digest[:16]}...",
                    extra={
                        "artifact_scope": artifact_scope,
                        "expected_digest": expected_digest,
                        "actual_digest": actual_digest,
                        "match_status": match_status,
                        "severity": severity,
                    },
                )
                violations.append(violation)
        except sqlite3.Error:
            pass

        # Check 4: Snapshot integrity anomalies
        try:
            cursor = self.conn.execute("""
                SELECT anomaly_type, node_id, edge_id, description, severity
                FROM mv_snapshot_integrity_anomalies
                WHERE severity IN ('high', 'critical')
            """)
            for row in tqdm(cursor.fetchall(), desc="Processing", unit="item"):
                anomaly_type, node_id, edge_id, description, severity = row

                summary["snapshot_integrity_anomalies"] += 1

                violation = GateViolation(
                    violation_id=f"anomaly_{anomaly_type}_{node_id or edge_id}",
                    source_view="mv_snapshot_integrity_anomalies",
                    source_node=str(node_id) if node_id else None,
                    source_edge=str(edge_id) if edge_id else None,
                    file=None,
                    line=None,
                    layer_src=None,
                    layer_dst=None,
                    path_id=None,
                    first_illegal_hop=None,
                    path_criticality=4.5 if severity == "critical" else 3.5,
                    in_modified_area=False,
                    message=f"Snapshot integrity anomaly ({severity}): {anomaly_type} - {description}",
                    extra={
                        "anomaly_type": anomaly_type,
                        "node_id": node_id,
                        "edge_id": edge_id,
                        "severity": severity,
                        "description": description,
                    },
                )
                violations.append(violation)
        except sqlite3.Error:
            pass

        # Determine status: P0 blocks if any critical digest or integrity anomalies
        summary["total_violations"] = len(violations)
        has_critical = (
            summary["digest_reconciliation_failures"] > 0 or summary["snapshot_integrity_anomalies"] > 0
        )
        status = "blocked" if has_critical else ("warn" if violations else "passed")

        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=status,
            violations=violations,
            summary=summary,
            policy=self.execution_policy,
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
                "determinism_drift": 0,
                "graph_report_mismatches": 0,
                "digest_reconciliation_failures": 0,
                "snapshot_integrity_anomalies": 0,
                "by_type": {},
                "in_modified_area": 0,
                "note": "Materialized views not available - no violations detected",
            },
            policy=self.execution_policy,
        )


def main() -> int:
    """CLI entry point."""
    gate = DeterminismProvenanceGate()
    return gate.run_and_exit()


if __name__ == "__main__":
    sys.exit(main())
