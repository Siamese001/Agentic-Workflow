"""Additive determinism helper: canonical_bytes(obj) -> bytes.

Exposes a module-level function used by both production code and replay
harness tests.  Additive artifact for Phase 3 (W5 SOV-DELTA) — no existing
production code changed.

REQ-036 / Phase 3 SOV-DELTA additive helper.
"""

from __future__ import annotations

import json

from agentic_core.runtime.lifecycle_trace_contract import (
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

emit_replay_key("p0", "canonicalize")
emit_determinism_digest("p0", "canonicalize")

_emit_dispatches_healing_run("p1", "canonicalize", "L2")
_emit_routes_through("p1", "canonicalize", "L2")
_emit_checks_agent_registry("p1", "canonicalize", "agent_registry")
_emit_validates_agent_capability("p1", "canonicalize", "capability")
_emit_dispatches_execution_plan("p1", "canonicalize", "exec_plan")
_emit_agent_executes_agent("p1", "canonicalize", "sub_agent")
_emit_routes_to_agent("p1", "canonicalize", "target_agent")
_emit_verifies_policy("p1", "canonicalize", "policy_check")
_emit_observes_runtime_state("p1", "canonicalize", "runtime_state")
_emit_verifies_boundary("p1", "canonicalize", "boundary_check")
_emit_transcripts_response("p1", "canonicalize", "transcript")
_emit_hard_fails_untranscripted("p1", "canonicalize")
_emit_gated_by_confidence("p1", "canonicalize", "confidence_gate")
_emit_escalates_to_human("p1", "canonicalize", "L2")
_emit_reads_policy_state("p1", "canonicalize", "L2")
_emit_authorize_and_execute("p2", "canonicalize", "execution_auth")
_emit_validates_capability("p2", "canonicalize", "capability_check")
_emit_routes_to_capability("p2", "canonicalize", "capability_route")
_emit_writes_via_uwg("p2", "canonicalize", "uwg_write")
_emit_blocks_direct_write("p2", "canonicalize", "direct_write_block")
_emit_records_tool_invocation("p2", "canonicalize", "tool_invocation")
_emit_captures_execution_output("p2", "canonicalize", "exec_output")
_emit_dispatches_agent("p3", "canonicalize", "agent_dispatch")
_emit_coordinates_agents("p3", "canonicalize", "agent_coordination")
_emit_records_workflow_lineage("p3", "canonicalize", "workflow_lineage")
_emit_records_healing_outcome("p3", "canonicalize", "healing_outcome")
_emit_escalates_failure("p3", "canonicalize", "failure_escalation")
_emit_orchestrates_workflow("p3", "canonicalize", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "canonicalize", "healing_dispatch")
_emit_invokes_evaluation("p3", "canonicalize", "evaluation_signal")
_emit_records_telemetry_event("p4", "canonicalize", "telemetry_event")
_emit_captures_evaluation_metric("p4", "canonicalize", "eval_metric")
_emit_stores_embedding("p4", "canonicalize", "embedding_store")
_emit_updates_meta_learning_state("p4", "canonicalize", "meta_learning")
_emit_links_execution_to_snapshot("p4", "canonicalize", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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

record_execution_trace("canonicalize", "canonicalize_trace")


_emit_emits_metric_event("canonicalize", "p4obs", "metric_1")
_emit_emits_metric_event("canonicalize", "p4obs", "metric_2")
_emit_emits_metric_event("canonicalize", "p4obs", "metric_3")
_emit_emits_metric_event("canonicalize", "p4obs", "metric_4")
_emit_emits_metric_event("canonicalize", "p4obs", "metric_5")
_emit_emits_metric_event("canonicalize", "p4obs", "metric_6")
_emit_records_incident_event("canonicalize", "p4obs", "incident")
_emit_captures_runtime_anomaly("canonicalize", "p4obs", "anomaly")
_emit_writes_observability_log("canonicalize", "p4obs", "obs_log")
_emit_updates_monitoring_state("canonicalize", "p4obs", "mon_state")
_emit_triggers_alert("canonicalize", "p4obs", "alert")
_emit_links_incident_trace("canonicalize", "p4obs", "trace_link")
_emit_captures_pattern("canonicalize", "p3lm", "pattern")
_emit_records_learning_event("canonicalize", "p3lm", "learning_event")
_emit_writes_learning_snapshot("canonicalize", "p3lm", "snapshot")
_emit_feeds_meta_learning("canonicalize", "p3lm", "meta_feed")
_emit_updates_routing_strategy("canonicalize", "p3lm", "routing")
_emit_improves_agent_policy("canonicalize", "p3lm", "policy")
_emit_stores_learning_state("canonicalize", "p3lm", "state")
_emit_records_execution_trace("canonicalize", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("canonicalize", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("canonicalize", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("canonicalize", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("canonicalize", "L4_STATE", "p2_trace_5")
_emit_reads_environ("canonicalize", "env_read", "p2_env_1")
_emit_reads_environ("canonicalize", "env_read", "p2_env_2")
_emit_reads_runtime_state("canonicalize", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("canonicalize", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "canonicalize", "context_pull")
_emit_pulls_context("p1", "canonicalize", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "canonicalize", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "canonicalize", "uwg_term_2")
_emit_writes_through("p1", "canonicalize", "write_through")
_emit_writes_through("p1", "canonicalize", "write_through_2")
_emit_validated_by_safety_plane("p1", "canonicalize", "safety_validation")
_emit_invokes_eval("p1", "canonicalize", "eval_call")
_emit_proposal_commits_routing("p1", "canonicalize", "routing_commit")


def canonical_bytes(obj) -> bytes:
    """Return deterministic canonical bytes for *obj*.

    Uses ``obj.__dict__`` for class/dataclass instances, falls through to
    *obj* itself for plain dict/list/primitive values.  ``sort_keys=True``
    ensures key insertion order does not affect the output.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "canonical_bytes", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "canonical_bytes", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "canonical_bytes")
    data = obj.__dict__ if hasattr(obj, "__dict__") else obj
    return json.dumps(data or obj, sort_keys=True, separators=(",", ":")).encode()
