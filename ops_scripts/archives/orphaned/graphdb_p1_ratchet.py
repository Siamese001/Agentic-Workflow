#!/usr/bin/env python3
"""GraphDB P1 Ratchet Gates — Regressions in correctness and usefulness.

This module implements P1 (Ratchet) gates for GraphDB CI:
    P1-1: Projection coverage regression
    P1-2: Explanation parity regression
    P1-3: Snapshot diff regression
    P1-4: Query latency regression
    P1-5: Findings drift

P1 gates ratchet (track and warn on) regressions but don't block commits
unless explicitly configured to do so.

Architecture:
    Canonical ADG SQLite → GraphDB Projection → P1 Ratchets → Trend/Warning

Exit codes:
    0 — All P1 gates pass or only warnings
    1 — P1 gate configured as blocking and detected regression

Reference: docs/technical/graphdb_ci_hardening.md
"""

from __future__ import annotations

import json
import sqlite3
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Optional NetworkX import with graceful degradation
try:
    import networkx as nx

    HAS_NETWORKX = True
except ImportError:  # pragma: no cover
    HAS_NETWORKX = False
    nx = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[2]
ADG_DIR = REPO_ROOT / "artifacts" / "adg"
BASELINE_DIR = ADG_DIR / "baselines"

# Latency thresholds (seconds) for protected queries
LATENCY_THRESHOLDS = {
    "blast_radius": 5.0,
    "historical_diff": 10.0,
    "violation_explanation": 3.0,
}

# Minimum coverage ratios for projection parity
MIN_COVERAGE_RATIOS = {
    "node_type_coverage": 0.95,  # 95% of node types must be projected
    "edge_type_coverage": 0.90,  # 90% of edge types must be projected
}


@dataclass
class P1RatchetResult:
    """Result from a P1 ratchet check."""

    gate_id: str
    passed: bool
    severity: str = "P1"
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    regression_detected: bool = False
    delta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "passed": self.passed,
            "severity": self.severity,
            "message": self.message,
            "details": self.details,
            "regression_detected": self.regression_detected,
            "delta": self.delta,
        }


