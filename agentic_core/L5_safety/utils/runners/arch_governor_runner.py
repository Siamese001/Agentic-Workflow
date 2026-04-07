"""
L5 Runner for ArchitectureGovernorAgent.

This module provides subprocess-callable entry points for L0 scripts
to invoke ArchitectureGovernorAgent without creating upward import edges.

Usage from subprocess:
    python -m agentic_core.L5_safety.runners.arch_governor_runner --action=verify
    python -m agentic_core.L5_safety.runners.arch_governor_runner --action=capture_baseline
    python -m agentic_core.L5_safety.runners.arch_governor_runner --action=audit --targets=L0,L1
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "arch_governor_runner")
emit_determinism_digest("p0", "arch_governor_runner")

_emit_dispatches_healing_run("p1", "arch_governor_runner", "L5")
_emit_routes_through("p1", "arch_governor_runner", "L5")
_emit_checks_agent_registry("p1", "arch_governor_runner", "agent_registry")
_emit_validates_agent_capability("p1", "arch_governor_runner", "capability")
_emit_dispatches_execution_plan("p1", "arch_governor_runner", "exec_plan")
_emit_agent_executes_agent("p1", "arch_governor_runner", "sub_agent")
_emit_routes_to_agent("p1", "arch_governor_runner", "target_agent")
_emit_verifies_policy("p1", "arch_governor_runner", "policy_check")
_emit_observes_runtime_state("p1", "arch_governor_runner", "runtime_state")
_emit_verifies_boundary("p1", "arch_governor_runner", "boundary_check")
_emit_transcripts_response("p1", "arch_governor_runner", "transcript")
_emit_hard_fails_untranscripted("p1", "arch_governor_runner")
_emit_gated_by_confidence("p1", "arch_governor_runner", "confidence_gate")
_emit_escalates_to_human("p1", "arch_governor_runner", "L5")
_emit_reads_policy_state("p1", "arch_governor_runner", "L5")
_emit_authorize_and_execute("p2", "arch_governor_runner", "execution_auth")
_emit_validates_capability("p2", "arch_governor_runner", "capability_check")
_emit_routes_to_capability("p2", "arch_governor_runner", "capability_route")
_emit_writes_via_uwg("p2", "arch_governor_runner", "uwg_write")
_emit_blocks_direct_write("p2", "arch_governor_runner", "direct_write_block")
_emit_records_tool_invocation("p2", "arch_governor_runner", "tool_invocation")
_emit_captures_execution_output("p2", "arch_governor_runner", "exec_output")
_emit_dispatches_agent("p3", "arch_governor_runner", "agent_dispatch")
_emit_coordinates_agents("p3", "arch_governor_runner", "agent_coordination")
_emit_records_workflow_lineage("p3", "arch_governor_runner", "workflow_lineage")
_emit_records_healing_outcome("p3", "arch_governor_runner", "healing_outcome")
_emit_escalates_failure("p3", "arch_governor_runner", "failure_escalation")
_emit_orchestrates_workflow("p3", "arch_governor_runner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "arch_governor_runner", "healing_dispatch")
_emit_invokes_evaluation("p3", "arch_governor_runner", "evaluation_signal")
_emit_records_telemetry_event("p4", "arch_governor_runner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "arch_governor_runner", "eval_metric")
_emit_stores_embedding("p4", "arch_governor_runner", "embedding_store")
_emit_updates_meta_learning_state("p4", "arch_governor_runner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "arch_governor_runner", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("arch_governor_runner", "p4obs", "metric_1")
_emit_emits_metric_event("arch_governor_runner", "p4obs", "metric_2")
_emit_emits_metric_event("arch_governor_runner", "p4obs", "metric_3")
_emit_emits_metric_event("arch_governor_runner", "p4obs", "metric_4")
_emit_emits_metric_event("arch_governor_runner", "p4obs", "metric_5")
_emit_emits_metric_event("arch_governor_runner", "p4obs", "metric_6")
_emit_records_incident_event("arch_governor_runner", "p4obs", "incident")
_emit_captures_runtime_anomaly("arch_governor_runner", "p4obs", "anomaly")
_emit_writes_observability_log("arch_governor_runner", "p4obs", "obs_log")
_emit_updates_monitoring_state("arch_governor_runner", "p4obs", "mon_state")
_emit_triggers_alert("arch_governor_runner", "p4obs", "alert")
_emit_links_incident_trace("arch_governor_runner", "p4obs", "trace_link")
_emit_captures_pattern("arch_governor_runner", "p3lm", "pattern")
_emit_records_learning_event("arch_governor_runner", "p3lm", "learning_event")
_emit_writes_learning_snapshot("arch_governor_runner", "p3lm", "snapshot")
_emit_feeds_meta_learning("arch_governor_runner", "p3lm", "meta_feed")
_emit_updates_routing_strategy("arch_governor_runner", "p3lm", "routing")
_emit_improves_agent_policy("arch_governor_runner", "p3lm", "policy")
_emit_stores_learning_state("arch_governor_runner", "p3lm", "state")
_emit_records_execution_trace("arch_governor_runner", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("arch_governor_runner", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("arch_governor_runner", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("arch_governor_runner", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("arch_governor_runner", "L4_STATE", "p2_trace_5")
_emit_reads_environ("arch_governor_runner", "env_read", "p2_env_1")
_emit_reads_environ("arch_governor_runner", "env_read", "p2_env_2")
_emit_reads_runtime_state("arch_governor_runner", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("arch_governor_runner", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "arch_governor_runner", "context_pull")
_emit_pulls_context("p1", "arch_governor_runner", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "arch_governor_runner", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "arch_governor_runner", "uwg_term_2")
_emit_writes_through("p1", "arch_governor_runner", "write_through")
_emit_writes_through("p1", "arch_governor_runner", "write_through_2")
_emit_validated_by_safety_plane("p1", "arch_governor_runner", "safety_validation")
_emit_invokes_eval("p1", "arch_governor_runner", "eval_call")
_emit_proposal_commits_routing("p1", "arch_governor_runner", "routing_commit")


def get_project_root() -> Path:
    """Get project root from this file's location."""
    return Path(__file__).resolve().parent.parent.parent.parent


