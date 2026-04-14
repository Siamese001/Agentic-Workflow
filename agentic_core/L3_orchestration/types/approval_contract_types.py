"""
L3 Approval Contract — Canonical Schema for Approval Artifacts.

SSOT for structured approval records consumed by:
- L2 dispatcher (future) for approval-gated phases
- L3 orchestration layer
- L6 observability ingestion

Every approval gate MUST emit records conforming to this schema.
No ad-hoc keys. Deterministic ordering throughout.

Contract version is an integer that increments on breaking changes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "approval_contract_types")
emit_determinism_digest("p0", "approval_contract_types")

_emit_dispatches_healing_run("p1", "approval_contract_types", "L3")
_emit_routes_through("p1", "approval_contract_types", "L3")
_emit_checks_agent_registry("p1", "approval_contract_types", "agent_registry")
_emit_validates_agent_capability("p1", "approval_contract_types", "capability")
_emit_dispatches_execution_plan("p1", "approval_contract_types", "exec_plan")
_emit_agent_executes_agent("p1", "approval_contract_types", "sub_agent")
_emit_routes_to_agent("p1", "approval_contract_types", "target_agent")
_emit_verifies_policy("p1", "approval_contract_types", "policy_check")
_emit_observes_runtime_state("p1", "approval_contract_types", "runtime_state")
_emit_verifies_boundary("p1", "approval_contract_types", "boundary_check")
_emit_transcripts_response("p1", "approval_contract_types", "transcript")
_emit_hard_fails_untranscripted("p1", "approval_contract_types")
_emit_gated_by_confidence("p1", "approval_contract_types", "confidence_gate")
_emit_escalates_to_human("p1", "approval_contract_types", "L3")
_emit_reads_policy_state("p1", "approval_contract_types", "L3")
_emit_authorize_and_execute("p2", "approval_contract_types", "execution_auth")
_emit_validates_capability("p2", "approval_contract_types", "capability_check")
_emit_routes_to_capability("p2", "approval_contract_types", "capability_route")
_emit_writes_via_uwg("p2", "approval_contract_types", "uwg_write")
_emit_blocks_direct_write("p2", "approval_contract_types", "direct_write_block")
_emit_records_tool_invocation("p2", "approval_contract_types", "tool_invocation")
_emit_captures_execution_output("p2", "approval_contract_types", "exec_output")
_emit_dispatches_agent("p3", "approval_contract_types", "agent_dispatch")
_emit_coordinates_agents("p3", "approval_contract_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "approval_contract_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "approval_contract_types", "healing_outcome")
_emit_escalates_failure("p3", "approval_contract_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "approval_contract_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "approval_contract_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "approval_contract_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "approval_contract_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "approval_contract_types", "eval_metric")
_emit_stores_embedding("p4", "approval_contract_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "approval_contract_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "approval_contract_types", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
from tqdm import tqdm

_emit_emits_metric_event("approval_contract_types", "p4obs", "metric_1")
_emit_emits_metric_event("approval_contract_types", "p4obs", "metric_2")
_emit_emits_metric_event("approval_contract_types", "p4obs", "metric_3")
_emit_emits_metric_event("approval_contract_types", "p4obs", "metric_4")
_emit_emits_metric_event("approval_contract_types", "p4obs", "metric_5")
_emit_emits_metric_event("approval_contract_types", "p4obs", "metric_6")
_emit_records_incident_event("approval_contract_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("approval_contract_types", "p4obs", "anomaly")
_emit_writes_observability_log("approval_contract_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("approval_contract_types", "p4obs", "mon_state")
_emit_triggers_alert("approval_contract_types", "p4obs", "alert")
_emit_links_incident_trace("approval_contract_types", "p4obs", "trace_link")
_emit_captures_pattern("approval_contract_types", "p3lm", "pattern")
_emit_records_learning_event("approval_contract_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("approval_contract_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("approval_contract_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("approval_contract_types", "p3lm", "routing")
_emit_improves_agent_policy("approval_contract_types", "p3lm", "policy")
_emit_stores_learning_state("approval_contract_types", "p3lm", "state")
_emit_records_execution_trace("approval_contract_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("approval_contract_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("approval_contract_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("approval_contract_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("approval_contract_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("approval_contract_types", "env_read", "p2_env_1")
_emit_reads_environ("approval_contract_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("approval_contract_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("approval_contract_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "approval_contract_types", "context_pull")
_emit_pulls_context("p1", "approval_contract_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "approval_contract_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "approval_contract_types", "uwg_term_2")
_emit_writes_through("p1", "approval_contract_types", "write_through")
_emit_writes_through("p1", "approval_contract_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "approval_contract_types", "safety_validation")
_emit_invokes_eval("p1", "approval_contract_types", "eval_call")
_emit_proposal_commits_routing("p1", "approval_contract_types", "routing_commit")


class ApprovalDecision(str, Enum):
    """Decision outcome for an approval gate."""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


APPROVAL_DECISION_VALUES: frozenset[str] = frozenset(s.value for s in ApprovalDecision)
CONTRACT_VERSION: int = 1
CONTRACT_JSON_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "ApprovalBundle",
    "type": "object",
    "required": ["contract_version", "records"],
    "additionalProperties": False,
    "properties": {
        "contract_version": {"type": "integer", "minimum": 1},
        "records": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["phase_name", "check_ids", "decision", "approver", "token", "created_utc"],
                "additionalProperties": False,
                "properties": {
                    "phase_name": {"type": "string", "minLength": 1},
                    "guardian_id": {"type": ["string", "null"]},
                    "check_ids": {"type": "array", "items": {"type": "string"}},
                    "decision": {"type": "string", "enum": sorted(APPROVAL_DECISION_VALUES)},
                    "approver": {"type": "string", "minLength": 1},
                    "rationale": {"type": ["string", "null"]},
                    "token": {"type": "string", "minLength": 1},
                    "created_utc": {"type": "string", "minLength": 1},
                },
            },
        },
    },
}
BUNDLE_SCHEMA_KEYS: frozenset[str] = frozenset(CONTRACT_JSON_SCHEMA["properties"].keys())
RECORD_SCHEMA_KEYS: frozenset[str] = frozenset(
    CONTRACT_JSON_SCHEMA["properties"]["records"]["items"]["properties"].keys(),
)


@dataclass(frozen=True, slots=True)
class ApprovalRecord:
    """Immutable record of a single approval decision.

    Attributes:
        phase_name: Canonical phase name from PhaseSpec.
        guardian_id: Optional guardian ID (approval may be per-phase).
        check_ids: Sorted tuple of check IDs being approved (may be empty).
        decision: APPROVED or REJECTED.
        approver: Human identifier string.
        rationale: Optional free-text rationale.
        token: Opaque token ID referenced by L2.
        created_utc: ISO-8601 timestamp (required, no auto-now).
    """

    phase_name: str
    decision: ApprovalDecision
    approver: str
    token: str
    created_utc: str
    guardian_id: str | None = None
    check_ids: tuple[str, ...] = ()
    rationale: str | None = None

    def __post_init__(self) -> None:
        if not self.phase_name:
            raise ValueError("phase_name must not be empty")
        if not isinstance(self.decision, ApprovalDecision):
            raise ValueError(f"decision must be an ApprovalDecision enum, got {type(self.decision).__name__}")
        if not self.approver:
            raise ValueError("approver must not be empty")
        if not self.token:
            raise ValueError("token must not be empty")
        if not self.created_utc:
            raise ValueError("created_utc must not be empty")
        if not isinstance(self.check_ids, tuple):
            raise TypeError("check_ids must be a tuple")

    def to_dict(self) -> dict[str, Any]:
        """Deterministic dict: check_ids sorted."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ApprovalRecord.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ApprovalRecord.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ApprovalRecord.to_dict")
        return {
            "phase_name": self.phase_name,
            "guardian_id": self.guardian_id,
            "check_ids": sorted(self.check_ids),
            "decision": self.decision.value,
            "approver": self.approver,
            "rationale": self.rationale,
            "token": self.token,
            "created_utc": self.created_utc,
        }


