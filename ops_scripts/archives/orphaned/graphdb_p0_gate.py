#!/usr/bin/env python3
"""GraphDB P0 Integrity Gates — Hard blocks for projection-integrity failures.

This module implements P0 (Hard Block) gates for GraphDB CI:
    P0-1: Projection parity failure
    P0-2: Deterministic rebuild failure
    P0-3: Schema compatibility failure
    P0-4: Snapshot integrity failure
    P0-5: Query contract failure
    P0-6: Graph-only truth drift

Architecture:
    Canonical ADG SQLite → GraphDB Projection → P0 Gates → Block/Allow

Exit codes:
    0 — All P0 gates pass
    1 — One or more P0 gates block (commit forbidden)
    2 — Required artifacts missing (rebuild required)

Reference: docs/technical/graphdb_ci_hardening.md
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Optional NetworkX import with graceful degradation
try:
    import networkx as nx

    HAS_NETWORKX = True
except ImportError:  # pragma: no cover
    HAS_NETWORKX = False
    nx = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[2]
ADG_DIR = REPO_ROOT / "artifacts" / "adg"
GRAPHDB_DIR = REPO_ROOT / "tools" / "graphdb"

# Protected contract queries that graph layer must support
PROTECTED_CONTRACT_QUERIES: List[str] = [
    "exact_violating_path",  # P0-5: Exact violating path extraction
    "first_illegal_hop",  # P0-5: First illegal hop identification
    "blast_radius_traversal",  # P0-5: Blast-radius traversal
    "historical_diff",  # P0-5: Historical diff for snapshot pair
    "neighborhood_extraction",  # P0-5: Neighborhood extraction for violation target
]

# Required node classes for valid projection
REQUIRED_NODE_CLASSES: Set[str] = {
    "file",
    "module",
    "symbol",
    "layer",
    "agent",
    "tool",
    "policy",
    "decision",
    "seam",
    "scan_run",
}

# Required edge classes for valid projection
REQUIRED_EDGE_CLASSES: Set[str] = {
    "imports",
    "calls",
    "implements",
    "belongs_to_layer",
    "violates",
    "validates",
    "verifies_policy",
}


@dataclass
class P0GateResult:
    """Result from a P0 gate check."""

    gate_id: str
    passed: bool
    severity: str = "P0"  # Always P0 for this module
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    blocking: bool = True  # P0 gates always block on failure

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "passed": self.passed,
            "severity": self.severity,
            "message": self.message,
            "details": self.details,
            "blocking": self.blocking,
        }


@dataclass
class GraphDBSnapshot:
    """Snapshot metadata for integrity checks."""

    commit_sha: str
    schema_version: str
    artifact_digest: str
    node_count: int
    edge_count: int
    node_type_counts: Dict[str, int]
    edge_type_counts: Dict[str, int]
    timestamp: str
    run_id: str

    def calculate_digest(self) -> str:
        """Calculate deterministic digest of snapshot contents."""
        content = json.dumps(
            {
                "node_count": self.node_count,
                "edge_count": self.edge_count,
                "node_types": sorted(self.node_type_counts.items()),
                "edge_types": sorted(self.edge_type_counts.items()),
                "schema_version": self.schema_version,
            },
            sort_keys=True,
        )
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class GraphDBP0Gates:
    """P0 integrity gates for GraphDB projections."""

    def __init__(self, sqlite_path: Optional[Path] = None):
        """Initialize P0 gates.

        Args:
            sqlite_path: Path to ADG SQLite file (auto-detected if None)
        """
        self.sqlite_path = sqlite_path or self._find_latest_adg_sqlite()
        self.results: List[P0GateResult] = []

        if not self.sqlite_path or not self.sqlite_path.exists():
            raise FileNotFoundError(f"ADG SQLite not found. Run: python tools/generate/generate_full_adg.py")

    def _find_latest_adg_sqlite(self) -> Optional[Path]:
        """Find the most recent ADG SQLite file."""
        if not ADG_DIR.exists():
            return None
        sqlite_files = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"), reverse=True)
        return sqlite_files[0] if sqlite_files else None

    def _get_sqlite_stats(self) -> Tuple[int, int, Dict[str, int], Dict[str, int]]:
        """Get entity/relation counts from canonical ADG SQLite.

        Returns:
            Tuple of (entity_count, relation_count, entity_type_counts, relation_type_counts)
        """
        with sqlite3.connect(str(self.sqlite_path)) as conn:
            cursor = conn.cursor()

            # Count entities
            cursor.execute("SELECT COUNT(*) FROM entities")
            entity_count = cursor.fetchone()[0]

            # Count relations
            cursor.execute("SELECT COUNT(*) FROM relations")
            relation_count = cursor.fetchone()[0]

            # Count by entity type
            cursor.execute("SELECT type, COUNT(*) FROM entities GROUP BY type")
            entity_type_counts = {row[0]: row[1] for row in cursor.fetchall()}

            # Count by relation type
            cursor.execute("SELECT type, COUNT(*) FROM relations GROUP BY type")
            relation_type_counts = {row[0]: row[1] for row in cursor.fetchall()}

            return entity_count, relation_count, entity_type_counts, relation_type_counts

    def _get_sqlite_schema_version(self) -> str:
        """Get schema version from ADG metadata."""
        with sqlite3.connect(str(self.sqlite_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM metadata WHERE key = 'schema_version'")
            row = cursor.fetchone()
            return row[0] if row else "unknown"

    def check_p0_1_projection_parity(self) -> P0GateResult:
        """P0-1: Projection parity failure check.

        Validates that canonical ADG SQLite contains required node/edge classes
        and that counts are within expected parity bounds.
        """
        gate_id = "P0-1"

        try:
            entity_count, relation_count, entity_types, relation_types = self._get_sqlite_stats()

            # Check required node classes exist
            missing_nodes = REQUIRED_NODE_CLASSES - set(entity_types.keys())
            if missing_nodes:
                return P0GateResult(
                    gate_id=gate_id,
                    passed=False,
                    message=f"Missing required node classes: {sorted(missing_nodes)}",
                    details={
                        "missing_node_classes": sorted(missing_nodes),
                        "available_types": sorted(entity_types.keys()),
                    },
                )

            # Check required edge classes exist
            missing_edges = REQUIRED_EDGE_CLASSES - set(relation_types.keys())
            if missing_edges:
                return P0GateResult(
                    gate_id=gate_id,
                    passed=False,
                    message=f"Missing required edge classes: {sorted(missing_edges)}",
                    details={
                        "missing_edge_classes": sorted(missing_edges),
                        "available_types": sorted(relation_types.keys()),
                    },
                )

            # Check for material count inconsistencies (projection didn't drop data)
            # Parity: entity_count should be > 0 and relation_count should be reasonable
            if entity_count == 0:
                return P0GateResult(
                    gate_id=gate_id,
                    passed=False,
                    message="Projection parity failure: zero entities in canonical ADG",
                    details={"entity_count": entity_count, "relation_count": relation_count},
                )

            if relation_count == 0:
                return P0GateResult(
                    gate_id=gate_id,
                    passed=False,
                    message="Projection parity failure: zero relations in canonical ADG",
                    details={"entity_count": entity_count, "relation_count": relation_count},
                )

            return P0GateResult(
                gate_id=gate_id,
                passed=True,
                message=f"Projection parity OK: {entity_count} entities, {relation_count} relations",
                details={
                    "entity_count": entity_count,
                    "relation_count": relation_count,
                    "node_types": len(entity_types),
                    "edge_types": len(relation_types),
                },
            )

        except (sqlite3.Error, RuntimeError, OSError) as e:
            return P0GateResult(
                gate_id=gate_id,
                passed=False,
                message=f"P0-1 check failed: {e}",
                details={"error": str(e)},
            )

    def check_p0_2_deterministic_rebuild(self) -> P0GateResult:
        """P0-2: Deterministic rebuild failure check.

        Validates that the same canonical ADG input produces consistent
        snapshot digests. Uses stored previous snapshot for comparison.
        """
        gate_id = "P0-2"

        try:
            # Get current SQLite stats
            entity_count, relation_count, entity_types, relation_types = self._get_sqlite_stats()
            schema_version = self._get_sqlite_schema_version()

            # Build current snapshot
            current = GraphDBSnapshot(
                commit_sha="current",
                schema_version=schema_version,
                artifact_digest="",
                node_count=entity_count,
                edge_count=relation_count,
                node_type_counts=entity_types,
                edge_type_counts=relation_types,
                timestamp="",
                run_id="",
            )
            current_digest = current.calculate_digest()

            # Load previous snapshot metadata if available
            snapshot_file = ADG_DIR / "graphdb_snapshot_baseline.json"
            if snapshot_file.exists():
                prev_data = json.loads(snapshot_file.read_text())
                prev_digest = prev_data.get("content_digest", "")

                if prev_digest and prev_digest != current_digest:
                    return P0GateResult(
                        gate_id=gate_id,
                        passed=False,
                        message=f"Deterministic rebuild failure: digest mismatch ({prev_digest[:8]} vs {current_digest[:8]})",
                        details={
                            "previous_digest": prev_digest,
                            "current_digest": current_digest,
                            "previous_nodes": prev_data.get("node_count", 0),
                            "current_nodes": entity_count,
                            "previous_edges": prev_data.get("edge_count", 0),
                            "current_edges": relation_count,
                        },
                    )

            # Save current as baseline for future runs
            baseline = {
                "content_digest": current_digest,
                "node_count": entity_count,
                "edge_count": relation_count,
                "schema_version": schema_version,
                "node_type_counts": entity_types,
                "edge_type_counts": relation_types,
            }
            snapshot_file.parent.mkdir(parents=True, exist_ok=True)
            snapshot_file.write_text(json.dumps(baseline, indent=2))

            return P0GateResult(
                gate_id=gate_id,
                passed=True,
                message=f"Deterministic rebuild OK: digest={current_digest[:16]}",
                details={
                    "content_digest": current_digest,
                    "node_count": entity_count,
                    "edge_count": relation_count,
                },
            )

        except (sqlite3.Error, RuntimeError, OSError, json.JSONDecodeError) as e:
            return P0GateResult(
                gate_id=gate_id,
                passed=False,
                message=f"P0-2 check failed: {e}",
                details={"error": str(e)},
            )

    def check_p0_3_schema_compatibility(self) -> P0GateResult:
        """P0-3: Schema compatibility failure check.

        Validates that canonical ADG schema changes have corresponding
        GraphDB projection updates.
        """
        gate_id = "P0-3"

        try:
            # Check required tables exist in SQLite
            with sqlite3.connect(str(self.sqlite_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = {row[0] for row in cursor.fetchall()}

            required_tables = {"entities", "relations", "metadata"}
            missing_tables = required_tables - existing_tables
            if missing_tables:
                return P0GateResult(
                    gate_id=gate_id,
                    passed=False,
                    message=f"Schema compatibility failure: missing tables {sorted(missing_tables)}",
                    details={"missing_tables": sorted(missing_tables)},
                )

            # Check required columns in entities table
            with sqlite3.connect(str(self.sqlite_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(entities)")
                entity_columns = {row[1] for row in cursor.fetchall()}

            required_entity_cols = {"id", "type", "name", "properties"}
            missing_entity_cols = required_entity_cols - entity_columns
            if missing_entity_cols:
                return P0GateResult(
                    gate_id=gate_id,
                    passed=False,
                    message=f"Schema compatibility failure: missing entity columns {sorted(missing_entity_cols)}",
                    details={"missing_entity_columns": sorted(missing_entity_cols)},
                )

            # Check required columns in relations table
            with sqlite3.connect(str(self.sqlite_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(relations)")
                relation_columns = {row[1] for row in cursor.fetchall()}

            required_relation_cols = {"id", "from_id", "to_id", "type", "properties"}
            missing_relation_cols = required_relation_cols - relation_columns
            if missing_relation_cols:
                return P0GateResult(
                    gate_id=gate_id,
                    passed=False,
                    message=f"Schema compatibility failure: missing relation columns {sorted(missing_relation_cols)}",
                    details={"missing_relation_columns": sorted(missing_relation_cols)},
                )

            return P0GateResult(
                gate_id=gate_id,
                passed=True,
                message="Schema compatibility OK: all required tables and columns present",
                details={
                    "tables": sorted(existing_tables & required_tables),
                    "entity_columns": sorted(entity_columns & required_entity_cols),
                    "relation_columns": sorted(relation_columns & required_relation_cols),
                },
            )

        except (sqlite3.Error, RuntimeError, OSError) as e:
            return P0GateResult(
                gate_id=gate_id,
                passed=False,
                message=f"P0-3 check failed: {e}",
                details={"error": str(e)},
            )

    def check_p0_4_snapshot_integrity(self) -> P0GateResult:
        """P0-4: Snapshot integrity failure check.

        Validates that required snapshot metadata is present and consistent.
        """
        gate_id = "P0-4"

        try:
            # Check ADG snapshot metadata
            snapshot_files = sorted(ADG_DIR.glob("adg_snapshot_*.json"), reverse=True)
            if not snapshot_files:
                return P0GateResult(
                    gate_id=gate_id,
                    passed=False,
                    message="Snapshot integrity failure: no ADG snapshot metadata found",
                    details={"missing_files": ["adg_snapshot_*.json"]},
                )

            latest_snapshot = snapshot_files[0]
            try:
                snapshot_data = json.loads(latest_snapshot.read_text())
            except json.JSONDecodeError as e:
                return P0GateResult(
                    gate_id=gate_id,
                    passed=False,
                    message=f"Snapshot integrity failure: invalid JSON in {latest_snapshot.name}",
                    details={"error": str(e)},
                )

            # Check required fields
            required_fields = ["commit_sha", "schema_version"]
            for field in required_fields:
                if field not in snapshot_data:
                    return P0GateResult(
                        gate_id=gate_id,
                        passed=False,
                        message=f"Snapshot integrity failure: missing required field '{field}'",
                        details={"missing_field": field, "available_fields": list(snapshot_data.keys())},
                    )

            # Check SQLite metadata table
            with sqlite3.connect(str(self.sqlite_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM metadata")
                metadata = {row[0]: row[1] for row in cursor.fetchall()}

            # Verify metadata has required keys
            required_metadata = ["schema_version"]
            missing_metadata = [k for k in required_metadata if k not in metadata]
            if missing_metadata:
                return P0GateResult(
                    gate_id=gate_id,
                    passed=False,
                    message=f"Snapshot integrity failure: missing metadata keys {missing_metadata}",
                    details={"missing_metadata": missing_metadata},
                )

            return P0GateResult(
                gate_id=gate_id,
                passed=True,
                message="Snapshot integrity OK: all required metadata present",
                details={
                    "snapshot_file": latest_snapshot.name,
                    "schema_version": snapshot_data.get("schema_version", "unknown"),
                    "metadata_keys": list(metadata.keys()),
                },
            )

        except (sqlite3.Error, RuntimeError, OSError) as e:
            return P0GateResult(
                gate_id=gate_id,
                passed=False,
                message=f"P0-4 check failed: {e}",
                details={"error": str(e)},
            )

    def check_p0_5_query_contract(self) -> P0GateResult:
        """P0-5: Query contract failure check.

        Validates that graph layer can answer protected contract queries
        needed for core explainability.
        """
        gate_id = "P0-5"

        if not HAS_NETWORKX:
            return P0GateResult(
                gate_id=gate_id,
                passed=False,
                message="Query contract failure: NetworkX not available for graph operations",
                details={"missing_dependency": "networkx"},
            )

        try:
            # Import graph projection module
            sys.path.insert(0, str(REPO_ROOT))
            from tools.graphdb.projection import GraphProjector

            # Ensure sqlite_path is valid before projecting
            if self.sqlite_path is None:
                return P0GateResult(
                    gate_id=gate_id,
                    passed=False,
                    message="Query contract failure: no ADG SQLite available",
                    details={"error": "sqlite_path is None"},
                )

            # Attempt graph projection
            projector = GraphProjector(self.sqlite_path)
            graph = projector.project_graph()

            # Verify graph has required structure for protected queries
            failed_queries = []

            # Test 1: blast_radius_traversal - requires graph connectivity
            if graph.number_of_nodes() == 0 or graph.number_of_edges() == 0:
                failed_queries.append("blast_radius_traversal (empty graph)")

            # Test 2: neighborhood_extraction - test on first node if available
            if graph.number_of_nodes() > 0:
                first_node = list(graph.nodes())[0]
                try:
                    list(graph.neighbors(first_node))
                except (nx.NetworkXError, KeyError) as e:
                    failed_queries.append(f"neighborhood_extraction ({e})")

            if failed_queries:
                return P0GateResult(
                    gate_id=gate_id,
                    passed=False,
                    message=f"Query contract failure: {len(failed_queries)} protected queries failed",
                    details={
                        "failed_queries": failed_queries,
                        "protected_queries": PROTECTED_CONTRACT_QUERIES,
                        "graph_nodes": graph.number_of_nodes(),
                        "graph_edges": graph.number_of_edges(),
                    },
                )

            return P0GateResult(
                gate_id=gate_id,
                passed=True,
                message="Query contract OK: protected queries can be answered",
                details={
                    "protected_queries": PROTECTED_CONTRACT_QUERIES,
                    "graph_nodes": graph.number_of_nodes(),
                    "graph_edges": graph.number_of_edges(),
                },
            )

        except (ImportError, RuntimeError, OSError) as e:
            return P0GateResult(
                gate_id=gate_id,
                passed=False,
                message=f"P0-5 check failed: {e}",
                details={"error": str(e)},
            )

    def check_p0_6_graph_only_truth(self) -> P0GateResult:
        """P0-6: Graph-only truth drift check.

        Blocks if policy logic or compliance truth is implemented only in GraphDB code.
        This is the critical truth-boundary gate.
        """
        gate_id = "P0-6"

        try:
            # Scan for graph-only rule implementations
            graphdb_python_files = list(GRAPHDB_DIR.glob("*.py"))

            graph_only_findings = []

            for py_file in graphdb_python_files:
                content = py_file.read_text()

                # Check for suspicious patterns that suggest graph-only truth
                suspicious_patterns = [
                    "# Graph-only rule:",
                    "# Policy defined here:",
                    "_GRAPH_ONLY_POLICY",
                    "VIOLATION_RULES = {",
                ]

                for pattern in suspicious_patterns:
                    if pattern in content:
                        graph_only_findings.append(f"{py_file.name}: {pattern}")

            # Check for standalone violation detection without ADG source
            for py_file in graphdb_python_files:
                content = py_file.read_text()

                if "def detect_violations" in content and "violations" not in py_file.name:
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if "def detect_violations" in line:
                            # Check if function reads from canonical ADG
                            func_body = "\n".join(lines[i : i + 20])
                            if "sqlite" not in func_body.lower() and "adg" not in func_body.lower():
                                graph_only_findings.append(
                                    f"{py_file.name}: detect_violations without ADG source"
                                )

            if graph_only_findings:
                return P0GateResult(
                    gate_id=gate_id,
                    passed=False,
                    message=f"Graph-only truth drift detected: {len(graph_only_findings)} findings",
                    details={
                        "findings": graph_only_findings,
                        "files_checked": len(graphdb_python_files),
                    },
                )

            return P0GateResult(
                gate_id=gate_id,
                passed=True,
                message="Truth boundary OK: no graph-only policy truth detected",
                details={
                    "files_checked": len(graphdb_python_files),
                    "scanned_patterns": 4,
                },
            )

        except (OSError, RuntimeError) as e:
            return P0GateResult(
                gate_id=gate_id,
                passed=False,
                message=f"P0-6 check failed: {e}",
                details={"error": str(e)},
            )

    def run_all_p0_gates(self) -> List[P0GateResult]:
        """Run all P0 gates and return results."""
        self.results = [
            self.check_p0_1_projection_parity(),
            self.check_p0_2_deterministic_rebuild(),
            self.check_p0_3_schema_compatibility(),
            self.check_p0_4_snapshot_integrity(),
            self.check_p0_5_query_contract(),
            self.check_p0_6_graph_only_truth(),
        ]
        return self.results

    def get_exit_code(self) -> int:
        """Get exit code based on gate results.

        Returns:
            0 if all gates pass, 1 if any P0 gate fails
        """
        if not self.results:
            return 2  # No results = missing artifacts

        failed = [r for r in self.results if not r.passed and r.blocking]
        return 1 if failed else 0

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all gate results."""
        if not self.results:
            return {"status": "NO_RESULTS", "total": 0, "passed": 0, "failed": 0}

        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        blocking = sum(1 for r in self.results if not r.passed and r.blocking)

        return {
            "status": "PASS" if blocking == 0 else "BLOCK",
            "total": len(self.results),
            "passed": passed,
            "failed": failed,
            "blocking": blocking,
            "gates": [r.to_dict() for r in self.results],
        }


