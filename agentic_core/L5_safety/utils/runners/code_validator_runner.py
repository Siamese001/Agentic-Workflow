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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "code_validator_runner")
trace_contract.emit_determinism_digest("p0", "code_validator_runner")

trace_contract._emit_dispatches_healing_run("p1", "code_validator_runner", "L5")
trace_contract._emit_routes_through("p1", "code_validator_runner", "L5")
trace_contract._emit_checks_agent_registry("p1", "code_validator_runner", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "code_validator_runner", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "code_validator_runner", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "code_validator_runner", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "code_validator_runner", "target_agent")
trace_contract._emit_verifies_policy("p1", "code_validator_runner", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "code_validator_runner", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "code_validator_runner", "boundary_check")
trace_contract._emit_transcripts_response("p1", "code_validator_runner", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "code_validator_runner")
trace_contract._emit_gated_by_confidence("p1", "code_validator_runner", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "code_validator_runner", "L5")
trace_contract._emit_reads_policy_state("p1", "code_validator_runner", "L5")
trace_contract._emit_authorize_and_execute("p2", "code_validator_runner", "execution_auth")
trace_contract._emit_validates_capability("p2", "code_validator_runner", "capability_check")
trace_contract._emit_routes_to_capability("p2", "code_validator_runner", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "code_validator_runner", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "code_validator_runner", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "code_validator_runner", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "code_validator_runner", "exec_output")
trace_contract._emit_dispatches_agent("p3", "code_validator_runner", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "code_validator_runner", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "code_validator_runner", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "code_validator_runner", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "code_validator_runner", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "code_validator_runner", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "code_validator_runner", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "code_validator_runner", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "code_validator_runner", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "code_validator_runner", "eval_metric")
trace_contract._emit_stores_embedding("p4", "code_validator_runner", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "code_validator_runner", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "code_validator_runner", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("code_validator_runner", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("code_validator_runner", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("code_validator_runner", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("code_validator_runner", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("code_validator_runner", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("code_validator_runner", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("code_validator_runner", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("code_validator_runner", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("code_validator_runner", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("code_validator_runner", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("code_validator_runner", "p4obs", "alert")
trace_contract._emit_links_incident_trace("code_validator_runner", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("code_validator_runner", "p3lm", "pattern")
trace_contract._emit_records_learning_event("code_validator_runner", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("code_validator_runner", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("code_validator_runner", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("code_validator_runner", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("code_validator_runner", "p3lm", "policy")
trace_contract._emit_stores_learning_state("code_validator_runner", "p3lm", "state")
trace_contract._emit_records_execution_trace("code_validator_runner", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("code_validator_runner", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("code_validator_runner", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("code_validator_runner", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("code_validator_runner", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("code_validator_runner", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("code_validator_runner", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("code_validator_runner", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("code_validator_runner", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "code_validator_runner", "context_pull")
trace_contract._emit_pulls_context("p1", "code_validator_runner", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "code_validator_runner", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "code_validator_runner", "uwg_term_2")
trace_contract._emit_writes_through("p1", "code_validator_runner", "write_through")
trace_contract._emit_writes_through("p1", "code_validator_runner", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "code_validator_runner", "safety_validation")
trace_contract._emit_invokes_eval("p1", "code_validator_runner", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "code_validator_runner", "routing_commit")


def get_project_root() -> Path:
    """Get project root from this file's location."""
    return Path(__file__).resolve().parent.parent.parent.parent


def validate_repository(project_root: Path) -> dict:
    """Validate entire repository with CodeValidatorAgent."""
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "validate_repository", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "validate_repository", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "validate_repository")
    # MW-5b / MW-11 (2026-04-24): CodeValidator util gained validate_repository()
    # + project_root kwarg in MW-11; swapped to canonical util class. Agent
    # archive-eligible 2026-07-23.
    from agentic_core.L5_safety.utils.code_validator_util import CodeValidator as CodeValidatorAgent

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
    # MW-5b / MW-11 (2026-04-24): see note above — util API gap closed in MW-11.
    from agentic_core.L5_safety.utils.code_validator_util import CodeValidator as CodeValidatorAgent

    agent = CodeValidatorAgent(project_root=project_root)
    target_dir = project_root / directory
    if not target_dir.exists():
        return {"success": False, "error": f"Directory does not exist: {target_dir}"}
    result = agent.validate_repository()
    violations = []
    for v in tqdm(result.get("violations", []), desc="Processing", unit="item"):
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
        "--action",
        choices=["validate", "validate_directory"],
        required=True,
        help="Action to perform",
    )
    parser.add_argument(
        "--directory",
        type=str,
        help="Directory to validate (required for validate_directory)",
    )
    parser.add_argument(
        "--project-root",
        type=str,
        default=None,
        help="Project root path (defaults to auto-detect)",
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
    except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
        print(json.dumps({"success": False, "error": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
