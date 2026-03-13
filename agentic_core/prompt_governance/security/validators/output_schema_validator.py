"""
output_schema_validator.py - Runtime output schema validation.

Supports:
  1) Pydantic BaseModel subclasses (via model_validate)
  2) Dict schema subset: type=object, properties, required,
     additionalProperties, enum, items, primitive types

No new dependencies — uses only stdlib + optional pydantic (already in project).
Fail-closed on unsupported schema keywords.
"""

from __future__ import annotations

import json
import logging
from typing import Any

Logger = logging.getLogger(__name__)
_PRIMITIVE_TYPES = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "null": type(None),
}


def validate_against_schema(obj: Any, schema: Any) -> tuple[bool, str | None, dict]:
    """Validate *obj* against *schema*.

    Args:
        obj: The parsed object to validate (dict, list, or primitive).
        schema: Either a Pydantic BaseModel **class**, or a dict-based
                JSON Schema subset.

    Returns:
        (ok, code, details) where:
          ok    — True if valid
          code  — None if valid, else a stable error code string
          details — dict with diagnostic information (never raw user text)
    """
    if schema is None:
        return (True, None, {})
    if _is_pydantic_model(schema):
        return _validate_pydantic(obj, schema)
    if isinstance(schema, dict):
        return _validate_dict_schema(obj, schema)
    return (False, "SCHEMA_UNSUPPORTED", {"reason": f"Unsupported schema type: {type(schema).__name__}"})


def _is_pydantic_model(schema: Any) -> bool:
    """Return True if *schema* is a Pydantic BaseModel class."""
    try:
        from pydantic import BaseModel

        return isinstance(schema, type) and issubclass(schema, BaseModel)
    except ImportError:
        return False


def _validate_pydantic(obj: Any, model_cls: Any) -> tuple[bool, str | None, dict]:
    """Validate via Pydantic model_validate (v2) or parse_obj (v1)."""
    try:
        if isinstance(obj, str):
            obj = json.loads(obj)
    except (json.JSONDecodeError, TypeError) as e:
        return (False, "JSON_PARSE_ERROR", {"error": str(e)})
    try:
        if hasattr(model_cls, "model_validate"):
            model_cls.model_validate(obj)
        else:
            model_cls.parse_obj(obj)
        return (True, None, {})
    # guardian: allow-silent-swallow
    except Exception as e:
        return (False, "PYDANTIC_VALIDATION_ERROR", {"error": str(e)})


def _validate_dict_schema(obj: Any, schema: dict) -> tuple[bool, str | None, dict]:
    """Validate *obj* against a dict-based JSON Schema subset."""
    schema_type = schema.get("type")
    if isinstance(obj, str) and schema_type in ("object", "array", None):
        try:
            obj = json.loads(obj)
        except (json.JSONDecodeError, TypeError) as e:
            return (False, "JSON_PARSE_ERROR", {"error": str(e)})
    errors = _check_node(obj, schema, path="$")
    if errors:
        return (False, "DICT_SCHEMA_VALIDATION_ERROR", {"errors": errors})
    return (True, None, {})


_REQUIRED_RETRIEVAL_KEYS: tuple[str, ...] = ("namespace", "max_k", "version")
_REQUIRED_CITATION_KEYS: tuple[str, ...] = ("source_doc_id", "offset_start", "offset_end", "timestamp")
MISSING_CITATION_FIELDS = "MISSING_CITATION_FIELDS"
INCOMPLETE_RETRIEVAL_METADATA = "INCOMPLETE_RETRIEVAL_METADATA"
MUTATION_VERB_IN_RETRIEVAL = "MUTATION_VERB_IN_RETRIEVAL"
INVALID_RETRIEVAL_FIELD_CONSTRAINT = "INVALID_RETRIEVAL_FIELD_CONSTRAINT"
INVALID_TELEMETRY_ENVELOPE = "INVALID_TELEMETRY_ENVELOPE"
HEALER_REENTRY_VIOLATION = "HEALER_REENTRY_VIOLATION"
_MUTATION_AUTHORITY_MARKERS: tuple[str, ...] = ("durable_write", "fs_mutation", "db_commit")
_invariant_validated = False


def validate_healer_reentry(metadata: dict) -> tuple[bool, str | None]:
    """Validate that a healing proposal carries the required re-entry gate marker.

    Rules:
    - If metadata["healing_proposal"] is True, metadata["reentry_gate"] must also be True.
    - No durable mutation authority markers are allowed in metadata values.

    Returns:
        (ok, error_code) — ok=True if valid, error_code=None if valid.
    """
    if not isinstance(metadata, dict):
        return (False, HEALER_REENTRY_VIOLATION)
    if metadata.get("healing_proposal") is True:
        if metadata.get("reentry_gate") is not True:
            return (False, HEALER_REENTRY_VIOLATION)
    for value in metadata.values():
        if isinstance(value, str) and value in _MUTATION_AUTHORITY_MARKERS:
            return (False, HEALER_REENTRY_VIOLATION)
    return (True, None)


