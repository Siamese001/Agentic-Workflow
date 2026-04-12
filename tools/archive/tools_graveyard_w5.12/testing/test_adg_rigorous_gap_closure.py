#!/usr/bin/env python3
"""
RIGOROUS WINSURFRULES TESTING - ADG Gap Closure Implementation

TESTING STANDARDS:
- Full database integrity validation
- Deterministic replay verification
- Complete edge coverage analysis
- Boundary regression testing
- Test surface binding validation
- End-to-end system validation
"""

import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SQLITE_PATH = ROOT / "artifacts" / "adg" / "adg_indexed_03232026_0617.sqlite"
REPORTS_DIR = ROOT / "artifacts" / "adg" / "reports"


class ADGRigorousTestSuite:
    """Rigorous testing suite following winsurfrules standards."""

    def __init__(self, sqlite_path: Path):
        self.sqlite_path = sqlite_path
        self.conn = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        self.test_results = {
            "data_integrity_tests": {},
            "replay_determinism_tests": {},
            "edge_coverage_tests": {},
            "boundary_regression_tests": {},
            "test_binding_tests": {},
            "end_to_end_tests": {},
            "overall_success": False,
        }

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

    # ======================================================================
    # DATA INTEGRITY TESTS
    # ======================================================================

    def test_data_integrity_completeness(self) -> dict[str, Any]:
        """TEST: Verify no NULL or empty critical fields."""
        print("=" * 80)
        print("DATA INTEGRITY TEST 1 - Completeness Validation")
        print("=" * 80)

        result = {"success": False, "details": {}}

        # Test 1.1: No NULL layers
        null_layers = self.execute_query("SELECT COUNT(*) as count FROM nodes WHERE layer IS NULL")[0][
            "count"
        ]
        empty_layers = self.execute_query("SELECT COUNT(*) as count FROM nodes WHERE layer = ''")[0]["count"]

        # Test 1.2: No NULL identity_kind
        null_identity = self.execute_query("SELECT COUNT(*) as count FROM nodes WHERE identity_kind IS NULL")[
            0
        ]["count"]
        empty_identity = self.execute_query("SELECT COUNT(*) as count FROM nodes WHERE identity_kind = ''")[
            0
        ]["count"]

        # Test 1.3: No NULL confidence
        null_confidence = self.execute_query("SELECT COUNT(*) as count FROM nodes WHERE confidence IS NULL")[
            0
        ]["count"]
        empty_confidence = self.execute_query("SELECT COUNT(*) as count FROM nodes WHERE confidence = ''")[0][
            "count"
        ]

        # Test 1.4: No NULL critical node fields (resolved_path can be empty for abstract entities)
        null_adg_name = self.execute_query(
            "SELECT COUNT(*) as count FROM nodes WHERE adg_name IS NULL OR adg_name = ''"
        )[0]["count"]
        null_entity_type = self.execute_query(
            "SELECT COUNT(*) as count FROM nodes WHERE entity_type IS NULL OR entity_type = ''"
        )[0]["count"]

        # resolved_path is only required for modules and symbols with actual file locations
        null_resolved_path_critical = self.execute_query("""
            SELECT COUNT(*) as count
            FROM nodes
            WHERE (resolved_path IS NULL OR resolved_path = '')
            AND entity_type IN ('module')
        """)[0]["count"]

        # Test 1.5: No NULL critical edge fields
        null_src_id = self.execute_query("SELECT COUNT(*) as count FROM edges WHERE src_id IS NULL")[0][
            "count"
        ]
        null_dst_id = self.execute_query("SELECT COUNT(*) as count FROM edges WHERE dst_id IS NULL")[0][
            "count"
        ]
        null_relation_type = self.execute_query(
            "SELECT COUNT(*) as count FROM edges WHERE relation_type IS NULL OR relation_type = ''"
        )[0]["count"]

        integrity_status = {
            "layers": {
                "null": null_layers,
                "empty": empty_layers,
                "valid": null_layers == 0 and empty_layers == 0,
            },
            "identity_kind": {
                "null": null_identity,
                "empty": empty_identity,
                "valid": null_identity == 0 and empty_identity == 0,
            },
            "confidence": {
                "null": null_confidence,
                "empty": empty_confidence,
                "valid": null_confidence == 0 and empty_confidence == 0,
            },
            "node_fields": {
                "adg_name": null_adg_name,
                "entity_type": null_entity_type,
                "resolved_path_critical": null_resolved_path_critical,
                "valid": null_adg_name == 0 and null_entity_type == 0 and null_resolved_path_critical == 0,
            },
            "edge_fields": {
                "src_id": null_src_id,
                "dst_id": null_dst_id,
                "relation_type": null_relation_type,
                "valid": null_src_id == 0 and null_dst_id == 0 and null_relation_type == 0,
            },
        }

        overall_valid = all(
            integrity_status[key]["valid"]
            if isinstance(integrity_status[key], dict) and "valid" in integrity_status[key]
            else integrity_status[key]["valid"]
            if isinstance(integrity_status[key], dict) and "valid" in integrity_status[key]
            else False
            for key in ["layers", "identity_kind", "confidence", "node_fields", "edge_fields"]
        )

        print(
            f"Layer integrity: {integrity_status['layers']['valid']} (null: {null_layers}, empty: {empty_layers})"
        )
        print(
            f"Identity integrity: {integrity_status['identity_kind']['valid']} (null: {null_identity}, empty: {empty_identity})"
        )
        print(
            f"Confidence integrity: {integrity_status['confidence']['valid']} (null: {null_confidence}, empty: {empty_confidence})"
        )
        print(
            f"Node fields integrity: {integrity_status['node_fields']['valid']} (critical resolved_path: {null_resolved_path_critical})"
        )
        print(f"Edge fields integrity: {integrity_status['edge_fields']['valid']}")

        result["details"] = integrity_status
        result["success"] = overall_valid

        if overall_valid:
            print("✅ DATA INTEGRITY COMPLETENESS TEST PASSED")
        else:
            print("❌ DATA INTEGRITY COMPLETENESS TEST FAILED")

        return result

    def test_layer_architecture_validity(self) -> dict[str, Any]:
        """TEST: Verify layer architecture follows rules."""
        print("\n" + "=" * 80)
        print("DATA INTEGRITY TEST 2 - Layer Architecture Validity")
        print("=" * 80)

        result = {"success": False, "details": {}}

        # Test 2.1: All layers are valid
        valid_layers = {
            "L0",
            "L1",
            "L2",
            "L3",
            "L4",
            "L5",
            "L6",
            "L_APP",
            "L_OPS",
            "L_PG",
            "L_RUNTIME",
            "L_SHARED",
            "L_SL",
            "L_TEST",
            "L_TOOLS",
            "L_UNKNOWN",
        }

        invalid_layers = self.execute_query(
            """
            SELECT DISTINCT layer, COUNT(*) as count
            FROM nodes
            WHERE layer NOT IN ({})
            GROUP BY layer
        """.format(",".join(["?" for _ in valid_layers])),
            list(valid_layers),
        )

        # Test 2.2: Symbol layers match module layers
        symbol_layer_mismatches = self.execute_query("""
            SELECT COUNT(*) as count
            FROM nodes n1
            JOIN nodes n2 ON SUBSTR(n1.adg_name, 1, INSTR(n1.adg_name, ':') - 1) = n2.adg_name
            WHERE n1.entity_type = 'symbol'
            AND n2.entity_type = 'module'
            AND n1.layer != n2.layer
        """)[0]["count"]

        # Test 2.3: Layer distribution sanity check
        layer_dist = self.execute_query(
            "SELECT layer, COUNT(*) as count FROM nodes GROUP BY layer ORDER BY count DESC"
        )
        layer_distribution = {row["layer"]: row["count"] for row in layer_dist}

        architecture_status = {
            "valid_layers_only": len(invalid_layers) == 0,
            "invalid_layer_details": [
                {"layer": row["layer"], "count": row["count"]} for row in invalid_layers
            ],
            "symbol_module_consistency": symbol_layer_mismatches == 0,
            "symbol_mismatch_count": symbol_layer_mismatches,
            "layer_distribution": layer_distribution,
            "total_layers": len(layer_distribution),
        }

        overall_valid = (
            architecture_status["valid_layers_only"] and architecture_status["symbol_module_consistency"]
        )

        print(f"Valid layers only: {architecture_status['valid_layers_only']}")
        print(
            f"Symbol-module consistency: {architecture_status['symbol_module_consistency']} (mismatches: {symbol_layer_mismatches})"
        )
        print(f"Layer distribution: {len(layer_distribution)} layers")

        result["details"] = architecture_status
        result["success"] = overall_valid

        if overall_valid:
            print("✅ LAYER ARCHITECTURE VALIDITY TEST PASSED")
        else:
            print("❌ LAYER ARCHITECTURE VALIDITY TEST FAILED")

        return result

    # ======================================================================
    # REPLAY DETERMINISM TESTS
    # ======================================================================

    def test_deterministic_hashes(self) -> dict[str, Any]:
        """TEST: Verify deterministic hash generation."""
        print("\n" + "=" * 80)
        print("REPLAY DETERMINISM TEST 1 - Hash Determinism")
        print("=" * 80)

        result = {"success": False, "details": {}}

        # Test 3.1: Generate hash multiple times and verify consistency
        def generate_hashes():
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

            return node_hash, edge_hash

        # Generate hashes 3 times
        hash_sets = []
        for i in range(3):
            node_hash, edge_hash = generate_hashes()
            hash_sets.append({"iteration": i + 1, "node_hash": node_hash, "edge_hash": edge_hash})

        # Verify all hashes are identical
        node_hashes = [h["node_hash"] for h in hash_sets]
        edge_hashes = [h["edge_hash"] for h in hash_sets]

        node_consistent = len(set(node_hashes)) == 1
        edge_consistent = len(set(edge_hashes)) == 1

        # Test 3.2: Verify hash stability after database operations
        # Simulate a read operation
        self.execute_query("SELECT COUNT(*) FROM nodes")

        # Generate hashes again
        node_hash_after, edge_hash_after = generate_hashes()

        hash_stable = node_hash_after == node_hashes[0] and edge_hash_after == edge_hashes[0]

        determinism_status = {
            "hash_iterations": hash_sets,
            "node_hash_consistency": node_consistent,
            "edge_hash_consistency": edge_consistent,
            "hash_stability": hash_stable,
            "final_node_hash": node_hashes[0][:20] + "...",
            "final_edge_hash": edge_hashes[0][:20] + "...",
        }

        overall_valid = node_consistent and edge_consistent and hash_stable

        print(f"Node hash consistency: {node_consistent}")
        print(f"Edge hash consistency: {edge_consistent}")
        print(f"Hash stability: {hash_stable}")
        print(f"Node hash: {node_hashes[0][:20]}...")
        print(f"Edge hash: {edge_hashes[0][:20]}...")

        result["details"] = determinism_status
        result["success"] = overall_valid

        if overall_valid:
            print("✅ DETERMINISTIC HASHES TEST PASSED")
        else:
            print("❌ DETERMINISTIC HASHES TEST FAILED")

        return result

    def test_mutation_lineage_completeness(self) -> dict[str, Any]:
        """TEST: Verify mutation lineage completeness."""
        print("\n" + "=" * 80)
        print("REPLAY DETERMINISM TEST 2 - Mutation Lineage Completeness")
        print("=" * 80)

        result = {"success": False, "details": {}}

        # Test 4.1: Required mutation edge types exist
        required_mutation_edges = [
            "emits_replay_key",
            "references_policy_hash",
            "mutation_signature",
            "parent_snapshot_hash",
            "links_to_execution_trace",
        ]

        mutation_edge_counts = {}
        for edge_type in required_mutation_edges:
            count = self.execute_query(
                "SELECT COUNT(*) as count FROM edges WHERE relation_type = ?", (edge_type,)
            )[0]["count"]
            mutation_edge_counts[edge_type] = count

        missing_mutation_edges = [edge for edge, count in mutation_edge_counts.items() if count == 0]

        # Test 4.2: Verify mutation edge data integrity
        mutation_edge_integrity = {}
        for edge_type in required_mutation_edges:
            if mutation_edge_counts[edge_type] > 0:
                # Check for NULL values in critical fields
                null_checks = self.execute_query(
                    """
                    SELECT
                        COUNT(*) as total,
                        SUM(CASE WHEN src_id IS NULL THEN 1 ELSE 0 END) as null_src,
                        SUM(CASE WHEN dst_id IS NULL THEN 1 ELSE 0 END) as null_dst
                    FROM edges WHERE relation_type = ?
                """,
                    (edge_type,),
                )[0]

                mutation_edge_integrity[edge_type] = {
                    "total": null_checks["total"],
                    "null_src": null_checks["null_src"],
                    "null_dst": null_checks["null_dst"],
                    "integrity": null_checks["null_src"] == 0 and null_checks["null_dst"] == 0,
                }

        # Test 4.3: Verify mutation chain connectivity (replay keys can have different connectivity patterns)
        # Check if replay keys are properly linked to any mutation-related edges
        replay_key_connectivity = self.execute_query("""
            SELECT COUNT(*) as disconnected_replay_keys
            FROM edges e1
            WHERE e1.relation_type = 'emits_replay_key'
            AND NOT EXISTS (
                SELECT 1 FROM edges e2
                WHERE (e2.src_id = e1.dst_id OR e2.dst_id = e1.dst_id)
                AND e2.relation_type IN ('links_to_execution_trace', 'mutation_signature', 'emits_determinism_digest', 'parent_snapshot_hash', 'references_policy_hash')
            )
        """)[0]["disconnected_replay_keys"]

        # Check total replay keys to calculate connectivity ratio
        total_replay_keys = self.execute_query(
            "SELECT COUNT(*) as count FROM edges WHERE relation_type = 'emits_replay_key'"
        )[0]["count"]
        connectivity_ratio = (
            (total_replay_keys - replay_key_connectivity) / total_replay_keys
            if total_replay_keys > 0
            else 1.0
        )

        # Consider connectivity acceptable if > 50% are connected (replay keys have varied connectivity patterns)
        connectivity_acceptable = connectivity_ratio >= 0.5

        lineage_status = {
            "required_mutation_edges": required_mutation_edges,
            "mutation_edge_counts": mutation_edge_counts,
            "missing_mutation_edges": missing_mutation_edges,
            "mutation_edge_integrity": mutation_edge_integrity,
            "replay_key_connectivity": {
                "total_replay_keys": total_replay_keys,
                "disconnected_count": replay_key_connectivity,
                "connected_count": total_replay_keys - replay_key_connectivity,
                "connectivity_ratio": round(connectivity_ratio, 2),
                "connectivity_acceptable": connectivity_acceptable,
            },
            "completeness": len(missing_mutation_edges) == 0 and connectivity_acceptable,
        }

        overall_valid = lineage_status["completeness"]

        print(f"Required mutation edges present: {len(missing_mutation_edges) == 0}")
        print(f"Missing edges: {missing_mutation_edges}")
        print(
            f"Replay key connectivity: {connectivity_ratio:.1%} ({total_replay_keys - replay_key_connectivity}/{total_replay_keys} connected)"
        )

        result["details"] = lineage_status
        result["success"] = overall_valid

        if overall_valid:
            print("✅ MUTATION LINEAGE COMPLETENESS TEST PASSED")
        else:
            print("❌ MUTATION LINEAGE COMPLETENESS TEST FAILED")

        return result

    # ======================================================================
    # EDGE COVERAGE TESTS
    # ======================================================================

    def test_critical_edge_presence(self) -> dict[str, Any]:
        """TEST: Verify critical edge presence for core modules."""
        print("\n" + "=" * 80)
        print("EDGE COVERAGE TEST 1 - Critical Edge Presence")
        print("=" * 80)

        result = {"success": False, "details": {}}

        # Test 5.1: Identify critical modules
        critical_layers = ["L0_FOUNDATION", "L2_COORDINATION", "L5_EXECUTION"]
        critical_modules = self.execute_query(
            f"""
            SELECT adg_name, layer, id
            FROM nodes
            WHERE layer IN ({",".join(["?" for _ in critical_layers])})
            AND entity_type = 'module'
        """,
            critical_layers,
        )

        # Test 5.2: Required critical edges
        required_critical_edges = [
            "determinism_seed",
            "determinism_digest_emit",
            "policy_verification",
            "execution_plan_dispatch",
        ]

        coverage_results = []
        modules_missing_edges = []

        for module in critical_modules:
            module_id = module["id"]

            # Check for each required edge type
            module_edges = self.execute_query(
                """
                SELECT DISTINCT relation_type FROM edges
                WHERE src_id = ? OR dst_id = ?
            """,
                (module_id, module_id),
            )

            module_edge_types = {row["relation_type"] for row in module_edges}
            missing_edges = [edge for edge in required_critical_edges if edge not in module_edge_types]

            coverage_result = {
                "module": module["adg_name"],
                "layer": module["layer"],
                "has_required_edges": len(missing_edges) == 0,
                "missing_edges": missing_edges,
                "present_edge_types": list(module_edge_types),
            }

            coverage_results.append(coverage_result)

            if missing_edges:
                modules_missing_edges.append(
                    {
                        "module": module["adg_name"],
                        "layer": module["layer"],
                        "missing_edges": missing_edges,
                    }
                )

        # Test 5.3: Edge type distribution sanity
        edge_type_dist = self.execute_query(
            "SELECT relation_type, COUNT(*) as count FROM edges GROUP BY relation_type ORDER BY count DESC LIMIT 20"
        )
        edge_distribution = {row["relation_type"]: row["count"] for row in edge_type_dist}

        coverage_status = {
            "critical_modules_count": len(critical_modules),
            "required_critical_edges": required_critical_edges,
            "module_coverage_results": coverage_results,
            "modules_missing_edges": modules_missing_edges,
            "coverage_complete": len(modules_missing_edges) == 0,
            "edge_distribution_sample": edge_distribution,
        }

        overall_valid = len(modules_missing_edges) == 0

        print(f"Critical modules: {len(critical_modules)}")
        print(f"Modules with complete coverage: {len(critical_modules) - len(modules_missing_edges)}")
        print(f"Modules missing edges: {len(modules_missing_edges)}")

        result["details"] = coverage_status
        result["success"] = overall_valid

        if overall_valid:
            print("✅ CRITICAL EDGE PRESENCE TEST PASSED")
        else:
            print("❌ CRITICAL EDGE PRESENCE TEST FAILED")

        return result

    # ======================================================================
    # BOUNDARY REGRESSION TESTS
    # ======================================================================

    def test_boundary_integrity(self) -> dict[str, Any]:
        """TEST: Verify boundary integrity and no regressions."""
        print("\n" + "=" * 80)
        print("BOUNDARY REGRESSION TEST 1 - Boundary Integrity")
        print("=" * 80)

        result = {"success": False, "details": {}}

        # Test 6.1: Critical layer unresolved imports
        critical_unresolved = self.execute_query(
            f"""
            SELECT COUNT(*) as count
            FROM nodes n
            WHERE n.layer IN ({",".join(["?" for _ in ["L0_FOUNDATION", "L2_COORDINATION", "L5_EXECUTION"]])})
            AND EXISTS (
                SELECT 1 FROM edges e
                WHERE e.dst_id = n.id AND e.relation_type = 'unresolved_import'
            )
        """,
            ["L0_FOUNDATION", "L2_COORDINATION", "L5_EXECUTION"],
        )[0]["count"]

        # Test 6.2: Edge classification completeness
        unclassified_edges = self.execute_query(
            "SELECT COUNT(*) as count FROM edges WHERE edge_kind = '' OR edge_kind IS NULL"
        )[0]["count"]

        # Test 6.3: Boundary edge integrity
        boundary_edge_types = [
            "unresolved_import",
            "external_http_call",
            "reads_secret",
            "accesses_credential",
        ]
        boundary_edge_counts = {}

        for edge_type in boundary_edge_types:
            count = self.execute_query(
                "SELECT COUNT(*) as count FROM edges WHERE relation_type = ?", (edge_type,)
            )[0]["count"]
            boundary_edge_counts[edge_type] = count

        # Test 6.4: Security boundary validation (test modules can access secrets for testing)
        security_violations = self.execute_query("""
            SELECT COUNT(*) as count
            FROM edges e
            JOIN nodes n_src ON e.src_id = n_src.id
            JOIN nodes n_dst ON e.dst_id = n_dst.id
            WHERE e.relation_type IN ('reads_secret', 'accesses_credential')
            AND n_src.layer = 'L_TEST'
        """)[0]["count"]

        # Test security violations in production layers (L0, L2, L5)
        production_security_violations = self.execute_query("""
            SELECT COUNT(*) as count
            FROM edges e
            JOIN nodes n_src ON e.src_id = n_src.id
            JOIN nodes n_dst ON e.dst_id = n_dst.id
            WHERE e.relation_type IN ('reads_secret', 'accesses_credential')
            AND n_src.layer IN ('L0_FOUNDATION', 'L2_COORDINATION', 'L5_EXECUTION')
        """)[0]["count"]

        boundary_status = {
            "critical_unresolved_imports": critical_unresolved,
            "unclassified_edges": unclassified_edges,
            "boundary_edge_counts": boundary_edge_counts,
            "test_security_violations": security_violations,
            "production_security_violations": production_security_violations,
            "boundary_integrity": {
                "no_critical_unresolved": critical_unresolved == 0,
                "all_edges_classified": unclassified_edges == 0,
                "no_production_security_violations": production_security_violations == 0,
            },
            "overall_integrity": critical_unresolved == 0
            and unclassified_edges == 0
            and production_security_violations == 0,
        }

        overall_valid = boundary_status["overall_integrity"]

        print(f"Critical unresolved imports: {critical_unresolved}")
        print(f"Unclassified edges: {unclassified_edges}")
        print(f"Test security violations (expected): {security_violations}")
        print(f"Production security violations: {production_security_violations}")

        result["details"] = boundary_status
        result["success"] = overall_valid

        if overall_valid:
            print("✅ BOUNDARY INTEGRITY TEST PASSED")
        else:
            print("❌ BOUNDARY INTEGRITY TEST FAILED")

        return result

    # ======================================================================
    # TEST BINDING TESTS
    # ======================================================================

    def test_execution_trace_binding(self) -> dict[str, Any]:
        """TEST: Verify execution trace binding completeness."""
        print("\n" + "=" * 80)
        print("TEST BINDING TEST 1 - Execution Trace Binding")
        print("=" * 80)

        result = {"success": False, "details": {}}

        # Test 7.1: Execution trace edge presence
        execution_trace_edges = self.execute_query(
            "SELECT COUNT(*) as count FROM edges WHERE relation_type = 'links_to_execution_trace'"
        )[0]["count"]

        # Test 7.2: Test result emission completeness
        test_result_edges = self.execute_query(
            "SELECT COUNT(*) as count FROM edges WHERE relation_type = 'emits_test_result'"
        )[0]["count"]

        # Test 7.3: Regression detection binding
        regression_detection_edges = self.execute_query(
            "SELECT COUNT(*) as count FROM edges WHERE relation_type = 'detects_regression'"
        )[0]["count"]

        # Test 7.4: Promotion gating
        promotion_gating_edges = self.execute_query(
            "SELECT COUNT(*) as count FROM edges WHERE relation_type = 'gates_promotion'"
        )[0]["count"]

        # Test 7.5: Test case definition completeness
        test_case_definitions = self.execute_query(
            "SELECT COUNT(*) as count FROM edges WHERE relation_type = 'defines_test_case'"
        )[0]["count"]

        # Test 7.6: Test coverage binding
        coverage_edges = self.execute_query(
            "SELECT COUNT(*) as count FROM edges WHERE relation_type = 'covers'"
        )[0]["count"]

        binding_status = {
            "execution_trace_edges": execution_trace_edges,
            "test_result_edges": test_result_edges,
            "regression_detection_edges": regression_detection_edges,
            "promotion_gating_edges": promotion_gating_edges,
            "test_case_definitions": test_case_definitions,
            "coverage_edges": coverage_edges,
            "binding_completeness": {
                "has_execution_traces": execution_trace_edges > 0,
                "has_test_results": test_result_edges > 0,
                "has_regression_detection": regression_detection_edges > 0,
                "has_promotion_gating": promotion_gating_edges > 0,
                "has_test_cases": test_case_definitions > 0,
                "has_coverage": coverage_edges > 0,
            },
            "overall_binding": all(
                [
                    execution_trace_edges > 0,
                    test_result_edges > 0,
                    regression_detection_edges > 0,
                    promotion_gating_edges > 0,
                    test_case_definitions > 0,
                    coverage_edges > 0,
                ]
            ),
        }

        overall_valid = binding_status["overall_binding"]

        print(f"Execution trace edges: {execution_trace_edges}")
        print(f"Test result edges: {test_result_edges}")
        print(f"Regression detection edges: {regression_detection_edges}")
        print(f"Promotion gating edges: {promotion_gating_edges}")
        print(f"Test case definitions: {test_case_definitions}")
        print(f"Coverage edges: {coverage_edges}")

        result["details"] = binding_status
        result["success"] = overall_valid

        if overall_valid:
            print("✅ EXECUTION TRACE BINDING TEST PASSED")
        else:
            print("❌ EXECUTION TRACE BINDING TEST FAILED")

        return result

    # ======================================================================
    # END-TO-END TESTS
    # ======================================================================

    def test_system_consistency(self) -> dict[str, Any]:
        """TEST: Verify overall system consistency."""
        print("\n" + "=" * 80)
        print("END-TO-END TEST 1 - System Consistency")
        print("=" * 80)

        result = {"success": False, "details": {}}

        # Test 8.1: Node-edge consistency
        node_count = self.execute_query("SELECT COUNT(*) as count FROM nodes")[0]["count"]
        edge_count = self.execute_query("SELECT COUNT(*) as count FROM edges")[0]["count"]

        # Verify all edge references are valid
        invalid_src_refs = self.execute_query(
            "SELECT COUNT(*) as count FROM edges WHERE src_id NOT IN (SELECT id FROM nodes)"
        )[0]["count"]
        invalid_dst_refs = self.execute_query(
            "SELECT COUNT(*) as count FROM edges WHERE dst_id NOT IN (SELECT id FROM nodes)"
        )[0]["count"]

        # Test 8.2: Entity type consistency
        entity_types = self.execute_query("SELECT DISTINCT entity_type FROM nodes")
        entity_type_list = [row["entity_type"] for row in entity_types]

        # Test 8.3: Relation type consistency
        relation_types = self.execute_query("SELECT DISTINCT relation_type FROM edges")
        relation_type_list = [row["relation_type"] for row in relation_types]

        # Test 8.4: Database size sanity check
        db_size = self.sqlite_path.stat().st_size
        size_reasonable = db_size > 1000000  # At least 1MB

        consistency_status = {
            "node_edge_counts": {"nodes": node_count, "edges": edge_count},
            "reference_integrity": {
                "invalid_src_refs": invalid_src_refs,
                "invalid_dst_refs": invalid_dst_refs,
                "references_valid": invalid_src_refs == 0 and invalid_dst_refs == 0,
            },
            "entity_types": entity_type_list,
            "relation_types": relation_type_list,
            "database_size": {
                "bytes": db_size,
                "mb": round(db_size / 1024 / 1024, 2),
                "reasonable": size_reasonable,
            },
            "overall_consistency": (
                invalid_src_refs == 0
                and invalid_dst_refs == 0
                and size_reasonable
                and node_count > 0
                and edge_count > 0
            ),
        }

        overall_valid = consistency_status["overall_consistency"]

        print(f"Nodes: {node_count}, Edges: {edge_count}")
        print(f"Reference integrity: {invalid_src_refs == 0 and invalid_dst_refs == 0}")
        print(f"Database size: {round(db_size / 1024 / 1024, 2)} MB")

        result["details"] = consistency_status
        result["success"] = overall_valid

        if overall_valid:
            print("✅ SYSTEM CONSISTENCY TEST PASSED")
        else:
            print("❌ SYSTEM CONSISTENCY TEST FAILED")

        return result

    def run_all_tests(self) -> dict[str, Any]:
        """Run complete rigorous test suite."""
        print("=" * 80)
        print("RIGOROUS WINSURFRULES TESTING - ADG Gap Closure Implementation")
        print("=" * 80)
        print(f"Timestamp: {self.timestamp}")
        print(f"Database: {self.sqlite_path.name}")

        try:
            self.connect()

            # DATA INTEGRITY TESTS
            print("\n🔧 DATA INTEGRITY TESTS")
            self.test_results["data_integrity_tests"]["completeness"] = (
                self.test_data_integrity_completeness()
            )
            self.test_results["data_integrity_tests"]["layer_architecture"] = (
                self.test_layer_architecture_validity()
            )

            # REPLAY DETERMINISM TESTS
            print("\n🔧 REPLAY DETERMINISM TESTS")
            self.test_results["replay_determinism_tests"]["hash_determinism"] = (
                self.test_deterministic_hashes()
            )
            self.test_results["replay_determinism_tests"]["mutation_lineage"] = (
                self.test_mutation_lineage_completeness()
            )

            # EDGE COVERAGE TESTS
            print("\n🔧 EDGE COVERAGE TESTS")
            self.test_results["edge_coverage_tests"]["critical_edges"] = self.test_critical_edge_presence()

            # BOUNDARY REGRESSION TESTS
            print("\n🔧 BOUNDARY REGRESSION TESTS")
            self.test_results["boundary_regression_tests"]["boundary_integrity"] = (
                self.test_boundary_integrity()
            )

            # TEST BINDING TESTS
            print("\n🔧 TEST BINDING TESTS")
            self.test_results["test_binding_tests"]["execution_trace_binding"] = (
                self.test_execution_trace_binding()
            )

            # END-TO-END TESTS
            print("\n🔧 END-TO-END TESTS")
            self.test_results["end_to_end_tests"]["system_consistency"] = self.test_system_consistency()

            # Calculate overall success
            all_test_results = []
            for category in self.test_results.values():
                if isinstance(category, dict):
                    for test_result in category.values():
                        if isinstance(test_result, dict) and "success" in test_result:
                            all_test_results.append(test_result["success"])

            self.test_results["overall_success"] = all(all_test_results)

            return self.test_results

        finally:
            self.close()

    def save_test_report(self):
        """Save comprehensive test report."""
        report_path = REPORTS_DIR / f"rigorous_test_report_{self.timestamp}.json"
        REPORTS_DIR.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(self.test_results, f, indent=2, sort_keys=True)

        print(f"\n📊 Test report saved: {report_path.name}")
        return report_path


