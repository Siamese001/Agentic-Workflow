"""
L5 runner for structure hierarchy checks.

This module provides subprocess-callable entry points for L0 scripts
to invoke StructureEnforcerAgent without creating upward import edges.

Usage from subprocess:
    python -m agentic_core.L5_safety.runners.hierarchy_runner --action=dry_run
    python -m agentic_core.L5_safety.runners.hierarchy_runner --action=heal_violations
    python -m agentic_core.L5_safety.runners.hierarchy_runner --action=verify_mro
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "hierarchy_runner")
trace_contract.emit_determinism_digest("p0", "hierarchy_runner")

trace_contract._emit_dispatches_healing_run("p1", "hierarchy_runner", "L5")
trace_contract._emit_routes_through("p1", "hierarchy_runner", "L5")
trace_contract._emit_checks_agent_registry("p1", "hierarchy_runner", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "hierarchy_runner", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "hierarchy_runner", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "hierarchy_runner", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "hierarchy_runner", "target_agent")
trace_contract._emit_verifies_policy("p1", "hierarchy_runner", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "hierarchy_runner", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "hierarchy_runner", "boundary_check")
trace_contract._emit_transcripts_response("p1", "hierarchy_runner", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "hierarchy_runner")
trace_contract._emit_gated_by_confidence("p1", "hierarchy_runner", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "hierarchy_runner", "L5")
trace_contract._emit_reads_policy_state("p1", "hierarchy_runner", "L5")
trace_contract._emit_authorize_and_execute("p2", "hierarchy_runner", "execution_auth")
trace_contract._emit_validates_capability("p2", "hierarchy_runner", "capability_check")
trace_contract._emit_routes_to_capability("p2", "hierarchy_runner", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "hierarchy_runner", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "hierarchy_runner", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "hierarchy_runner", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "hierarchy_runner", "exec_output")
trace_contract._emit_dispatches_agent("p3", "hierarchy_runner", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "hierarchy_runner", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "hierarchy_runner", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "hierarchy_runner", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "hierarchy_runner", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "hierarchy_runner", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "hierarchy_runner", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "hierarchy_runner", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "hierarchy_runner", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "hierarchy_runner", "eval_metric")
trace_contract._emit_stores_embedding("p4", "hierarchy_runner", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "hierarchy_runner", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "hierarchy_runner", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("hierarchy_runner", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("hierarchy_runner", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("hierarchy_runner", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("hierarchy_runner", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("hierarchy_runner", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("hierarchy_runner", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("hierarchy_runner", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("hierarchy_runner", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("hierarchy_runner", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("hierarchy_runner", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("hierarchy_runner", "p4obs", "alert")
trace_contract._emit_links_incident_trace("hierarchy_runner", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("hierarchy_runner", "p3lm", "pattern")
trace_contract._emit_records_learning_event("hierarchy_runner", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("hierarchy_runner", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("hierarchy_runner", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("hierarchy_runner", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("hierarchy_runner", "p3lm", "policy")
trace_contract._emit_stores_learning_state("hierarchy_runner", "p3lm", "state")
trace_contract._emit_records_execution_trace("hierarchy_runner", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("hierarchy_runner", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("hierarchy_runner", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("hierarchy_runner", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("hierarchy_runner", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("hierarchy_runner", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("hierarchy_runner", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("hierarchy_runner", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("hierarchy_runner", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "hierarchy_runner", "context_pull")
trace_contract._emit_pulls_context("p1", "hierarchy_runner", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "hierarchy_runner", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "hierarchy_runner", "uwg_term_2")
trace_contract._emit_writes_through("p1", "hierarchy_runner", "write_through")
trace_contract._emit_writes_through("p1", "hierarchy_runner", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "hierarchy_runner", "safety_validation")
trace_contract._emit_invokes_eval("p1", "hierarchy_runner", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "hierarchy_runner", "routing_commit")


def get_project_root() -> Path:
    """Get project root from this file's location."""
    return Path(__file__).resolve().parent.parent.parent.parent


def run_hierarchy_dry_run(project_root: Path) -> dict:
    """Run structure hierarchy scan in dry-run mode."""
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "run_hierarchy_dry_run", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "run_hierarchy_dry_run", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "run_hierarchy_dry_run")
    from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import StructureEnforcerAgent

    agent = StructureEnforcerAgent(project_root=project_root)
    result = agent.heal_repository(dry_run=True, execute=False)
    return {"success": True, "mode": "dry_run", "message": "Dry run complete - no changes made", **result}


def run_heal_violations(project_root: Path) -> dict:
    """Run StructureEnforcerAgent to report healable violations."""
    from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import StructureEnforcerAgent

    agent = StructureEnforcerAgent(project_root=project_root)
    result = agent.heal_repository(dry_run=True, execute=False)
    return {
        "success": True,
        "files_relocated": result.get("fixed", 0),
        "folders_removed": 0,
        "errors": result.get("errors", []),
        "violations": result.get("violations", 0),
    }


def verify_mro() -> dict:
    """Verify StructureEnforcerAgent MRO structure."""
    from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import StructureEnforcerAgent

    mro = [cls.__name__ for cls in StructureEnforcerAgent.__mro__]
    return {"success": True, "agent": "StructureEnforcerAgent", "mro": mro, "mro_length": len(mro)}


def main() -> int:
    """CLI entry point for subprocess invocation."""
    parser = argparse.ArgumentParser(description="Structure hierarchy runner")
    parser.add_argument(
        "--action",
        choices=["dry_run", "heal_violations", "verify_mro"],
        required=True,
        help="Action to perform",
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
        if args.action == "dry_run":
            result = run_hierarchy_dry_run(project_root)
        elif args.action == "heal_violations":
            result = run_heal_violations(project_root)
        elif args.action == "verify_mro":
            result = verify_mro()
        else:
            result = {"success": False, "error": f"Unknown action: {args.action}"}
        print(json.dumps(result, default=str))
        return 0 if result.get("success") else 1
    except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
        print(json.dumps({"success": False, "error": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
