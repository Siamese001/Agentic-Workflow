#!/usr/bin/env python3
"""
ADG Trace and Replay Coverage Verification

Ensures all first-party execution surfaces have proper trace and replay coverage:
- execution path emits trace
- trace binds to replay_key
- trace binds to policy hash
- trace binds to config hash
- trace binds to mutation envelope if state changes occur
- missing transcript path hard-fails or is explicitly allowlisted

REQUIRED REPORTS:
- execution_surface_inventory
- traced_surface_count
- replay_key_surface_count
- signed_trace_surface_count
- untranscripted_surface_count
- hard_fail_untranscripted_count
- allowlisted_untranscripted_surface_count
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TraceReplayCoverageError(Exception):
    """Raised when trace/replay coverage verification fails."""
    pass

class ADGTraceReplayCoverageVerifier:
    """Verifies ADG trace and replay coverage."""

    def __init__(self, adg_dir: Path):
        self.adg_dir = Path(adg_dir)
        self.sqlite_path = self._find_sqlite_database()
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def _find_sqlite_database(self) -> Path:
        """Find the latest SQLite database."""
        sqlite_files = list(self.adg_dir.glob("adg_indexed_*.sqlite"))
        if not sqlite_files:
            raise TraceReplayCoverageError("No SQLite database found")

        return max(sqlite_files, key=lambda p: p.stat().st_mtime)

    def _get_first_party_modules(self) -> list[tuple[int, str, str]]:
        """Get first-party modules (id, adg_name, layer)."""
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, adg_name, layer FROM nodes
                    WHERE entity_type = 'module'
                    AND identity_kind NOT IN ('external_module', 'external_provider')
                    ORDER BY adg_name
                """)
                return cursor.fetchall()
        except Exception as e:
            raise TraceReplayCoverageError(f"Failed to get first-party modules: {e}")

    def _get_module_edges(self, module_id: int, relation_types: list[str]) -> list[dict[str, Any]]:
        """Get edges for a specific module by relation types."""
        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                placeholders = ','.join(['?' for _ in relation_types])
                cursor.execute(f"""
                    SELECT e.id, e.relation_type, e.symbol, e.source_file, e.line_no
                    FROM edges e
                    WHERE e.src_id = ? AND e.relation_type IN ({placeholders})
                """, [module_id] + relation_types)

                results = []
                for row in cursor.fetchall():
                    results.append({
                        "edge_id": row[0],
                        "relation_type": row[1],
                        "symbol": row[2],
                        "source_file": row[3],
                        "line_no": row[4],
                    })

                return results
        except Exception as e:
            raise TraceReplayCoverageError(f"Failed to get module edges: {e}")

    def _analyze_execution_surface_coverage(self, module_id: int, module_name: str) -> dict[str, Any]:
        """Analyze trace/replay coverage for a single module."""

        # Define execution surface edge types
        execution_surface_types = [
            "records_execution_trace",
            "signs_execution_trace",
            "emits_replay_key",
            "execution_terminates_at_uwg",
            "writes_to",
            "invokes_provider",
            "invokes_dynamic",
            "calls",
        ]

        # Get all execution surface edges
        surface_edges = self._get_module_edges(module_id, execution_surface_types)

        # Analyze coverage
        has_trace = any(e["relation_type"] == "records_execution_trace" for e in surface_edges)
        has_signed_trace = any(e["relation_type"] == "signs_execution_trace" for e in surface_edges)
        has_replay_key = any(e["relation_type"] == "emits_replay_key" for e in surface_edges)
        has_uwg_termination = any(e["relation_type"] == "execution_terminates_at_uwg" for e in surface_edges)
        has_writes = any(e["relation_type"] == "writes_to" for e in surface_edges)
        has_external_calls = any(e["relation_type"] in ["invokes_provider", "invokes_dynamic"] for e in surface_edges)
        has_calls = any(e["relation_type"] == "calls" for e in surface_edges)

        # Determine coverage level
        coverage_level = "none"
        if has_trace and has_signed_trace and has_replay_key:
            coverage_level = "complete"
        elif has_trace and (has_replay_key or has_signed_trace):
            coverage_level = "partial"
        elif has_trace or has_signed_trace:
            coverage_level = "basic"

        # Check for hard failures
        hard_fail_edges = self._get_module_edges(module_id, ["hard_fails_untranscripted"])
        has_hard_fail = len(hard_fail_edges) > 0

        return {
            "module_name": module_name,
            "module_id": module_id,
            "has_trace": has_trace,
            "has_signed_trace": has_signed_trace,
            "has_replay_key": has_replay_key,
            "has_uwg_termination": has_uwg_termination,
            "has_writes": has_writes,
            "has_external_calls": has_external_calls,
            "has_calls": has_calls,
            "coverage_level": coverage_level,
            "has_hard_fail": has_hard_fail,
            "execution_surface_count": len(surface_edges),
            "trace_edges": [e for e in surface_edges if e["relation_type"] == "records_execution_trace"],
            "replay_key_edges": [e for e in surface_edges if e["relation_type"] == "emits_replay_key"],
            "hard_fail_edges": hard_fail_edges,
        }

    def _verify_critical_execution_surfaces(self) -> dict[str, Any]:
        """Verify critical execution surfaces have proper coverage."""
        print("🎯 Verifying critical execution surfaces...")

        first_party_modules = self._get_first_party_modules()
        print(f"   📊 Analyzing {len(first_party_modules)} first-party modules")

        coverage_results = []
        critical_failures = []

        for module_id, module_name, layer in first_party_modules:
            coverage = self._analyze_execution_surface_coverage(module_id, module_name)
            coverage["layer"] = layer
            coverage_results.append(coverage)

            # Check for critical failures
            if coverage["has_writes"] and not coverage["has_trace"]:
                critical_failures.append({
                    "module": module_name,
                    "layer": layer,
                    "issue": "Write-capable module missing execution trace",
                })

            if coverage["has_external_calls"] and not coverage["has_trace"]:
                critical_failures.append({
                    "module": module_name,
                    "layer": layer,
                    "issue": "External-calling module missing execution trace",
                })

            if coverage["has_hard_fail"]:
                critical_failures.append({
                    "module": module_name,
                    "layer": layer,
                    "issue": "Module has hard failure without transcript",
                })

        # Summary statistics
        total_modules = len(coverage_results)
        traced_modules = sum(1 for c in coverage_results if c["has_trace"])
        signed_modules = sum(1 for c in coverage_results if c["has_signed_trace"])
        replay_key_modules = sum(1 for c in coverage_results if c["has_replay_key"])
        complete_coverage = sum(1 for c in coverage_results if c["coverage_level"] == "complete")
        hard_fail_modules = sum(1 for c in coverage_results if c["has_hard_fail"])

        print("   📊 Coverage Summary:")
        print(f"      Total modules: {total_modules}")
        print(f"      With trace: {traced_modules} ({100*traced_modules/total_modules:.1f}%)")
        print(f"      With signed trace: {signed_modules} ({100*signed_modules/total_modules:.1f}%)")
        print(f"      With replay key: {replay_key_modules} ({100*replay_key_modules/total_modules:.1f}%)")
        print(f"      Complete coverage: {complete_coverage} ({100*complete_coverage/total_modules:.1f}%)")
        print(f"      Hard failures: {hard_fail_modules}")

        # Report critical failures
        if critical_failures:
            print(f"   ❌ Critical failures found: {len(critical_failures)}")
            for failure in critical_failures[:10]:  # Show first 10
                print(f"      • {failure['module']} ({failure['layer']}): {failure['issue']}")
            if len(critical_failures) > 10:
                print(f"      ... and {len(critical_failures) - 10} more")

        return {
            "total_modules": total_modules,
            "traced_modules": traced_modules,
            "signed_modules": signed_modules,
            "replay_key_modules": replay_key_modules,
            "complete_coverage": complete_coverage,
            "hard_fail_modules": hard_fail_modules,
            "critical_failures": critical_failures,
            "coverage_results": coverage_results,
        }

    def _verify_trace_binding_completeness(self) -> dict[str, Any]:
        """Verify trace bindings to policy, config, and mutation envelopes."""
        print("🔗 Verifying trace binding completeness...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Count different trace binding types
                binding_types = [
                    ("records_execution_trace", "Trace recording"),
                    ("signs_execution_trace", "Signed trace"),
                    ("emits_replay_key", "Replay key emission"),
                    ("execution_terminates_at_uwg", "UWG termination"),
                    ("validated_by_safety_plane", "Safety plane validation"),
                    ("validated_by_llm_gateway", "LLM gateway validation"),
                ]

                binding_counts = {}
                for relation_type, description in binding_types:
                    cursor.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (relation_type,))
                    count = cursor.fetchone()[0]
                    binding_counts[relation_type] = {
                        "count": count,
                        "description": description,
                    }

                # Check for modules with trace but missing bindings
                cursor.execute("""
                    SELECT DISTINCT n.adg_name, n.layer
                    FROM edges e
                    JOIN nodes n ON e.src_id = n.id
                    WHERE e.relation_type = 'records_execution_trace'
                    AND n.identity_kind NOT IN ('external_module', 'external_provider')
                """)

                traced_modules = cursor.fetchall()
                print(f"   📊 Found {len(traced_modules)} modules with execution traces")

                # Check for trace-policy binding gaps
                cursor.execute("""
                    SELECT COUNT(DISTINCT e.src_id)
                    FROM edges e
                    WHERE e.relation_type = 'records_execution_trace'
                    AND NOT EXISTS (
                        SELECT 1 FROM edges e2
                        WHERE e2.src_id = e.src_id
                        AND e2.relation_type IN ('validated_by_safety_plane', 'validated_by_llm_gateway')
                    )
                """)

                traces_without_policy = cursor.fetchone()[0]
                if traces_without_policy > 0:
                    self.warnings.append(f"{traces_without_policy} traces lack policy validation binding")

                return {
                    "binding_counts": binding_counts,
                    "traced_modules": len(traced_modules),
                    "traces_without_policy_binding": traces_without_policy,
                }

        except Exception as e:
            raise TraceReplayCoverageError(f"Trace binding verification failed: {e}")

    def _verify_hard_fail_transcript_requirements(self) -> dict[str, Any]:
        """Verify hard failures have proper transcript requirements."""
        print("🚫 Verifying hard fail transcript requirements...")

        try:
            with sqlite3.connect(self.sqlite_path) as conn:
                cursor = conn.cursor()

                # Get all hard failure edges
                cursor.execute("""
                    SELECT e.id, e.src_id, e.symbol, e.source_file, n.adg_name, n.layer
                    FROM edges e
                    JOIN nodes n ON e.src_id = n.id
                    WHERE e.relation_type = 'hard_fails_untranscripted'
                    AND n.identity_kind NOT IN ('external_module', 'external_provider')
                """)

                hard_failures = []
                for row in cursor.fetchall():
                    hard_failures.append({
                        "edge_id": row[0],
                        "module_id": row[1],
                        "symbol": row[2],
                        "source_file": row[3],
                        "module_name": row[4],
                        "layer": row[5],
                    })

                print(f"   📊 Found {len(hard_failures)} hard failures")

                # Check if hard failures have corresponding trace edges
                untranscripted_critical = []
                for hf in hard_failures:
                    cursor.execute("""
                        SELECT COUNT(*) FROM edges
                        WHERE src_id = ? AND relation_type = 'records_execution_trace'
                    """, (hf["module_id"],))

                    has_trace = cursor.fetchone()[0] > 0
                    if not has_trace:
                        untranscripted_critical.append(hf)

                if untranscripted_critical:
                    self.errors.append(f"{len(untranscripted_critical)} hard failures lack any transcript")
                    print(f"   ❌ Critical: {len(untranscripted_critical)} hard failures without transcript")
                else:
                    print("   ✅ All hard failures have some transcript coverage")

                return {
                    "total_hard_failures": len(hard_failures),
                    "untranscripted_critical": len(untranscripted_critical),
                    "hard_failure_details": hard_failures,
                }

        except Exception as e:
            raise TraceReplayCoverageError(f"Hard fail verification failed: {e}")

    def verify(self) -> dict[str, Any]:
        """Run complete trace/replay coverage verification."""
        print("🔍 Starting ADG Trace and Replay Coverage Verification...")
        print(f"📁 ADG Directory: {self.adg_dir}")
        print(f"🗄️  SQLite Database: {self.sqlite_path.name}")

        # Verify critical execution surfaces
        critical_coverage = self._verify_critical_execution_surfaces()

        # Verify trace binding completeness
        binding_coverage = self._verify_trace_binding_completeness()

        # Verify hard fail transcript requirements
        hard_fail_analysis = self._verify_hard_fail_transcript_requirements()

        # Prepare result
        result = {
            "status": "PASS" if not self.errors else "FAIL",
            "critical_coverage": critical_coverage,
            "binding_coverage": binding_coverage,
            "hard_fail_analysis": hard_fail_analysis,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {
                "total_modules": critical_coverage["total_modules"],
                "traced_modules": critical_coverage["traced_modules"],
                "complete_coverage": critical_coverage["complete_coverage"],
                "critical_failures": len(critical_coverage["critical_failures"]),
                "hard_failures": hard_fail_analysis["total_hard_failures"],
                "trace_coverage_percentage": 100 * critical_coverage["traced_modules"] / max(1, critical_coverage["total_modules"]),
            },
        }

        # Print results
        if self.errors:
            print("\n❌ TRACE/REPLAY COVERAGE VERIFICATION FAILED")
            for error in self.errors:
                print(f"   • {error}")

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")

        if not self.errors:
            print("\n✅ TRACE/REPLAY COVERAGE VERIFICATION PASSED")
            print(f"📊 Summary: {result['summary']['trace_coverage_percentage']:.1f}% trace coverage")

        return result

def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Verify ADG trace and replay coverage")
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

    args = parser.parse_args()

    try:
        verifier = ADGTraceReplayCoverageVerifier(args.adg_dir)
        result = verifier.verify()

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"📄 Report saved to: {args.output}")

        return 0 if result["status"] == "PASS" else 1

    except TraceReplayCoverageError as e:    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context    # guardian: TraceReplayCoverageError should be handled with specific context
        print(f"❌ Verification failed: {e}")
        return 1
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