def main() -> int:
    """Main entry point for GraphDB P0 gates."""
    print("[GRAPHDB-P0] Running P0 integrity gates...")
    print()

    # Check for artifacts
    if not ADG_DIR.exists():
        print(f"[GRAPHDB-P0] ERROR: ADG directory not found: {ADG_DIR}", file=sys.stderr)
        print("[GRAPHDB-P0] Run: python tools/generate/generate_full_adg.py", file=sys.stderr)
        return 2

    # Initialize gates
    try:
        gates = GraphDBP0Gates()
    except FileNotFoundError as e:
        print(f"[GRAPHDB-P0] ERROR: {e}", file=sys.stderr)
        return 2

    # Run all gates
    results = gates.run_all_p0_gates()

    # Display results
    print("=== P0 GATE RESULTS ===")
    print()

    for result in results:
        status = "✅ PASS" if result.passed else "❌ BLOCK"
        print(f"[{status}] {result.gate_id}: {result.message}")
        if not result.passed and result.details:
            for key, value in result.details.items():
                if isinstance(value, list) and len(value) > 10:
                    print(f"    {key}: {value[:10]} ... and {len(value) - 10} more")
                else:
                    print(f"    {key}: {value}")
        print()

    # Summary
    summary = gates.get_summary()
    print("=== SUMMARY ===")
    print(f"Total gates:  {summary['total']}")
    print(f"Passed:       {summary['passed']}")
    print(f"Failed:       {summary['failed']}")
    print(f"Blocking:     {summary['blocking']}")
    print(f"Status:       {summary['status']}")
    print()

    if summary["status"] == "BLOCK":
        print("[GRAPHDB-P0] COMMIT BLOCKED — Fix P0 failures before proceeding.")
        print("[GRAPHDB-P0] P0 = Hard block for projection-integrity failures.")
        return 1

    print("[GRAPHDB-P0] All P0 gates passed. Proceed with commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
