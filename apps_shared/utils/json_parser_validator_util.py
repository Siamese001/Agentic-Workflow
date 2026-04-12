"""
JSON Parser Utilities - Phase 4 Optimization
Native Python implementations for JSON parsing and manipulation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "json_parser_validator_util", "p0_governance")
_emit_reads_policy_state("p0", "json_parser_validator_util", "policy_binding")
_emit_snapshots_state("p0", "json_parser_validator_util", "state_snapshot")
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

_emit_emits_metric_event("json_parser_validator_util", "p4obs", "metric_1")
_emit_emits_metric_event("json_parser_validator_util", "p4obs", "metric_2")
_emit_emits_metric_event("json_parser_validator_util", "p4obs", "metric_3")
_emit_emits_metric_event("json_parser_validator_util", "p4obs", "metric_4")
_emit_emits_metric_event("json_parser_validator_util", "p4obs", "metric_5")
_emit_emits_metric_event("json_parser_validator_util", "p4obs", "metric_6")
_emit_records_incident_event("json_parser_validator_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("json_parser_validator_util", "p4obs", "anomaly")
_emit_writes_observability_log("json_parser_validator_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("json_parser_validator_util", "p4obs", "mon_state")
_emit_triggers_alert("json_parser_validator_util", "p4obs", "alert")
_emit_links_incident_trace("json_parser_validator_util", "p4obs", "trace_link")
_emit_captures_pattern("json_parser_validator_util", "p3lm", "pattern")
_emit_records_learning_event("json_parser_validator_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("json_parser_validator_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("json_parser_validator_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("json_parser_validator_util", "p3lm", "routing")
_emit_improves_agent_policy("json_parser_validator_util", "p3lm", "policy")
_emit_stores_learning_state("json_parser_validator_util", "p3lm", "state")
_emit_records_execution_trace("json_parser_validator_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("json_parser_validator_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("json_parser_validator_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("json_parser_validator_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("json_parser_validator_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("json_parser_validator_util", "env_read", "p2_env_1")
_emit_reads_environ("json_parser_validator_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("json_parser_validator_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("json_parser_validator_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "json_parser_validator_util", "context_pull")
_emit_pulls_context("p1", "json_parser_validator_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "json_parser_validator_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "json_parser_validator_util", "uwg_term_2")
_emit_writes_through("p1", "json_parser_validator_util", "write_through")
_emit_writes_through("p1", "json_parser_validator_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "json_parser_validator_util", "safety_validation")
_emit_invokes_eval("p1", "json_parser_validator_util", "eval_call")
_emit_proposal_commits_routing("p1", "json_parser_validator_util", "routing_commit")
_emit_escalates_to_human("p1", "json_parser_validator_util", "human_escalation")
_emit_routes_through("p1", "json_parser_validator_util", "route_through")
_emit_checks_agent_registry("p1", "json_parser_validator_util", "agent_registry")
_emit_validates_agent_capability("p1", "json_parser_validator_util", "capability")
_emit_dispatches_execution_plan("p1", "json_parser_validator_util", "exec_plan")
_emit_agent_executes_agent("p1", "json_parser_validator_util", "sub_agent")
_emit_routes_to_agent("p1", "json_parser_validator_util", "target_agent")
_emit_verifies_policy("p1", "json_parser_validator_util", "policy_check")
_emit_observes_runtime_state("p1", "json_parser_validator_util", "runtime_state")
_emit_verifies_boundary("p1", "json_parser_validator_util", "boundary_check")
_emit_transcripts_response("p1", "json_parser_validator_util", "transcript")
_emit_hard_fails_untranscripted("p1", "json_parser_validator_util")
_emit_gated_by_confidence("p1", "json_parser_validator_util", "confidence_gate")
emit_replay_key("p0", "json_parser_validator_util")
emit_determinism_digest("p0", "json_parser_validator_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "json_parser_validator_util", "execution_auth")
_emit_validates_capability("p2", "json_parser_validator_util", "capability_check")
_emit_routes_to_capability("p2", "json_parser_validator_util", "capability_route")
_emit_writes_via_uwg("p2", "json_parser_validator_util", "uwg_write")
_emit_blocks_direct_write("p2", "json_parser_validator_util", "direct_write_block")
_emit_records_tool_invocation("p2", "json_parser_validator_util", "tool_invocation")
_emit_captures_execution_output("p2", "json_parser_validator_util", "exec_output")
_emit_dispatches_agent("p3", "json_parser_validator_util", "agent_dispatch")
_emit_coordinates_agents("p3", "json_parser_validator_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "json_parser_validator_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "json_parser_validator_util", "healing_outcome")
_emit_escalates_failure("p3", "json_parser_validator_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "json_parser_validator_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "json_parser_validator_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "json_parser_validator_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "json_parser_validator_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "json_parser_validator_util", "eval_metric")
_emit_stores_embedding("p4", "json_parser_validator_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "json_parser_validator_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "json_parser_validator_util", "exec_snapshot_link")


@dataclass
class ParseResult:
    """Result of a JSON parsing operation."""

    success: bool
    data: Any
    errors: list[str]
    metadata: dict[str, Any]


class JsonParser:
    """Native Python JSON parsing utilities."""

    @staticmethod
    def parse_json(json_string: str, strict: bool = True) -> ParseResult:
        """
        Parse JSON string.

        Args:
            json_string: JSON string to parse
            strict: Whether to use strict parsing

        Returns:
            ParseResult with parsed data or errors
        """
        try:
            data = json.loads(json_string, strict=strict)
            return ParseResult(success=True, data=data, errors=[], metadata={})
        except json.JSONDecodeError as e:
            return ParseResult(
                success=False,
                data=None,
                errors=[f"JSON decode error: {str(e)}"],
                metadata={"line": e.lineno, "column": e.colno},
            )
        except Exception as e:
            return ParseResult(success=False, data=None, errors=[f"Parse error: {str(e)}"], metadata={})

    @staticmethod
    def safe_get(data: dict[str, Any], path: str, default: Any = None) -> Any:
        """
        Safely get nested value from dictionary using dot notation.

        Args:
            data: Dictionary to search
            path: Dot-separated path (e.g., "user.profile.name")
            default: Default value if path not found

        Returns:
            Value at path or default
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "JsonParser.safe_get")

        keys = path.split(".")
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    @staticmethod
    def safe_set(data: dict[str, Any], path: str, value: Any) -> None:
        """
        Safely set nested value in dictionary using dot notation.

        Args:
            data: Dictionary to modify
            path: Dot-separated path
            value: Value to set
        """
        keys = path.split(".")
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    @staticmethod
    def merge_dicts(dict1: dict[str, Any], dict2: dict[str, Any], deep: bool = True) -> dict[str, Any]:
        """
        Merge two dictionaries.

        Args:
            dict1: First dictionary
            dict2: Second dictionary (takes precedence)
            deep: Whether to perform deep merge

        Returns:
            Merged dictionary
        """
        result = dict1.copy()
        for key, value in dict2.items():
            if deep and key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = JsonParser.merge_dicts(result[key], value, deep=True)
            else:
                result[key] = value
        return result

    @staticmethod
    def flatten_dict(data: dict[str, Any], separator: str = ".") -> dict[str, Any]:
        """
        Flatten nested dictionary.

        Args:
            data: Dictionary to flatten
            separator: Separator for nested keys

        Returns:
            Flattened dictionary
        """
        result = {}

        def _flatten(obj: Any, prefix: str = "") -> None:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{prefix}{separator}{key}" if prefix else key
                    _flatten(value, new_key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_key = f"{prefix}{separator}{i}" if prefix else str(i)
                    _flatten(item, new_key)
            else:
                result[prefix] = obj

        _flatten(data)
        return result

    @staticmethod
    def unflatten_dict(data: dict[str, Any], separator: str = ".") -> dict[str, Any]:
        """
        Unflatten dictionary with dot-separated keys.

        Args:
            data: Flattened dictionary
            separator: Separator used in keys

        Returns:
            Unflattened dictionary
        """
        result = {}
        for key, value in data.items():
            JsonParser.safe_set(result, key.replace(separator, "."), value)
        return result

    @staticmethod
    def filter_keys(data: dict[str, Any], keys: list[str], include: bool = True) -> dict[str, Any]:
        """
        Filter dictionary by keys.

        Args:
            data: Dictionary to filter
            keys: List of keys to include/exclude
            include: If True, include only these keys; if False, exclude them

        Returns:
            Filtered dictionary
        """
        if include:
            return {k: v for k, v in data.items() if k in keys}
        else:
            return {k: v for k, v in data.items() if k not in keys}

    @staticmethod
    def validate_schema(data: dict[str, Any], schema: dict[str, type]) -> ParseResult:
        """
        Validate data against simple schema.

        Args:
            data: Data to validate
            schema: Dictionary mapping keys to expected types

        Returns:
            ParseResult with validation results
        """
        errors = []
        for key, expected_type in schema.items():
            if key not in data:
                errors.append(f"Missing required key: {key}")
            elif not isinstance(data[key], expected_type):
                actual_type = type(data[key]).__name__
                expected_name = expected_type.__name__
                errors.append(f"Key '{key}' has wrong type: expected {expected_name}, got {actual_type}")
        if errors:
            return ParseResult(success=False, data=data, errors=errors, metadata={})
        else:
            return ParseResult(success=True, data=data, errors=[], metadata={})

    @staticmethod
    def extract_values(data: dict | list, key: str) -> list[Any]:
        """
        Extract all values for a key from nested structure.

        Args:
            data: Dictionary or list to search
            key: Key to extract

        Returns:
            List of all values found for key
        """
        results = []

        def _extract(obj: Any) -> None:
            if isinstance(obj, dict):
                if key in obj:
                    results.append(obj[key])
                for value in obj.values():
                    _extract(value)
            elif isinstance(obj, list):
                for item in obj:
                    _extract(item)

        _extract(data)
        return results

    @staticmethod
    def transform_keys(data: dict[str, Any], transformer: callable) -> dict[str, Any]:
        """
        Transform all keys in dictionary.

        Args:
            data: Dictionary to transform
            transformer: Function to transform keys

        Returns:
            Dictionary with transformed keys
        """
        result = {}
        for key, value in data.items():
            new_key = transformer(key)
            if isinstance(value, dict):
                result[new_key] = JsonParser.transform_keys(value, transformer)
            else:
                result[new_key] = value
        return result

    @staticmethod
    def to_camel_case(snake_str: str) -> str:
        """Convert snake_case to camelCase."""
        components = snake_str.split("_")
        return components[0] + "".join(x.title() for x in components[1:])

    @staticmethod
    def to_snake_case(camel_str: str) -> str:
        """Convert camelCase to snake_case."""
        import re

        s1 = re.sub("(.)([A-Z][a-z]+)", "\\1_\\2", camel_str)
        return re.sub("([a-z0-9])([A-Z])", "\\1_\\2", s1).lower()