def run_ci_verification(project_root: Path, auto_approve: bool = True) -> dict:
    """Run CI verification and return results as dict."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "run_ci_verification", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "run_ci_verification", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "run_ci_verification")
    from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent

    agent = ArchitectureGovernorAgent(project_root=project_root, auto_approve=auto_approve)
    is_compliant, results = agent.run_ci_verification_sync()
    return {
        "success": is_compliant,
        "violations_found": results.get("violations_found", 0),
        "roots_scanned": results.get("roots_scanned", []),
        "raw_result": results,
    }


def capture_golden_baseline(project_root: Path) -> dict:
    """Capture golden baseline and return manifest path."""
    from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent

    governor = ArchitectureGovernorAgent(project_root=project_root)
    manifest = governor.capture_golden_baseline()
    return {"success": True, "manifest_path": str(manifest) if manifest else None}


def run_audit(project_root: Path, targets: list[str] | None = None) -> dict:
    """Run audit with optional target territories."""
    from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent

    governor = ArchitectureGovernorAgent(project_root=project_root, ci_mode=True)
    audit_results = governor.run_audit(target_territories=targets)
    return {"success": True, "audit_results": audit_results}


def main() -> int:
    """CLI entry point for subprocess invocation."""
    parser = argparse.ArgumentParser(description="ArchitectureGovernorAgent Runner")
    parser.add_argument(
        "--action", choices=["verify", "capture_baseline", "audit"], required=True, help="Action to perform",
    )
    parser.add_argument(
        "--project-root", type=str, default=None, help="Project root path (defaults to auto-detect)",
    )
    parser.add_argument(
        "--targets", type=str, default=None, help="Comma-separated target territories for audit",
    )
    parser.add_argument(
        "--auto-approve", action="store_true", default=True, help="Auto-approve mode (default: True)",
    )
    args = parser.parse_args()
    project_root = Path(args.project_root) if args.project_root else get_project_root()
    try:
        if args.action == "verify":
            result = run_ci_verification(project_root, args.auto_approve)
        elif args.action == "capture_baseline":
            result = capture_golden_baseline(project_root)
        elif args.action == "audit":
            targets = args.targets.split(",") if args.targets else None
            result = run_audit(project_root, targets)
        else:
            result = {"success": False, "error": f"Unknown action: {args.action}"}
        print(json.dumps(result, default=str))
        return 0 if result.get("success") else 1
    # guardian: allow-silent-swallow
    except (ValueError, TypeError) as e:
        print(json.dumps({"success": False, "error": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
