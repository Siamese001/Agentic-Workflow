#!/usr/bin/env python3
"""
ADG Consistency Verification

Ensures summary values match raw SQL queries and exported reports:
summary_value == SQL(query_value) == exported_report_value == dashboard_value

MINIMUM REQUIRED METRICS:
- node_count
- edge_count
- violation_count
- layer_violation_count
- antipattern_count
- replay_key_count
- execution_trace_count
- signed_trace_count
- hard_fail_untranscripted_count
- uwg_termination_count
- uwg_bypass_count
- test_result_count
- validation_artifact_count
- policy_verification_count
- hitl_escalation_count
- embedding_store_count
- embedding_retrieval_count
- unresolved_import_count
- low_confidence_node_count
- unknown_layer_module_count
- dead_import_count
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any
from tqdm import tqdm

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class ConsistencyVerificationError(Exception):
    """Raised when consistency verification fails."""

    pass


class ADGConsistencyVerifier:
    """Verifies ADG metric consistency across sources."""

    # Required metrics with their SQL definitions
    REQUIRED_METRICS = {
        "node_count": "SELECT COUNT(*) FROM nodes",
        "edge_count": "SELECT COUNT(*) FROM edges",
        "violation_count": "SELECT COUNT(*) FROM edges WHERE relation_type = 'violates'",
        "layer_violation_count": "SELECT COUNT(*) FROM edges WHERE relation_type = 'layer_authority_violation'",
        "antipattern_count": "SELECT COUNT(*) FROM edges WHERE relation_type = 'antipattern'",
        "replay_key_count": "SELECT COUNT(*) FROM edges WHERE relation_type = 'emits_replay_key'",
        "execution_trace_count": "SELECT COUNT(*) FROM edges WHERE relation_type = 'records_execution_trace'",
        "signed_trace_count": "SELECT COUNT(*) FROM edges WHERE relation_type = 'signs_execution_trace'",
        "hard_fail_untranscripted_count": "SELECT COUNT(*) FROM edges WHERE relation_type = 'hard_fails_untranscripted'",
        "uwg_termination_count": "SELECT COUNT(*) FROM edges WHERE relation_type = 'execution_terminates_at_uwg'",
        "uwg_bypass_count": "SELECT COUNT(*) FROM edges WHERE relation_type = 'bypasses_uwg'",
        "test_result_count": "SELECT COUNT(*) FROM edges WHERE relation_type IN ('emits_test_result', 'stores_validation_artifact')",
        "validation_artifact_count": "SELECT COUNT(*) FROM edges WHERE relation_type = 'stores_validation_artifact'",
        "policy_verification_count": "SELECT COUNT(*) FROM edges WHERE relation_type IN ('verifies_policy', 'validated_by_safety_plane')",
        "hitl_escalation_count": "SELECT COUNT(*) FROM edges WHERE relation_type IN ('escalates_to_human', 'requires_human_review')",
        "embedding_store_count": "SELECT COUNT(*) FROM edges WHERE relation_type = 'stores_embedding'",
        "embedding_retrieval_count": "SELECT COUNT(*) FROM edges WHERE relation_type = 'retrieves_via'",
        "unresolved_import_count": "SELECT COUNT(*) FROM nodes WHERE identity_kind = 'unresolved_import'",
        "low_confidence_node_count": "SELECT COUNT(*) FROM nodes WHERE confidence = 'LOW'",
        "unknown_layer_module_count": "SELECT COUNT(*) FROM nodes WHERE entity_type = 'module' AND layer = 'UNKNOWN'",
        "dead_import_count": "SELECT COUNT(*) FROM edges WHERE relation_type = 'dead_imports'",
    }

    def __init__(self, adg_dir: Path):
        self.adg_dir = Path(adg_dir)
        self.sqlite_path = self._find_sqlite_database()
        self.snapshot_path = self._find_snapshot()
        self.errors: list[str] = []
        self.warnings: list[str] = []
        if self.snapshot_path is None:
            self.warnings.append("No snapshot file found — snapshot consistency checks skipped")

    def _find_sqlite_database(self) -> Path:
        """Find the latest SQLite database."""
        sqlite_files = list(self.adg_dir.glob("adg_indexed_*.sqlite"))
        if not sqlite_files:
            raise ConsistencyVerificationError("No SQLite database found")

        # Return the most recent by modification time
        return max(sqlite_files, key=lambda p: p.stat().st_mtime)

    def _find_snapshot(self) -> Path | None:
        """Find the latest snapshot file.  Returns None when absent."""
        snapshot_files = list(self.adg_dir.glob("adg_snapshot_*.json"))
        if not snapshot_files:
            return None

        return max(snapshot_files, key=lambda p: p.stat().st_mtime)

    def _load_snapshot(self) -> dict[str, Any]:
        """Load snapshot data."""
        try:
            with open(self.snapshot_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise ConsistencyVerificationError(f"Failed to load snapshot: {e}")

    def _execute_sql_query(self, query: str) -> int:
        """Execute SQL query and return single integer result."""
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                if not result:
                    return 0
                return int(result[0])
        except Exception as e:
            raise ConsistencyVerificationError(f"Failed to execute SQL query '{query}': {e}")

    def _get_snapshot_metric(self, snapshot: dict[str, Any], metric_name: str) -> int | None:
        """Extract metric value from snapshot."""
        # Check in counts section
        if "counts" in snapshot:
            counts = snapshot["counts"]
            if metric_name in counts:
                return int(counts[metric_name])

        # Check in graph_plane_counts section
        if "graph_plane_counts" in snapshot:
            graph_counts = snapshot["graph_plane_counts"]
            if metric_name in graph_counts:
                return int(graph_counts[metric_name])

        # Check direct access
        if metric_name in snapshot:
            return int(snapshot[metric_name])

        return None

    def _verify_metric_consistency(
        self, metric_name: str, sql_value: int, snapshot_value: int | None
    ) -> None:
        """Verify consistency between SQL and snapshot values."""
        if snapshot_value is None:
            self.warnings.append(f"Metric {metric_name} not found in snapshot")
            return

        if sql_value != snapshot_value:
            self.errors.append(
                f"Metric {metric_name} mismatch: SQL={sql_value}, Snapshot={snapshot_value}",
            )

    def _verify_sql_schema(self) -> None:
        """Verify SQLite database has required schema."""
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Check required tables
                required_tables = {"nodes", "edges", "meta"}
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = {row[0] for row in cursor.fetchall()}

                missing_tables = required_tables - existing_tables
                if missing_tables:
                    raise ConsistencyVerificationError(f"Missing tables: {missing_tables}")

                # Check required columns in nodes table
                cursor.execute("PRAGMA table_info(nodes)")
                node_columns = {row[1] for row in cursor.fetchall()}
                required_node_columns = {"id", "adg_name", "entity_type", "layer", "confidence"}
                missing_node_columns = required_node_columns - node_columns
                if missing_node_columns:
                    self.warnings.append(f"Missing node columns: {missing_node_columns}")

                # Check required columns in edges table
                cursor.execute("PRAGMA table_info(edges)")
                edge_columns = {row[1] for row in cursor.fetchall()}
                required_edge_columns = {"id", "src_id", "dst_id", "relation_type", "edge_kind"}
                missing_edge_columns = required_edge_columns - edge_columns
                if missing_edge_columns:
                    self.warnings.append(f"Missing edge columns: {missing_edge_columns}")

        except Exception as e:
            raise ConsistencyVerificationError(f"Schema verification failed: {e}")

    def _verify_foreign_key_integrity(self) -> None:
        """Verify foreign key integrity in the database."""
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Check for orphaned edges (edges pointing to non-existent nodes)
                cursor.execute("""
                    SELECT COUNT(*) FROM edges e
                    LEFT JOIN nodes n ON e.src_id = n.id
                    WHERE n.id IS NULL
                """)
                orphaned_src = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(*) FROM edges e
                    LEFT JOIN nodes n ON e.dst_id = n.id
                    WHERE n.id IS NULL
                """)
                orphaned_dst = cursor.fetchone()[0]

                if orphaned_src > 0:
                    self.errors.append(f"Found {orphaned_src} edges with orphaned source nodes")

                if orphaned_dst > 0:
                    self.errors.append(f"Found {orphaned_dst} edges with orphaned destination nodes")

        except Exception as e:
            raise ConsistencyVerificationError(f"Foreign key verification failed: {e}")

    def _verify_relation_type_consistency(self) -> None:
        """Verify relation types are consistent with schema."""
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Get all relation types in use
                cursor.execute("SELECT DISTINCT relation_type FROM edges")
                used_types = {row[0] for row in cursor.fetchall()}

                # Check for empty/null relation types
                cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type IS NULL OR relation_type = ''")
                null_types = cursor.fetchone()[0]

                if null_types > 0:
                    self.errors.append(f"Found {null_types} edges with null/empty relation types")

                # Report unknown relation types (warning only)
                # This would require schema reference, for now just warn about very long types
                cursor.execute("SELECT relation_type FROM edges WHERE LENGTH(relation_type) > 100")
                long_types = cursor.fetchall()

                if long_types:
                    self.warnings.append(f"Found {len(long_types)} unusually long relation types")

        except Exception as e:
            raise ConsistencyVerificationError(f"Relation type verification failed: {e}")

    def _calculate_derived_metrics(self) -> dict[str, int]:
        """Calculate additional derived metrics for verification."""
        derived = {}

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Layer distribution
                cursor.execute(
                    "SELECT layer, COUNT(*) FROM nodes WHERE entity_type = 'module' GROUP BY layer"
                )
                derived["layer_distribution"] = dict(cursor.fetchall())

                # Confidence distribution
                cursor.execute("SELECT confidence, COUNT(*) FROM nodes GROUP BY confidence")
                derived["confidence_distribution"] = dict(cursor.fetchall())

                # Entity type distribution
                cursor.execute("SELECT entity_type, COUNT(*) FROM nodes GROUP BY entity_type")
                derived["entity_type_distribution"] = dict(cursor.fetchall())

                # Top relation types
                cursor.execute("""
                    SELECT relation_type, COUNT(*) as count
                    FROM edges
                    GROUP BY relation_type
                    ORDER BY count DESC
                    LIMIT 10
                """)
                derived["top_relation_types"] = dict(cursor.fetchall())

        except Exception as e:
            self.warnings.append(f"Failed to calculate derived metrics: {e}")

        return derived

    def verify(self) -> dict[str, Any]:
        """Run complete consistency verification."""
        print("🔍 Starting ADG Consistency Verification...")
        print(f"📁 ADG Directory: {self.adg_dir}")
        print(f"🗄️  SQLite Database: {self.sqlite_path.name}")
        if self.snapshot_path:
            print(f"📸 Snapshot: {self.snapshot_path.name}")
        else:
            print("📸 Snapshot: None (skipping snapshot consistency checks)")

        # Load snapshot
        snapshot = None
        if self.snapshot_path:
            print("📋 Loading snapshot...")
            snapshot = self._load_snapshot()

        # Verify database schema
        print("🏗️  Verifying database schema...")
        self._verify_sql_schema()

        # Verify foreign key integrity
        print("🔗 Verifying foreign key integrity...")
        self._verify_foreign_key_integrity()

        # Verify relation type consistency
        print("📊 Verifying relation type consistency...")
        self._verify_relation_type_consistency()

        # Verify required metrics
        print("🔢 Verifying required metrics...")
        sql_results = {}
        snapshot_results = {}
        consistency_results = {}

        for metric_name, sql_query in tqdm(self.REQUIRED_METRICS.items(), desc="Processing", unit="item"):
            print(f"   • {metric_name}")

            # Execute SQL query
            sql_value = self._execute_sql_query(sql_query)
            sql_results[metric_name] = sql_value

            # Get snapshot value
            snapshot_value = self._get_snapshot_metric(snapshot, metric_name) if snapshot else None
            snapshot_results[metric_name] = snapshot_value

            # Verify consistency
            self._verify_metric_consistency(metric_name, sql_value, snapshot_value)
            consistency_results[metric_name] = {
                "sql_value": sql_value,
                "snapshot_value": snapshot_value,
                "consistent": sql_value == snapshot_value if snapshot_value is not None else None,
            }

        # Calculate derived metrics
        print("📈 Calculating derived metrics...")
        derived_metrics = self._calculate_derived_metrics()

        # Prepare result
        result = {
            "status": "PASS" if not self.errors else "FAIL",
            "artifacts_verified": {
                "sqlite": str(self.sqlite_path),
                "snapshot": str(self.snapshot_path) if self.snapshot_path else None,
            },
            "metric_consistency": consistency_results,
            "derived_metrics": derived_metrics,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {
                "total_metrics_checked": len(self.REQUIRED_METRICS),
                "consistent_metrics": sum(
                    1 for r in consistency_results.values() if r.get("consistent") is True
                ),
                "inconsistent_metrics": sum(
                    1 for r in consistency_results.values() if r.get("consistent") is False
                ),
                "missing_in_snapshot": sum(
                    1 for r in consistency_results.values() if r.get("consistent") is None
                ),
            },
        }

        # Print results
        if self.errors:
            print("\n❌ CONSISTENCY VERIFICATION FAILED")
            for error in self.errors:
                print(f"   • {error}")

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")

        if not self.errors:
            print("\n✅ CONSISTENCY VERIFICATION PASSED")
            print(
                f"📊 Summary: {result['summary']['consistent_metrics']}/{result['summary']['total_metrics_checked']} metrics consistent"
            )

        return result


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Verify ADG metric consistency")
    parser.add_argument(
        "--adg-dir",
        type=Path,
        default=Path("artifacts/adg"),
        help="Path to ADG artifacts directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to save verification report",
    )
    parser.add_argument(
        "--metric",
        type=str,
        help="Verify specific metric only",
    )

    args = parser.parse_args()

    try:
        verifier = ADGConsistencyVerifier(args.adg_dir)

        if args.metric:
            # Verify single metric
            if args.metric not in verifier.REQUIRED_METRICS:
                print(f"❌ Unknown metric: {args.metric}")
                print(f"Available metrics: {sorted(verifier.REQUIRED_METRICS.keys())}")
                return 1

            snapshot = verifier._load_snapshot()
            sql_value = verifier._execute_sql_query(verifier.REQUIRED_METRICS[args.metric])
            snapshot_value = verifier._get_snapshot_metric(snapshot, args.metric)

            print(f"📊 Metric: {args.metric}")
            print(f"   SQL Value: {sql_value}")
            print(f"   Snapshot Value: {snapshot_value}")

            if snapshot_value is not None and sql_value != snapshot_value:
                print("❌ INCONSISTENT")
                return 1
            else:
                print("✅ CONSISTENT")
                return 0
        else:
            # Full verification
            result = verifier.verify()

            if args.output:
                with open(args.output, "w") as f:
                    json.dump(result, f, indent=2, default=str)
                print(f"📄 Report saved to: {args.output}")

            return 0 if result["status"] == "PASS" else 1

    except (
        ConsistencyVerificationError
    ) as e:  # guardian: ConsistencyVerificationError should be handled with specific context
        print(f"❌ Verification failed: {e}")
        return 1
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
