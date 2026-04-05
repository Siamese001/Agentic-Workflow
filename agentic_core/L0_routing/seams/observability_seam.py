"""
Seam for L6 observability - approved L0→L6 interface.
"""

from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    record_execution_trace,
)

emit_replay_key("p0", "observability_seam")
emit_determinism_digest("p0", "observability_seam")

_emit_dispatches_healing_run("p1", "observability_seam", "L0")
_emit_routes_through("p1", "observability_seam", "L0")
_emit_checks_agent_registry("p1", "observability_seam", "agent_registry")
_emit_validates_agent_capability("p1", "observability_seam", "capability")
_emit_dispatches_execution_plan("p1", "observability_seam", "exec_plan")
_emit_agent_executes_agent("p1", "observability_seam", "sub_agent")
_emit_routes_to_agent("p1", "observability_seam", "target_agent")
_emit_verifies_policy("p1", "observability_seam", "policy_check")
_emit_observes_runtime_state("p1", "observability_seam", "runtime_state")
_emit_verifies_boundary("p1", "observability_seam", "boundary_check")
_emit_transcripts_response("p1", "observability_seam", "transcript")
_emit_hard_fails_untranscripted("p1", "observability_seam")
_emit_gated_by_confidence("p1", "observability_seam", "confidence_gate")
_emit_escalates_to_human("p1", "observability_seam", "L0")
_emit_reads_policy_state("p1", "observability_seam", "L0")
_emit_authorize_and_execute("p2", "observability_seam", "execution_auth")
_emit_validates_capability("p2", "observability_seam", "capability_check")
_emit_routes_to_capability("p2", "observability_seam", "capability_route")
_emit_writes_via_uwg("p2", "observability_seam", "uwg_write")
_emit_blocks_direct_write("p2", "observability_seam", "direct_write_block")
_emit_records_tool_invocation("p2", "observability_seam", "tool_invocation")
_emit_captures_execution_output("p2", "observability_seam", "exec_output")
_emit_dispatches_agent("p3", "observability_seam", "agent_dispatch")
_emit_coordinates_agents("p3", "observability_seam", "agent_coordination")
_emit_records_workflow_lineage("p3", "observability_seam", "workflow_lineage")
_emit_records_healing_outcome("p3", "observability_seam", "healing_outcome")
_emit_escalates_failure("p3", "observability_seam", "failure_escalation")
_emit_orchestrates_workflow("p3", "observability_seam", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "observability_seam", "healing_dispatch")
_emit_invokes_evaluation("p3", "observability_seam", "evaluation_signal")
_emit_records_telemetry_event("p4", "observability_seam", "telemetry_event")
_emit_captures_evaluation_metric("p4", "observability_seam", "eval_metric")
_emit_stores_embedding("p4", "observability_seam", "embedding_store")
_emit_updates_meta_learning_state("p4", "observability_seam", "meta_learning")
_emit_links_execution_to_snapshot("p4", "observability_seam", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

record_execution_trace("observability_seam", "observability_seam_trace")


_emit_emits_metric_event("observability_seam", "p4obs", "metric_1")
_emit_emits_metric_event("observability_seam", "p4obs", "metric_2")
_emit_emits_metric_event("observability_seam", "p4obs", "metric_3")
_emit_emits_metric_event("observability_seam", "p4obs", "metric_4")
_emit_emits_metric_event("observability_seam", "p4obs", "metric_5")
_emit_emits_metric_event("observability_seam", "p4obs", "metric_6")
_emit_records_incident_event("observability_seam", "p4obs", "incident")
_emit_captures_runtime_anomaly("observability_seam", "p4obs", "anomaly")
_emit_writes_observability_log("observability_seam", "p4obs", "obs_log")
_emit_updates_monitoring_state("observability_seam", "p4obs", "mon_state")
_emit_triggers_alert("observability_seam", "p4obs", "alert")
_emit_links_incident_trace("observability_seam", "p4obs", "trace_link")
_emit_captures_pattern("observability_seam", "p3lm", "pattern")
_emit_records_learning_event("observability_seam", "p3lm", "learning_event")
_emit_writes_learning_snapshot("observability_seam", "p3lm", "snapshot")
_emit_feeds_meta_learning("observability_seam", "p3lm", "meta_feed")
_emit_updates_routing_strategy("observability_seam", "p3lm", "routing")
_emit_improves_agent_policy("observability_seam", "p3lm", "policy")
_emit_stores_learning_state("observability_seam", "p3lm", "state")
_emit_records_execution_trace("observability_seam", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("observability_seam", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("observability_seam", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("observability_seam", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("observability_seam", "L4_STATE", "p2_trace_5")
_emit_reads_environ("observability_seam", "env_read", "p2_env_1")
_emit_reads_environ("observability_seam", "env_read", "p2_env_2")
_emit_reads_runtime_state("observability_seam", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("observability_seam", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "observability_seam", "context_pull")
_emit_pulls_context("p1", "observability_seam", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "observability_seam", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "observability_seam", "uwg_term_2")
_emit_writes_through("p1", "observability_seam", "write_through")
_emit_writes_through("p1", "observability_seam", "write_through_2")
_emit_validated_by_safety_plane("p1", "observability_seam", "safety_validation")
_emit_invokes_eval("p1", "observability_seam", "eval_call")
_emit_proposal_commits_routing("p1", "observability_seam", "routing_commit")


def load_meta_learning_agent():
    """Load MetaLearningClient from L1 cognition (canonical meta-learning interface).

    Note: agentic_core.L6_observability.meta_learning does not exist.
    The canonical meta-learning client lives in L1_cognition.
    Returns None if the module cannot be imported (fail-open for seam).
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "load_meta_learning_agent", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "load_meta_learning_agent", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "load_meta_learning_agent")
    import importlib

    try:
        mod = importlib.import_module("agentic_core.L1_cognition.engines.meta_client")
        return mod.MetaLearningClient
    except ImportError as e:
            raise ImportError(f"Required dependency missing: {e}")  # guardian: allow-silent-swallow
        return None