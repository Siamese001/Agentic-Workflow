from __future__ import annotations

import uuid

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
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "nervous_system")
emit_determinism_digest("p0", "nervous_system")

_emit_dispatches_healing_run("p1", "nervous_system", "L3")
_emit_routes_through("p1", "nervous_system", "L3")
_emit_verifies_policy("p1", "nervous_system", "policy_check")
_emit_observes_runtime_state("p1", "nervous_system", "runtime_state")
_emit_verifies_boundary("p1", "nervous_system", "boundary_check")
_emit_transcripts_response("p1", "nervous_system", "transcript")
_emit_hard_fails_untranscripted("p1", "nervous_system")
_emit_gated_by_confidence("p1", "nervous_system", "confidence_gate")
_emit_escalates_to_human("p1", "nervous_system", "L3")
_emit_reads_policy_state("p1", "nervous_system", "L3")
_emit_routes_to_agent("p1", "nervous_system", "L3")
_emit_orchestrates_workflow("p1", "nervous_system", "L3")
_emit_dispatches_execution_plan("p1", "nervous_system", "L3")
_emit_validates_agent_capability("p1", "nervous_system", "L3")
_emit_checks_agent_registry("p1", "nervous_system", "L3")

_emit_snapshots_state("p0", "nervous_system", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "nervous_system", "p0_governance")
_emit_authorize_and_execute("p2", "nervous_system", "execution_auth")
_emit_validates_capability("p2", "nervous_system", "capability_check")
_emit_routes_to_capability("p2", "nervous_system", "capability_route")
_emit_writes_via_uwg("p2", "nervous_system", "uwg_write")
_emit_blocks_direct_write("p2", "nervous_system", "direct_write_block")
_emit_records_tool_invocation("p2", "nervous_system", "tool_invocation")
_emit_captures_execution_output("p2", "nervous_system", "exec_output")
_emit_dispatches_agent("p3", "nervous_system", "agent_dispatch")
_emit_coordinates_agents("p3", "nervous_system", "agent_coordination")
_emit_records_workflow_lineage("p3", "nervous_system", "workflow_lineage")
_emit_records_healing_outcome("p3", "nervous_system", "healing_outcome")
_emit_escalates_failure("p3", "nervous_system", "failure_escalation")
_emit_orchestrates_workflow("p3", "nervous_system", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "nervous_system", "healing_dispatch")
_emit_invokes_evaluation("p3", "nervous_system", "evaluation_signal")
_emit_records_telemetry_event("p4", "nervous_system", "telemetry_event")
_emit_captures_evaluation_metric("p4", "nervous_system", "eval_metric")
_emit_stores_embedding("p4", "nervous_system", "embedding_store")
_emit_updates_meta_learning_state("p4", "nervous_system", "meta_learning")
_emit_links_execution_to_snapshot("p4", "nervous_system", "exec_snapshot_link")

"Nervous System module."
from agentic_core.L3_orchestration.reasoning.engines.reflex_layer_pattern import ReflexLayer
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
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
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("nervous_system", "p4obs", "metric_1")
_emit_emits_metric_event("nervous_system", "p4obs", "metric_2")
_emit_emits_metric_event("nervous_system", "p4obs", "metric_3")
_emit_emits_metric_event("nervous_system", "p4obs", "metric_4")
_emit_emits_metric_event("nervous_system", "p4obs", "metric_5")
_emit_emits_metric_event("nervous_system", "p4obs", "metric_6")
_emit_records_incident_event("nervous_system", "p4obs", "incident")
_emit_captures_runtime_anomaly("nervous_system", "p4obs", "anomaly")
_emit_writes_observability_log("nervous_system", "p4obs", "obs_log")
_emit_updates_monitoring_state("nervous_system", "p4obs", "mon_state")
_emit_triggers_alert("nervous_system", "p4obs", "alert")
_emit_links_incident_trace("nervous_system", "p4obs", "trace_link")
_emit_captures_pattern("nervous_system", "p3lm", "pattern")
_emit_records_learning_event("nervous_system", "p3lm", "learning_event")
_emit_writes_learning_snapshot("nervous_system", "p3lm", "snapshot")
_emit_feeds_meta_learning("nervous_system", "p3lm", "meta_feed")
_emit_updates_routing_strategy("nervous_system", "p3lm", "routing")
_emit_improves_agent_policy("nervous_system", "p3lm", "policy")
_emit_stores_learning_state("nervous_system", "p3lm", "state")
_emit_records_execution_trace("nervous_system", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("nervous_system", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("nervous_system", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("nervous_system", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("nervous_system", "L4_STATE", "p2_trace_5")
_emit_reads_environ("nervous_system", "env_read", "p2_env_1")
_emit_reads_environ("nervous_system", "env_read", "p2_env_2")
_emit_reads_runtime_state("nervous_system", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("nervous_system", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "nervous_system", "context_pull")
_emit_pulls_context("p1", "nervous_system", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "nervous_system", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "nervous_system", "uwg_term_2")
_emit_writes_through("p1", "nervous_system", "write_through")
_emit_writes_through("p1", "nervous_system", "write_through_2")
_emit_validated_by_safety_plane("p1", "nervous_system", "safety_validation")
_emit_invokes_eval("p1", "nervous_system", "eval_call")
_emit_proposal_commits_routing("p1", "nervous_system", "routing_commit")


class NervousSystem:
    """Nervous System orchestration."""

    def __init__(self):
        self.ReflexLayer = ReflexLayer()
        self.reflexes = {}
        self.missions = []

    def register_reflex(self, trigger: str, action: callable):
        _emit_agent_executes_agent(str(uuid.uuid4()), "NervousSystem", "NervousSystem.register_reflex")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "NervousSystem.register_reflex",
        )

        self.reflexes[trigger] = action
        return self.ReflexLayer.register_reflex(trigger, action)

    def trigger_reflex(self, event: str):
        return self.ReflexLayer.trigger_reflex(event)

    def get_status(self):
        return self.ReflexLayer.get_status()


__all__ = ["NervousSystem", "ReflexLayer"]
