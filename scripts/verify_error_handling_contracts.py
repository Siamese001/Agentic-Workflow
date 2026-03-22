#!/usr/bin/env python3
"""
ADG Error Handling and Retry Enforcement

Enforces deterministic error handling and retry patterns:
- no bare except in first-party production paths
- no broad except Exception without structured handling contract
- no silent return False/None/empty-list patterns for critical execution paths
- retries must declare: max_attempts, backoff policy, terminal failure behavior, trace linkage, reason classification

ADD EDGE TYPES:
- handles_exception_structured
- rethrows_with_context
- retries_with_backoff
- retries_with_bound
- swallows_exception
- retries_without_backoff
- retries_without_bound
- retries_without_trace

ADD VIOLATION TYPES:
- exception_swallow
- bare_except
- broad_exception_without_structured_handling
- retry_without_backoff
- retry_without_bound
- retry_without_trace_link
"""

from __future__ import annotations

import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class ErrorHandlingEnforcementError(Exception):
    """Raised when error handling enforcement verification fails."""
    pass

class ADGErrorHandlingEnforcementVerifier:
    """Verifies ADG error handling and retry enforcement."""

    # Error handling edge types to detect
    ERROR_HANDLING_EDGES = {
        "handles_exception_structured",
        "rethrows_with_context",
        "retries_with_backoff",
        "retries_with_bound",
        "swallows_exception",
        "retries_without_backoff",
        "retries_without_bound",
        "retries_without_trace"
    }

    # Violation types to detect
    VIOLATION_TYPES = {
        "exception_swallow",
        "bare_except",
        "broad_exception_without_structured_handling",
        "retry_without_backoff",
        "retry_without_bound",
        "retry_without_trace_link"
    }

    # Critical execution paths that require proper error handling
    CRITICAL_PATHS = {
        "L0", "L1", "L2", "L3", "L4", "L5"
    }

    def __init__(self, adg_dir: Path):
        self.adg_dir = Path(adg_dir)
        self.sqlite_path = self._find_sqlite_database()
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def _find_sqlite_database(self) -> Path:
        """Find the latest SQLite database."""
        sqlite_files = list(self.adg_dir.glob("adg_indexed_*.sqlite"))
        if not sqlite_files:
            raise ErrorHandlingEnforcementError("No SQLite database found")

        return max(sqlite_files, key=lambda p: p.stat().st_mtime)

    def _verify_error_handling_edge_detection(self) -> Dict[str, Any]:
        """Verify error handling edges are properly detected."""
        print("🔍 Verifying error handling edge detection...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Check for error handling edge types
                edge_counts = {}
                total_error_handling_edges = 0

                for edge_type in self.ERROR_HANDLING_EDGES:
                    cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (edge_type,))
                    count = cursor.fetchone()[0]
                    edge_counts[edge_type] = count
                    total_error_handling_edges += count

                print(f"   📊 Error handling edges found:")
                for edge_type, count in edge_counts.items():
                    print(f"      {edge_type}: {count}")

                print(f"   📊 Total error handling edges: {total_error_handling_edges}")

                # Check for violation edges
                violation_counts = {}
                total_violations = 0

                for violation_type in self.VIOLATION_TYPES:
                    cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (violation_type,))
                    count = cursor.fetchone()[0]
                    violation_counts[violation_type] = count
                    total_violations += count

                print(f"   📊 Error handling violations:")
                for violation_type, count in violation_counts.items():
                    print(f"      {violation_type}: {count}")

                print(f"   📊 Total violations: {total_violations}")

                # Calculate violation rate
                cursor.execute("SELECT COUNT(*) FROM edges")
                total_edges = cursor.fetchone()[0]

                violation_rate = (total_violations / max(1, total_edges)) * 100
                error_handling_rate = (total_error_handling_edges / max(1, total_edges)) * 100

                return {
                    "error_handling_edges": edge_counts,
                    "violation_edges": violation_counts,
                    "total_error_handling_edges": total_error_handling_edges,
                    "total_violations": total_violations,
                    "total_edges": total_edges,
                    "violation_rate": violation_rate,
                    "error_handling_rate": error_handling_rate
                }

        except Exception as e:
            raise ErrorHandlingEnforcementError(f"Error handling edge detection failed: {e}")

    def _verify_critical_path_error_handling(self) -> Dict[str, Any]:
        """Verify critical execution paths have proper error handling."""
        print("🛡️  Verifying critical path error handling...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Get first-party modules in critical layers
                layer_placeholders = ','.join(['?' for _ in self.CRITICAL_PATHS])
                cursor.execute(f"""
                    SELECT id, adg_name, layer FROM nodes
                    WHERE entity_type = 'module'
                    AND layer IN ({layer_placeholders})
                    AND identity_kind NOT IN ('external_module', 'external_provider')
                """, list(self.CRITICAL_PATHS))

                critical_modules = cursor.fetchall()
                print(f"   📊 Found {len(critical_modules)} critical path modules")

                # Analyze error handling in critical modules
                modules_with_violations = []
                modules_with_structured_handling = []

                for module_id, module_name, layer in critical_modules:
                    # Check for violations in this module
                    cursor.execute("""
                        SELECT relation_type, COUNT(*) FROM edges
                        WHERE src_id = ? AND relation_type IN ({})
                        GROUP BY relation_type
                    """.format(','.join(['?' for _ in self.VIOLATION_TYPES])),
                    [module_id] + list(self.VIOLATION_TYPES))

                    violations = dict(cursor.fetchall())

                    # Check for structured error handling
                    cursor.execute("""
                        SELECT relation_type, COUNT(*) FROM edges
                        WHERE src_id = ? AND relation_type IN ({})
                        GROUP BY relation_type
                    """.format(','.join(['?' for _ in ["handles_exception_structured", "rethrows_with_context"]])),
                    [module_id, "handles_exception_structured", "rethrows_with_context"])

                    structured_handling = dict(cursor.fetchall())

                    total_violations = sum(violations.values())
                    total_structured = sum(structured_handling.values())

                    if total_violations > 0:
                        modules_with_violations.append({
                            "module_name": module_name,
                            "layer": layer,
                            "violations": violations,
                            "total_violations": total_violations
                        })

                    if total_structured > 0:
                        modules_with_structured_handling.append({
                            "module_name": module_name,
                            "layer": layer,
                            "structured_handling": structured_handling,
                            "total_structured": total_structured
                        })

                print(f"   📊 Critical modules with violations: {len(modules_with_violations)}")
                print(f"   📊 Critical modules with structured handling: {len(modules_with_structured_handling)}")

                # Layer-specific analysis
                violation_by_layer = defaultdict(int)
                structured_by_layer = defaultdict(int)

                for module in modules_with_violations:
                    violation_by_layer[module["layer"]] += 1

                for module in modules_with_structured_handling:
                    structured_by_layer[module["layer"]] += 1

                print(f"   📊 Violations by layer:")
                for layer in sorted(self.CRITICAL_PATHS):
                    violations = violation_by_layer.get(layer, 0)
                    structured = structured_by_layer.get(layer, 0)
                    print(f"      {layer}: {violations} violations, {structured} structured")

                return {
                    "total_critical_modules": len(critical_modules),
                    "modules_with_violations": len(modules_with_violations),
                    "modules_with_structured_handling": len(modules_with_structured_handling),
                    "violation_by_layer": dict(violation_by_layer),
                    "structured_by_layer": dict(structured_by_layer),
                    "violation_details": modules_with_violations[:10],  # First 10 for details
                    "structured_details": modules_with_structured_handling[:10]
                }

        except Exception as e:
            raise ErrorHandlingEnforcementError(f"Critical path error handling verification failed: {e}")

    def _verify_retry_pattern_compliance(self) -> Dict[str, Any]:
        """Verify retry patterns follow required structure."""
        print("🔄 Verifying retry pattern compliance...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Get all retry-related edges
                retry_edges = [
                    "retries_with_backoff", "retries_with_bound",
                    "retries_without_backoff", "retries_without_bound",
                    "retries_without_trace"
                ]

                retry_analysis = {}
                total_retry_edges = 0

                for retry_type in retry_edges:
                    cursor.execute("""
                        SELECT e.src_id, n.adg_name, n.layer, e.symbol, e.source_file, e.line_no
                        FROM edges e
                        JOIN nodes n ON e.src_id = n.id
                        WHERE e.relation_type = ?
                        AND n.identity_kind NOT IN ('external_module', 'external_provider')
                    """, (retry_type,))

                    retry_instances = []
                    for row in cursor.fetchall():
                        retry_instances.append({
                            "module_id": row[0],
                            "module_name": row[1],
                            "layer": row[2],
                            "symbol": row[3],
                            "source_file": row[4],
                            "line_no": row[5]
                        })

                    retry_analysis[retry_type] = retry_instances
                    total_retry_edges += len(retry_instances)

                print(f"   📊 Retry pattern analysis:")
                for retry_type, instances in retry_analysis.items():
                    print(f"      {retry_type}: {len(instances)}")

                # Analyze retry compliance
                compliant_retries = 0
                non_compliant_retries = 0

                # Compliant retries have backoff and bound
                compliant_instances = retry_analysis.get("retries_with_backoff", [])
                compliant_instances.extend(retry_analysis.get("retries_with_bound", []))
                compliant_retries = len(compliant_instances)

                # Non-compliant retries
                non_compliant_instances = retry_analysis.get("retries_without_backoff", [])
                non_compliant_instances.extend(retry_analysis.get("retries_without_bound", []))
                non_compliant_instances.extend(retry_analysis.get("retries_without_trace", []))
                non_compliant_retries = len(non_compliant_instances)

                compliance_rate = (compliant_retries / max(1, total_retry_edges)) * 100

                print(f"   📊 Retry compliance: {compliant_retries}/{total_retry_edges} ({compliance_rate:.1f}%)")

                # Check for retry patterns in critical layers
                critical_retry_violations = []
                for retry_type in ["retries_without_backoff", "retries_without_bound", "retries_without_trace"]:
                    instances = retry_analysis.get(retry_type, [])
                    for instance in instances:
                        if instance["layer"] in self.CRITICAL_PATHS:
                            critical_retry_violations.append({
                                "module": instance["module_name"],
                                "layer": instance["layer"],
                                "violation_type": retry_type,
                                "symbol": instance["symbol"]
                            })

                print(f"   📊 Critical layer retry violations: {len(critical_retry_violations)}")

                return {
                    "retry_analysis": retry_analysis,
                    "total_retry_edges": total_retry_edges,
                    "compliant_retries": compliant_retries,
                    "non_compliant_retries": non_compliant_retries,
                    "compliance_rate": compliance_rate,
                    "critical_retry_violations": len(critical_retry_violations),
                    "critical_violation_details": critical_retry_violations[:10]
                }

        except Exception as e:
            raise ErrorHandlingEnforcementError(f"Retry pattern compliance verification failed: {e}")

    def _verify_exception_hygiene_by_layer(self) -> Dict[str, Any]:
        """Verify exception hygiene by architectural layer."""
        print("🧼 Verifying exception hygiene by layer...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Analyze exception handling by layer
                layer_analysis = {}

                for layer in list(self.CRITICAL_PATHS) + ["L_RUNTIME", "L_TEST", "L_TOOLS"]:
                    # Get modules in this layer
                    cursor.execute("""
                        SELECT id, adg_name FROM nodes
                        WHERE layer = ? AND entity_type = 'module'
                        AND identity_kind NOT IN ('external_module', 'external_provider')
                    """, (layer,))

                    modules = cursor.fetchall()
                    if not modules:
                        continue

                    # Analyze each module
                    layer_stats = {
                        "total_modules": len(modules),
                        "bare_except_count": 0,
                        "broad_exception_count": 0,
                        "structured_handling_count": 0,
                        "exception_swallow_count": 0,
                        "retry_violations_count": 0
                    }

                    for module_id, module_name in modules:
                        # Check for bare except
                        cursor.execute("""
                            SELECT COUNT(*) FROM edges
                            WHERE src_id = ? AND relation_type = 'bare_except'
                        """, (module_id,))
                        bare_except = cursor.fetchone()[0]
                        layer_stats["bare_except_count"] += bare_except

                        # Check for broad exception
                        cursor.execute("""
                            SELECT COUNT(*) FROM edges
                            WHERE src_id = ? AND relation_type = 'broad_exception_without_structured_handling'
                        """, (module_id,))
                        broad_exception = cursor.fetchone()[0]
                        layer_stats["broad_exception_count"] += broad_exception

                        # Check for structured handling
                        cursor.execute("""
                            SELECT COUNT(*) FROM edges
                            WHERE src_id = ? AND relation_type = 'handles_exception_structured'
                        """, (module_id,))
                        structured = cursor.fetchone()[0]
                        layer_stats["structured_handling_count"] += structured

                        # Check for exception swallowing
                        cursor.execute("""
                            SELECT COUNT(*) FROM edges
                            WHERE src_id = ? AND relation_type = 'exception_swallow'
                        """, (module_id,))
                        swallow = cursor.fetchone()[0]
                        layer_stats["exception_swallow_count"] += swallow

                        # Check for retry violations
                        retry_violations = ["retry_without_backoff", "retry_without_bound", "retry_without_trace"]
                        placeholders = ','.join(['?' for _ in retry_violations])
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM edges
                            WHERE src_id = ? AND relation_type IN ({placeholders})
                        """, [module_id] + retry_violations)
                        retry_violations_count = cursor.fetchone()[0]
                        layer_stats["retry_violations_count"] += retry_violations_count

                    # Calculate hygiene metrics
                    total_issues = (layer_stats["bare_except_count"] +
                                 layer_stats["broad_exception_count"] +
                                 layer_stats["exception_swallow_count"] +
                                 layer_stats["retry_violations_count"])

                    layer_stats["total_issues"] = total_issues
                    layer_stats["issues_per_module"] = total_issues / max(1, layer_stats["total_modules"])
                    layer_stats["hygiene_score"] = max(0, 100 - (layer_stats["issues_per_module"] * 20))  # Arbitrary scaling

                    layer_analysis[layer] = layer_stats

                print(f"   📊 Exception hygiene by layer:")
                print(f"      Layer | Modules | Issues | Score | Bare | Broad | Swallow | Retry")
                print(f"      -------|---------|--------|-------|------|-------|---------|------")

                for layer in sorted(layer_analysis.keys()):
                    stats = layer_analysis[layer]
                    print(f"      {layer:6} | {stats['total_modules']:7} | {stats['total_issues']:6} | {stats['hygiene_score']:5.1f} | "
                          f"{stats['bare_except_count']:4} | {stats['broad_exception_count']:6} | "
                          f"{stats['exception_swallow_count']:7} | {stats['retry_violations_count']:5}")

                # Find worst layers
                worst_layers = sorted(layer_analysis.items(), key=lambda x: x[1]["hygiene_score"])[:3]

                return {
                    "layer_analysis": layer_analysis,
                    "worst_layers": worst_layers,
                    "overall_hygiene_score": sum(stats["hygiene_score"] for stats in layer_analysis.values()) / max(1, len(layer_analysis))
                }

        except Exception as e:
            raise ErrorHandlingEnforcementError(f"Exception hygiene verification failed: {e}")

    def verify(self) -> Dict[str, Any]:
        """Run complete error handling enforcement verification."""
        print("🔍 Starting ADG Error Handling Enforcement Verification...")
        print(f"📁 ADG Directory: {self.adg_dir}")
        print(f"🗄️  SQLite Database: {self.sqlite_path.name}")

        # Verify error handling edge detection
        edge_detection = self._verify_error_handling_edge_detection()

        # Verify critical path error handling
        critical_paths = self._verify_critical_path_error_handling()

        # Verify retry pattern compliance
        retry_compliance = self._verify_retry_pattern_compliance()

        # Verify exception hygiene by layer
        exception_hygiene = self._verify_exception_hygiene_by_layer()

        # Determine overall status
        critical_issues = (
            critical_paths.get("modules_with_violations", 0) > 10 or
            retry_compliance.get("critical_retry_violations", 0) > 5 or
            exception_hygiene.get("overall_hygiene_score", 100) < 70
        )

        # Prepare result
        result = {
            "status": "FAIL" if critical_issues else "PASS",
            "edge_detection": edge_detection,
            "critical_paths": critical_paths,
            "retry_compliance": retry_compliance,
            "exception_hygiene": exception_hygiene,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {
                "total_violations": edge_detection.get("total_violations", 0),
                "violation_rate": edge_detection.get("violation_rate", 0),
                "critical_modules_with_violations": critical_paths.get("modules_with_violations", 0),
                "retry_compliance_rate": retry_compliance.get("compliance_rate", 0),
                "critical_retry_violations": retry_compliance.get("critical_retry_violations", 0),
                "overall_hygiene_score": exception_hygiene.get("overall_hygiene_score", 100)
            }
        }

        # Print results
        if self.errors:
            print("\n❌ ERROR HANDLING ENFORCEMENT VERIFICATION FAILED")
            for error in self.errors:
                print(f"   • {error}")

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")

        if critical_issues:
            print("\n❌ ERROR HANDLING ISSUES FOUND")
            print(f"   • Total violations: {result['summary']['total_violations']}")
            print(f"   • Critical modules with violations: {result['summary']['critical_modules_with_violations']}")
            print(f"   • Retry compliance: {result['summary']['retry_compliance_rate']:.1f}%")
            print(f"   • Overall hygiene score: {result['summary']['overall_hygiene_score']:.1f}%")
        else:
            print("\n✅ ERROR HANDLING ENFORCEMENT VERIFICATION PASSED")
            print(f"📊 Violation rate: {result['summary']['violation_rate']:.2f}%")
            print(f"📊 Retry compliance: {result['summary']['retry_compliance_rate']:.1f}%")
            print(f"📊 Hygiene score: {result['summary']['overall_hygiene_score']:.1f}%")

        return result

def main():
    """CLI entry point."""
    import argparse
    from collections import defaultdict

    parser = argparse.ArgumentParser(description="Verify ADG error handling enforcement")
    parser.add_argument(
        "--adg-dir",
        type=Path,
        default=Path("artifacts/adg"),
        help="Path to ADG artifacts directory"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to save verification report"
    )

    args = parser.parse_args()

    try:
        verifier = ADGErrorHandlingEnforcementVerifier(args.adg_dir)
        result = verifier.verify()

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"📄 Report saved to: {args.output}")

        return 0 if result["status"] == "PASS" else 1

    except ErrorHandlingEnforcementError as e:
        print(f"❌ Verification failed: {e}")
        return 1
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
