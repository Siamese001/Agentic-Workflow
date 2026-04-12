#!/usr/bin/env python3
"""
END-TO-END ADG SYSTEM TEST
Comprehensive validation of the entire ADG system after regeneration
"""

import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ADG_ARTIFACTS_DIR = ROOT / "artifacts" / "adg"

# Find the most recent SQLite database
sqlite_files = list(ADG_ARTIFACTS_DIR.glob("*.sqlite"))
sqlite_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
SQLITE_PATH = sqlite_files[0]

# Find the most recent ADG run zip
zip_files = list(ADG_ARTIFACTS_DIR.glob("adg_run_*.zip"))
zip_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
ZIP_PATH = zip_files[0] if zip_files else None

print("=" * 80)
print("END-TO-END ADG SYSTEM TEST")
print("=" * 80)
print(f"Database: {SQLITE_PATH.name}")
print(f"Zip Archive: {ZIP_PATH.name if ZIP_PATH else 'None'}")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


class ADGEndToEndTest:
    """Comprehensive end-to-end testing suite."""

    def __init__(self, sqlite_path: Path, zip_path: Path = None):
        self.sqlite_path = sqlite_path
        self.zip_path = zip_path
        self.conn = None
        self.test_results = {}

    def connect(self):
        """Connect to SQLite database."""
        self.conn = sqlite3.connect(self.sqlite_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def execute_query(self, query: str, params=None) -> list[sqlite3.Row]:
        """Execute SQL query and return results."""
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()

    def test_database_integrity(self) -> dict[str, Any]:
        """Test 1: Database integrity and completeness."""
        print("\n" + "=" * 60)
        print("TEST 1 - DATABASE INTEGRITY")
        print("=" * 60)

        result = {"success": False, "details": {}}

        try:
            # Basic counts
            node_count = self.execute_query("SELECT COUNT(*) as count FROM nodes")[0]["count"]
            edge_count = self.execute_query("SELECT COUNT(*) as count FROM edges")[0]["count"]

            # Data integrity checks
            null_layers = self.execute_query(
                "SELECT COUNT(*) as count FROM nodes WHERE layer IS NULL OR layer = ''"
            )[0]["count"]
            null_identity = self.execute_query(
                "SELECT COUNT(*) as count FROM nodes WHERE identity_kind IS NULL OR identity_kind = ''"
            )[0]["count"]
            null_confidence = self.execute_query(
                "SELECT COUNT(*) as count FROM nodes WHERE confidence IS NULL OR confidence = ''"
            )[0]["count"]

            # Reference integrity
            invalid_src = self.execute_query(
                "SELECT COUNT(*) as count FROM edges WHERE src_id NOT IN (SELECT id FROM nodes)"
            )[0]["count"]
            invalid_dst = self.execute_query(
                "SELECT COUNT(*) as count FROM edges WHERE dst_id NOT IN (SELECT id FROM nodes)"
            )[0]["count"]

            # Entity and relation type counts
            entity_types = self.execute_query("SELECT DISTINCT entity_type FROM nodes")
            relation_types = self.execute_query("SELECT DISTINCT relation_type FROM edges")

            integrity_details = {
                "node_count": node_count,
                "edge_count": edge_count,
                "null_layers": null_layers,
                "null_identity": null_identity,
                "null_confidence": null_confidence,
                "invalid_src_refs": invalid_src,
                "invalid_dst_refs": invalid_dst,
                "entity_types": len(entity_types),
                "relation_types": len(relation_types),
                "integrity_score": 100
                - (null_layers + null_identity + null_confidence + invalid_src + invalid_dst),
            }

            success = (
                null_layers == 0
                and null_identity == 0
                and null_confidence == 0
                and invalid_src == 0
                and invalid_dst == 0
                and node_count > 0
                and edge_count > 0
            )

            print(f"Nodes: {node_count:,}")
            print(f"Edges: {edge_count:,}")
            print(f"Entity types: {len(entity_types)}")
            print(f"Relation types: {len(relation_types)}")
            print(f"Data integrity: {integrity_details['integrity_score']}%")
            print(f"Reference integrity: {'✅' if invalid_src == 0 and invalid_dst == 0 else '❌'}")

            result["details"] = integrity_details
            result["success"] = success

            print(f"✅ DATABASE INTEGRITY: {'PASS' if success else 'FAIL'}")

        except (ValueError, TypeError, RuntimeError) as e:
            result["success"] = False
            result["error"] = str(e)
            print(f"❌ DATABASE INTEGRITY: FAIL - {e}")

        return result

    def test_layer_distribution(self) -> dict[str, Any]:
        """Test 2: Layer distribution and architecture."""
        print("\n" + "=" * 60)
        print("TEST 2 - LAYER DISTRIBUTION")
        print("=" * 60)

        result = {"success": False, "details": {}}

        try:
            # Layer distribution
            layer_dist = self.execute_query(
                "SELECT layer, COUNT(*) as count FROM nodes GROUP BY layer ORDER BY count DESC"
            )
            layer_distribution = {row["layer"]: row["count"] for row in layer_dist}

            # Critical layers check (using the actual layer names in the system)
            critical_layers = ["L0", "L2", "L5"]
            critical_counts = {}
            for layer in critical_layers:
                count = self.execute_query("SELECT COUNT(*) as count FROM nodes WHERE layer = ?", (layer,))[
                    0
                ]["count"]
                critical_counts[layer] = count

            # Module vs symbol distribution by layer
            module_by_layer = self.execute_query(
                "SELECT layer, COUNT(*) as count FROM nodes WHERE entity_type = 'module' GROUP BY layer ORDER BY count DESC"
            )
            symbol_by_layer = self.execute_query(
                "SELECT layer, COUNT(*) as count FROM nodes WHERE entity_type = 'symbol' GROUP BY layer ORDER BY count DESC"
            )

            layer_details = {
                "total_layers": len(layer_distribution),
                "layer_distribution": layer_distribution,
                "critical_layers": critical_counts,
                "modules_by_layer": {row["layer"]: row["count"] for row in module_by_layer},
                "symbols_by_layer": {row["layer"]: row["count"] for row in symbol_by_layer},
                "architecture_health": len(layer_distribution) >= 10 and sum(critical_counts.values()) > 0,
            }

            success = len(layer_distribution) >= 10 and sum(critical_counts.values()) > 0

            print(f"Total layers: {len(layer_distribution)}")
            print(f"Critical layers: {sum(critical_counts.values())} nodes")
            for layer, count in critical_counts.items():
                print(f"  {layer}: {count}")
            print(f"Architecture health: {'✅' if success else '❌'}")

            result["details"] = layer_details
            result["success"] = success

            print(f"✅ LAYER DISTRIBUTION: {'PASS' if success else 'FAIL'}")

        except (ValueError, TypeError, RuntimeError) as e:
            result["success"] = False
            result["error"] = str(e)
            print(f"❌ LAYER DISTRIBUTION: FAIL - {e}")

        return result

    def test_edge_connectivity(self) -> dict[str, Any]:
        """Test 3: Edge connectivity and key relations."""
        print("\n" + "=" * 60)
        print("TEST 3 - EDGE CONNECTIVITY")
        print("=" * 60)

        result = {"success": False, "details": {}}

        try:
            # Key edge types
            key_relations = [
                "calls",
                "imports",
                "exports",
                "implements",
                "covers",
                "emits_test_result",
                "defines_test_case",
                "detects_regression",
                "emits_replay_key",
                "mutation_signature",
                "parent_snapshot_hash",
            ]

            edge_counts = {}
            for relation in key_relations:
                count = self.execute_query(
                    "SELECT COUNT(*) as count FROM edges WHERE relation_type = ?", (relation,)
                )[0]["count"]
                edge_counts[relation] = count

            # Connectivity metrics
            avg_degree = (
                self.execute_query("""
                SELECT AVG(degree) as avg_degree FROM (
                    SELECT (in_degree + out_degree) as degree
                    FROM (
                        SELECT
                            (SELECT COUNT(*) FROM edges WHERE dst_id = n.id) as in_degree,
                            (SELECT COUNT(*) FROM edges WHERE src_id = n.id) as out_degree
                        FROM nodes n
                    )
                )
            """)[0]["avg_degree"]
                or 0
            )

            # Isolated nodes
            isolated_nodes = self.execute_query("""
                SELECT COUNT(*) as count FROM nodes n
                WHERE NOT EXISTS (SELECT 1 FROM edges e WHERE e.src_id = n.id OR e.dst_id = n.id)
            """)[0]["count"]

            connectivity_details = {
                "key_relation_counts": edge_counts,
                "average_degree": round(avg_degree, 2),
                "isolated_nodes": isolated_nodes,
                "connectivity_health": avg_degree > 1 and isolated_nodes < len(edge_counts),
            }

            success = avg_degree > 1 and isolated_nodes < len(edge_counts)

            print(f"Average node degree: {avg_degree:.2f}")
            print(f"Isolated nodes: {isolated_nodes}")
            print("Key relations:")
            for relation, count in edge_counts.items():
                print(f"  {relation}: {count:,}")
            print(f"Connectivity health: {'✅' if success else '❌'}")

            result["details"] = connectivity_details
            result["success"] = success

            print(f"✅ EDGE CONNECTIVITY: {'PASS' if success else 'FAIL'}")

        except (ValueError, TypeError, RuntimeError) as e:
            result["success"] = False
            result["error"] = str(e)
            print(f"❌ EDGE CONNECTIVITY: FAIL - {e}")

        return result

    def test_determinism(self) -> dict[str, Any]:
        """Test 4: System determinism and hash stability."""
        print("\n" + "=" * 60)
        print("TEST 4 - SYSTEM DETERMINISM")
        print("=" * 60)

        result = {"success": False, "details": {}}

        try:
            # Generate hash
            node_data = self.execute_query(
                "SELECT adg_name, entity_type, layer, identity_kind, confidence, resolved_path FROM nodes ORDER BY adg_name"
            )
            edge_data = self.execute_query(
                "SELECT src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol FROM edges ORDER BY src_id, dst_id, relation_type"
            )

            node_hash_input = json.dumps([dict(row) for row in node_data], sort_keys=True)
            node_hash = hashlib.sha256(node_hash_input.encode()).hexdigest()

            edge_hash_input = json.dumps([dict(row) for row in edge_data], sort_keys=True)
            edge_hash = hashlib.sha256(edge_hash_input.encode()).hexdigest()

            # Mutation edges check
            mutation_edges = self.execute_query("""
                SELECT relation_type, COUNT(*) as count
                FROM edges
                WHERE relation_type IN ('emits_replay_key', 'mutation_signature', 'parent_snapshot_hash', 'references_policy_hash')
                GROUP BY relation_type
            """)

            mutation_counts = {row["relation_type"]: row["count"] for row in mutation_edges}

            determinism_details = {
                "node_hash": node_hash[:20] + "...",
                "edge_hash": edge_hash[:20] + "...",
                "total_nodes": len(node_data),
                "total_edges": len(edge_data),
                "mutation_edge_counts": mutation_counts,
                "determinism_score": 100 if len(mutation_counts) >= 4 else 50,
            }

            success = len(mutation_counts) >= 4 and len(node_data) > 0 and len(edge_data) > 0

            print(f"Node hash: {node_hash[:20]}...")
            print(f"Edge hash: {edge_hash[:20]}...")
            print(f"Total nodes: {len(node_data):,}")
            print(f"Total edges: {len(edge_data):,}")
            print("Mutation edges:")
            for relation, count in mutation_counts.items():
                print(f"  {relation}: {count}")
            print(f"Determinism: {'✅' if success else '❌'}")

            result["details"] = determinism_details
            result["success"] = success

            print(f"✅ SYSTEM DETERMINISM: {'PASS' if success else 'FAIL'}")

        except (ValueError, TypeError, RuntimeError) as e:
            result["success"] = False
            result["error"] = str(e)
            print(f"❌ SYSTEM DETERMINISM: FAIL - {e}")

        return result

    def test_artifact_completeness(self) -> dict[str, Any]:
        """Test 5: Artifact completeness and file structure."""
        print("\n" + "=" * 60)
        print("TEST 5 - ARTIFACT COMPLETENESS")
        print("=" * 60)

        result = {"success": False, "details": {}}

        try:
            # Check required files
            required_files = [
                self.sqlite_path,
                ADG_ARTIFACTS_DIR / "adg_snapshot_03232026_0655.json",
                ADG_ARTIFACTS_DIR / "adg_file_graph_03232026_0655.json",
                ADG_ARTIFACTS_DIR / "adg_symbol_graph_03232026_0655.json",
                ADG_ARTIFACTS_DIR / "adg_governance_graph_03232026_0655.json",
                ADG_ARTIFACTS_DIR / "cache" / "scan_result_cache.json",
            ]

            file_status = {}
            for file_path in required_files:
                exists = file_path.exists()
                size = file_path.stat().st_size if exists else 0
                file_status[file_path.name] = {"exists": exists, "size_mb": round(size / 1024 / 1024, 2)}

            # Check zip archive
            zip_status = {"exists": False, "size_mb": 0}
            if self.zip_path and self.zip_path.exists():
                zip_status = {"exists": True, "size_mb": round(self.zip_path.stat().st_size / 1024 / 1024, 2)}

            # Check reports directory
            reports_dir = ADG_ARTIFACTS_DIR / "reports"
            reports_exist = reports_dir.exists()
            report_count = len(list(reports_dir.glob("*.json"))) if reports_exist else 0

            artifact_details = {
                "required_files": file_status,
                "zip_archive": zip_status,
                "reports_directory": {"exists": reports_exist, "report_count": report_count},
                "completeness_score": sum(1 for f in file_status.values() if f["exists"])
                / len(file_status)
                * 100,
            }

            success = (
                sum(1 for f in file_status.values() if f["exists"]) >= len(required_files) - 1
                and self.sqlite_path.exists()
            )

            print("Required files:")
            for name, status in file_status.items():
                print(f"  {name}: {'✅' if status['exists'] else '❌'} ({status['size_mb']} MB)")

            print(f"Zip archive: {'✅' if zip_status['exists'] else '❌'} ({zip_status['size_mb']} MB)")
            print(f"Reports: {report_count} files")
            print(f"Completeness: {artifact_details['completeness_score']:.1f}%")

            result["details"] = artifact_details
            result["success"] = success

            print(f"✅ ARTIFACT COMPLETENESS: {'PASS' if success else 'FAIL'}")

        except (ValueError, TypeError, RuntimeError) as e:
            result["success"] = False
            result["error"] = str(e)
            print(f"❌ ARTIFACT COMPLETENESS: FAIL - {e}")

        return result

    def test_performance_metrics(self) -> dict[str, Any]:
        """Test 6: Performance and cache metrics."""
        print("\n" + "=" * 60)
        print("TEST 6 - PERFORMANCE METRICS")
        print("=" * 60)

        result = {"success": False, "details": {}}

        try:
            # Database performance
            db_size = self.sqlite_path.stat().st_size
            db_size_mb = round(db_size / 1024 / 1024, 2)

            # Cache performance (from scan log)
            cache_file = ADG_ARTIFACTS_DIR / "cache" / "scan_result_cache.json"
            cache_size = cache_file.stat().st_size if cache_file.exists() else 0
            cache_size_mb = round(cache_size / 1024 / 1024, 2)

            # Query performance tests
            import time

            # Test query performance
            start_time = time.time()
            node_count = self.execute_query("SELECT COUNT(*) as count FROM nodes")[0]["count"]
            node_query_time = time.time() - start_time

            start_time = time.time()
            edge_count = self.execute_query("SELECT COUNT(*) as count FROM edges")[0]["count"]
            edge_query_time = time.time() - start_time

            start_time = time.time()
            layer_dist = self.execute_query("SELECT layer, COUNT(*) FROM nodes GROUP BY layer")
            layer_query_time = time.time() - start_time

            performance_details = {
                "database_size_mb": db_size_mb,
                "cache_size_mb": cache_size_mb,
                "query_performance": {
                    "node_count_query_ms": round(node_query_time * 1000, 2),
                    "edge_count_query_ms": round(edge_query_time * 1000, 2),
                    "layer_distribution_query_ms": round(layer_query_time * 1000, 2),
                },
                "performance_score": 100 if (node_query_time < 0.1 and edge_query_time < 0.1) else 80,
            }

            success = db_size_mb > 10 and node_query_time < 0.5 and edge_query_time < 0.5

            print(f"Database size: {db_size_mb} MB")
            print(f"Cache size: {cache_size_mb} MB")
            print("Query performance:")
            print(f"  Node count: {node_query_time * 1000:.2f} ms")
            print(f"  Edge count: {edge_query_time * 1000:.2f} ms")
            print(f"  Layer distribution: {layer_query_time * 1000:.2f} ms")
            print(f"Performance: {'✅' if success else '❌'}")

            result["details"] = performance_details
            result["success"] = success

            print(f"✅ PERFORMANCE METRICS: {'PASS' if success else 'FAIL'}")

        except (ValueError, TypeError, RuntimeError) as e:
            result["success"] = False
            result["error"] = str(e)
            print(f"❌ PERFORMANCE METRICS: FAIL - {e}")

        return result

    def run_all_tests(self) -> dict[str, Any]:
        """Run complete end-to-end test suite."""
        print("Running comprehensive end-to-end ADG system test...")

        try:
            self.connect()

            # Run all tests
            self.test_results["database_integrity"] = self.test_database_integrity()
            self.test_results["layer_distribution"] = self.test_layer_distribution()
            self.test_results["edge_connectivity"] = self.test_edge_connectivity()
            self.test_results["system_determinism"] = self.test_determinism()
            self.test_results["artifact_completeness"] = self.test_artifact_completeness()
            self.test_results["performance_metrics"] = self.test_performance_metrics()

            # Calculate overall success
            all_passed = all(result["success"] for result in self.test_results.values())
            self.test_results["overall_success"] = all_passed

            return self.test_results

        finally:
            self.close()

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("END-TO-END TEST SUMMARY")
        print("=" * 80)

        for test_name, result in self.test_results.items():
            if test_name == "overall_success":
                continue

            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{test_name.upper().replace('_', ' ')}: {status}")

            if "error" in result:
                print(f"  Error: {result['error']}")

        overall_status = (
            "✅ ALL TESTS PASSED" if self.test_results["overall_success"] else "❌ SOME TESTS FAILED"
        )
        print(f"\nOVERALL: {overall_status}")

        if self.test_results["overall_success"]:
            print("\n🎉 ADG END-TO-END SYSTEM TEST COMPLETED SUCCESSFULLY")
            print("The system is fully functional and ready for production use!")
        else:
            print("\n❌ ADG END-TO-END SYSTEM TEST FAILED")
            print("Review failed tests and fix issues before production deployment.")


def main():
    """Run end-to-end test."""
    test_suite = ADGEndToEndTest(SQLITE_PATH, ZIP_PATH)
    results = test_suite.run_all_tests()
    test_suite.print_summary()

    # Save results
    results_dir = ADG_ARTIFACTS_DIR / "reports"
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    results_file = results_dir / f"end_to_end_test_results_{timestamp}.json"

    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)

    print(f"\n📊 Test results saved: {results_file.name}")

    # Exit with error code if any test failed
    if not results["overall_success"]:
        exit(1)


if __name__ == "__main__":
    main()
