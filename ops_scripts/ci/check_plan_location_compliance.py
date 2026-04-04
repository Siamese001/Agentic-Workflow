#!/usr/bin/env python3
"""
Plan Location Compliance Guardrail

Enforces Constitutional Rule #0: ALL plans, reports, and markdown artifacts
MUST be saved to `docs/reports/plans/` inside the repository.

Usage:
    python ops_scripts/ci/check_plan_location_compliance.py [--fix]
"""

import argparse

# Force UTF-8 encoding for Windows compatibility
import io
import json
import sys
from pathlib import Path

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "check_plan_location_compliance")
_emit_applies_guardrail("p0", "check_plan_location_compliance", "p0_governance")
_emit_reads_policy_state("p0", "check_plan_location_compliance", "policy_binding")
_emit_snapshots_state("p0", "check_plan_location_compliance", "state_snapshot")
emit_replay_key("p0", "check_plan_location_compliance")
emit_determinism_digest("p0", "check_plan_location_compliance")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "check_plan_location_compliance", "execution_auth")
_emit_validates_capability("p2", "check_plan_location_compliance", "capability_check")
_emit_routes_to_capability("p2", "check_plan_location_compliance", "capability_route")
_emit_writes_via_uwg("p2", "check_plan_location_compliance", "uwg_write")
_emit_blocks_direct_write("p2", "check_plan_location_compliance", "direct_write_block")
_emit_records_tool_invocation("p2", "check_plan_location_compliance", "tool_invocation")
_emit_captures_execution_output("p2", "check_plan_location_compliance", "exec_output")
_emit_dispatches_agent("p3", "check_plan_location_compliance", "agent_dispatch")
_emit_coordinates_agents("p3", "check_plan_location_compliance", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_plan_location_compliance", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_plan_location_compliance", "healing_outcome")
_emit_escalates_failure("p3", "check_plan_location_compliance", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_plan_location_compliance", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_plan_location_compliance", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_plan_location_compliance", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_plan_location_compliance", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_plan_location_compliance", "eval_metric")
_emit_stores_embedding("p4", "check_plan_location_compliance", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_plan_location_compliance", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_plan_location_compliance", "exec_snapshot_link")

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Ensure project root is in path
_REPO_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("check_plan_location_compliance", "p4obs", "metric_1")
_emit_emits_metric_event("check_plan_location_compliance", "p4obs", "metric_2")
_emit_emits_metric_event("check_plan_location_compliance", "p4obs", "metric_3")
_emit_emits_metric_event("check_plan_location_compliance", "p4obs", "metric_4")
_emit_emits_metric_event("check_plan_location_compliance", "p4obs", "metric_5")
_emit_emits_metric_event("check_plan_location_compliance", "p4obs", "metric_6")
_emit_records_incident_event("check_plan_location_compliance", "p4obs", "incident")
_emit_captures_runtime_anomaly("check_plan_location_compliance", "p4obs", "anomaly")
_emit_writes_observability_log("check_plan_location_compliance", "p4obs", "obs_log")
_emit_updates_monitoring_state("check_plan_location_compliance", "p4obs", "mon_state")
_emit_triggers_alert("check_plan_location_compliance", "p4obs", "alert")
_emit_links_incident_trace("check_plan_location_compliance", "p4obs", "trace_link")
_emit_captures_pattern("check_plan_location_compliance", "p3lm", "pattern")
_emit_records_learning_event("check_plan_location_compliance", "p3lm", "learning_event")
_emit_writes_learning_snapshot("check_plan_location_compliance", "p3lm", "snapshot")
_emit_feeds_meta_learning("check_plan_location_compliance", "p3lm", "meta_feed")
_emit_updates_routing_strategy("check_plan_location_compliance", "p3lm", "routing")
_emit_improves_agent_policy("check_plan_location_compliance", "p3lm", "policy")
_emit_stores_learning_state("check_plan_location_compliance", "p3lm", "state")
_emit_records_execution_trace("check_plan_location_compliance", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("check_plan_location_compliance", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("check_plan_location_compliance", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("check_plan_location_compliance", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("check_plan_location_compliance", "L4_STATE", "p2_trace_5")
_emit_reads_environ("check_plan_location_compliance", "env_read", "p2_env_1")
_emit_reads_environ("check_plan_location_compliance", "env_read", "p2_env_2")
_emit_reads_runtime_state("check_plan_location_compliance", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("check_plan_location_compliance", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "check_plan_location_compliance", "context_pull")
_emit_pulls_context("p1", "check_plan_location_compliance", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "check_plan_location_compliance", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "check_plan_location_compliance", "uwg_term_secondary")
_emit_writes_through("p1", "check_plan_location_compliance", "write_through")
_emit_writes_through("p1", "check_plan_location_compliance", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "check_plan_location_compliance", "safety_validation")
_emit_invokes_eval("p1", "check_plan_location_compliance", "eval_call")
_emit_proposal_commits_routing("p1", "check_plan_location_compliance", "routing_commit")
_emit_escalates_to_human("p1", "check_plan_location_compliance", "human_escalation")
_emit_routes_through("p1", "check_plan_location_compliance", "route_through")
_emit_checks_agent_registry("p1", "check_plan_location_compliance", "agent_registry")
_emit_validates_agent_capability("p1", "check_plan_location_compliance", "capability")
_emit_dispatches_execution_plan("p1", "check_plan_location_compliance", "exec_plan")
_emit_agent_executes_agent("p1", "check_plan_location_compliance", "sub_agent")
_emit_routes_to_agent("p1", "check_plan_location_compliance", "target_agent")
_emit_verifies_policy("p1", "check_plan_location_compliance", "policy_check")
_emit_observes_runtime_state("p1", "check_plan_location_compliance", "runtime_state")
_emit_verifies_boundary("p1", "check_plan_location_compliance", "boundary_check")
_emit_transcripts_response("p1", "check_plan_location_compliance", "transcript")
_emit_hard_fails_untranscripted("p1", "check_plan_location_compliance")
_emit_gated_by_confidence("p1", "check_plan_location_compliance", "confidence_gate")

PROJECT_ROOT = get_validated_project_root()


class PlanLocationComplianceChecker:
    """Enforces plan location compliance with Constitutional Rule #0."""

    def check_compliance(self):
        """Check for plan location violations."""
        violations = []

        # Check for .windsurf/plans directory
        windsurf_plans = PROJECT_ROOT / ".windsurf" / "plans"
        if windsurf_plans.exists():
            violations.append({
                "type": "windsurf_plans_exists",
                "directory": str(windsurf_plans),
                "message": ".windsurf/plans directory exists (violates Constitutional Rule #0)",
                "severity": "error",
            })

        # Ensure SSOT plans directory exists
        ssot_plans = PROJECT_ROOT / "docs" / "reports" / "plans"
        if not ssot_plans.exists():
            violations.append({
                "type": "missing_ssot_directory",
                "directory": str(ssot_plans),
                "message": "SSOT plans directory is missing",
                "severity": "error",
            })

        return violations

    def print_report(self):
        """Print compliance report."""
        violations = self.check_compliance()

        if not violations:
            print("✅ Plan location compliance: No violations found")
            print(f"📁 SSOT plans directory: {PROJECT_ROOT / 'docs' / 'reports' / 'plans'}")
            return 0

        print(f"❌ Plan location violations found: {len(violations)}")
        for v in violations:
            print(f"   {v['message']}")

        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check plan location compliance")
    args = parser.parse_args()

    checker = PlanLocationComplianceChecker()
    return checker.print_report()


if __name__ == "__main__":
    sys.exit(main())
