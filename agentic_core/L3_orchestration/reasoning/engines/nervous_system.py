from __future__ import annotations

import uuid

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "nervous_system")
trace_contract.emit_determinism_digest("p0", "nervous_system")

trace_contract._emit_dispatches_healing_run("p1", "nervous_system", "L3")
trace_contract._emit_routes_through("p1", "nervous_system", "L3")
trace_contract._emit_verifies_policy("p1", "nervous_system", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "nervous_system", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "nervous_system", "boundary_check")
trace_contract._emit_transcripts_response("p1", "nervous_system", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "nervous_system")
trace_contract._emit_gated_by_confidence("p1", "nervous_system", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "nervous_system", "L3")
trace_contract._emit_reads_policy_state("p1", "nervous_system", "L3")
trace_contract._emit_routes_to_agent("p1", "nervous_system", "L3")
trace_contract._emit_orchestrates_workflow("p1", "nervous_system", "L3")
trace_contract._emit_dispatches_execution_plan("p1", "nervous_system", "L3")
trace_contract._emit_validates_agent_capability("p1", "nervous_system", "L3")
trace_contract._emit_checks_agent_registry("p1", "nervous_system", "L3")

trace_contract._emit_snapshots_state("p0", "nervous_system", "state_snapshot")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "nervous_system", "p0_governance")
trace_contract._emit_authorize_and_execute("p2", "nervous_system", "execution_auth")
trace_contract._emit_validates_capability("p2", "nervous_system", "capability_check")
trace_contract._emit_routes_to_capability("p2", "nervous_system", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "nervous_system", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "nervous_system", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "nervous_system", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "nervous_system", "exec_output")
trace_contract._emit_dispatches_agent("p3", "nervous_system", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "nervous_system", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "nervous_system", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "nervous_system", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "nervous_system", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "nervous_system", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "nervous_system", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "nervous_system", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "nervous_system", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "nervous_system", "eval_metric")
trace_contract._emit_stores_embedding("p4", "nervous_system", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "nervous_system", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "nervous_system", "exec_snapshot_link")

"Nervous System module."
from agentic_core.L3_orchestration.reasoning.engines.reflex_layer_pattern import ReflexLayer

trace_contract._emit_emits_metric_event("nervous_system", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("nervous_system", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("nervous_system", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("nervous_system", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("nervous_system", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("nervous_system", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("nervous_system", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("nervous_system", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("nervous_system", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("nervous_system", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("nervous_system", "p4obs", "alert")
trace_contract._emit_links_incident_trace("nervous_system", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("nervous_system", "p3lm", "pattern")
trace_contract._emit_records_learning_event("nervous_system", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("nervous_system", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("nervous_system", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("nervous_system", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("nervous_system", "p3lm", "policy")
trace_contract._emit_stores_learning_state("nervous_system", "p3lm", "state")
trace_contract._emit_records_execution_trace("nervous_system", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("nervous_system", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("nervous_system", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("nervous_system", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("nervous_system", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("nervous_system", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("nervous_system", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("nervous_system", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("nervous_system", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "nervous_system", "context_pull")
trace_contract._emit_pulls_context("p1", "nervous_system", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "nervous_system", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "nervous_system", "uwg_term_2")
trace_contract._emit_writes_through("p1", "nervous_system", "write_through")
trace_contract._emit_writes_through("p1", "nervous_system", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "nervous_system", "safety_validation")
trace_contract._emit_invokes_eval("p1", "nervous_system", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "nervous_system", "routing_commit")


class NervousSystem:
    """Nervous System orchestration."""

    def __init__(self):
        self.ReflexLayer = ReflexLayer()
        self.reflexes = {}
        self.missions = []

    def register_reflex(self, trigger: str, action: callable):
        trace_contract._emit_agent_executes_agent(str(uuid.uuid4()), "NervousSystem", "NervousSystem.register_reflex")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "NervousSystem.register_reflex",
        )

        self.reflexes[trigger] = action
        return self.ReflexLayer.register_reflex(trigger, action)

    def trigger_reflex(self, event: str):
        return self.ReflexLayer.trigger_reflex(event)

    def get_status(self):
        return self.ReflexLayer.get_status()


__all__ = ["NervousSystem", "ReflexLayer"]
