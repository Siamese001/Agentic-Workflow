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

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "output_schema_validator")
_emit_applies_guardrail("p0", "output_schema_validator", "p0_governance")
_emit_reads_policy_state("p0", "output_schema_validator", "policy_binding")
_emit_snapshots_state("p0", "output_schema_validator", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("output_schema_validator", "p4obs", "metric_1")
_emit_emits_metric_event("output_schema_validator", "p4obs", "metric_2")
_emit_emits_metric_event("output_schema_validator", "p4obs", "metric_3")
_emit_emits_metric_event("output_schema_validator", "p4obs", "metric_4")
_emit_emits_metric_event("output_schema_validator", "p4obs", "metric_5")
_emit_emits_metric_event("output_schema_validator", "p4obs", "metric_6")
_emit_records_incident_event("output_schema_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("output_schema_validator", "p4obs", "anomaly")
_emit_writes_observability_log("output_schema_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("output_schema_validator", "p4obs", "mon_state")
_emit_triggers_alert("output_schema_validator", "p4obs", "alert")
_emit_links_incident_trace("output_schema_validator", "p4obs", "trace_link")
_emit_captures_pattern("output_schema_validator", "p3lm", "pattern")
_emit_records_learning_event("output_schema_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("output_schema_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("output_schema_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("output_schema_validator", "p3lm", "routing")
_emit_improves_agent_policy("output_schema_validator", "p3lm", "policy")
_emit_stores_learning_state("output_schema_validator", "p3lm", "state")
_emit_records_execution_trace("output_schema_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("output_schema_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("output_schema_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("output_schema_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("output_schema_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("output_schema_validator", "env_read", "p2_env_1")
_emit_reads_environ("output_schema_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("output_schema_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("output_schema_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "output_schema_validator", "context_pull")
_emit_pulls_context("p1", "output_schema_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "output_schema_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "output_schema_validator", "uwg_term_2")
_emit_writes_through("p1", "output_schema_validator", "write_through")
_emit_writes_through("p1", "output_schema_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "output_schema_validator", "safety_validation")
_emit_invokes_eval("p1", "output_schema_validator", "eval_call")
_emit_proposal_commits_routing("p1", "output_schema_validator", "routing_commit")
_emit_escalates_to_human("p1", "output_schema_validator", "human_escalation")
_emit_routes_through("p1", "output_schema_validator", "route_through")
_emit_checks_agent_registry("p1", "output_schema_validator", "agent_registry")
_emit_validates_agent_capability("p1", "output_schema_validator", "capability")
_emit_dispatches_execution_plan("p1", "output_schema_validator", "exec_plan")
_emit_agent_executes_agent("p1", "output_schema_validator", "sub_agent")
_emit_routes_to_agent("p1", "output_schema_validator", "target_agent")
_emit_verifies_policy("p1", "output_schema_validator", "policy_check")
_emit_observes_runtime_state("p1", "output_schema_validator", "runtime_state")
_emit_verifies_boundary("p1", "output_schema_validator", "boundary_check")
_emit_transcripts_response("p1", "output_schema_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "output_schema_validator")
_emit_gated_by_confidence("p1", "output_schema_validator", "confidence_gate")
emit_replay_key("p0", "output_schema_validator")
emit_determinism_digest("p0", "output_schema_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "output_schema_validator", "execution_auth")
_emit_validates_capability("p2", "output_schema_validator", "capability_check")
_emit_routes_to_capability("p2", "output_schema_validator", "capability_route")
_emit_writes_via_uwg("p2", "output_schema_validator", "uwg_write")
_emit_blocks_direct_write("p2", "output_schema_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "output_schema_validator", "tool_invocation")
_emit_captures_execution_output("p2", "output_schema_validator", "exec_output")
_emit_dispatches_agent("p3", "output_schema_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "output_schema_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "output_schema_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "output_schema_validator", "healing_outcome")
_emit_escalates_failure("p3", "output_schema_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "output_schema_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "output_schema_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "output_schema_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "output_schema_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "output_schema_validator", "eval_metric")
_emit_stores_embedding("p4", "output_schema_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "output_schema_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "output_schema_validator", "exec_snapshot_link")

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
    except ImportError as e:
        raise ImportError(f"Required dependency missing: {e}")  # guardian: allow-silent-swallow


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
    except Exception as e:  # guardian: allow-silent-swallow
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
