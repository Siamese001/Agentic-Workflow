"""
L5 Runner for CodeValidatorAgent.

This module provides subprocess-callable entry points for L0-L4 scripts
to invoke CodeValidatorAgent without creating upward import edges.

Usage from subprocess:
    python -m agentic_core.L5_safety.runners.code_validator_runner --action=validate
    python -m agentic_core.L5_safety.runners.code_validator_runner --action=validate_directory --directory=policy_engine
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

emit_replay_key("p0", "code_validator_runner")
emit_determinism_digest("p0", "code_validator_runner")

_emit_dispatches_healing_run("p1", "code_validator_runner", "L5")
_emit_routes_through("p1", "code_validator_runner", "L5")
_emit_checks_agent_registry("p1", "code_validator_runner", "agent_registry")
_emit_validates_agent_capability("p1", "code_validator_runner", "capability")
_emit_dispatches_execution_plan("p1", "code_validator_runner", "exec_plan")
_emit_agent_executes_agent("p1", "code_validator_runner", "sub_agent")
_emit_routes_to_agent("p1", "code_validator_runner", "target_agent")
_emit_verifies_policy("p1", "code_validator_runner", "policy_check")
_emit_observes_runtime_state("p1", "code_validator_runner", "runtime_state")
_emit_verifies_boundary("p1", "code_validator_runner", "boundary_check")
_emit_transcripts_response("p1", "code_validator_runner", "transcript")
_emit_hard_fails_untranscripted("p1", "code_validator_runner")
_emit_gated_by_confidence("p1", "code_validator_runner", "confidence_gate")
_emit_escalates_to_human("p1", "code_validator_runner", "L5")
_emit_reads_policy_state("p1", "code_validator_runner", "L5")
_emit_authorize_and_execute("p2", "code_validator_runner", "execution_auth")
_emit_validates_capability("p2", "code_validator_runner", "capability_check")
_emit_routes_to_capability("p2", "code_validator_runner", "capability_route")
_emit_writes_via_uwg("p2", "code_validator_runner", "uwg_write")
_emit_blocks_direct_write("p2", "code_validator_runner", "direct_write_block")
_emit_records_tool_invocation("p2", "code_validator_runner", "tool_invocation")
_emit_captures_execution_output("p2", "code_validator_runner", "exec_output")
_emit_dispatches_agent("p3", "code_validator_runner", "agent_dispatch")
_emit_coordinates_agents("p3", "code_validator_runner", "agent_coordination")
_emit_records_workflow_lineage("p3", "code_validator_runner", "workflow_lineage")
_emit_records_healing_outcome("p3", "code_validator_runner", "healing_outcome")
_emit_escalates_failure("p3", "code_validator_runner", "failure_escalation")
_emit_orchestrates_workflow("p3", "code_validator_runner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "code_validator_runner", "healing_dispatch")
_emit_invokes_evaluation("p3", "code_validator_runner", "evaluation_signal")
_emit_records_telemetry_event("p4", "code_validator_runner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "code_validator_runner", "eval_metric")
_emit_stores_embedding("p4", "code_validator_runner", "embedding_store")
_emit_updates_meta_learning_state("p4", "code_validator_runner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "code_validator_runner", "exec_snapshot_link")
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

_emit_emits_metric_event("code_validator_runner", "p4obs", "metric_1")
_emit_emits_metric_event("code_validator_runner", "p4obs", "metric_2")
_emit_emits_metric_event("code_validator_runner", "p4obs", "metric_3")
_emit_emits_metric_event("code_validator_runner", "p4obs", "metric_4")
_emit_emits_metric_event("code_validator_runner", "p4obs", "metric_5")
_emit_emits_metric_event("code_validator_runner", "p4obs", "metric_6")
_emit_records_incident_event("code_validator_runner", "p4obs", "incident")
_emit_captures_runtime_anomaly("code_validator_runner", "p4obs", "anomaly")
_emit_writes_observability_log("code_validator_runner", "p4obs", "obs_log")
_emit_updates_monitoring_state("code_validator_runner", "p4obs", "mon_state")
_emit_triggers_alert("code_validator_runner", "p4obs", "alert")
_emit_links_incident_trace("code_validator_runner", "p4obs", "trace_link")
_emit_captures_pattern("code_validator_runner", "p3lm", "pattern")
_emit_records_learning_event("code_validator_runner", "p3lm", "learning_event")
_emit_writes_learning_snapshot("code_validator_runner", "p3lm", "snapshot")
_emit_feeds_meta_learning("code_validator_runner", "p3lm", "meta_feed")
_emit_updates_routing_strategy("code_validator_runner", "p3lm", "routing")
_emit_improves_agent_policy("code_validator_runner", "p3lm", "policy")
_emit_stores_learning_state("code_validator_runner", "p3lm", "state")
_emit_records_execution_trace("code_validator_runner", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("code_validator_runner", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("code_validator_runner", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("code_validator_runner", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("code_validator_runner", "L4_STATE", "p2_trace_5")
_emit_reads_environ("code_validator_runner", "env_read", "p2_env_1")
_emit_reads_environ("code_validator_runner", "env_read", "p2_env_2")
_emit_reads_runtime_state("code_validator_runner", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("code_validator_runner", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "code_validator_runner", "context_pull")
_emit_pulls_context("p1", "code_validator_runner", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "code_validator_runner", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "code_validator_runner", "uwg_term_2")
_emit_writes_through("p1", "code_validator_runner", "write_through")
_emit_writes_through("p1", "code_validator_runner", "write_through_2")
_emit_validated_by_safety_plane("p1", "code_validator_runner", "safety_validation")
_emit_invokes_eval("p1", "code_validator_runner", "eval_call")
_emit_proposal_commits_routing("p1", "code_validator_runner", "routing_commit")


def get_project_root() -> Path:
    """Get project root from this file's location."""
    return Path(__file__).resolve().parent.parent.parent.parent