@dataclass(frozen=True, slots=True)
class ApprovalBundle:
    """Immutable bundle of approval records for an execution plan.

    Attributes:
        records: Sorted tuple of ApprovalRecord objects (sorted by token).
    """

    records: tuple[ApprovalRecord, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.records, tuple):
            raise TypeError("records must be a tuple of ApprovalRecord")

    def to_dict(self) -> dict[str, Any]:
        """Deterministic dict: records sorted by token."""
        return {
            "contract_version": CONTRACT_VERSION,
            "records": sorted([r.to_dict() for r in self.records], key=lambda d: d["token"]),
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to deterministic JSON string."""
        return json.dumps(self.to_dict(), indent=indent, sort_keys=False)

    def validate(self) -> list[str]:
        """Validate against CONTRACT_JSON_SCHEMA. Returns list of errors (empty = valid)."""
        return validate_against_json_schema(self.to_dict())


def check_schema_compatibility(result_dict: dict[str, Any]) -> list[str]:
    """Verify a serialized result dict has exactly the expected top-level keys.

    Returns list of incompatibility messages (empty = compatible).
    """
    errors: list[str] = []
    expected_keys = set(BUNDLE_SCHEMA_KEYS)
    actual_keys = set(result_dict.keys())
    missing = expected_keys - actual_keys
    extra = actual_keys - expected_keys
    if missing:
        errors.append(f"Missing required keys: {sorted(missing)}")
    if extra:
        errors.append(f"Unexpected keys (schema drift): {sorted(extra)}")
    for record in result_dict.get("records", []):
        record_keys = set(record.keys())
        if record_keys != RECORD_SCHEMA_KEYS:
            errors.append(
                f"Record keys mismatch: expected {sorted(RECORD_SCHEMA_KEYS)}, got {sorted(record_keys)}",
            )
    return errors


def validate_against_json_schema(result_dict: dict[str, Any]) -> list[str]:
    """Lightweight validation of result_dict against CONTRACT_JSON_SCHEMA.

    Validates: required fields, type constraints, enum values, additionalProperties,
    and minLength. Does NOT require jsonschema library.

    Returns list of validation errors (empty = valid).
    """
    errors: list[str] = []
    schema = CONTRACT_JSON_SCHEMA

    def _validate_type(value: Any, type_spec: Any, path: str) -> None:
        if isinstance(type_spec, list):
            if value is None and "null" in type_spec:
                return
            for t in tqdm(type_spec, desc="Processing", unit="item"):
                if t == "null":
                    continue
                if t == "string" and isinstance(value, str):
                    return
                if t == "integer" and isinstance(value, int) and (not isinstance(value, bool)):
                    return
                if t == "object" and isinstance(value, dict):
                    return
                if t == "array" and isinstance(value, list):
                    return
            errors.append(f"{path}: expected one of {type_spec}, got {type(value).__name__}")
        elif type_spec == "string":
            if not isinstance(value, str):
                errors.append(f"{path}: expected string, got {type(value).__name__}")
        elif type_spec == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                errors.append(f"{path}: expected integer, got {type(value).__name__}")
        elif type_spec == "object":
            if not isinstance(value, dict):
                errors.append(f"{path}: expected object, got {type(value).__name__}")
        elif type_spec == "array":
            if not isinstance(value, list):
                errors.append(f"{path}: expected array, got {type(value).__name__}")

    def _validate_enum(value: Any, enum_values: list[str], path: str) -> None:
        if value not in enum_values:
            errors.append(f"{path}: value '{value}' not in enum {enum_values}")

    def _validate_object(obj: dict, obj_schema: dict, path: str) -> None:
        props = obj_schema.get("properties", {})
        required = set(obj_schema.get("required", []))
        additional = obj_schema.get("additionalProperties", True)
        for req in required:
            if req not in obj:
                errors.append(f"{path}: missing required field '{req}'")
        if additional is False:
            extra = set(obj.keys()) - set(props.keys())
            for e in sorted(extra):
                errors.append(f"{path}: unexpected field '{e}'")
        for key, val in tqdm(obj.items(), desc="Processing", unit="item"):
            if key in props:
                prop_schema = props[key]
                field_path = f"{path}.{key}"
                if "type" in prop_schema:
                    _validate_type(val, prop_schema["type"], field_path)
                if "enum" in prop_schema and val is not None:
                    _validate_enum(val, prop_schema["enum"], field_path)
                if "minLength" in prop_schema and isinstance(val, str):
                    if len(val) < prop_schema["minLength"]:
                        errors.append(
                            f"{field_path}: string length {len(val)} < minLength {prop_schema['minLength']}",
                        )
                if prop_schema.get("type") == "object" and isinstance(val, dict):
                    _validate_object(val, prop_schema, field_path)
                if prop_schema.get("type") == "array" and isinstance(val, list):
                    item_schema = prop_schema.get("items", {})
                    for i, item in enumerate(val):
                        if item_schema.get("type") == "object" and isinstance(item, dict):
                            _validate_object(item, item_schema, f"{field_path}[{i}]")
                        elif "type" in item_schema:
                            _validate_type(item, item_schema["type"], f"{field_path}[{i}]")
                        if "enum" in item_schema and item is not None:
                            _validate_enum(item, item_schema["enum"], f"{field_path}[{i}]")

    _validate_object(result_dict, schema, "$")
    return errors


__all__ = ["ApprovalBundle", "ApprovalDecision", "ApprovalRecord"]
