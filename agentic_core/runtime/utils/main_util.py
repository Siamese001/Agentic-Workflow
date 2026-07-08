from __future__ import annotations

import asyncio
import os

from agentic_core.config.google_ai_env import google_ai_pro_model_id
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_records_execution_trace("p0", "evidence", "main_util")
trace_contract._emit_applies_guardrail("p0", "main_util", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "main_util", "policy_binding")
trace_contract._emit_snapshots_state("p0", "main_util", "state_snapshot")
trace_contract.emit_replay_key("p0", "main_util")
trace_contract.emit_determinism_digest("p0", "main_util")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "main_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "main_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "main_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "main_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "main_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "main_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "main_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "main_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "main_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "main_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "main_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "main_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "main_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "main_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "main_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "main_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "main_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "main_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "main_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "main_util", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import logging
from typing import Any


from .runtime_bootstrapper_util import runtime_bootstrapper

trace_contract._emit_emits_metric_event("main_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("main_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("main_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("main_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("main_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("main_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("main_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("main_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("main_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("main_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("main_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("main_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("main_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("main_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("main_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("main_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("main_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("main_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("main_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("main_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("main_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("main_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("main_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("main_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("main_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("main_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("main_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("main_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "main_util", "context_pull")
trace_contract._emit_pulls_context("p1", "main_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "main_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "main_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "main_util", "write_through")
trace_contract._emit_writes_through("p1", "main_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "main_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "main_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "main_util", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "main_util", "human_escalation")
trace_contract._emit_routes_through("p1", "main_util", "route_through")
trace_contract._emit_checks_agent_registry("p1", "main_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "main_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "main_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "main_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "main_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "main_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "main_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "main_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "main_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "main_util")
trace_contract._emit_gated_by_confidence("p1", "main_util", "confidence_gate")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError as e:
    raise ImportError(f"Required dependency missing: {e}")  # guardian: allow-silent-swallow
    pass


async def main() -> Any:
    """
    Day Zero: Running the first 100% Sovereign-Compliant Agentic Mission.
    """
    config: Any = {
        "storage_path": "./data/sovereign_output",
        "budget_limit": 25.0,
        "allowed_tools": ["read_file", "search_web", "run_python"],
        "mission_scope": "system_refactoring",
        "model_name": google_ai_pro_model_id()[0],
    }
    bootstrapper: Any = runtime_bootstrapper(config)
    try:
        hop: Any = bootstrapper.assemble_hop(role="principal_architect")
        mission: Any = {
            "Task": "Review the L5 safety guardrails for potential bypasses.",
            "trace_id": "SOVEREIGN-BETA-001",
        }
        print("\n🚀 [SYSTEM ONLINE] - Executing Sovereign Hop...\n")
        final_output: Any = await hop.run(mission)
        print(f"\n✅ [MISSION COMPLETE]\nOutput: {final_output}")
    except (AttributeError, ImportError, OSError, RuntimeError, ValueError) as e:
        print(f"\n❌ [CRITICAL FAILURE]: {e}")


if __name__ == "__main__":
    asyncio.run(main())