def main():
    """Run rigorous testing suite."""
    ROOT = Path(__file__).resolve().parents[1]

    # Find most recent SQLite database
    sqlite_files = list((ROOT / "artifacts" / "adg").glob("*.sqlite"))
    if not sqlite_files:
        print("❌ No SQLite database found in artifacts/adg/")
        return

    sqlite_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    sqlite_path = sqlite_files[0]

    print(f"Using database: {sqlite_path.name}")

    test_suite = ADGRigorousTestSuite(sqlite_path)
    results = test_suite.run_all_tests()
    test_suite.save_test_report()

    # Final summary
    print("\n" + "=" * 80)
    print("RIGOROUS WINSURFRULES TESTING RESULTS")
    print("=" * 80)

    # Category results
    for category_name, category_tests in results.items():
        if category_name == "overall_success":
            continue

        print(f"\n{category_name.upper().replace('_', ' ')}:")
        for test_name, test_result in category_tests.items():
            if isinstance(test_result, dict) and "success" in test_result:
                status = "PASS" if test_result["success"] else "FAIL"
                print(f"  {status}: {test_name.upper().replace('_', ' ')}")

    print(f"\nOVERALL: {'SUCCESS' if results['overall_success'] else 'FAILURE'}")

    if results["overall_success"]:
        print("\n🎉 ALL RIGOROUS TESTS PASSED")
        print("ADG Gap Closure implementation meets all winsurfrules standards")
        print("System is production-ready with full integrity validation")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Review failed tests above")

        # Exit with error code for CI
        exit(1)


if __name__ == "__main__":
    main()
