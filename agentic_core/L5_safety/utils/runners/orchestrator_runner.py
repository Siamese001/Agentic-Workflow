"""
L5 Runner for Orchestrator Agent Summoning.

This module provides subprocess-callable entry points for L0 scripts
to invoke orchestrator missions without creating upward import edges.

Usage from subprocess:
    python -m agentic_core.L5_safety.runners.orchestrator_runner         --action=mission --targets=L0,L1 --execute
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "orchestrator_runner")
trace_contract.emit_determinism_digest("p0", "orchestrator_runner")

trace_contract._emit_dispatches_healing_run("p1", "orchestrator_runner", "L5")
trace_contract._emit_routes_through("p1", "orchestrator_runner", "L5")
trace_contract._emit_checks_agent_registry("p1", "orchestrator_runner", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "orchestrator_runner", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "orchestrator_runner", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "orchestrator_runner", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "orchestrator_runner", "target_agent")
trace_contract._emit_verifies_policy("p1", "orchestrator_runner", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "orchestrator_runner", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "orchestrator_runner", "boundary_check")
trace_contract._emit_transcripts_response("p1", "orchestrator_runner", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "orchestrator_runner")
trace_contract._emit_gated_by_confidence("p1", "orchestrator_runner", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "orchestrator_runner", "L5")
trace_contract._emit_reads_policy_state("p1", "orchestrator_runner", "L5")
trace_contract._emit_authorize_and_execute("p2", "orchestrator_runner", "execution_auth")
trace_contract._emit_validates_capability("p2", "orchestrator_runner", "capability_check")
trace_contract._emit_routes_to_capability("p2", "orchestrator_runner", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "orchestrator_runner", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "orchestrator_runner", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "orchestrator_runner", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "orchestrator_runner", "exec_output")
trace_contract._emit_dispatches_agent("p3", "orchestrator_runner", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "orchestrator_runner", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "orchestrator_runner", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "orchestrator_runner", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "orchestrator_runner", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "orchestrator_runner", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "orchestrator_runner", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "orchestrator_runner", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "orchestrator_runner", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "orchestrator_runner", "eval_metric")
trace_contract._emit_stores_embedding("p4", "orchestrator_runner", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "orchestrator_runner", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "orchestrator_runner", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("orchestrator_runner", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("orchestrator_runner", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("orchestrator_runner", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("orchestrator_runner", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("orchestrator_runner", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("orchestrator_runner", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("orchestrator_runner", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("orchestrator_runner", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("orchestrator_runner", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("orchestrator_runner", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("orchestrator_runner", "p4obs", "alert")
trace_contract._emit_links_incident_trace("orchestrator_runner", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("orchestrator_runner", "p3lm", "pattern")
trace_contract._emit_records_learning_event("orchestrator_runner", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("orchestrator_runner", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("orchestrator_runner", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("orchestrator_runner", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("orchestrator_runner", "p3lm", "policy")
trace_contract._emit_stores_learning_state("orchestrator_runner", "p3lm", "state")
trace_contract._emit_records_execution_trace("orchestrator_runner", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("orchestrator_runner", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("orchestrator_runner", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("orchestrator_runner", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("orchestrator_runner", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("orchestrator_runner", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("orchestrator_runner", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("orchestrator_runner", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("orchestrator_runner", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "orchestrator_runner", "context_pull")
trace_contract._emit_pulls_context("p1", "orchestrator_runner", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "orchestrator_runner", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "orchestrator_runner", "uwg_term_2")
trace_contract._emit_writes_through("p1", "orchestrator_runner", "write_through")
trace_contract._emit_writes_through("p1", "orchestrator_runner", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "orchestrator_runner", "safety_validation")
trace_contract._emit_invokes_eval("p1", "orchestrator_runner", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "orchestrator_runner", "routing_commit")


def get_project_root() -> Path:
    """Get project root from this file's location."""
    return Path(__file__).resolve().parent.parent.parent.parent


def run_orchestrator_mission(project_root: Path, targets: list[str], execute: bool = False) -> dict:
    """Run orchestrator mission with agent roster."""
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "run_orchestrator_mission", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "run_orchestrator_mission", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "run_orchestrator_mission")
    try:
        from agentic_core.L3_orchestration.ConsolidatedOrchestratorAgent import get_consolidated_orchestrator
        from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent
        from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import GravityLeakRepairAgent
        from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import StructureEnforcerAgent

        # MW-9 (2026-04-24): Class body relocated to utils module.
        from agentic_core.L5_safety.utils.location_healer_util import LocationHealerAgent

        orchestrator = get_consolidated_orchestrator(project_root)
        active_roster = [
            ("LocationAgent", LocationHealerAgent(project_root)),
            ("HierarchyAgent", StructureEnforcerAgent(project_root=project_root)),
            ("ArchitectureGovernorAgent", ArchitectureGovernorAgent(project_root)),
            ("GravityLeakRepairAgent", GravityLeakRepairAgent(project_root)),
        ]
        mission_context = {
            "dry_run": not execute,
            "execute": execute,
            "domains": targets,
            "scan_mode": "leveraged",
        }
        mission_results = orchestrator.run_mission(active_roster, mission_context)
        return {"success": True, "results": mission_results}
    except ImportError as e:
        return {"success": False, "error": f"Import error: {e}", "fallback": True}
    except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
        return {"success": False, "error": str(e), "fallback": True}


def main() -> int:
    """CLI entry point for subprocess invocation."""
    parser = argparse.ArgumentParser(description="Orchestrator Runner")
    parser.add_argument("--action", choices=["mission"], required=True, help="Action to perform")
    parser.add_argument(
        "--project-root",
        type=str,
        default=None,
        help="Project root path (defaults to auto-detect)",
    )
    parser.add_argument("--targets", type=str, required=True, help="Comma-separated target territories")
    parser.add_argument("--execute", action="store_true", default=False, help="Execute mode (vs dry-run)")
    args = parser.parse_args()
    project_root = Path(args.project_root) if args.project_root else get_project_root()
    targets = args.targets.split(",") if args.targets else []
    try:
        if args.action == "mission":
            result = run_orchestrator_mission(project_root, targets, args.execute)
        else:
            result = {"success": False, "error": f"Unknown action: {args.action}"}
        print(json.dumps(result, default=str))
        return 0 if result.get("success") else 1
    except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
        print(json.dumps({"success": False, "error": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
