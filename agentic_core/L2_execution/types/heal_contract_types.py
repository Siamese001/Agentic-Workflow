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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

_emit_dispatches_healing_run("p1", "heal_contract_types", "L2")
_emit_routes_through("p1", "heal_contract_types", "L2")
_emit_escalates_to_human("p1", "heal_contract_types", "L2")
_emit_reads_policy_state("p1", "heal_contract_types", "L2")


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
    CONTRACT_JSON_SCHEMA["properties"]["results"]["items"]["properties"].keys()
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

        _emit_snapshots_state(str(_uuid.uuid4()), "HealCheckResult.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "HealCheckResult.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "HealCheckResult.to_dict")
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
                f"Check keys mismatch: expected {sorted(CHECK_RESULT_SCHEMA_KEYS)}, got {sorted(check_keys)}"
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
            for t in type_spec:
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
        for key, val in obj.items():
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
                            f"{field_path}: string length {len(val)} < minLength {prop_schema['minLength']}"
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


__all__ = ["CombinedHealResult", "HealCheckResult", "HealStatus"]