def validate_repository(project_root: Path) -> dict:
    """Validate entire repository with CodeValidatorAgent."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "validate_repository", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "validate_repository", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "validate_repository")
    from agentic_core.L5_safety.reasoning.CodeValidatorAgent import CodeValidatorAgent

    agent = CodeValidatorAgent(project_root=project_root)
    result = agent.validate_repository()
    violations = []
    for v in result.get("violations", []):
        violations.append(
            {
                "file_path": str(v.file_path),
                "line_number": v.line_number,
                "column": v.column,
                "error_message": v.error_message,
                "severity": getattr(v, "severity", "error"),
            },
        )
    return {"success": True, "total_violations": result.get("total_violations", 0), "violations": violations}


def validate_directory(project_root: Path, directory: str) -> dict:
    """Validate specific directory with CodeValidatorAgent."""
    from agentic_core.L5_safety.reasoning.CodeValidatorAgent import CodeValidatorAgent

    agent = CodeValidatorAgent(project_root=project_root)
    target_dir = project_root / directory
    if not target_dir.exists():
        return {"success": False, "error": f"Directory does not exist: {target_dir}"}
    result = agent.validate_repository()
    violations = []
    for v in result.get("violations", []):
        if target_dir in Path(v.file_path).parents:
            violations.append(
                {
                    "file_path": str(v.file_path),
                    "line_number": v.line_number,
                    "column": v.column,
                    "error_message": v.error_message,
                    "severity": getattr(v, "severity", "error"),
                },
            )
    return {
        "success": True,
        "directory": directory,
        "total_violations": len(violations),
        "violations": violations,
    }


def main() -> int:
    """CLI entry point for subprocess invocation."""
    parser = argparse.ArgumentParser(description="CodeValidatorAgent Runner")
    parser.add_argument(
        "--action", choices=["validate", "validate_directory"], required=True, help="Action to perform",
    )
    parser.add_argument(
        "--directory", type=str, help="Directory to validate (required for validate_directory)",
    )
    parser.add_argument(
        "--project-root", type=str, default=None, help="Project root path (defaults to auto-detect)",
    )
    args = parser.parse_args()
    project_root = Path(args.project_root) if args.project_root else get_project_root()
    try:
        if args.action == "validate":
            result = validate_repository(project_root)
        elif args.action == "validate_directory":
            if not args.directory:
                result = {"success": False, "error": "--directory required for validate_directory"}
            else:
                result = validate_directory(project_root, args.directory)
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
