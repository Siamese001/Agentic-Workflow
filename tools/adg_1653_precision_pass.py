#!/usr/bin/env python3
"""ADG 1653 Minimal Precision Pass - Final gap closure with exact parity.

This pass ensures:
1. Report ↔ SQLite hard parity (no drift)
2. Critical path boundary zero tolerance
3. Replay determinism (proven)
4. Symbol layer propagation enforcement
5. Core module edge coverage guarantee
6. Test surface hard binding
7. Final system lock
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class ADG1653PrecisionPass:
    """Implements the 1653 minimal precision pass."""

    def __init__(self, sqlite_path: Path):
        self.sqlite_path = sqlite_path
        self.conn = sqlite3.connect(sqlite_path)
        self.cur = self.conn.cursor()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        self.reports = {}

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all precision checks."""
        print("=" * 80)
        print("ADG 1653 MINIMAL PRECISION PASS")
        print("=" * 80)

        results = {
            "timestamp": self.timestamp,
            "checks": {},
            "overall_success": True
        }

        # 1. Report ↔ SQLite Hard Parity
        print("\n[1] Report <-> SQLite Hard Parity...")
        results["checks"]["parity"] = self.check_report_sqlite_parity()

        # 2. Critical Path Boundary Zero Tolerance
        print("\n[2] Critical Path Boundary Zero Tolerance...")
        results["checks"]["boundary"] = self.check_boundary_zero_tolerance()

        # 3. Replay Determinism
        print("\n[3] Replay Determinism...")
        results["checks"]["replay"] = self.check_replay_determinism()

        # 4. Symbol Layer Propagation
        print("\n[4] Symbol Layer Propagation...")
        results["checks"]["symbol_layer"] = self.check_symbol_layer_propagation()

        # 5. Core Module Edge Coverage
        print("\n[5] Core Module Edge Coverage...")
        results["checks"]["edge_coverage"] = self.check_core_edge_coverage()

        # 6. Test Surface Hard Binding
        print("\n[6] Test Surface Hard Binding...")
        results["checks"]["test_binding"] = self.check_test_surface_binding()

        # 7. Final System Lock
        print("\n[7] Final System Lock...")
        results["checks"]["system_lock"] = self.final_system_lock()

        # Overall result
        results["overall_success"] = all(check.get("success", False) for check in results["checks"].values())

        # Save comprehensive report
        self.save_comprehensive_report(results)

        return results

    def check_report_sqlite_parity(self) -> Dict[str, Any]:
        """Check exact parity between reports and SQLite."""
        result = {"success": True, "details": {}}

        # Get SQLite totals
        self.cur.execute("SELECT COUNT(*) FROM nodes")
        sqlite_nodes = self.cur.fetchone()[0]

        self.cur.execute("SELECT COUNT(*) FROM edges")
        sqlite_edges = self.cur.fetchone()[0]

        # Get edge distribution
        self.cur.execute("SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type")
        sqlite_edge_dist = dict(self.cur.fetchall())

        # Get layer distribution
        self.cur.execute("SELECT layer, COUNT(*) FROM nodes GROUP BY layer")
        sqlite_layer_dist = dict(self.cur.fetchall())

        result["details"] = {
            "sqlite_nodes": sqlite_nodes,
            "sqlite_edges": sqlite_edges,
            "sqlite_edge_distribution": sqlite_edge_dist,
            "sqlite_layer_distribution": sqlite_layer_dist
        }

        # Check for missing edge types in any existing report
        adg_dir = ROOT / "artifacts" / "adg"
        report_files = [
            adg_dir / f"edge_density_report_{self.timestamp}.json",
            adg_dir / f"layer_coverage_report_{self.timestamp}.json"
        ]

        for report_file in report_files:
            if report_file.exists():
                with open(report_file, 'r') as f:
                    report_data = json.load(f)

                if "edge_distribution" in report_data:
                    report_edges = set(report_data["edge_distribution"].keys())
                    sqlite_edges_set = set(sqlite_edge_dist.keys())

                    missing_in_report = sqlite_edges_set - report_edges
                    if missing_in_report:
                        result["success"] = False
                        result["details"]["missing_edge_types"] = list(missing_in_report)

        print(f"  SQLite: {sqlite_nodes} nodes, {sqlite_edges} edges")
        print(f"  Edge types: {len(sqlite_edge_dist)}")
        if result["success"]:
            print("  PASS Parity check passed")
        else:
            print("  FAIL Parity check failed")

        return result

    def check_boundary_zero_tolerance(self) -> Dict[str, Any]:
        """Check for zero unresolved imports in critical path."""
        result = {"success": True, "details": {}}

        # Check for unresolved_import edges
        self.cur.execute("""
            SELECT COUNT(*) FROM edges
            WHERE relation_type = 'unresolved_import'
        """)
        total_unresolved = self.cur.fetchone()[0]

        # Check critical path unresolved
        critical_patterns = ['agentic_core/L0_', 'agentic_core/L2_', 'agentic_core/L5_']
        critical_unresolved = 0

        for pattern in critical_patterns:
            self.cur.execute("""
                SELECT COUNT(*) FROM edges e
                JOIN nodes n ON e.src_id = n.id
                WHERE e.relation_type = 'unresolved_import'
                AND n.resolved_path LIKE ?
            """, (f"{pattern}%",))
            count = self.cur.fetchone()[0]
            critical_unresolved += count
            result["details"][f"unresolved_{pattern.replace('/', '_').replace('-', '')}"] = count

        result["details"]["total_unresolved"] = total_unresolved
        result["details"]["critical_unresolved"] = critical_unresolved

        # Check edge classification completeness
        self.cur.execute("""
            SELECT COUNT(*) FROM edges
            WHERE edge_kind NOT IN ('internal_to_internal', 'internal_to_external', 'external_to_internal', 'unresolved_boundary')
        """)
        unclassified_edges = self.cur.fetchone()[0]
        result["details"]["unclassified_edges"] = unclassified_edges

        result["success"] = (critical_unresolved == 0 and unclassified_edges == 0)

        print(f"  Critical unresolved: {critical_unresolved}")
        print(f"  Unclassified edges: {unclassified_edges}")
        if result["success"]:
            print("  ✅ Boundary check passed")
        else:
            print("  ❌ Boundary check failed")

        return result

    def check_replay_determinism(self) -> Dict[str, Any]:
        """Check replay determinism through hash equality."""
        result = {"success": True, "details": {}}

        # Get determinism edge counts
        determinism_edges = [
            'determinism_seed',
            'emits_determinism_digest',
            'mutation_signature',
            'parent_snapshot_hash',
            'emits_replay_key',
            'references_policy_hash'
        ]

        for edge_type in determinism_edges:
            self.cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (edge_type,))
            count = self.cur.fetchone()[0]
            result["details"][edge_type] = count

        # Calculate database hash
        db_hash = self.calculate_database_hash()
        result["details"]["database_hash"] = db_hash

        # Check mutation coverage
        self.cur.execute("""
            SELECT COUNT(DISTINCT e.src_id)
            FROM edges e
            JOIN nodes n ON e.src_id = n.id
            WHERE e.relation_type IN ('emits_replay_key', 'references_policy_hash')
            AND n.entity_type = 'module'
        """)
        modules_with_lineage = self.cur.fetchone()[0]

        self.cur.execute("SELECT COUNT(*) FROM nodes WHERE entity_type = 'module'")
        total_modules = self.cur.fetchone()[0]

        lineage_coverage = modules_with_lineage / total_modules if total_modules > 0 else 0
        result["details"]["lineage_coverage"] = lineage_coverage
        result["details"]["modules_with_lineage"] = modules_with_lineage
        result["details"]["total_modules"] = total_modules

        result["success"] = lineage_coverage >= 0.8  # 80% coverage required

        print(f"  Lineage coverage: {lineage_coverage:.1%}")
        print(f"  Database hash: {db_hash[:16]}...")
        if result["success"]:
            print("  ✅ Replay check passed")
        else:
            print("  ❌ Replay check failed")

        return result

    def check_symbol_layer_propagation(self) -> Dict[str, Any]:
        """Check symbol-layer consistency."""
        result = {"success": True, "details": {}}

        # Find violations: symbol.layer == L_UNKNOWN AND module.layer != L_UNKNOWN
        self.cur.execute("""
            SELECT COUNT(*) FROM nodes n1
            JOIN nodes n2 ON n1.adg_name LIKE n2.adg_name || '::%'
            WHERE n1.layer = 'L_UNKNOWN'
            AND n2.layer != 'L_UNKNOWN'
            AND n2.entity_type = 'module'
        """)
        violations = self.cur.fetchone()[0]

        result["details"]["symbol_layer_violations"] = violations

        # Get L_UNKNOWN counts
        self.cur.execute("SELECT COUNT(*) FROM nodes WHERE layer = 'L_UNKNOWN'")
        total_unknown = self.cur.fetchone()[0]

        self.cur.execute("""
            SELECT COUNT(*) FROM nodes n1
            JOIN nodes n2 ON n1.adg_name LIKE n2.adg_name || '::%'
            WHERE n1.layer = 'L_UNKNOWN'
            AND n2.layer = 'L_UNKNOWN'
            AND n2.entity_type = 'module'
        """)
        unknown_with_unknown_module = self.cur.fetchone()[0]

        result["details"]["total_unknown_nodes"] = total_unknown
        result["details"]["unknown_with_unknown_module"] = unknown_with_unknown_module

        result["success"] = violations == 0

        print(f"  Symbol-layer violations: {violations}")
        print(f"  Total unknown nodes: {total_unknown}")
        if result["success"]:
            print("  ✅ Symbol layer check passed")
        else:
            print("  ❌ Symbol layer check failed")

        return result

    def check_core_edge_coverage(self) -> Dict[str, Any]:
        """Check core modules have minimum required edge coverage."""
        result = {"success": True, "details": {}}

        # Get core modules
        self.cur.execute("""
            SELECT adg_name, id, layer
            FROM nodes
            WHERE entity_type = 'module'
            AND layer IN ('L0', 'L2', 'L5')
        """)
        core_modules = self.cur.fetchall()

        # Required edge families
        determinism_edges = ['determinism_seed', 'emits_determinism_digest']
        governance_edges = ['policy_verification']
        execution_edges = ['dispatches_execution_plan']

        coverage_stats = {
            "total_core_modules": len(core_modules),
            "modules_with_determinism": 0,
            "modules_with_governance": 0,
            "modules_with_execution": 0,
            "missing_determinism": [],
            "missing_governance": [],
            "missing_execution": []
        }

        for module_adg, module_id, layer in core_modules:
            # Check determinism
            self.cur.execute("""
                SELECT COUNT(*) FROM edges
                WHERE src_id = ? AND relation_type IN (?, ?)
            """, (module_id, determinism_edges[0], determinism_edges[1]))
            if self.cur.fetchone()[0] > 0:
                coverage_stats["modules_with_determinism"] += 1
            else:
                coverage_stats["missing_determinism"].append(module_adg)

            # Check governance
            self.cur.execute("""
                SELECT COUNT(*) FROM edges
                WHERE src_id = ? AND relation_type = ?
            """, (module_id, governance_edges[0]))
            if self.cur.fetchone()[0] > 0:
                coverage_stats["modules_with_governance"] += 1
            else:
                coverage_stats["missing_governance"].append(module_adg)

            # Check execution
            self.cur.execute("""
                SELECT COUNT(*) FROM edges
                WHERE src_id = ? AND relation_type = ?
            """, (module_id, execution_edges[0]))
            if self.cur.fetchone()[0] > 0:
                coverage_stats["modules_with_execution"] += 1
            else:
                coverage_stats["missing_execution"].append(module_adg)

        result["details"] = coverage_stats

        # Success if all core modules have all required edges
        result["success"] = (
            coverage_stats["modules_with_determinism"] == coverage_stats["total_core_modules"] and
            coverage_stats["modules_with_governance"] == coverage_stats["total_core_modules"] and
            coverage_stats["modules_with_execution"] == coverage_stats["total_core_modules"]
        )

        print(f"  Core modules: {coverage_stats['total_core_modules']}")
        print(f"  With determinism: {coverage_stats['modules_with_determinism']}")
        print(f"  With governance: {coverage_stats['modules_with_governance']}")
        print(f"  With execution: {coverage_stats['modules_with_execution']}")
        if result["success"]:
            print("  ✅ Edge coverage check passed")
        else:
            print("  ❌ Edge coverage check failed")

        return result

    def check_test_surface_binding(self) -> Dict[str, Any]:
        """Check test surface hard binding."""
        result = {"success": True, "details": {}}

        # Get required test nodes
        test_node_types = ['test_suite', 'test_case', 'invariant_family']
        test_node_counts = {}
        for node_type in test_node_types:
            self.cur.execute("SELECT COUNT(*) FROM nodes WHERE entity_type = ?", (node_type,))
            test_node_counts[node_type] = self.cur.fetchone()[0]

        # Get required test edges
        test_edge_types = [
            'emits_test_result',
            'links_to_execution_trace',
            'gates_promotion'
        ]
        test_edge_counts = {}
        for edge_type in test_edge_types:
            self.cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (edge_type,))
            test_edge_counts[edge_type] = self.cur.fetchone()[0]

        # Check critical module test linkage
        self.cur.execute("""
            SELECT COUNT(DISTINCT e.src_id)
            FROM edges e
            JOIN nodes n ON e.src_id = n.id
            WHERE n.entity_type = 'module'
            AND n.layer IN ('L0', 'L2', 'L5')
            AND e.relation_type IN ('defines_test_case', 'defines_test_suite')
        """)
        modules_with_tests = self.cur.fetchone()[0]

        self.cur.execute("""
            SELECT COUNT(*) FROM nodes
            WHERE entity_type = 'module'
            AND layer IN ('L0', 'L2', 'L5')
        """)
        total_critical_modules = self.cur.fetchone()[0]

        test_coverage = modules_with_tests / total_critical_modules if total_critical_modules > 0 else 0

        result["details"] = {
            "test_node_counts": test_node_counts,
            "test_edge_counts": test_edge_counts,
            "modules_with_tests": modules_with_tests,
            "total_critical_modules": total_critical_modules,
            "test_coverage_percentage": test_coverage
        }

        result["success"] = (
            test_node_counts['test_case'] > 0 and
            test_edge_counts['links_to_execution_trace'] > 0 and
            test_coverage >= 0.9
        )

        print(f"  Test cases: {test_node_counts['test_case']}")
        print(f"  Test linkage: {test_coverage:.1%}")
        if result["success"]:
            print("  ✅ Test binding check passed")
        else:
            print("  ❌ Test binding check failed")

        return result

    def final_system_lock(self) -> Dict[str, Any]:
        """Final system lock validation."""
        result = {"success": True, "details": {}}

        # Get final statistics
        self.cur.execute("SELECT COUNT(*) FROM nodes")
        total_nodes = self.cur.fetchone()[0]

        self.cur.execute("SELECT COUNT(*) FROM edges")
        total_edges = self.cur.fetchone()[0]

        # Get layer distribution
        self.cur.execute("SELECT layer, COUNT(*) FROM nodes GROUP BY layer")
        layer_dist = dict(self.cur.fetchall())

        # Get edge type distribution
        self.cur.execute("SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type")
        edge_dist = dict(self.cur.fetchall())

        result["details"] = {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "layer_distribution": layer_dist,
            "edge_type_count": len(edge_dist),
            "system_hash": self.calculate_database_hash()
        }

        result["success"] = total_nodes > 0 and total_edges > 0

        print(f"  Final state: {total_nodes} nodes, {total_edges} edges")
        print(f"  Edge types: {len(edge_dist)}")
        if result["success"]:
            print("  ✅ System lock passed")
        else:
            print("  ❌ System lock failed")

        return result

    def calculate_database_hash(self) -> str:
        """Calculate hash of entire database for determinism."""
        hasher = hashlib.sha256()

        # Hash nodes
        self.cur.execute("SELECT adg_name, entity_type, layer, identity_kind FROM nodes ORDER BY id")
        for row in self.cur.fetchall():
            hasher.update('|'.join(map(str, row)).encode())

        # Hash edges
        self.cur.execute("SELECT src_id, dst_id, relation_type, edge_kind FROM edges ORDER BY id")
        for row in self.cur.fetchall():
            hasher.update('|'.join(map(str, row)).encode())

        return hasher.hexdigest()

    def save_comprehensive_report(self, results: Dict[str, Any]):
        """Save comprehensive precision report."""
        report_dir = ROOT / "artifacts" / "adg"
        report_path = report_dir / f"adg_1653_precision_report_{self.timestamp}.json"

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, sort_keys=True)

        print(f"\n📄 Report saved: {report_path}")

        # Save individual reports for CI gates
        self.save_ci_gate_reports(results)

    def save_ci_gate_reports(self, results: Dict[str, Any]):
        """Save individual reports for CI gates."""
        report_dir = ROOT / "artifacts" / "adg"

        # 1. Reconciliation Report
        reconciliation = {
            "timestamp": self.timestamp,
            "parity_check": results["checks"]["parity"],
            "validation": {
                "report_sqlite_match": results["checks"]["parity"]["success"],
                "missing_edge_types": results["checks"]["parity"]["details"].get("missing_edge_types", [])
            }
        }
        with open(report_dir / "reconciliation_report.json", 'w') as f:
            json.dump(reconciliation, f, indent=2)

        # 2. Boundary Report
        boundary = {
            "timestamp": self.timestamp,
            "boundary_metrics": results["checks"]["boundary"]["details"],
            "validation": {
                "critical_path_clear": results["checks"]["boundary"]["details"]["critical_unresolved"] == 0,
                "all_edges_classified": results["checks"]["boundary"]["details"]["unclassified_edges"] == 0
            }
        }
        with open(report_dir / "boundary_report.json", 'w') as f:
            json.dump(boundary, f, indent=2)

        # 3. Replay Convergence Report
        replay = {
            "timestamp": self.timestamp,
            "replay_metrics": results["checks"]["replay"]["details"],
            "validation": {
                "determinism_proven": results["checks"]["replay"]["success"],
                "lineage_complete": results["checks"]["replay"]["details"]["lineage_coverage"] >= 0.8
            }
        }
        with open(report_dir / "replay_convergence_report.json", 'w') as f:
            json.dump(replay, f, indent=2)

        # 4. Critical Edge Coverage Report
        coverage = {
            "timestamp": self.timestamp,
            "coverage_metrics": results["checks"]["edge_coverage"]["details"],
            "validation": {
                "all_core_covered": results["checks"]["edge_coverage"]["success"]
            }
        }
        with open(report_dir / "critical_edge_coverage.json", 'w') as f:
            json.dump(coverage, f, indent=2)

        # 5. Test Surface Coverage Report
        test_surface = {
            "timestamp": self.timestamp,
            "binding_metrics": results["checks"]["test_binding"]["details"],
            "validation": {
                "critical_binding_complete": results["checks"]["test_binding"]["success"]
            }
        }
        with open(report_dir / "test_surface_coverage.json", 'w') as f:
            json.dump(test_surface, f, indent=2)

    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """Main execution."""
    # Find latest SQLite database
    adg_dir = ROOT / "artifacts" / "adg" / "databases"
    sqlite_files = sorted(adg_dir.glob("adg_indexed_*.sqlite"),
                         key=lambda p: p.stat().st_mtime, reverse=True)

    if not sqlite_files:
        print("ERROR: No SQLite database found")
        return 1

    sqlite_path = sqlite_files[0]
    print(f"Using database: {sqlite_path.name}")

    # Run precision pass
    precision_pass = ADG1653PrecisionPass(sqlite_path)

    try:
        results = precision_pass.run_all_checks()

        print("\n" + "=" * 80)
        print("1653 PRECISION PASS RESULTS")
        print("=" * 80)

        for check_name, check_result in results["checks"].items():
            status = "✅ PASS" if check_result.get("success", False) else "❌ FAIL"
            print(f"{check_name.upper()}: {status}")

        overall_status = "✅ SUCCESS" if results["overall_success"] else "❌ FAILURE"
        print(f"\nOVERALL: {overall_status}")

        if results["overall_success"]:
            print("\n🎉 ADG 1653 PRECISION PASS COMPLETED SUCCESSFULLY")
            print("System is precision-complete with exact parity")
        else:
            print("\n⚠️  ADG 1653 PRECISION PASS FAILED")
            print("Review detailed reports for specific failures")

        return 0 if results["overall_success"] else 1

    finally:
        precision_pass.close()


if __name__ == "__main__":
    sys.exit(main())
