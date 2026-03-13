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


def _to_raw_dict(obj: object) -> dict[str, Any]:
    """Convert dataclass or dict-like to plain dict without mutating input."""
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
