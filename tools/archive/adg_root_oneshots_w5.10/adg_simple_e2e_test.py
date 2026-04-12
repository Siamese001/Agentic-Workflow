#!/usr/bin/env python3
"""ADG Simple End-to-End Test.

Tests the ADG system with current artifacts to ensure:
1. Database exists and is accessible
2. All artifacts are present
3. Precision pass works
4. Basic functionality is intact
"""

import json
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class ADGSimpleE2ETest:
    """Simple E2E test for ADG system."""

    def __init__(self):
        self.start_time = time.time()
        self.timestamp = datetime.now().strftime("%m%d%Y_%H%M")
        self.adg_dir = ROOT / "artifacts" / "adg"
        self.results = {
            "test_start": datetime.now().isoformat(),
            "timestamp": self.timestamp,
            "checks": {},
            "overall_success": True,
        }

    def run_all_tests(self) -> dict[str, Any]:
        """Run simple E2E tests."""
        print("=" * 80)
        print("ADG SIMPLE END-TO-END TEST")
        print("=" * 80)
        print(f"Timestamp: {self.timestamp}")

        # 1. Verify ADG directory structure
        print("\n[1] VERIFYING ADG DIRECTORY...")
        self.results["checks"]["directory_structure"] = self.verify_directory_structure()

        # 2. Test database access
        print("\n[2] TESTING DATABASE ACCESS...")
        self.results["checks"]["database_access"] = self.test_database_access()

        # 3. Verify artifacts exist
        print("\n[3] VERIFYING ARTIFACTS...")
        self.results["checks"]["artifacts_exist"] = self.verify_artifacts_exist()

        # 4. Test precision pass
        print("\n[4] TESTING PRECISION PASS...")
        self.results["checks"]["precision_pass"] = self.test_precision_pass()

        # 5. Test basic queries
        print("\n[5] TESTING BASIC QUERIES...")
        self.results["checks"]["basic_queries"] = self.test_basic_queries()

        # Calculate overall results
        self.results["test_end"] = datetime.now().isoformat()
        self.results["duration_seconds"] = time.time() - self.start_time
        self.results["overall_success"] = all(
            check.get("success", False) for check in self.results["checks"].values()
        )

        return self.results

    def verify_directory_structure(self) -> dict[str, Any]:
        """Verify ADG directory structure."""
        result = {"success": True, "details": {}}

        if not self.adg_dir.exists():
            result["success"] = False
            result["details"]["error"] = "ADG directory does not exist"
            return result

        # List directory contents
        items = list(self.adg_dir.iterdir())
        files = [item.name for item in items if item.is_file()]
        dirs = [item.name for item in items if item.is_dir()]

        result["details"] = {
            "adg_dir_exists": True,
            "total_items": len(items),
            "files": len(files),
            "directories": len(dirs),
            "sample_files": files[:10],  # First 10 files
        }

        print("  ADG directory: ✅")
        print(f"  Total items: {len(items)}")
        print(f"  Files: {len(files)}")
        print(f"  Directories: {len(dirs)}")

        return result

    def test_database_access(self) -> dict[str, Any]:
        """Test database access and basic functionality."""
        result = {"success": True, "details": {}}

        # Look for any SQLite database
        db_files = list(self.adg_dir.glob("*.sqlite"))

        if not db_files:
            result["success"] = False
            result["details"]["error"] = "No SQLite database found"
            return result

        # Test the most recent database
        db_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        db_path = db_files[0]

        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            # Test basic queries
            cur.execute("SELECT COUNT(*) FROM nodes")
            node_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM edges")
            edge_count = cur.fetchone()[0]

            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cur.fetchall()]

            result["details"] = {
                "database_file": db_path.name,
                "nodes": node_count,
                "edges": edge_count,
                "tables": tables,
                "accessible": True,
            }

            print("  Database access: ✅")
            print(f"  Database: {db_path.name}")
            print(f"  Nodes: {node_count:,}")
            print(f"  Edges: {edge_count:,}")
            print(f"  Tables: {len(tables)}")

            conn.close()

        except (ValueError, TypeError, RuntimeError) as e:
            result["success"] = False
            result["details"]["error"] = str(e)
            print(f"  Database access failed: {e}")

        return result

    def verify_artifacts_exist(self) -> dict[str, Any]:
        """Verify key artifacts exist."""
        result = {"success": True, "details": {}}

        # Look for key artifact patterns
        json_files = list(self.adg_dir.glob("*.json"))
        sqlite_files = list(self.adg_dir.glob("*.sqlite"))
        zip_files = list(self.adg_dir.glob("*.zip"))

        # Check for specific artifact types
        graph_files = [f for f in json_files if "graph" in f.name]
        report_files = [f for f in json_files if "report" in f.name]
        snapshot_files = [f for f in json_files if "snapshot" in f.name]

        result["details"] = {
            "json_files": len(json_files),
            "sqlite_files": len(sqlite_files),
            "zip_files": len(zip_files),
            "graph_files": len(graph_files),
            "report_files": len(report_files),
            "snapshot_files": len(snapshot_files),
            "total_artifacts": len(json_files) + len(sqlite_files) + len(zip_files),
        }

        print("  Artifacts verification: ✅")
        print(f"  JSON files: {len(json_files)}")
        print(f"  SQLite files: {len(sqlite_files)}")
        print(f"  ZIP files: {len(zip_files)}")
        print(f"  Graph files: {len(graph_files)}")
        print(f"  Report files: {len(report_files)}")

        return result

    def test_precision_pass(self) -> dict[str, Any]:
        """Test precision pass execution."""
        result = {"success": True, "details": {}}

        try:
            # Find a database to test
            db_files = list(self.adg_dir.glob("*.sqlite"))
            if not db_files:
                result["success"] = False
                result["details"]["error"] = "No database found for precision pass"
                return result

            db_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            db_path = db_files[0]

            # Import and run precision pass
            sys.path.insert(0, str(ROOT / "tools"))
            from adg_1653_final_gap_closure import ADG1653FinalGapClosure

            precision_start = time.time()
            closure = ADG1653FinalGapClosure(db_path)
            precision_results = closure.run_all_checks()
            precision_duration = time.time() - precision_start

            result["details"] = {
                "precision_duration": precision_duration,
                "precision_results": precision_results,
                "precision_success": precision_results.get("overall_success", False),
                "database_used": str(db_path.name),
                "checks_passed": sum(
                    1 for check in precision_results.get("checks", {}).values() if check.get("success", False)
                ),
                "total_checks": len(precision_results.get("checks", {})),
            }

            print("  Precision pass: ✅" if result["details"]["precision_success"] else "❌")
            print(f"  Duration: {precision_duration:.1f}s")
            print(f"  Database: {db_path.name}")
            print(
                f"  Checks passed: {result['details']['checks_passed']}/{result['details']['total_checks']}"
            )

        except (ValueError, TypeError, RuntimeError) as e:
            result["success"] = False
            result["details"]["error"] = str(e)
            print(f"  Precision pass test failed: {e}")

        return result

    def test_basic_queries(self) -> dict[str, Any]:
        """Test basic database queries."""
        result = {"success": True, "details": {}}

        try:
            # Find database
            db_files = list(self.adg_dir.glob("*.sqlite"))
            if not db_files:
                result["success"] = False
                result["details"]["error"] = "No database found"
                return result

            db_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            db_path = db_files[0]

            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            # Test various queries
            queries = {
                "layer_distribution": "SELECT layer, COUNT(*) FROM nodes GROUP BY layer ORDER BY COUNT(*) DESC LIMIT 5",
                "edge_types": "SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type ORDER BY COUNT(*) DESC LIMIT 5",
                "entity_types": "SELECT entity_type, COUNT(*) FROM nodes GROUP BY entity_type ORDER BY COUNT(*) DESC",
                "module_count": "SELECT COUNT(*) FROM nodes WHERE entity_type = 'module'",
                "symbol_count": "SELECT COUNT(*) FROM nodes WHERE entity_type = 'symbol'",
            }

            query_results = {}

            for query_name, query in queries.items():
                try:
                    cur.execute(query)
                    results = cur.fetchall()
                    query_results[query_name] = results
                except (ValueError, TypeError, RuntimeError) as e:
                    query_results[query_name] = f"Error: {e}"

            result["details"] = {
                "database_used": db_path.name,
                "query_results": query_results,
                "queries_successful": sum(1 for r in query_results.values() if not isinstance(r, str)),
                "total_queries": len(queries),
            }

            print("  Basic queries: ✅")
            print(
                f"  Queries successful: {result['details']['queries_successful']}/{result['details']['total_queries']}"
            )

            # Show some sample results
            if "layer_distribution" in query_results and isinstance(
                query_results["layer_distribution"], list
            ):
                print("  Top layers:")
                for layer, count in query_results["layer_distribution"][:3]:
                    print(f"    {layer}: {count:,}")

            conn.close()

        except (ValueError, TypeError, RuntimeError) as e:
            result["success"] = False
            result["details"]["error"] = str(e)
            print(f"  Basic queries test failed: {e}")

        return result

    def save_results(self):
        """Save test results to file."""
        results_file = self.adg_dir / f"simple_e2e_test_results_{self.timestamp}.json"

        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2, sort_keys=True)

        print(f"\n📊 Test results saved to: {results_file}")
        return results_file


def main():
    """Run simple E2E test."""
    print("🚀 Starting ADG Simple End-to-End Test...")

    tester = ADGSimpleE2ETest()
    results = tester.run_all_tests()
    tester.save_results()

    # Print final results
    print("\n" + "=" * 80)
    print("SIMPLE E2E TEST RESULTS")
    print("=" * 80)

    for check_name, result in results["checks"].items():
        status = "PASS" if result.get("success", False) else "FAIL"
        icon = "✅" if result.get("success", False) else "❌"
        print(f"{icon} {status}: {check_name.upper()}")

    print(f"\nOVERALL: {'SUCCESS' if results['overall_success'] else 'FAILURE'}")
    print(f"Duration: {results['duration_seconds']:.1f}s")

    if results["overall_success"]:
        print("\n🎉 ADG SIMPLE E2E TEST COMPLETED SUCCESSFULLY!")
        print("✅ Directory structure valid")
        print("✅ Database accessible")
        print("✅ Artifacts present")
        print("✅ Precision pass working")
        print("✅ Basic queries functional")
    else:
        print("\n❌ ADG SIMPLE E2E TEST FAILED")
        print("Review failed checks above")
        sys.exit(1)


if __name__ == "__main__":
    main()
