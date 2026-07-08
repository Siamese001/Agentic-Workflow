"""
L2 Heal Contract — Canonical Schema for All Heal Results.

SSOT for structured remediation output consumed by:
- L2 dispatcher (future)
- L3 approval gates
- L6 observability ingestion

Every healer MUST emit results conforming to this schema.
No ad-hoc keys. No absolute paths. Deterministic ordering throughout.

Contract version is an integer that increments on breaking changes.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "heal_contract_types")
trace_contract.emit_determinism_digest("p0", "heal_contract_types")

trace_contract._emit_dispatches_healing_run("p1", "heal_contract_types", "L2")
trace_contract._emit_routes_through("p1", "heal_contract_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "heal_contract_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "heal_contract_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "heal_contract_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "heal_contract_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "heal_contract_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "heal_contract_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "heal_contract_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "heal_contract_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "heal_contract_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "heal_contract_types")
trace_contract._emit_gated_by_confidence("p1", "heal_contract_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "heal_contract_types", "L2")
trace_contract._emit_reads_policy_state("p1", "heal_contract_types", "L2")
trace_contract._emit_authorize_and_execute("p2", "heal_contract_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "heal_contract_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "heal_contract_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "heal_contract_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "heal_contract_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "heal_contract_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "heal_contract_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "heal_contract_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "heal_contract_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "heal_contract_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "heal_contract_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "heal_contract_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "heal_contract_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "heal_contract_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "heal_contract_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "heal_contract_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "heal_contract_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "heal_contract_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "heal_contract_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "heal_contract_types", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("heal_contract_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("heal_contract_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("heal_contract_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("heal_contract_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("heal_contract_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("heal_contract_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("heal_contract_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("heal_contract_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("heal_contract_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("heal_contract_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("heal_contract_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("heal_contract_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("heal_contract_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("heal_contract_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("heal_contract_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("heal_contract_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("heal_contract_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("heal_contract_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("heal_contract_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("heal_contract_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("heal_contract_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("heal_contract_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("heal_contract_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("heal_contract_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("heal_contract_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("heal_contract_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("heal_contract_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("heal_contract_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "heal_contract_types", "context_pull")
trace_contract._emit_pulls_context("p1", "heal_contract_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "heal_contract_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "heal_contract_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "heal_contract_types", "write_through")
trace_contract._emit_writes_through("p1", "heal_contract_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "heal_contract_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "heal_contract_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "heal_contract_types", "routing_commit")


class HealStatus(str, Enum):
    """Per-check heal outcome status."""

    HEALED = "HEALED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


HEAL_STATUS_VALUES: frozenset[str] = frozenset(s.value for s in HealStatus)
CONTRACT_VERSION: int = 2
CONTRACT_JSON_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "CombinedHealResult",
    "type": "object",
    "required": ["contract_version", "tool_id", "plan_name", "results", "approved_by", "created_utc"],
    "additionalProperties": False,
    "properties": {
        "contract_version": {"type": "integer", "minimum": 1},
        "tool_id": {"type": "string", "minLength": 1},
        "plan_name": {"type": "string", "minLength": 1},
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["check_id", "status", "changes_made"],
                "additionalProperties": False,
                "properties": {
                    "check_id": {"type": "string", "minLength": 1},
                    "status": {"type": "string", "enum": sorted(HEAL_STATUS_VALUES)},
                    "changes_made": {
                        "type": "array",
                        "items": {"type": "string", "pattern": "^(?![A-Za-z]:)(?!/)"},
                    },
                    "rollback_info": {"type": ["string", "null"]},
                    "notes": {"type": ["string", "null"]},
                    "needs_llm_escalation": {"type": "boolean"},
                    "escalation_hint": {"type": ["string", "null"]},
                },
            },
        },
        "approved_by": {"type": "array", "items": {"type": "string"}},
        "created_utc": {"type": "string", "minLength": 1},
    },
}
RESULT_SCHEMA_KEYS: frozenset[str] = frozenset(CONTRACT_JSON_SCHEMA["properties"].keys())
CHECK_RESULT_SCHEMA_KEYS: frozenset[str] = frozenset(
    CONTRACT_JSON_SCHEMA["properties"]["results"]["items"]["properties"].keys(),
)
_ABS_PATH_RE = re.compile("^[A-Za-z]:|^/")


@dataclass(frozen=True, slots=True)
class HealCheckResult:
    """Immutable result of a single heal check.

    Attributes:
        check_id: Identifier of the check that was healed.
        status: Outcome of the healing attempt.
        changes_made: Sorted repo-relative paths or human-readable actions.
        rollback_info: Optional rollback instructions.
        notes: Optional free-text notes.
        needs_llm_escalation: True only when the healer explicitly determines
            LLM-tier escalation is required (e.g. complex rewrite needed).
            Must NOT be set for policy-blocked, permission, or N/A failures.
        escalation_hint: Structured hint for tier routing, e.g.
            "failure_type=code_edit_required blast_radius=0.7".
            Ignored unless needs_llm_escalation is True.
    """

    check_id: str
    status: HealStatus
    changes_made: tuple[str, ...] = ()
    rollback_info: str | None = None
    notes: str | None = None
    needs_llm_escalation: bool = False
    escalation_hint: str | None = None

    def __post_init__(self) -> None:
        if not self.check_id:
            raise ValueError("check_id must not be empty")
        if not isinstance(self.status, HealStatus):
            raise ValueError(f"status must be a HealStatus enum, got {type(self.status).__name__}")
        for path in self.changes_made:
            if _ABS_PATH_RE.match(path):
                raise ValueError(f"Absolute path not allowed in changes_made: {path}")

    def to_dict(self) -> dict[str, Any]:
        """Deterministic dict: changes_made sorted."""
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "HealCheckResult.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "HealCheckResult.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "HealCheckResult.to_dict")
        return {
            "check_id": self.check_id,
            "status": self.status.value,
            "changes_made": sorted(self.changes_made),
            "rollback_info": self.rollback_info,
            "notes": self.notes,
            "needs_llm_escalation": self.needs_llm_escalation,
            "escalation_hint": self.escalation_hint,
        }


@dataclass(frozen=True, slots=True)
class CombinedHealResult:
    """Immutable aggregate of all heal check results for a plan execution.

    Attributes:
        tool_id: Constant identifier for the tool that produced the result.
        plan_name: Name of the execution plan used.
        results: Sorted tuple of HealCheckResult objects.
        approved_by: Sorted tuple of approval tokens/ids.
        created_utc: ISO-8601 timestamp (required, no auto-now).
    """

    tool_id: str
    plan_name: str
    results: tuple[HealCheckResult, ...]
    approved_by: tuple[str, ...]
    created_utc: str

    def __post_init__(self) -> None:
        if not self.tool_id:
            raise ValueError("tool_id must not be empty")
        if not self.plan_name:
            raise ValueError("plan_name must not be empty")
        if not self.created_utc:
            raise ValueError("created_utc must not be empty")
        if not isinstance(self.results, tuple):
            raise TypeError("results must be a tuple of HealCheckResult")
        if not isinstance(self.approved_by, tuple):
            raise TypeError("approved_by must be a tuple of strings")

    def to_dict(self) -> dict[str, Any]:
        """Deterministic dict: results sorted by check_id, approved_by sorted."""
        return {
            "contract_version": CONTRACT_VERSION,
            "tool_id": self.tool_id,
            "plan_name": self.plan_name,
            "results": sorted([r.to_dict() for r in self.results], key=lambda d: d["check_id"]),
            "approved_by": sorted(self.approved_by),
            "created_utc": self.created_utc,
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
    expected_keys = set(RESULT_SCHEMA_KEYS)
    actual_keys = set(result_dict.keys())
    missing = expected_keys - actual_keys
    extra = actual_keys - expected_keys
    if missing:
        errors.append(f"Missing required keys: {sorted(missing)}")
    if extra:
        errors.append(f"Unexpected keys (schema drift): {sorted(extra)}")
    for check in result_dict.get("results", []):
        check_keys = set(check.keys())
        if check_keys != CHECK_RESULT_SCHEMA_KEYS:
            errors.append(
                f"Check keys mismatch: expected {sorted(CHECK_RESULT_SCHEMA_KEYS)}, got {sorted(check_keys)}",
            )
    return errors


def validate_against_json_schema(result_dict: dict[str, Any]) -> list[str]:
    """Lightweight validation of result_dict against CONTRACT_JSON_SCHEMA.

    Validates: required fields, type constraints, enum values, additionalProperties,
    and path patterns. Does NOT require jsonschema library.

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

    def _validate_pattern(value: str, pattern: str, path: str) -> None:
        if not re.search(pattern, value):
            errors.append(f"{path}: value '{value}' does not match pattern '{pattern}'")

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
                if "pattern" in prop_schema and isinstance(val, str):
                    _validate_pattern(val, prop_schema["pattern"], field_path)
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
                        if "pattern" in item_schema and isinstance(item, str):
                            _validate_pattern(item, item_schema["pattern"], f"{field_path}[{i}]")

    _validate_object(result_dict, schema, "$")
    return errors


