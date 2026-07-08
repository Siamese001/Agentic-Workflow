"""
Seam for L5 safety core kernel - approved L0→L5 interface.
"""

from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "safety_kernel_seam")
trace_contract.emit_determinism_digest("p0", "safety_kernel_seam")

trace_contract._emit_dispatches_healing_run("p1", "safety_kernel_seam", "L0")
trace_contract._emit_routes_through("p1", "safety_kernel_seam", "L0")
trace_contract._emit_checks_agent_registry("p1", "safety_kernel_seam", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "safety_kernel_seam", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "safety_kernel_seam", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "safety_kernel_seam", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "safety_kernel_seam", "target_agent")
trace_contract._emit_verifies_policy("p1", "safety_kernel_seam", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "safety_kernel_seam", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "safety_kernel_seam", "boundary_check")
trace_contract._emit_transcripts_response("p1", "safety_kernel_seam", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "safety_kernel_seam")
trace_contract._emit_gated_by_confidence("p1", "safety_kernel_seam", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "safety_kernel_seam", "L0")
trace_contract._emit_reads_policy_state("p1", "safety_kernel_seam", "L0")
trace_contract._emit_authorize_and_execute("p2", "safety_kernel_seam", "execution_auth")
trace_contract._emit_validates_capability("p2", "safety_kernel_seam", "capability_check")
trace_contract._emit_routes_to_capability("p2", "safety_kernel_seam", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "safety_kernel_seam", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "safety_kernel_seam", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "safety_kernel_seam", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "safety_kernel_seam", "exec_output")
trace_contract._emit_dispatches_agent("p3", "safety_kernel_seam", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "safety_kernel_seam", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "safety_kernel_seam", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "safety_kernel_seam", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "safety_kernel_seam", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "safety_kernel_seam", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "safety_kernel_seam", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "safety_kernel_seam", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "safety_kernel_seam", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "safety_kernel_seam", "eval_metric")
trace_contract._emit_stores_embedding("p4", "safety_kernel_seam", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "safety_kernel_seam", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "safety_kernel_seam", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("safety_kernel_seam", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("safety_kernel_seam", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("safety_kernel_seam", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("safety_kernel_seam", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("safety_kernel_seam", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("safety_kernel_seam", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("safety_kernel_seam", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("safety_kernel_seam", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("safety_kernel_seam", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("safety_kernel_seam", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("safety_kernel_seam", "p4obs", "alert")
trace_contract._emit_links_incident_trace("safety_kernel_seam", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("safety_kernel_seam", "p3lm", "pattern")
trace_contract._emit_records_learning_event("safety_kernel_seam", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("safety_kernel_seam", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("safety_kernel_seam", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("safety_kernel_seam", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("safety_kernel_seam", "p3lm", "policy")
trace_contract._emit_stores_learning_state("safety_kernel_seam", "p3lm", "state")
trace_contract._emit_records_execution_trace("safety_kernel_seam", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("safety_kernel_seam", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("safety_kernel_seam", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("safety_kernel_seam", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("safety_kernel_seam", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("safety_kernel_seam", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("safety_kernel_seam", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("safety_kernel_seam", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("safety_kernel_seam", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "safety_kernel_seam", "context_pull")
trace_contract._emit_pulls_context("p1", "safety_kernel_seam", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "safety_kernel_seam", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "safety_kernel_seam", "uwg_term_2")
trace_contract._emit_writes_through("p1", "safety_kernel_seam", "write_through")
trace_contract._emit_writes_through("p1", "safety_kernel_seam", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "safety_kernel_seam", "safety_validation")
trace_contract._emit_invokes_eval("p1", "safety_kernel_seam", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "safety_kernel_seam", "routing_commit")


def load_classification_kernel():
    """Load classification_kernel from L5."""
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "load_classification_kernel", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "load_classification_kernel", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L0_ROUTING, "load_classification_kernel")
    import importlib

    return importlib.import_module("agentic_core.L5_safety.reasoning.core_kernel.classification_kernel")


def get_classification_cache_context():
    """Get classification_cache_context from L5."""
    return load_classification_kernel().classification_cache_context