class GraphDBP1Ratchets:
    """P1 ratchet gates for GraphDB projections."""

    def __init__(self, sqlite_path: Optional[Path] = None, blocking: bool = False):
        """Initialize P1 ratchets.

        Args:
            sqlite_path: Path to ADG SQLite file (auto-detected if None)
            blocking: Whether P1 regressions should block commits
        """
        self.sqlite_path = sqlite_path or self._find_latest_adg_sqlite()
        self.blocking = blocking
        self.results: List[P1RatchetResult] = []
        self.baseline_data: Dict[str, Any] = {}

        if not self.sqlite_path or not self.sqlite_path.exists():
            raise FileNotFoundError(f"ADG SQLite not found. Run: python tools/generate/generate_full_adg.py")

        # Ensure baseline directory exists
        BASELINE_DIR.mkdir(parents=True, exist_ok=True)
        self._load_baseline()

    def _find_latest_adg_sqlite(self) -> Optional[Path]:
        """Find the most recent ADG SQLite file."""
        if not ADG_DIR.exists():
            return None
        sqlite_files = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"), reverse=True)
        return sqlite_files[0] if sqlite_files else None

    def _load_baseline(self) -> None:
        """Load previous baseline data for comparison."""
        baseline_file = BASELINE_DIR / "graphdb_p1_baseline.json"
        if baseline_file.exists():
            try:
                self.baseline_data = json.loads(baseline_file.read_text())
            except (json.JSONDecodeError, OSError):
                self.baseline_data = {}

    def _save_baseline(self, data: Dict[str, Any]) -> None:
        """Save current data as new baseline."""
        baseline_file = BASELINE_DIR / "graphdb_p1_baseline.json"
        baseline_file.write_text(json.dumps(data, indent=2))

    def _get_sqlite_stats(self) -> Tuple[int, int, Dict[str, int], Dict[str, int]]:
        """Get entity/relation counts from canonical ADG SQLite."""
        with sqlite3.connect(str(self.sqlite_path)) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM entities")
            entity_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM relations")
            relation_count = cursor.fetchone()[0]

            cursor.execute("SELECT type, COUNT(*) FROM entities GROUP BY type")
            entity_type_counts = {row[0]: row[1] for row in cursor.fetchall()}

            cursor.execute("SELECT type, COUNT(*) FROM relations GROUP BY type")
            relation_type_counts = {row[0]: row[1] for row in cursor.fetchall()}

            return entity_count, relation_count, entity_type_counts, relation_type_counts

    def check_p1_1_projection_coverage(self) -> P1RatchetResult:
        """P1-1: Projection coverage regression ratchet.

        Tracks regressions in projected node/edge coverage compared to baseline.
        """
        gate_id = "P1-1"

        try:
            entity_count, relation_count, entity_types, relation_types = self._get_sqlite_stats()

            # Calculate coverage metrics
            total_nodes = sum(entity_types.values())
            total_edges = sum(relation_types.values())

            current_data = {
                "entity_count": entity_count,
                "relation_count": relation_count,
                "entity_types": entity_types,
                "relation_types": relation_types,
            }

            # Compare with baseline if available
            regression_detected = False
            delta = {}

            if self.baseline_data:
                baseline_nodes = self.baseline_data.get("entity_count", 0)
                baseline_edges = self.baseline_data.get("relation_count", 0)

                node_delta = entity_count - baseline_nodes
                edge_delta = relation_count - baseline_edges

                if node_delta < 0:
                    regression_detected = True
                    delta["node_regression"] = abs(node_delta)

                if edge_delta < 0:
                    regression_detected = True
                    delta["edge_regression"] = abs(edge_delta)

            # Save current as new baseline
            self._save_baseline(current_data)

            if regression_detected:
                return P1RatchetResult(
                    gate_id=gate_id,
                    passed=not self.blocking,
                    severity="P1",
                    message=f"Projection coverage regression detected: {delta}",
                    details=current_data,
                    regression_detected=True,
                    delta=delta,
                )

            return P1RatchetResult(
                gate_id=gate_id,
                passed=True,
                severity="P1",
                message=f"Projection coverage OK: {entity_count} nodes, {relation_count} edges",
                details=current_data,
                regression_detected=False,
                delta={"node_delta": entity_count - self.baseline_data.get("entity_count", entity_count)},
            )

        except (sqlite3.Error, RuntimeError, OSError) as e:
            return P1RatchetResult(
                gate_id=gate_id,
                passed=not self.blocking,
                severity="P1",
                message=f"P1-1 check failed: {e}",
                details={"error": str(e)},
                regression_detected=True,
            )

    def check_p1_2_explanation_parity(self) -> P1RatchetResult:
        """P1-2: Explanation parity regression ratchet.

        Tracks cases where graph explanations diverge from canonical policy findings.
        """
        gate_id = "P1-2"

        try:
            # Query canonical ADG for violation findings
            with sqlite3.connect(str(self.sqlite_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM violations WHERE severity IN ('CRITICAL', 'HIGH')")
                canonical_violations = cursor.fetchone()[0]

            # In a full implementation, we would:
            # 1. Query graph projection for violations via graph traversal
            # 2. Compare counts and specific violation details
            # 3. Flag discrepancies as parity regressions

            # For now, track that we have violation data available
            parity_status = {
                "canonical_violations": canonical_violations,
                "graph_violations": "not_implemented",  # Would require full graph projection
            }

            # Compare with baseline if available
            baseline_violations = self.baseline_data.get("canonical_violations", 0)
            regression_detected = canonical_violations > baseline_violations

            return P1RatchetResult(
                gate_id=gate_id,
                passed=not regression_detected or not self.blocking,
                severity="P1",
                message=f"Explanation parity: {canonical_violations} canonical violations",
                details=parity_status,
                regression_detected=regression_detected,
                delta={"violation_delta": canonical_violations - baseline_violations},
            )

        except (sqlite3.Error, RuntimeError, OSError) as e:
            return P1RatchetResult(
                gate_id=gate_id,
                passed=not self.blocking,
                severity="P1",
                message=f"P1-2 check failed: {e}",
                details={"error": str(e)},
                regression_detected=True,
            )

    def check_p1_3_snapshot_diff(self) -> P1RatchetResult:
        """P1-3: Snapshot diff regression ratchet.

        Tracks degradations in historical diff behavior.
        """
        gate_id = "P1-3"

        try:
            # Check for available snapshots
            snapshot_files = sorted(ADG_DIR.glob("adg_snapshot_*.json"), reverse=True)

            if len(snapshot_files) < 2:
                return P1RatchetResult(
                    gate_id=gate_id,
                    passed=True,
                    severity="P1",
                    message="Snapshot diff: insufficient snapshots for diff comparison",
                    details={"available_snapshots": len(snapshot_files)},
                    regression_detected=False,
                )

            # Load two most recent snapshots for comparison
            try:
                current = json.loads(snapshot_files[0].read_text())
                previous = json.loads(snapshot_files[1].read_text())
            except (json.JSONDecodeError, OSError) as e:
                return P1RatchetResult(
                    gate_id=gate_id,
                    passed=not self.blocking,
                    severity="P1",
                    message=f"Snapshot diff: failed to load snapshots: {e}",
                    details={"error": str(e)},
                    regression_detected=True,
                )

            # Calculate diff metrics
            current_nodes = current.get("node_count", 0)
            previous_nodes = previous.get("node_count", 0)
            current_edges = current.get("edge_count", 0)
            previous_edges = previous.get("edge_count", 0)

            node_delta = current_nodes - previous_nodes
            edge_delta = current_edges - previous_edges

            # Flag significant drops as potential regressions
            regression_detected = False
            if previous_nodes > 0 and node_delta < -0.1 * previous_nodes:  # >10% drop
                regression_detected = True
            if previous_edges > 0 and edge_delta < -0.1 * previous_edges:  # >10% drop
                regression_detected = True

            diff_data = {
                "current_snapshot": snapshot_files[0].name,
                "previous_snapshot": snapshot_files[1].name,
                "node_delta": node_delta,
                "edge_delta": edge_delta,
                "current_nodes": current_nodes,
                "previous_nodes": previous_nodes,
                "current_edges": current_edges,
                "previous_edges": previous_edges,
            }

            return P1RatchetResult(
                gate_id=gate_id,
                passed=not regression_detected or not self.blocking,
                severity="P1",
                message=f"Snapshot diff: nodes {node_delta:+d}, edges {edge_delta:+d}",
                details=diff_data,
                regression_detected=regression_detected,
                delta={"node_delta": node_delta, "edge_delta": edge_delta},
            )

        except (OSError, RuntimeError) as e:
            return P1RatchetResult(
                gate_id=gate_id,
                passed=not self.blocking,
                severity="P1",
                message=f"P1-3 check failed: {e}",
                details={"error": str(e)},
                regression_detected=True,
            )

    def check_p1_4_query_latency(self) -> P1RatchetResult:
        """P1-4: Query latency regression ratchet.

        Tracks latency regressions on key graph queries.
        """
        gate_id = "P1-4"

        if not HAS_NETWORKX:
            return P1RatchetResult(
                gate_id=gate_id,
                passed=not self.blocking,
                severity="P1",
                message="Query latency: NetworkX not available",
                details={"missing_dependency": "networkx"},
                regression_detected=True,
            )

        try:
            sys.path.insert(0, str(REPO_ROOT))
            from tools.graphdb.projection import GraphProjector

            if self.sqlite_path is None:
                return P1RatchetResult(
                    gate_id=gate_id,
                    passed=not self.blocking,
                    severity="P1",
                    message="Query latency: no ADG SQLite available",
                    details={"error": "sqlite_path is None"},
                    regression_detected=True,
                )

            projector = GraphProjector(self.sqlite_path)

            # Measure projection time (proxy for blast-radius query latency)
            start_time = time.perf_counter()
            graph = projector.project_graph()
            projection_time = time.perf_counter() - start_time

            # Measure simple traversal (neighborhood extraction)
            traversal_time = 0.0
            if graph.number_of_nodes() > 0:
                sample_node = list(graph.nodes())[0]
                start_time = time.perf_counter()
                list(graph.neighbors(sample_node))
                traversal_time = time.perf_counter() - start_time

            latency_data = {
                "projection_time": projection_time,
                "traversal_time": traversal_time,
                "threshold_projection": LATENCY_THRESHOLDS["blast_radius"],
                "threshold_traversal": LATENCY_THRESHOLDS["violation_explanation"],
                "graph_nodes": graph.number_of_nodes(),
                "graph_edges": graph.number_of_edges(),
            }

            # Check against thresholds
            regression_detected = False
            if projection_time > LATENCY_THRESHOLDS["blast_radius"]:
                regression_detected = True

            if traversal_time > LATENCY_THRESHOLDS["violation_explanation"]:
                regression_detected = True

            return P1RatchetResult(
                gate_id=gate_id,
                passed=not regression_detected or not self.blocking,
                severity="P1",
                message=f"Query latency: projection={projection_time:.2f}s, traversal={traversal_time:.4f}s",
                details=latency_data,
                regression_detected=regression_detected,
                delta={"projection_vs_threshold": projection_time - LATENCY_THRESHOLDS["blast_radius"]},
            )

        except (ImportError, RuntimeError, OSError) as e:
            return P1RatchetResult(
                gate_id=gate_id,
                passed=not self.blocking,
                severity="P1",
                message=f"P1-4 check failed: {e}",
                details={"error": str(e)},
                regression_detected=True,
            )

    def check_p1_5_findings_drift(self) -> P1RatchetResult:
        """P1-5: Findings drift ratchet.

        Tracks cases where GraphDB summaries diverge from canonical findings.
        """
        gate_id = "P1-5"

        try:
            # Query canonical findings summary
            with sqlite3.connect(str(self.sqlite_path)) as conn:
                cursor = conn.cursor()

                # Get violation summary by severity
                cursor.execute("SELECT severity, COUNT(*) FROM violations GROUP BY severity")
                canonical_summary = {row[0]: row[1] for row in cursor.fetchall()}

                # Get violation summary by category
                cursor.execute("SELECT category, COUNT(*) FROM violations GROUP BY category")
                canonical_by_category = {row[0]: row[1] for row in cursor.fetchall()}

            findings_data = {
                "canonical_by_severity": canonical_summary,
                "canonical_by_category": canonical_by_category,
                "graph_summary": "not_implemented",  # Would compare with graph projection
            }

            # Compare with baseline
            baseline_summary = self.baseline_data.get("canonical_by_severity", {})

            # Flag if new high-severity violations appeared
            regression_detected = False
            current_critical = canonical_summary.get("CRITICAL", 0)
            baseline_critical = baseline_summary.get("CRITICAL", 0)
            if current_critical > baseline_critical:
                regression_detected = True

            return P1RatchetResult(
                gate_id=gate_id,
                passed=not regression_detected or not self.blocking,
                severity="P1",
                message=f"Findings drift: {current_critical} critical, {len(canonical_by_category)} categories",
                details=findings_data,
                regression_detected=regression_detected,
                delta={"critical_delta": current_critical - baseline_critical},
            )

        except (sqlite3.Error, RuntimeError, OSError) as e:
            return P1RatchetResult(
                gate_id=gate_id,
                passed=not self.blocking,
                severity="P1",
                message=f"P1-5 check failed: {e}",
                details={"error": str(e)},
                regression_detected=True,
            )

    def run_all_p1_ratchets(self) -> List[P1RatchetResult]:
        """Run all P1 ratchet gates and return results."""
        self.results = [
            self.check_p1_1_projection_coverage(),
            self.check_p1_2_explanation_parity(),
            self.check_p1_3_snapshot_diff(),
            self.check_p1_4_query_latency(),
            self.check_p1_5_findings_drift(),
        ]
        return self.results

    def get_exit_code(self) -> int:
        """Get exit code based on ratchet results.

        Returns:
            0 if no blocking regressions, 1 if blocking regression detected
        """
        if not self.results:
            return 2

        if not self.blocking:
            return 0  # P1 gates don't block by default

        regressions = [r for r in self.results if r.regression_detected]
        return 1 if regressions else 0

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all ratchet results."""
        if not self.results:
            return {"status": "NO_RESULTS", "total": 0, "regressions": 0}

        regressions = sum(1 for r in self.results if r.regression_detected)

        return {
            "status": "REGRESSION" if regressions > 0 else "OK",
            "total": len(self.results),
            "regressions": regressions,
            "blocking": self.blocking,
            "ratchets": [r.to_dict() for r in self.results],
        }


def main() -> int:
    """Main entry point for GraphDB P1 ratchets."""
    print("[GRAPHDB-P1] Running P1 ratchet gates...")
    print()

    # Check for blocking flag
    blocking = "--blocking" in sys.argv

    if not ADG_DIR.exists():
        print(f"[GRAPHDB-P1] ERROR: ADG directory not found: {ADG_DIR}", file=sys.stderr)
        return 2

    try:
        ratchets = GraphDBP1Ratchets(blocking=blocking)
    except FileNotFoundError as e:
        print(f"[GRAPHDB-P1] ERROR: {e}", file=sys.stderr)
        return 2

    results = ratchets.run_all_p1_ratchets()

    print("=== P1 RATCHET RESULTS ===")
    print()

    for result in results:
        if result.regression_detected:
            status = "⚠️  REGRESSION"
        else:
            status = "✅ OK"
        print(f"[{status}] {result.gate_id}: {result.message}")
        if result.delta:
            print(f"    delta: {result.delta}")
        print()

    summary = ratchets.get_summary()
    print("=== SUMMARY ===")
    print(f"Total ratchets: {summary['total']}")
    print(f"Regressions:    {summary['regressions']}")
    print(f"Blocking mode:  {summary['blocking']}")
    print(f"Status:         {summary['status']}")
    print()

    if summary["status"] == "REGRESSION":
        print("[GRAPHDB-P1] REGRESSIONS DETECTED — Review findings above.")
        if blocking:
            print("[GRAPHDB-P1] BLOCKING MODE: Commit blocked due to regressions.")
            return 1
        else:
            print("[GRAPHDB-P1] Warning only (non-blocking). Use --blocking to fail on regressions.")

    print("[GRAPHDB-P1] All P1 ratchets OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