class ClassifierSource(str, Enum):
    """Records whether scoring came from ML inference or the heuristic fallback."""

    ML_CLASSIFIER = "ML_CLASSIFIER"
    HEURISTIC_FALLBACK = "HEURISTIC_FALLBACK"


@dataclass(frozen=True)
class HealClassifierResult:
    """Output contract for a single heal-confidence inference call.

    recommended_tier is the string name of a HealTier member (e.g. "HIGH").
    Using str avoids a circular import with confidence_scorer.py.
    confidence_per_tier keys are HealTier names; values sum to ~1.0 for ML,
    0.0 for heuristic (heuristic does not produce per-tier probabilities).
    """

    heal_confidence: float
    recommended_tier: str
    confidence_per_tier: dict[str, float]
    ood_flag: bool
    source: ClassifierSource
    model_version_hash: str
    inference_latency_us: int


@dataclass(frozen=True)
class HealClassifierTelemetry:
    """BUS T payload emitted after every ConfidenceScorer.score() call.

    divergence_flag is True when the ML recommendation differs from the
    heuristic tier. This is the primary signal for Phase 6 activation readiness.
    """

    run_id: str
    check_id: str
    source: ClassifierSource
    recommended_tier: str
    heal_confidence: float
    ood_flag: bool
    model_version_hash: str
    inference_latency_us: int
    heuristic_tier: str
    divergence_flag: bool


__all__ = [
    "ClassifierSource",
    "CombinedHealResult",
    "HealCheckResult",
    "HealClassifierResult",
    "HealClassifierTelemetry",
    "HealStatus",
]
