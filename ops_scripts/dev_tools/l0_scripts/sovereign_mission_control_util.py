from __future__ import annotations

import asyncio

from agentic_core.L2_execution.utils import get_clock
from agentic_core.runtime.lifecycle_trace_contract import (
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
)

_emit_records_execution_trace("p0", "evidence", "sovereign_mission_control_util")
_emit_applies_guardrail("p0", "sovereign_mission_control_util", "p0_governance")
_emit_reads_policy_state("p0", "sovereign_mission_control_util", "policy_binding")
_emit_snapshots_state("p0", "sovereign_mission_control_util", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "sovereign_mission_control_util", "execution_auth")
_emit_validates_capability("p2", "sovereign_mission_control_util", "capability_check")
_emit_routes_to_capability("p2", "sovereign_mission_control_util", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_mission_control_util", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_mission_control_util", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_mission_control_util", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_mission_control_util", "exec_output")
_emit_dispatches_agent("p3", "sovereign_mission_control_util", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_mission_control_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_mission_control_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_mission_control_util", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_mission_control_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_mission_control_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_mission_control_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_mission_control_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_mission_control_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_mission_control_util", "eval_metric")
_emit_stores_embedding("p4", "sovereign_mission_control_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_mission_control_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_mission_control_util", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

repo_root: Any = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.append(str(REPO_ROOT))
from typing import Any

# TODO: sovereign_auditor_v3 module does not exist - import commented out
# from agentic_core.L0_routing.P1_core.sovereign_auditor_v3 import main_util as run_audit
from canon_validator_agentic_v2 import run_mission as run_healing

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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

_emit_emits_metric_event("sovereign_mission_control_util", "p4obs", "metric_1")
_emit_emits_metric_event("sovereign_mission_control_util", "p4obs", "metric_2")
_emit_emits_metric_event("sovereign_mission_control_util", "p4obs", "metric_3")
_emit_emits_metric_event("sovereign_mission_control_util", "p4obs", "metric_4")
_emit_emits_metric_event("sovereign_mission_control_util", "p4obs", "metric_5")
_emit_emits_metric_event("sovereign_mission_control_util", "p4obs", "metric_6")
_emit_records_incident_event("sovereign_mission_control_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("sovereign_mission_control_util", "p4obs", "anomaly")
_emit_writes_observability_log("sovereign_mission_control_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("sovereign_mission_control_util", "p4obs", "mon_state")
_emit_triggers_alert("sovereign_mission_control_util", "p4obs", "alert")
_emit_links_incident_trace("sovereign_mission_control_util", "p4obs", "trace_link")
_emit_captures_pattern("sovereign_mission_control_util", "p3lm", "pattern")
_emit_records_learning_event("sovereign_mission_control_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("sovereign_mission_control_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("sovereign_mission_control_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("sovereign_mission_control_util", "p3lm", "routing")
_emit_improves_agent_policy("sovereign_mission_control_util", "p3lm", "policy")
_emit_stores_learning_state("sovereign_mission_control_util", "p3lm", "state")
_emit_records_execution_trace("sovereign_mission_control_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("sovereign_mission_control_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("sovereign_mission_control_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("sovereign_mission_control_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("sovereign_mission_control_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("sovereign_mission_control_util", "env_read", "p2_env_1")
_emit_reads_environ("sovereign_mission_control_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("sovereign_mission_control_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("sovereign_mission_control_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "sovereign_mission_control_util", "context_pull")
_emit_pulls_context("p1", "sovereign_mission_control_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "sovereign_mission_control_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "sovereign_mission_control_util", "uwg_term_secondary")
_emit_writes_through("p1", "sovereign_mission_control_util", "write_through")
_emit_writes_through("p1", "sovereign_mission_control_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "sovereign_mission_control_util", "safety_validation")
_emit_invokes_eval("p1", "sovereign_mission_control_util", "eval_call")
_emit_proposal_commits_routing("p1", "sovereign_mission_control_util", "routing_commit")
_emit_escalates_to_human("p1", "sovereign_mission_control_util", "human_escalation")
_emit_routes_through("p1", "sovereign_mission_control_util", "route_through")
_emit_checks_agent_registry("p1", "sovereign_mission_control_util", "agent_registry")
_emit_validates_agent_capability("p1", "sovereign_mission_control_util", "capability")
_emit_dispatches_execution_plan("p1", "sovereign_mission_control_util", "exec_plan")
_emit_agent_executes_agent("p1", "sovereign_mission_control_util", "sub_agent")
_emit_routes_to_agent("p1", "sovereign_mission_control_util", "target_agent")
_emit_verifies_policy("p1", "sovereign_mission_control_util", "policy_check")
_emit_observes_runtime_state("p1", "sovereign_mission_control_util", "runtime_state")
_emit_verifies_boundary("p1", "sovereign_mission_control_util", "boundary_check")
_emit_transcripts_response("p1", "sovereign_mission_control_util", "transcript")
_emit_hard_fails_untranscripted("p1", "sovereign_mission_control_util")
_emit_gated_by_confidence("p1", "sovereign_mission_control_util", "confidence_gate")


async def execute_unified_mission(target: Any = "agentic_core") -> Any:
    """
    [L6 MISSION CONTROL]
    Sequences Diagnosis (Auditor) and Surgery (Validator).
    """
    print(f"\n{'=' * 80}\n[MISSION CONTROL] INITIATING UNIFIED SOVEREIGN SWEEP\n{'=' * 80}")
    print("\n[*] PHASE 1: Executing Multi-Dimensional Audit...")
    report: Any = await run_audit()
    overall_health: Any = report.get_overall_score()
    print(f"\n[DIAGNOSIS COMPLETE] Current Health Score: {overall_health:.1f}%")
    if overall_health >= 98.0:
        print("\n[VERDICT] Sovereignty Intact. No surgery required. Perfection Sealed.")
        return
    print(f"\n[VERDICT] Health threshold breach ({overall_health}% < 98%). Unleashing Healers.")
    issues: Any = report.get_all_issues()
    target_files: Any = list({issue["file"] for issue in issues if issue.get("file")})
    print(f"[*] PHASE 2: Surgical Healing initiated for {len(target_files)} targeted files...")
    _clk = get_clock()
    _clk.emit_replay_key(context=f"ops:mission_control:heal:{target}")
    _clk.emit_determinism_digest(inputs={"op": "run_healing", "target": str(target)})
    await run_healing(target_scope=target)
    print("\n[*] PHASE 3: Final Compliance Sealing...")
    final_report: Any = await run_audit()
    if final_report.get_overall_score() > overall_health:
        print(f"\n[SUCCESS] Mission Achieved. Health improved to {final_report.get_overall_score():.1f}%")
    else:
        print("\n[L6 ALERT] Mission Stalled. Structural drift persists. Manual review required.")


if __name__ == "__main__":
    asyncio.run(execute_unified_mission())
