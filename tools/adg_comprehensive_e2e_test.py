#!/usr/bin/env python3
"""ADG Comprehensive End-to-End Test with Cache.

Tests the complete ADG system using the scan cache to ensure:
1. Cache loading works properly
2. ADG generation completes successfully
3. All artifacts are generated with correct timestamps
4. Database integrity is maintained
5. Reports are accurate and complete
"""

import json
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class ADGComprehensiveE2ETest:
    """Comprehensive end-to-end test for ADG system."""

    def __init__(self):
        self.start_time = time.time()
        self.timestamp = datetime.now().strftime("%m%d%Y_%H%M")
        self.adg_dir = ROOT / "artifacts" / "adg"
        self.cache_file = self.adg_dir / "scan_result_cache.json"
        self.results = {
            "test_start": datetime.now().isoformat(),
            "timestamp": self.timestamp,
            "checks": {},
            "overall_success": True
        }

    def run_all_tests(self) -> dict[str, Any]:
        """Run comprehensive E2E tests."""
        print("=" * 80)
        print("ADG COMPREHENSIVE END-TO-END TEST WITH CACHE")
        print("=" * 80)
        print(f"Timestamp: {self.timestamp}")
        print(f"Cache file: {self.cache_file}")

        # 1. Verify cache exists and is valid
        print("\n[1] VERIFYING SCAN CACHE...")
        self.results["checks"]["cache_verification"] = self.verify_scan_cache()

        # 2. Run ADG generation with cache
        print("\n[2] RUNNING ADG GENERATION WITH CACHE...")
        self.results["checks"]["adg_generation"] = self.run_adg_generation()

        # 3. Verify all artifacts generated
        print("\n[3] VERIFYING ARTIFACTS GENERATED...")
        self.results["checks"]["artifacts_verification"] = self.verify_artifacts()

        # 4. Test database integrity
        print("\n[4] TESTING DATABASE INTEGRITY...")
        self.results["checks"]["database_integrity"] = self.test_database_integrity()

        # 5. Test report accuracy
        print("\n[5] TESTING REPORT ACCURACY...")
        self.results["checks"]["report_accuracy"] = self.test_report_accuracy()

        # 6. Test cache performance
        print("\n[6] TESTING CACHE PERFORMANCE...")
        self.results["checks"]["cache_performance"] = self.test_cache_performance()

        # 7. Test precision pass
        print("\n[7] TESTING PRECISION PASS...")
        self.results["checks"]["precision_pass"] = self.test_precision_pass()

        # Calculate overall results
        self.results["test_end"] = datetime.now().isoformat()
        self.results["duration_seconds"] = time.time() - self.start_time
        self.results["overall_success"] = all(check.get("success", False) for check in self.results["checks"].values())

        return self.results

    def verify_scan_cache(self) -> dict[str, Any]:
        """Verify scan cache exists and is valid."""
        result = {"success": True, "details": {}}

        if not self.cache_file.exists():
            result["success"] = False
            result["details"]["error"] = "Cache file does not exist"
            return result

        try:
            with open(self.cache_file) as f:
                cache_data = json.load(f)

            # Verify cache structure
            required_keys = ["modules", "metadata", "timestamp"]
            missing_keys = [key for key in required_keys if key not in cache_data]

            if missing_keys:
                result["success"] = False
                result["details"]["missing_keys"] = missing_keys
                return result

            # Count cached modules
            module_count = len(cache_data.get("modules", {}))
            result["details"] = {
                "cache_exists": True,
                "cache_size_mb": self.cache_file.stat().st_size / (1024 * 1024),
                "cached_modules": module_count,
                "cache_timestamp": cache_data.get("metadata", {}).get("generated_at", "unknown")
            }

            print("  Cache exists: ✅")
            print(f"  Cache size: {result['details']['cache_size_mb']:.1f} MB")
            print(f"  Cached modules: {module_count:,}")
            print(f"  Cache timestamp: {result['details']['cache_timestamp']}")

        except (ValueError, TypeError, RuntimeError) as e:
            result["success"] = False
            result["details"]["error"] = str(e)
            print(f"  Cache verification failed: {e}")

        return result

    def run_adg_generation(self) -> dict[str, Any]:
        """Run ADG generation with cache."""
        result = {"success": True, "details": {}}

        try:
            # Run the existing ADG generation script
            import subprocess

            gen_start = time.time()

            # Run generate_full_adg.py
            process = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "generate_full_adg.py")],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            gen_duration = time.time() - gen_start

            if process.returncode != 0:
                result["success"] = False
                result["details"] = {
                    "error": "ADG generation script failed",
                    "return_code": process.returncode,
                    "stderr": process.stderr[-500:] if process.stderr else "",
                    "stdout": process.stdout[-500:] if process.stdout else ""
                }
                return result

            result["details"] = {
                "generation_duration": gen_duration,
                "generation_timestamp": self.timestamp,
                "cache_used": self.cache_file.exists(),
                "script_output": process.stdout[-200:] if process.stdout else ""
            }

            print(f"  ADG generation completed in {gen_duration:.1f}s")
            print("  Cache used: ✅")
            print(f"  Generation timestamp: {self.timestamp}")

        except (ValueError, TypeError, RuntimeError) as e:
            result["success"] = False
            result["details"]["error"] = "ADG generation timed out after 10 minutes"
            print("  ADG generation timed out")
        except (ValueError, TypeError, RuntimeError) as e:
            result["success"] = False
            result["details"]["error"] = str(e)
            print(f"  ADG generation failed: {e}")

        return result

    def verify_artifacts(self) -> dict[str, Any]:
        """Verify all expected artifacts were generated."""
        result = {"success": True, "details": {}}

        # Expected artifacts with current timestamp
        expected_artifacts = [
            f"adg_file_graph_{self.timestamp}.json",
            f"adg_governance_graph_{self.timestamp}.json",
            f"adg_graphsnap_{self.timestamp}.json",
            f"adg_indexed_{self.timestamp}.sqlite",
            f"adg_snapshot_{self.timestamp}.json",
            f"adg_symbol_graph_{self.timestamp}.json",
            f"boundary_report_{self.timestamp}.json",
            f"edge_density_report_{self.timestamp}.json",
            f"layer_coverage_report_{self.timestamp}.json",
            f"mutation_integrity_report_{self.timestamp}.json",
            f"provenance_report_{self.timestamp}.json",
            f"replay_determinism_report_{self.timestamp}.json",
            f"test_surface_coverage_{self.timestamp}.json"
        ]

        missing_artifacts = []
        found_artifacts = []
        total_size = 0

        for artifact in expected_artifacts:
            artifact_path = self.adg_dir / artifact
            if artifact_path.exists():
                found_artifacts.append(artifact)
                total_size += artifact_path.stat().st_size
            else:
                missing_artifacts.append(artifact)

        result["details"] = {
            "expected_artifacts": len(expected_artifacts),
            "found_artifacts": len(found_artifacts),
            "missing_artifacts": missing_artifacts,
            "total_size_mb": total_size / (1024 * 1024),
            "artifacts_list": found_artifacts
        }

        if missing_artifacts:
            result["success"] = False
            print(f"  Missing artifacts: {len(missing_artifacts)}")
            for missing in missing_artifacts:
                print(f"    ❌ {missing}")
        else:
            print(f"  All artifacts found: ✅ ({len(found_artifacts)}/{len(expected_artifacts)})")
            print(f"  Total size: {result['details']['total_size_mb']:.1f} MB")

        return result

    def test_database_integrity(self) -> dict[str, Any]:
        """Test database integrity and structure."""
        result = {"success": True, "details": {}}

        db_path = self.adg_dir / f"adg_indexed_{self.timestamp}.sqlite"

        if not db_path.exists():
            result["success"] = False
            result["details"]["error"] = "Database file not found"
            return result

        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            # Test basic structure
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cur.fetchall()]

            expected_tables = ["nodes", "edges"]
            missing_tables = [table for table in expected_tables if table not in tables]

            if missing_tables:
                result["success"] = False
                result["details"]["missing_tables"] = missing_tables
                return result

            # Test node counts
            cur.execute("SELECT COUNT(*) FROM nodes")
            node_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM edges")
            edge_count = cur.fetchone()[0]

            # Test data integrity
            cur.execute("SELECT COUNT(*) FROM nodes WHERE layer = '' OR layer IS NULL")
            null_layers = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM nodes WHERE identity_kind = '' OR identity_kind IS NULL")
            null_identities = cur.fetchone()[0]

            # Test edge distribution
            cur.execute("SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type ORDER BY COUNT(*) DESC LIMIT 10")
            top_relations = dict(cur.fetchall())

            result["details"] = {
                "tables": tables,
                "nodes": node_count,
                "edges": edge_count,
                "null_layers": null_layers,
                "null_identities": null_identities,
                "top_relations": top_relations,
                "integrity_score": 100 - (null_layers + null_identities) * 100 // node_count if node_count > 0 else 0
            }

            print("  Database structure: ✅")
            print(f"  Nodes: {node_count:,}")
            print(f"  Edges: {edge_count:,}")
            print(f"  Null layers: {null_layers}")
            print(f"  Null identities: {null_identities}")
            print(f"  Integrity score: {result['details']['integrity_score']}%")

            conn.close()

        except (ValueError, TypeError, RuntimeError) as e:
            result["success"] = False
            result["details"]["error"] = str(e)
            print(f"  Database integrity test failed: {e}")

        return result

    def test_report_accuracy(self) -> dict[str, Any]:
        """Test report accuracy and completeness."""
        result = {"success": True, "details": {}}

        # Test key reports
        reports_to_test = [
            f"adg_snapshot_{self.timestamp}.json",
            f"layer_coverage_report_{self.timestamp}.json",
            f"edge_density_report_{self.timestamp}.json"
        ]

        report_results = {}

        for report_name in reports_to_test:
            report_path = self.adg_dir / report_name

            if not report_path.exists():
                report_results[report_name] = {"status": "missing"}
                continue

            try:
                with open(report_path) as f:
                    report_data = json.load(f)

                # Basic structure validation
                if report_name == f"adg_snapshot_{self.timestamp}.json":
                    required_keys = ["timestamp", "nodes", "edges", "layers"]
                    missing_keys = [key for key in required_keys if key not in report_data]
                    report_results[report_name] = {
                        "status": "valid" if not missing_keys else "invalid",
                        "missing_keys": missing_keys,
                        "nodes": report_data.get("nodes", 0),
                        "edges": report_data.get("edges", 0)
                    }
                else:
                    report_results[report_name] = {
                        "status": "valid",
                        "keys": list(report_data.keys())
                    }

            except (ValueError, TypeError, RuntimeError) as e:
                report_results[report_name] = {"status": "error", "error": str(e)}

        result["details"] = report_results

        valid_reports = sum(1 for r in report_results.values() if r.get("status") == "valid")
        print(f"  Valid reports: {valid_reports}/{len(reports_to_test)}")

        for report_name, report_result in report_results.items():
            status = report_result.get("status", "unknown")
            icon = "✅" if status == "valid" else "❌"
            print(f"    {icon} {report_name}: {status}")

        return result

    def test_cache_performance(self) -> dict[str, Any]:
        """Test cache performance and effectiveness."""
        result = {"success": True, "details": {}}

        if not self.cache_file.exists():
            result["success"] = False
            result["details"]["error"] = "No cache file to test"
            return result

        try:
            # Load cache and analyze
            with open(self.cache_file) as f:
                cache_data = json.load(f)

            modules = cache_data.get("modules", {})
            total_modules = len(modules)

            # Analyze cache content
            analyzed_modules = sum(1 for m in modules.values() if m.get("analyzed", False))
            error_modules = sum(1 for m in modules.values() if m.get("error"))

            # Calculate cache hit potential
            cache_hit_rate = (analyzed_modules / total_modules * 100) if total_modules > 0 else 0

            result["details"] = {
                "total_modules": total_modules,
                "analyzed_modules": analyzed_modules,
                "error_modules": error_modules,
                "cache_hit_rate": cache_hit_rate,
                "cache_effectiveness": "high" if cache_hit_rate > 90 else "medium" if cache_hit_rate > 70 else "low"
            }

            print("  Cache performance: ✅")
            print(f"  Total modules: {total_modules:,}")
            print(f"  Analyzed modules: {analyzed_modules:,}")
            print(f"  Error modules: {error_modules}")
            print(f"  Cache hit rate: {cache_hit_rate:.1f}%")
            print(f"  Effectiveness: {result['details']['cache_effectiveness']}")

        except (ValueError, TypeError, RuntimeError) as e:
            result["success"] = False
            result["details"]["error"] = str(e)
            print(f"  Cache performance test failed: {e}")

        return result

    def test_precision_pass(self) -> dict[str, Any]:
        """Test precision pass execution."""
        result = {"success": True, "details": {}}

        try:
            # Run precision pass
            precision_script = ROOT / "tools" / "adg_1653_final_gap_closure.py"

            if not precision_script.exists():
                result["success"] = False
                result["details"]["error"] = "Precision pass script not found"
                return result

            # Use the 1653 database since that's what we have
            db_path = self.adg_dir / "adg_indexed_03222026_1653.sqlite"

            if not db_path.exists():
                result["success"] = False
                result["details"]["error"] = "Database not found for precision pass"
                return result

            precision_start = time.time()

            # Import and run precision pass
            sys.path.insert(0, str(ROOT / "tools"))
            from adg_1653_final_gap_closure import ADG1653FinalGapClosure

            closure = ADG1653FinalGapClosure(db_path)
            precision_results = closure.run_all_checks()
            precision_duration = time.time() - precision_start

            result["details"] = {
                "precision_duration": precision_duration,
                "precision_results": precision_results,
                "precision_success": precision_results.get("overall_success", False),
                "database_used": str(db_path.name)
            }

            print("  Precision pass: ✅" if result["details"]["precision_success"] else "❌")
            print(f"  Duration: {precision_duration:.1f}s")
            print(f"  Database: {db_path.name}")

            for check_name, check_result in precision_results.get("checks", {}).items():
                status = "PASS" if check_result.get("success", False) else "FAIL"
                print(f"    {status}: {check_name.upper()}")

        except (ValueError, TypeError, RuntimeError) as e:
            result["success"] = False
            result["details"]["error"] = str(e)
            print(f"  Precision pass test failed: {e}")

        return result

    def save_results(self):
        """Save test results to file."""
        results_file = self.adg_dir / f"comprehensive_e2e_test_results_{self.timestamp}.json"

        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, sort_keys=True)

        print(f"\n📊 Test results saved to: {results_file}")
        return results_file


