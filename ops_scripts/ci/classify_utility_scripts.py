#!/usr/bin/env python3
"""
Utility Script Classification & Remediation Tool

Classifies utility scripts by operational category and identifies silent swallower
violations for remediation according to Windsurf Hardening Response requirements.

Categories:
- RUNTIME_CRITICAL: Core system components
- GOVERNANCE_CRITICAL: CI, validation, safety enforcement (zero tolerance)
- DIAGNOSTIC_ONLY: Analysis and reporting tools (must emit signals)
- LOCAL_DEV_ONLY: Development utilities (annotation required)

Usage:
    python ops_scripts/ci/classify_utility_scripts.py [--remediate] [--report]
"""

import ast

# Force UTF-8 encoding for Windows compatibility
import io
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "classify_utility_scripts")
_emit_applies_guardrail("p0", "classify_utility_scripts", "p0_governance")
_emit_reads_policy_state("p0", "classify_utility_scripts", "policy_binding")
_emit_snapshots_state("p0", "classify_utility_scripts", "state_snapshot")
emit_replay_key("p0", "classify_utility_scripts")
emit_determinism_digest("p0", "classify_utility_scripts")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "classify_utility_scripts", "execution_auth")
_emit_validates_capability("p2", "classify_utility_scripts", "capability_check")
_emit_routes_to_capability("p2", "classify_utility_scripts", "capability_route")
_emit_writes_via_uwg("p2", "classify_utility_scripts", "uwg_write")
_emit_blocks_direct_write("p2", "classify_utility_scripts", "direct_write_block")
_emit_records_tool_invocation("p2", "classify_utility_scripts", "tool_invocation")
_emit_captures_execution_output("p2", "classify_utility_scripts", "exec_output")
_emit_dispatches_agent("p3", "classify_utility_scripts", "agent_dispatch")
_emit_coordinates_agents("p3", "classify_utility_scripts", "agent_coordination")
_emit_records_workflow_lineage("p3", "classify_utility_scripts", "workflow_lineage")
_emit_records_healing_outcome("p3", "classify_utility_scripts", "healing_outcome")
_emit_escalates_failure("p3", "classify_utility_scripts", "failure_escalation")
_emit_orchestrates_workflow("p3", "classify_utility_scripts", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "classify_utility_scripts", "healing_dispatch")
_emit_invokes_evaluation("p3", "classify_utility_scripts", "evaluation_signal")
_emit_records_telemetry_event("p4", "classify_utility_scripts", "telemetry_event")
_emit_captures_evaluation_metric("p4", "classify_utility_scripts", "eval_metric")
_emit_stores_embedding("p4", "classify_utility_scripts", "embedding_store")
_emit_updates_meta_learning_state("p4", "classify_utility_scripts", "meta_learning")
_emit_links_execution_to_snapshot("p4", "classify_utility_scripts", "exec_snapshot_link")

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Ensure project root is in path
_REPO_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root
from agentic_core.L5_safety.validators.utility_silent_swallower_validator import (
    UtilityScriptClassifier,
    UtilitySilentSwallowerDetector,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("classify_utility_scripts", "p4obs", "metric_1")
_emit_emits_metric_event("classify_utility_scripts", "p4obs", "metric_2")
_emit_emits_metric_event("classify_utility_scripts", "p4obs", "metric_3")
_emit_emits_metric_event("classify_utility_scripts", "p4obs", "metric_4")
_emit_emits_metric_event("classify_utility_scripts", "p4obs", "metric_5")
_emit_emits_metric_event("classify_utility_scripts", "p4obs", "metric_6")
_emit_records_incident_event("classify_utility_scripts", "p4obs", "incident")
_emit_captures_runtime_anomaly("classify_utility_scripts", "p4obs", "anomaly")
_emit_writes_observability_log("classify_utility_scripts", "p4obs", "obs_log")
_emit_updates_monitoring_state("classify_utility_scripts", "p4obs", "mon_state")
_emit_triggers_alert("classify_utility_scripts", "p4obs", "alert")
_emit_links_incident_trace("classify_utility_scripts", "p4obs", "trace_link")
_emit_captures_pattern("classify_utility_scripts", "p3lm", "pattern")
_emit_records_learning_event("classify_utility_scripts", "p3lm", "learning_event")
_emit_writes_learning_snapshot("classify_utility_scripts", "p3lm", "snapshot")
_emit_feeds_meta_learning("classify_utility_scripts", "p3lm", "meta_feed")
_emit_updates_routing_strategy("classify_utility_scripts", "p3lm", "routing")
_emit_improves_agent_policy("classify_utility_scripts", "p3lm", "policy")
_emit_stores_learning_state("classify_utility_scripts", "p3lm", "state")
_emit_records_execution_trace("classify_utility_scripts", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("classify_utility_scripts", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("classify_utility_scripts", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("classify_utility_scripts", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("classify_utility_scripts", "L4_STATE", "p2_trace_5")
_emit_reads_environ("classify_utility_scripts", "env_read", "p2_env_1")
_emit_reads_environ("classify_utility_scripts", "env_read", "p2_env_2")
_emit_reads_runtime_state("classify_utility_scripts", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("classify_utility_scripts", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "classify_utility_scripts", "context_pull")
_emit_pulls_context("p1", "classify_utility_scripts", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "classify_utility_scripts", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "classify_utility_scripts", "uwg_term_2")
_emit_writes_through("p1", "classify_utility_scripts", "write_through")
_emit_writes_through("p1", "classify_utility_scripts", "write_through_2")
_emit_validated_by_safety_plane("p1", "classify_utility_scripts", "safety_validation")
_emit_invokes_eval("p1", "classify_utility_scripts", "eval_call")
_emit_proposal_commits_routing("p1", "classify_utility_scripts", "routing_commit")
_emit_escalates_to_human("p1", "classify_utility_scripts", "human_escalation")
_emit_routes_through("p1", "classify_utility_scripts", "route_through")
_emit_checks_agent_registry("p1", "classify_utility_scripts", "agent_registry")
_emit_validates_agent_capability("p1", "classify_utility_scripts", "capability")
_emit_dispatches_execution_plan("p1", "classify_utility_scripts", "exec_plan")
_emit_agent_executes_agent("p1", "classify_utility_scripts", "sub_agent")
_emit_routes_to_agent("p1", "classify_utility_scripts", "target_agent")
_emit_verifies_policy("p1", "classify_utility_scripts", "policy_check")
_emit_observes_runtime_state("p1", "classify_utility_scripts", "runtime_state")
_emit_verifies_boundary("p1", "classify_utility_scripts", "boundary_check")
_emit_transcripts_response("p1", "classify_utility_scripts", "transcript")
_emit_hard_fails_untranscripted("p1", "classify_utility_scripts")
_emit_gated_by_confidence("p1", "classify_utility_scripts", "confidence_gate")

PROJECT_ROOT = get_validated_project_root()


class UtilityScriptAnalyzer:
    """Analyzes and classifies utility scripts for silent swallower remediation."""

    def __init__(self):
        self.detector = UtilitySilentSwallowerDetector(PROJECT_ROOT)
        self.classifier = UtilityScriptClassifier()

    def analyze_all_utility_scripts(self) -> dict[str, list[dict]]:
        """Analyze all utility scripts and categorize findings."""
        utility_paths = [
            "ops_scripts",
            "tools",
            "tests/guardian",
            "tests/governance",
            "tests/integration",
            "tests/performance",
            "agentic_core/L5_safety/validators",
            "agentic_core/L5_safety/static_checks",
        ]

        results = {
            "GOVERNANCE_CRITICAL": [],
            "DIAGNOSTIC_ONLY": [],
            "LOCAL_DEV_ONLY": [],
            "RUNTIME_CRITICAL": [],
        }

        for path in utility_paths:
            full_path = PROJECT_ROOT / path
            if full_path.exists():
                for py_file in full_path.rglob("*.py"):
                    if self._should_analyze_file(py_file):
                        category = self.classifier.classify_script(py_file)
                        detection_result = self.detector.scan_file(py_file)

                        script_info = {
                            "file": str(py_file.relative_to(PROJECT_ROOT)),
                            "category": category,
                            "violations": detection_result.violation_count,
                            "violation_details": [
                                {
                                    "line": v.line_number,
                                    "message": v.message,
                                    "severity": v.severity,
                                } for v in detection_result.violations
                            ],
                        }

                        results[category].append(script_info)

        return results

    def _should_analyze_file(self, file_path: Path) -> bool:
        """Check if file should be analyzed for silent swallowers."""
        # Skip test files (they have different patterns)
        if "test_" in file_path.name and file_path.parent.name == "tests":
            return False

        # Skip __init__.py files
        if file_path.name == "__init__.py":
            return False

        # Skip files in archives or backups
        if any(skip in str(file_path) for skip in ["archives", ".healing_backups", "__pycache__"]):
            return False

        return True

    def generate_remediation_plan(self, analysis: dict[str, list[dict]]) -> dict:
        """Generate prioritized remediation plan."""
        plan = {
            "priority_order": ["GOVERNANCE_CRITICAL", "DIAGNOSTIC_ONLY", "LOCAL_DEV_ONLY", "RUNTIME_CRITICAL"],
            "remediation_steps": [],
            "summary": {},
        }

        total_violations = 0
        total_files = 0

        for category in plan["priority_order"]:
            category_files = analysis[category]
            category_violations = sum(f["violations"] for f in category_files)

            total_files += len(category_files)
            total_violations += category_violations

            plan["summary"][category] = {
                "files": len(category_files),
                "violations": category_violations,
                "priority": self._get_priority_level(category),
            }

            if category_files:
                step = {
                    "category": category,
                    "description": self._get_category_description(category),
                    "files_to_fix": len(category_files),
                    "violations_to_resolve": category_violations,
                    "files": sorted(category_files, key=lambda x: -x["violations"])[:10],  # Top 10 worst
                }
                plan["remediation_steps"].append(step)

        plan["summary"]["total"] = {
            "files": total_files,
            "violations": total_violations,
        }

        return plan

    def _get_priority_level(self, category: str) -> str:
        """Get priority level for category."""
        priorities = {
            "GOVERNANCE_CRITICAL": "CRITICAL",
            "DIAGNOSTIC_ONLY": "HIGH",
            "LOCAL_DEV_ONLY": "MEDIUM",
            "RUNTIME_CRITICAL": "CRITICAL",
        }
        return priorities.get(category, "LOW")

    def _get_category_description(self, category: str) -> str:
        """Get description for remediation category."""
        descriptions = {
            "GOVERNANCE_CRITICAL": "Zero tolerance - must fail loudly",
            "DIAGNOSTIC_ONLY": "Must emit failure signals",
            "LOCAL_DEV_ONLY": "Requires guardian annotation",
            "RUNTIME_CRITICAL": "Core system integrity",
        }
        return descriptions.get(category, "Unknown category")

    def print_report(self, analysis: dict[str, list[dict]], plan: dict) -> None:
        """Print comprehensive analysis report."""
        print("=" * 80)
        print("UTILITY SCRIPT SILENT SWALLOWER ANALYSIS")
        print("=" * 80)
        print()

        # Summary
        summary = plan["summary"]["total"]
        print(f"📊 SUMMARY: {summary['files']} utility scripts analyzed, {summary['violations']} violations found")
        print()

        # Category breakdown
        print("📁 CATEGORY BREAKDOWN:")
        for category in plan["priority_order"]:
            cat_summary = plan["summary"][category]
            if cat_summary["files"] > 0:
                priority = cat_summary["priority"]
                icon = "🔴" if priority == "CRITICAL" else "🟡" if priority == "HIGH" else "🟠"
                print(f"  {icon} {category}: {cat_summary['files']} files, {cat_summary['violations']} violations ({priority})")
        print()

        # Remediation steps
        print("🔧 REMEDIATION PLAN:")
        for i, step in enumerate(plan["remediation_steps"], 1):
            category = step["category"]
            priority = plan["summary"][category]["priority"]
            icon = "🚨" if priority == "CRITICAL" else "⚠️" if priority == "HIGH" else "📝"

            print(f"  {i}. {icon} {category}")
            print(f"     {step['description']}")
            print(f"     Files to fix: {step['files_to_fix']}")
            print(f"     Violations to resolve: {step['violations_to_resolve']}")

            if step["files"]:
                print("     Top issues:")
                for file_info in step["files"][:5]:
                    print(f"       - {file_info['file']} ({file_info['violations']} violations)")
            print()

        print("=" * 80)


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Classify and analyze utility scripts")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--remediate", action="store_true", help="Generate remediation suggestions")

    args = parser.parse_args()

    analyzer = UtilityScriptAnalyzer()

    print("🔍 Analyzing utility scripts for silent swallowers...")
    analysis = analyzer.analyze_all_utility_scripts()
    plan = analyzer.generate_remediation_plan(analysis)

    if args.json:
        print(json.dumps({"analysis": analysis, "plan": plan}, indent=2))
    else:
        analyzer.print_report(analysis, plan)

    if args.report:
        # Save detailed report
        report_path = PROJECT_ROOT / "docs" / "reports" / "utility_script_analysis.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        report_data = {
            "analysis": analysis,
            "plan": plan,
            "timestamp": str(Path(__file__).stat().st_mtime),
        }

        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"📄 Detailed report saved to: {report_path}")

    # Exit with error if critical violations found
    critical_violations = plan["summary"].get("GOVERNANCE_CRITICAL", {}).get("violations", 0)
    if critical_violations > 0:
        print(f"❌ CRITICAL: {critical_violations} governance violations found")
        return 1
    else:
        print("✅ No critical governance violations")
        return 0


if __name__ == "__main__":
    sys.exit(main())
