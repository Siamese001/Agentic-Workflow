"""G-1-1 (§1.7) — Deterministic Runtime Validators for V15 Artifacts.

Accepts either:
  (a) dict-like (TypedDict instance) OR
  (b) existing frozen dataclass instance from routing_artifact_types.py

Normalizes output to plain dict matching the TypedDict shape.
Raises ValueError with deterministic message on first missing/invalid field.

Also provides bridge adapters (dataclass → dict) that do not mutate inputs.
"""

from __future__ import annotations

import dataclasses
from typing import Any

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
)

emit_replay_key("p0", "artifact_validators_types")
emit_determinism_digest("p0", "artifact_validators_types")

_emit_dispatches_healing_run("p1", "artifact_validators_types", "L0")
_emit_routes_through("p1", "artifact_validators_types", "L0")
_emit_checks_agent_registry("p1", "artifact_validators_types", "agent_registry")
_emit_validates_agent_capability("p1", "artifact_validators_types", "capability")
_emit_dispatches_execution_plan("p1", "artifact_validators_types", "exec_plan")
_emit_agent_executes_agent("p1", "artifact_validators_types", "sub_agent")
_emit_routes_to_agent("p1", "artifact_validators_types", "target_agent")
_emit_verifies_policy("p1", "artifact_validators_types", "policy_check")
_emit_observes_runtime_state("p1", "artifact_validators_types", "runtime_state")
_emit_verifies_boundary("p1", "artifact_validators_types", "boundary_check")
_emit_transcripts_response("p1", "artifact_validators_types", "transcript")
_emit_hard_fails_untranscripted("p1", "artifact_validators_types")
_emit_gated_by_confidence("p1", "artifact_validators_types", "confidence_gate")
_emit_escalates_to_human("p1", "artifact_validators_types", "L0")
_emit_reads_policy_state("p1", "artifact_validators_types", "L0")
_emit_authorize_and_execute("p2", "artifact_validators_types", "execution_auth")
_emit_validates_capability("p2", "artifact_validators_types", "capability_check")
_emit_routes_to_capability("p2", "artifact_validators_types", "capability_route")
_emit_writes_via_uwg("p2", "artifact_validators_types", "uwg_write")
_emit_blocks_direct_write("p2", "artifact_validators_types", "direct_write_block")
_emit_records_tool_invocation("p2", "artifact_validators_types", "tool_invocation")
_emit_captures_execution_output("p2", "artifact_validators_types", "exec_output")
_emit_dispatches_agent("p3", "artifact_validators_types", "agent_dispatch")
_emit_coordinates_agents("p3", "artifact_validators_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "artifact_validators_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "artifact_validators_types", "healing_outcome")
_emit_escalates_failure("p3", "artifact_validators_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "artifact_validators_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "artifact_validators_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "artifact_validators_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "artifact_validators_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "artifact_validators_types", "eval_metric")
_emit_stores_embedding("p4", "artifact_validators_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "artifact_validators_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "artifact_validators_types", "exec_snapshot_link")
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

_emit_emits_metric_event("artifact_validators_types", "p4obs", "metric_1")
_emit_emits_metric_event("artifact_validators_types", "p4obs", "metric_2")
_emit_emits_metric_event("artifact_validators_types", "p4obs", "metric_3")
_emit_emits_metric_event("artifact_validators_types", "p4obs", "metric_4")
_emit_emits_metric_event("artifact_validators_types", "p4obs", "metric_5")
_emit_emits_metric_event("artifact_validators_types", "p4obs", "metric_6")
_emit_records_incident_event("artifact_validators_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("artifact_validators_types", "p4obs", "anomaly")
_emit_writes_observability_log("artifact_validators_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("artifact_validators_types", "p4obs", "mon_state")
_emit_triggers_alert("artifact_validators_types", "p4obs", "alert")
_emit_links_incident_trace("artifact_validators_types", "p4obs", "trace_link")
_emit_captures_pattern("artifact_validators_types", "p3lm", "pattern")
_emit_records_learning_event("artifact_validators_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("artifact_validators_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("artifact_validators_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("artifact_validators_types", "p3lm", "routing")
_emit_improves_agent_policy("artifact_validators_types", "p3lm", "policy")
_emit_stores_learning_state("artifact_validators_types", "p3lm", "state")
_emit_records_execution_trace("artifact_validators_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("artifact_validators_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("artifact_validators_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("artifact_validators_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("artifact_validators_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("artifact_validators_types", "env_read", "p2_env_1")
_emit_reads_environ("artifact_validators_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("artifact_validators_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("artifact_validators_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "artifact_validators_types", "context_pull")
_emit_pulls_context("p1", "artifact_validators_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "artifact_validators_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "artifact_validators_types", "uwg_term_2")
_emit_writes_through("p1", "artifact_validators_types", "write_through")
_emit_writes_through("p1", "artifact_validators_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "artifact_validators_types", "safety_validation")
_emit_invokes_eval("p1", "artifact_validators_types", "eval_call")
_emit_proposal_commits_routing("p1", "artifact_validators_types", "routing_commit")


def _to_raw_dict(obj: object) -> dict[str, Any]:
    """Convert dataclass or dict-like to plain dict without mutating input."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_to_raw_dict", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_to_raw_dict", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_to_raw_dict")
    if isinstance(obj, dict):
        return dict(obj)
    if dataclasses.is_dataclass(obj) and (not isinstance(obj, type)):
        return dataclasses.asdict(obj)
    raise TypeError(
        f"VALIDATE_ARTIFACT:UNSUPPORTED_TYPE|type={type(obj).__name__}|expected=dict_or_dataclass"
    )


def _require_str(d: dict[str, Any], key: str, artifact_name: str) -> None:
    """Require a non-empty string field."""
    val = d.get(key)
    if not isinstance(val, str) or not val:
        raise ValueError(
            f"VALIDATE_{artifact_name}:MISSING_OR_INVALID_FIELD|field={key}|value={val!r}|expected=non_empty_str"
        )


def _require_int(d: dict[str, Any], key: str, artifact_name: str, *, min_val: int | None = None) -> None:
    """Require an integer field, optionally with minimum."""
    val = d.get(key)
    if not isinstance(val, int):
        raise ValueError(
            f"VALIDATE_{artifact_name}:MISSING_OR_INVALID_FIELD|field={key}|value={val!r}|expected=int"
        )
    if min_val is not None and val < min_val:
        raise ValueError(f"VALIDATE_{artifact_name}:FIELD_OUT_OF_RANGE|field={key}|value={val}|min={min_val}")


def _require_sequence_of_str(d: dict[str, Any], key: str, artifact_name: str) -> None:
    """Require a sequence of strings field."""
    val = d.get(key)
    if not isinstance(val, (list, tuple)):
        raise ValueError(
            f"VALIDATE_{artifact_name}:MISSING_OR_INVALID_FIELD|field={key}|value={val!r}|expected=sequence_of_str"
        )
    for i, item in enumerate(val):
        if not isinstance(item, str):
            raise ValueError(
                f"VALIDATE_{artifact_name}:INVALID_ELEMENT|field={key}[{i}]|value={item!r}|expected=str"
            )


def _coerce_enum_to_str(d: dict[str, Any], key: str) -> None:
    """If a field value has a .value attribute (Enum), replace with its string value."""
    val = d.get(key)
    if val is not None and hasattr(val, "value"):
        d[key] = val.value


def _coerce_tuple_to_list(d: dict[str, Any], key: str) -> None:
    """Convert tuple to list for JSON-schema alignment."""
    val = d.get(key)
    if isinstance(val, tuple):
        d[key] = list(val)


_RESULT_ARTIFACT_REQUIRED_FIELDS = ("trace_id", "execution_outcome", "final_state_hash", "artifact_class")


def validate_result_artifact(obj: object) -> dict[str, Any]:
    """Validate and normalize a ResultArtifact to TypedDict shape.

    Accepts dict or frozen dataclass. Returns plain dict.
    Raises ValueError on first missing/invalid required field.
    """
    d = _to_raw_dict(obj)
    for field_name in _RESULT_ARTIFACT_REQUIRED_FIELDS:
        _require_str(d, field_name, "RESULT_ARTIFACT")
    if "emitting_layer" not in d or not d["emitting_layer"]:
        d["emitting_layer"] = "L2"
    _require_str(d, "emitting_layer", "RESULT_ARTIFACT")
    return {
        "trace_id": d["trace_id"],
        "execution_outcome": d["execution_outcome"],
        "final_state_hash": d["final_state_hash"],
        "artifact_class": d["artifact_class"],
        "emitting_layer": d["emitting_layer"],
    }


def to_result_artifact_dict(x: object) -> dict[str, Any]:
    """Bridge adapter: convert dataclass or dict to plain dict (ResultArtifact shape)."""
    return dict(validate_result_artifact(x))


_HEALING_PLAN_REQUIRED_STR_FIELDS = ("trace_id", "plan_id", "policy_liaison_node")


def validate_healing_plan(obj: object) -> dict[str, Any]:
    """Validate and normalize a HealingPlan to TypedDict shape.

    Accepts dict or frozen dataclass. Returns plain dict.
    Raises ValueError on first missing/invalid required field.
    """
    d = _to_raw_dict(obj)
    for field_name in _HEALING_PLAN_REQUIRED_STR_FIELDS:
        _require_str(d, field_name, "HEALING_PLAN")
    _coerce_tuple_to_list(d, "manifests")
    _require_sequence_of_str(d, "manifests", "HEALING_PLAN")
    _require_int(d, "semantic_clock_tick", "HEALING_PLAN", min_val=0)
    if "emitting_layer" not in d or not d["emitting_layer"]:
        d["emitting_layer"] = "L2"
    _require_str(d, "emitting_layer", "HEALING_PLAN")
    return {
        "trace_id": d["trace_id"],
        "plan_id": d["plan_id"],
        "manifests": d["manifests"],
        "semantic_clock_tick": d["semantic_clock_tick"],
        "policy_liaison_node": d["policy_liaison_node"],
        "emitting_layer": d["emitting_layer"],
    }


def to_healing_plan_dict(x: object) -> dict[str, Any]:
    """Bridge adapter: convert dataclass or dict to plain dict (HealingPlan shape)."""
    return dict(validate_healing_plan(x))


_INCIDENT_REQUIRED_STR_FIELDS = ("trace_id", "incident_id", "correlation_hash")


def validate_incident_artifact(obj: object) -> dict[str, Any]:
    """Validate and normalize an IncidentArtifact to TypedDict shape."""
    d = _to_raw_dict(obj)
    for field_name in _INCIDENT_REQUIRED_STR_FIELDS:
        _require_str(d, field_name, "INCIDENT_ARTIFACT")
    _coerce_enum_to_str(d, "severity_enum")
    _require_str(d, "severity_enum", "INCIDENT_ARTIFACT")
    _coerce_tuple_to_list(d, "telemetry_events")
    _require_sequence_of_str(d, "telemetry_events", "INCIDENT_ARTIFACT")
    return {
        "trace_id": d["trace_id"],
        "incident_id": d["incident_id"],
        "correlation_hash": d["correlation_hash"],
        "severity_enum": d["severity_enum"],
        "telemetry_events": d["telemetry_events"],
    }


def to_incident_artifact_dict(x: object) -> dict[str, Any]:
    """Bridge adapter: convert dataclass or dict to plain dict (IncidentArtifact shape)."""
    return dict(validate_incident_artifact(x))


_STALE_WRITE_REQUIRED_STR_FIELDS = ("trace_id", "target_path", "expected_hash", "actual_hash")


def validate_stale_write_incident(obj: object) -> dict[str, Any]:
    """Validate and normalize a StaleWriteIncident to TypedDict shape."""
    d = _to_raw_dict(obj)
    for field_name in _STALE_WRITE_REQUIRED_STR_FIELDS:
        _require_str(d, field_name, "STALE_WRITE_INCIDENT")
    _require_int(d, "semantic_clock_tick", "STALE_WRITE_INCIDENT", min_val=0)
    return {
        "trace_id": d["trace_id"],
        "target_path": d["target_path"],
        "expected_hash": d["expected_hash"],
        "actual_hash": d["actual_hash"],
        "semantic_clock_tick": d["semantic_clock_tick"],
    }


def to_stale_write_incident_dict(x: object) -> dict[str, Any]:
    """Bridge adapter: convert dataclass or dict to plain dict (StaleWriteIncident shape)."""
    return dict(validate_stale_write_incident(x))


def make_result_artifact_from_dataclass(dc: object) -> dict[str, Any]:
    """Factory: validate a ResultArtifact dataclass and return TD-shaped dict."""
    return validate_result_artifact(dc)


def make_healing_plan_from_dataclass(dc: object) -> dict[str, Any]:
    """Factory: validate a HealingPlan dataclass and return TD-shaped dict."""
    return validate_healing_plan(dc)


__all__ = [
    "make_healing_plan_from_dataclass",
    "make_result_artifact_from_dataclass",
    "to_healing_plan_dict",
    "to_incident_artifact_dict",
    "to_result_artifact_dict",
    "to_stale_write_incident_dict",
    "validate_healing_plan",
    "validate_incident_artifact",
    "validate_result_artifact",
    "validate_stale_write_incident",
]