def validate_context_contract(payload: dict) -> tuple[bool, str | None, dict]:
    """Validate a context payload against prompt governance contracts.

    Args:
        payload: Context dict to validate. Never mutated.

    Returns:
        (ok, error_code, normalized) where:
          ok           — True if valid
          error_code   — None if valid, else one of the ERROR_CODE constants
          normalized   — new dict (not same object as payload) on success, {} on failure
    """
    global _invariant_validated
    if not _invariant_validated:
        from agentic_core.prompt_governance.core.invariant_registry import validate_invariant_registry

        validate_invariant_registry()
        _invariant_validated = True
    from agentic_core.prompt_governance.core.invariant_registry import READ_ONLY_ISOLATION

    forbidden_verbs: list[str] = READ_ONLY_ISOLATION["forbidden_verbs"]
    normalized: dict = {}
    if "retrieval_metadata" in payload:
        rm = payload["retrieval_metadata"]
        if not isinstance(rm, dict):
            return (False, INCOMPLETE_RETRIEVAL_METADATA, {})
        missing = [k for k in _REQUIRED_RETRIEVAL_KEYS if k not in rm]
        if missing:
            return (False, INCOMPLETE_RETRIEVAL_METADATA, {})
        namespace = rm["namespace"]
        max_k = rm["max_k"]
        version = rm["version"]
        if not isinstance(namespace, str) or not namespace:
            return (False, INVALID_RETRIEVAL_FIELD_CONSTRAINT, {})
        if not isinstance(max_k, int) or max_k <= 0:
            return (False, INVALID_RETRIEVAL_FIELD_CONSTRAINT, {})
        if not isinstance(version, str) or not version:
            return (False, INVALID_RETRIEVAL_FIELD_CONSTRAINT, {})
        for key in rm:
            if key in forbidden_verbs:
                return (False, MUTATION_VERB_IN_RETRIEVAL, {})
        normalized["retrieval_metadata"] = {"namespace": namespace, "max_k": max_k, "version": version}
    if "citations" in payload:
        citations = payload["citations"]
        if not isinstance(citations, list):
            return (False, MISSING_CITATION_FIELDS, {})
        for item in citations:
            if not isinstance(item, dict):
                return (False, MISSING_CITATION_FIELDS, {})
            missing = [k for k in _REQUIRED_CITATION_KEYS if k not in item]
            if missing:
                return (False, MISSING_CITATION_FIELDS, {})
        normalized["citations"] = [{k: item[k] for k in _REQUIRED_CITATION_KEYS} for item in citations]
    if "telemetry_envelope" in payload:
        te = payload["telemetry_envelope"]
        if not isinstance(te, dict):
            return (False, INVALID_TELEMETRY_ENVELOPE, {})
        if not isinstance(te.get("hit_rate"), (int, float)):
            return (False, INVALID_TELEMETRY_ENVELOPE, {})
        if not isinstance(te.get("recall_estimate"), (int, float)):
            return (False, INVALID_TELEMETRY_ENVELOPE, {})
        if not isinstance(te.get("empty_result_signal"), bool):
            return (False, INVALID_TELEMETRY_ENVELOPE, {})
        normalized["telemetry_envelope"] = {
            "hit_rate": te["hit_rate"],
            "recall_estimate": te["recall_estimate"],
            "empty_result_signal": te["empty_result_signal"],
        }
    for key, value in payload.items():
        if key not in ("retrieval_metadata", "citations", "telemetry_envelope"):
            normalized[key] = value
    return (True, None, normalized)


def _check_node(value: Any, schema: dict, path: str) -> list[str]:
    """Recursively validate a value against a schema node. Returns list of error strings."""
    errors: list[str] = []
    if "enum" in schema:
        if value not in schema["enum"]:
            errors.append(f"{path}: value not in enum {schema['enum']}")
            return errors
    schema_type = schema.get("type")
    if schema_type is None:
        return errors
    if schema_type in _PRIMITIVE_TYPES:
        expected = _PRIMITIVE_TYPES[schema_type]
        if not isinstance(value, expected):
            if schema_type == "number" and isinstance(value, (int, float)):
                pass
            else:
                errors.append(f"{path}: expected {schema_type}, got {type(value).__name__}")
                return errors
    if schema_type == "object":
        if not isinstance(value, dict):
            errors.append(f"{path}: expected object, got {type(value).__name__}")
            return errors
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        additional = schema.get("additionalProperties", True)
        for req_key in required:
            if req_key not in value:
                errors.append(f"{path}: missing required key '{req_key}'")
        for key, val in value.items():
            if key in properties:
                errors.extend(_check_node(val, properties[key], path=f"{path}.{key}"))
            elif additional is False:
                errors.append(f"{path}: unexpected key '{key}'")
    if schema_type == "array":
        if not isinstance(value, list):
            errors.append(f"{path}: expected array, got {type(value).__name__}")
            return errors
        items_schema = schema.get("items")
        if items_schema:
            for i, item in enumerate(value):
                errors.extend(_check_node(item, items_schema, path=f"{path}[{i}]"))
    return errors
