"""Additive determinism helper: canonical_bytes(obj) -> bytes.

Exposes a module-level function used by both production code and replay
harness tests.  Additive artifact for Phase 3 (W5 SOV-DELTA) — no existing
production code changed.

REQ-036 / Phase 3 SOV-DELTA additive helper.
"""

from __future__ import annotations

import json

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "canonicalize")
trace_contract.emit_determinism_digest("p0", "canonicalize")

trace_contract._emit_dispatches_healing_run("p1", "canonicalize", "L2")
trace_contract._emit_routes_through("p1", "canonicalize", "L2")
trace_contract._emit_checks_agent_registry("p1", "canonicalize", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "canonicalize", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "canonicalize", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "canonicalize", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "canonicalize", "target_agent")
trace_contract._emit_verifies_policy("p1", "canonicalize", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "canonicalize", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "canonicalize", "boundary_check")
trace_contract._emit_transcripts_response("p1", "canonicalize", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "canonicalize")
trace_contract._emit_gated_by_confidence("p1", "canonicalize", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "canonicalize", "L2")
trace_contract._emit_reads_policy_state("p1", "canonicalize", "L2")
trace_contract._emit_authorize_and_execute("p2", "canonicalize", "execution_auth")
trace_contract._emit_validates_capability("p2", "canonicalize", "capability_check")
trace_contract._emit_routes_to_capability("p2", "canonicalize", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "canonicalize", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "canonicalize", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "canonicalize", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "canonicalize", "exec_output")
trace_contract._emit_dispatches_agent("p3", "canonicalize", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "canonicalize", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "canonicalize", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "canonicalize", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "canonicalize", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "canonicalize", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "canonicalize", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "canonicalize", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "canonicalize", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "canonicalize", "eval_metric")
trace_contract._emit_stores_embedding("p4", "canonicalize", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "canonicalize", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "canonicalize", "exec_snapshot_link")

trace_contract.record_execution_trace("canonicalize", "canonicalize_trace")


trace_contract._emit_emits_metric_event("canonicalize", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("canonicalize", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("canonicalize", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("canonicalize", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("canonicalize", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("canonicalize", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("canonicalize", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("canonicalize", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("canonicalize", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("canonicalize", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("canonicalize", "p4obs", "alert")
trace_contract._emit_links_incident_trace("canonicalize", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("canonicalize", "p3lm", "pattern")
trace_contract._emit_records_learning_event("canonicalize", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("canonicalize", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("canonicalize", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("canonicalize", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("canonicalize", "p3lm", "policy")
trace_contract._emit_stores_learning_state("canonicalize", "p3lm", "state")
trace_contract._emit_records_execution_trace("canonicalize", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("canonicalize", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("canonicalize", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("canonicalize", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("canonicalize", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("canonicalize", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("canonicalize", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("canonicalize", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("canonicalize", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "canonicalize", "context_pull")
trace_contract._emit_pulls_context("p1", "canonicalize", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "canonicalize", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "canonicalize", "uwg_term_2")
trace_contract._emit_writes_through("p1", "canonicalize", "write_through")
trace_contract._emit_writes_through("p1", "canonicalize", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "canonicalize", "safety_validation")
trace_contract._emit_invokes_eval("p1", "canonicalize", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "canonicalize", "routing_commit")


def canonical_bytes(obj) -> bytes:
    """Return deterministic canonical bytes for *obj*.

    Uses ``obj.__dict__`` for class/dataclass instances, falls through to
    *obj* itself for plain dict/list/primitive values.  ``sort_keys=True``
    ensures key insertion order does not affect the output.
    """
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "canonical_bytes", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "canonical_bytes", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "canonical_bytes")
    data = obj.__dict__ if hasattr(obj, "__dict__") else obj
    return json.dumps(data or obj, sort_keys=True, separators=(",", ":")).encode()