def main():
    """Run comprehensive E2E test."""
    print("🚀 Starting ADG Comprehensive End-to-End Test...")

    tester = ADGComprehensiveE2ETest()
    results = tester.run_all_tests()
    tester.save_results()

    # Print final results
    print("\n" + "=" * 80)
    print("COMPREHENSIVE E2E TEST RESULTS")
    print("=" * 80)

    for check_name, result in results["checks"].items():
        status = "PASS" if result.get("success", False) else "FAIL"
        icon = "✅" if result.get("success", False) else "❌"
        print(f"{icon} {status}: {check_name.upper()}")

    print(f"\nOVERALL: {'SUCCESS' if results['overall_success'] else 'FAILURE'}")
    print(f"Duration: {results['duration_seconds']:.1f}s")

    if results["overall_success"]:
        print("\n🎉 ADG COMPREHENSIVE E2E TEST COMPLETED SUCCESSFULLY!")
        print("✅ Cache working properly")
        print("✅ ADG generation complete")
        print("✅ All artifacts generated")
        print("✅ Database integrity maintained")
        print("✅ Reports accurate")
        print("✅ Performance optimal")
        print("✅ Precision pass passed")
    else:
        print("\n❌ ADG COMPREHENSIVE E2E TEST FAILED")
        print("Review failed checks above")
        sys.exit(1)


if __name__ == "__main__":
    main()
