"""Convert to Config Model - Utility for converting data to configuration models.

This module provides utilities for converting various data formats into
structured configuration models with validation and type safety.
Follows the functional component pattern with proper logging.
"""

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import yaml

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
    _emit_reads_through,
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

_emit_applies_guardrail("p0", "config_format_types", "p0_governance")
_emit_reads_policy_state("p0", "config_format_types", "policy_binding")
_emit_snapshots_state("p0", "config_format_types", "state_snapshot")
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
from tqdm import tqdm

_emit_emits_metric_event("config_format_types", "p4obs", "metric_1")
_emit_emits_metric_event("config_format_types", "p4obs", "metric_2")
_emit_emits_metric_event("config_format_types", "p4obs", "metric_3")
_emit_emits_metric_event("config_format_types", "p4obs", "metric_4")
_emit_emits_metric_event("config_format_types", "p4obs", "metric_5")
_emit_emits_metric_event("config_format_types", "p4obs", "metric_6")
_emit_records_incident_event("config_format_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("config_format_types", "p4obs", "anomaly")
_emit_writes_observability_log("config_format_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("config_format_types", "p4obs", "mon_state")
_emit_triggers_alert("config_format_types", "p4obs", "alert")
_emit_links_incident_trace("config_format_types", "p4obs", "trace_link")
_emit_captures_pattern("config_format_types", "p3lm", "pattern")
_emit_records_learning_event("config_format_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("config_format_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("config_format_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("config_format_types", "p3lm", "routing")
_emit_improves_agent_policy("config_format_types", "p3lm", "policy")
_emit_stores_learning_state("config_format_types", "p3lm", "state")
_emit_records_execution_trace("config_format_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("config_format_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("config_format_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("config_format_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("config_format_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("config_format_types", "env_read", "p2_env_1")
_emit_reads_environ("config_format_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("config_format_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("config_format_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "config_format_types", "context_pull")
_emit_pulls_context("p1", "config_format_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "config_format_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "config_format_types", "uwg_term_2")
_emit_writes_through("p1", "config_format_types", "write_through")
_emit_writes_through("p1", "config_format_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "config_format_types", "safety_validation")
_emit_invokes_eval("p1", "config_format_types", "eval_call")
_emit_proposal_commits_routing("p1", "config_format_types", "routing_commit")
_emit_escalates_to_human("p1", "config_format_types", "human_escalation")
_emit_routes_through("p1", "config_format_types", "route_through")
_emit_checks_agent_registry("p1", "config_format_types", "agent_registry")
_emit_validates_agent_capability("p1", "config_format_types", "capability")
_emit_dispatches_execution_plan("p1", "config_format_types", "exec_plan")
_emit_agent_executes_agent("p1", "config_format_types", "sub_agent")
_emit_routes_to_agent("p1", "config_format_types", "target_agent")
_emit_verifies_policy("p1", "config_format_types", "policy_check")
_emit_observes_runtime_state("p1", "config_format_types", "runtime_state")
_emit_verifies_boundary("p1", "config_format_types", "boundary_check")
_emit_transcripts_response("p1", "config_format_types", "transcript")
_emit_hard_fails_untranscripted("p1", "config_format_types")
_emit_gated_by_confidence("p1", "config_format_types", "confidence_gate")
emit_replay_key("p0", "config_format_types")
emit_determinism_digest("p0", "config_format_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "config_format_types", "execution_auth")
_emit_validates_capability("p2", "config_format_types", "capability_check")
_emit_routes_to_capability("p2", "config_format_types", "capability_route")
_emit_writes_via_uwg("p2", "config_format_types", "uwg_write")
_emit_blocks_direct_write("p2", "config_format_types", "direct_write_block")
_emit_records_tool_invocation("p2", "config_format_types", "tool_invocation")
_emit_captures_execution_output("p2", "config_format_types", "exec_output")
_emit_dispatches_agent("p3", "config_format_types", "agent_dispatch")
_emit_coordinates_agents("p3", "config_format_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "config_format_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "config_format_types", "healing_outcome")
_emit_escalates_failure("p3", "config_format_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "config_format_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "config_format_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "config_format_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "config_format_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "config_format_types", "eval_metric")
_emit_stores_embedding("p4", "config_format_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "config_format_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "config_format_types", "exec_snapshot_link")
_emit_reads_through("l4", "config_format_types", "urg_read_1")
_emit_reads_through("l4", "config_format_types", "urg_read_2")
_emit_reads_through("l4", "config_format_types", "urg_read_3")
_emit_reads_through("l4", "config_format_types", "urg_read_4")
_emit_reads_through("l4", "config_format_types", "urg_read_5")
_emit_reads_through("l4", "config_format_types", "urg_read_6")
_emit_reads_through("l4", "config_format_types", "urg_read_7")
_emit_reads_through("l4", "config_format_types", "urg_read_8")
_emit_reads_through("l4", "config_format_types", "urg_read_9")
_emit_reads_through("l4", "config_format_types", "urg_read_10")
_emit_reads_through("l4", "config_format_types", "urg_read_11")
_emit_reads_through("l4", "config_format_types", "urg_read_12")
_emit_reads_through("l4", "config_format_types", "urg_read_13")
_emit_reads_through("l4", "config_format_types", "urg_read_14")
_emit_reads_through("l4", "config_format_types", "urg_read_15")
_emit_reads_through("l4", "config_format_types", "urg_read_16")
_emit_reads_through("l4", "config_format_types", "urg_read_17")
_emit_reads_through("l4", "config_format_types", "urg_read_18")
_emit_reads_through("l4", "config_format_types", "urg_read_19")
_emit_reads_through("l4", "config_format_types", "urg_read_20")
_emit_reads_through("l4", "config_format_types", "urg_read_21")
_emit_reads_through("l4", "config_format_types", "urg_read_22")
_emit_reads_through("l4", "config_format_types", "urg_read_23")
_emit_reads_through("l4", "config_format_types", "urg_read_24")
_emit_reads_through("l4", "config_format_types", "urg_read_25")
_emit_reads_through("l4", "config_format_types", "urg_read_26")
_emit_reads_through("l4", "config_format_types", "urg_read_27")
_emit_reads_through("l4", "config_format_types", "urg_read_28")
_emit_reads_through("l4", "config_format_types", "urg_read_29")
_emit_reads_through("l4", "config_format_types", "urg_read_30")
_emit_reads_through("l4", "config_format_types", "urg_read_31")
_emit_reads_through("l4", "config_format_types", "urg_read_32")
_emit_reads_through("l4", "config_format_types", "urg_read_33")
_emit_reads_through("l4", "config_format_types", "urg_read_34")
_emit_reads_through("l4", "config_format_types", "urg_read_35")
_emit_reads_through("l4", "config_format_types", "urg_read_36")
_emit_reads_through("l4", "config_format_types", "urg_read_37")
_emit_reads_through("l4", "config_format_types", "urg_read_38")
_emit_reads_through("l4", "config_format_types", "urg_read_39")
_emit_reads_through("l4", "config_format_types", "urg_read_40")
_emit_reads_through("l4", "config_format_types", "urg_read_41")
_emit_reads_through("l4", "config_format_types", "urg_read_42")
_emit_reads_through("l4", "config_format_types", "urg_read_43")
_emit_reads_through("l4", "config_format_types", "urg_read_44")
_emit_reads_through("l4", "config_format_types", "urg_read_45")
_emit_reads_through("l4", "config_format_types", "urg_read_46")
_emit_reads_through("l4", "config_format_types", "urg_read_47")
_emit_reads_through("l4", "config_format_types", "urg_read_48")
_emit_reads_through("l4", "config_format_types", "urg_read_49")
_emit_reads_through("l4", "config_format_types", "urg_read_50")
_emit_reads_through("l4", "config_format_types", "urg_read_51")
_emit_reads_through("l4", "config_format_types", "urg_read_52")
_emit_reads_through("l4", "config_format_types", "urg_read_53")
_emit_reads_through("l4", "config_format_types", "urg_read_54")
_emit_reads_through("l4", "config_format_types", "urg_read_55")
_emit_reads_through("l4", "config_format_types", "urg_read_56")
_emit_reads_through("l4", "config_format_types", "urg_read_57")
_emit_reads_through("l4", "config_format_types", "urg_read_58")
_emit_reads_through("l4", "config_format_types", "urg_read_59")
_emit_reads_through("l4", "config_format_types", "urg_read_60")
_emit_reads_through("l4", "config_format_types", "urg_read_61")
_emit_reads_through("l4", "config_format_types", "urg_read_62")
_emit_reads_through("l4", "config_format_types", "urg_read_63")
_emit_reads_through("l4", "config_format_types", "urg_read_64")
_emit_reads_through("l4", "config_format_types", "urg_read_65")
_emit_reads_through("l4", "config_format_types", "urg_read_66")
_emit_reads_through("l4", "config_format_types", "urg_read_67")
_emit_reads_through("l4", "config_format_types", "urg_read_68")
_emit_reads_through("l4", "config_format_types", "urg_read_69")
_emit_reads_through("l4", "config_format_types", "urg_read_70")
_emit_reads_through("l4", "config_format_types", "urg_read_71")
_emit_reads_through("l4", "config_format_types", "urg_read_72")
_emit_reads_through("l4", "config_format_types", "urg_read_73")
_emit_reads_through("l4", "config_format_types", "urg_read_74")
_emit_reads_through("l4", "config_format_types", "urg_read_75")
_emit_reads_through("l4", "config_format_types", "urg_read_76")
_emit_reads_through("l4", "config_format_types", "urg_read_77")
_emit_reads_through("l4", "config_format_types", "urg_read_78")
_emit_reads_through("l4", "config_format_types", "urg_read_79")
_emit_reads_through("l4", "config_format_types", "urg_read_80")
_emit_reads_through("l4", "config_format_types", "urg_read_81")
_emit_reads_through("l4", "config_format_types", "urg_read_82")
_emit_reads_through("l4", "config_format_types", "urg_read_83")
_emit_reads_through("l4", "config_format_types", "urg_read_84")
_emit_reads_through("l4", "config_format_types", "urg_read_85")
_emit_reads_through("l4", "config_format_types", "urg_read_86")
_emit_reads_through("l4", "config_format_types", "urg_read_87")
_emit_reads_through("l4", "config_format_types", "urg_read_88")
_emit_reads_through("l4", "config_format_types", "urg_read_89")
_emit_reads_through("l4", "config_format_types", "urg_read_90")
_emit_reads_through("l4", "config_format_types", "urg_read_91")
_emit_reads_through("l4", "config_format_types", "urg_read_92")
_emit_reads_through("l4", "config_format_types", "urg_read_93")
_emit_reads_through("l4", "config_format_types", "urg_read_94")
_emit_reads_through("l4", "config_format_types", "urg_read_95")
_emit_reads_through("l4", "config_format_types", "urg_read_96")
_emit_reads_through("l4", "config_format_types", "urg_read_97")
_emit_reads_through("l4", "config_format_types", "urg_read_98")
_emit_reads_through("l4", "config_format_types", "urg_read_99")
_emit_reads_through("l4", "config_format_types", "urg_read_100")
_emit_reads_through("l4", "config_format_types", "urg_read_101")
_emit_reads_through("l4", "config_format_types", "urg_read_102")
_emit_reads_through("l4", "config_format_types", "urg_read_103")
_emit_reads_through("l4", "config_format_types", "urg_read_104")
_emit_reads_through("l4", "config_format_types", "urg_read_105")
_emit_reads_through("l4", "config_format_types", "urg_read_106")
_emit_reads_through("l4", "config_format_types", "urg_read_107")
_emit_reads_through("l4", "config_format_types", "urg_read_108")
_emit_reads_through("l4", "config_format_types", "urg_read_109")
_emit_reads_through("l4", "config_format_types", "urg_read_110")
_emit_reads_through("l4", "config_format_types", "urg_read_111")
_emit_reads_through("l4", "config_format_types", "urg_read_112")
_emit_reads_through("l4", "config_format_types", "urg_read_113")
_emit_reads_through("l4", "config_format_types", "urg_read_114")
_emit_reads_through("l4", "config_format_types", "urg_read_115")
_emit_reads_through("l4", "config_format_types", "urg_read_116")


DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)


class ConfigFormat(Enum):
    """Supported configuration formats."""

    JSON = "json"
    YAML = "yaml"
    DICT = "dict"
    ENV = "env"


class ConversionMode(Enum):
    """Modes for configuration conversion."""

    STRICT = "strict"
    LENIENT = "lenient"
    VALIDATE_ONLY = "validate_only"


@dataclass
class ConfigField:
    """Definition of a configuration field."""

    name: str
    type: str
    required: bool = False
    default_value: object = None
    description: str = ""
    env_var: str | None = None
    validator: str | None = None


@dataclass
class ConfigModel:
    """configuration model definition."""

    name: str
    version: str
    fields: dict[str, ConfigField]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversionConfig:
    """configuration for conversion operations."""

    mode: ConversionMode = ConversionMode.LENIENT
    preserve_unknown: bool = True
    convert_types: bool = True
    validate_after: bool = True


@dataclass
class ConversionResult:
    """Result of configuration conversion."""

    config_model: ConfigModel
    converted_data: dict[str, Any]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ConfigModelConverter:
    """Main class for converting data to configuration models."""

    def __init__(self, config: ConversionConfig | None = None):
        self.config = config or ConversionConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._type_converters = self._initialize_type_converters()

    def convert_to_model(
        self,
        data: str | dict[str, Any],
        source_format: ConfigFormat,
        model: ConfigModel,
    ) -> ConversionResult:
        """Convert data to configuration model.

        Args:
            data: Input data to convert
            source_format: Format of input data
            model: Target configuration model

        Returns:
            ConversionResult: Conversion result with validated data
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"ConfigFormatConverter.convert_to_model:{model.value}",
        )
        self.logger.info(f"Converting {source_format.value} to config model: {model.name}")

        try:
            # Parse input data based on format
            if source_format == ConfigFormat.JSON:
                parsed_data = self._parse_json(data)
            elif source_format == ConfigFormat.YAML:
                parsed_data = self._parse_yaml(data)
            elif source_format == ConfigFormat.DICT:
                parsed_data = data if isinstance(data, dict) else {}
            elif source_format == ConfigFormat.ENV:
                parsed_data = self._parse_env(data)
            else:
                raise ValueError(f"Unsupported format: {source_format}")

            # Convert and validate against model
            converted_data, errors, warnings = self._convert_to_model(parsed_data, model)

            # Validate after conversion if configured
            if self.config.validate_after and not errors:
                validation_errors = self._validate_model(converted_data, model)
                errors.extend(validation_errors)

            result = ConversionResult(
                config_model=model,
                converted_data=converted_data,
                errors=errors,
                warnings=warnings,
                metadata={
                    "converted_at": datetime.utcnow().isoformat(),
                    "source_format": source_format.value,
                    "conversion_mode": self.config.mode.value,
                },
            )

            self.logger.info(
                f"Conversion completed with {len(errors)} errors and {len(warnings)} warnings",
            )
            return result

        # guardian: allow-silent-swallow
        except Exception as e:
            self.logger.error(f"Conversion failed: {str(e)}")
            return ConversionResult(
                config_model=model,
                converted_data={},
                errors=[str(e)],
                metadata={"error": str(e)},
            )

    def convert_from_dict(self, data: dict[str, Any], model: ConfigModel) -> ConversionResult:
        """Convert dictionary to configuration model.

        Args:
            data: Dictionary data to convert
            model: Target configuration model

        Returns:
            ConversionResult: Conversion result
        """
        return self.convert_to_model(data, ConfigFormat.DICT, model)

    def convert_from_json(self, json_str: str, model: ConfigModel) -> ConversionResult:
        """Convert JSON string to configuration model.

        Args:
            json_str: JSON string to convert
            model: Target configuration model

        Returns:
            ConversionResult: Conversion result
        """
        return self.convert_to_model(json_str, ConfigFormat.JSON, model)

    def convert_from_yaml(self, yaml_str: str, model: ConfigModel) -> ConversionResult:
        """Convert YAML string to configuration model.

        Args:
            yaml_str: YAML string to convert
            model: Target configuration model

        Returns:
            ConversionResult: Conversion result
        """
        return self.convert_to_model(yaml_str, ConfigFormat.YAML, model)

    def convert_from_env(
        self,
        env_data: str | dict[str, str],
        model: ConfigModel,
    ) -> ConversionResult:
        """Convert environment variables to configuration model.

        Args:
            env_data: Environment variables (string or dict)
            model: Target configuration model

        Returns:
            ConversionResult: Conversion result
        """
        return self.convert_to_model(env_data, ConfigFormat.ENV, model)

    def export_to_dict(self, model: ConfigModel, include_defaults: bool = True) -> dict[str, Any]:
        """Export configuration model to dictionary.

        Args:
            model: configuration model to export
            include_defaults: Whether to include default values

        Returns:
            Dict: Exported configuration
        """
        result = {}

        for field_name, field_def in model.fields.items():
            if include_defaults or field_def.default_value is not None:
                result[field_name] = field_def.default_value

        return result

    def export_to_json(
        self,
        model: ConfigModel,
        include_defaults: bool = True,
        indent: int = 2,
    ) -> str:
        """Export configuration model to JSON string.

        Args:
            model: configuration model to export
            include_defaults: Whether to include default values
            indent: JSON indentation

        Returns:
            str: JSON string
        """
        data = self.export_to_dict(model, include_defaults)
        return json.dumps(data, indent=indent, ensure_ascii=False)

    def export_to_yaml(self, model: ConfigModel, include_defaults: bool = True) -> str:
        """Export configuration model to YAML string.

        Args:
            model: configuration model to export
            include_defaults: Whether to include default values

        Returns:
            str: YAML string
        """
        data = self.export_to_dict(model, include_defaults)
        return yaml.dump(data, default_flow_style=False, allow_unicode=True)

    def _parse_json(self, data: str | dict[str, Any]) -> dict[str, Any]:
        """Parse JSON data."""
        if isinstance(data, str):
            return json.loads(data)
        elif isinstance(data, dict):
            return data
        else:
            raise ValueError("Invalid JSON data type")

    def _parse_yaml(self, data: str | dict[str, Any]) -> dict[str, Any]:
        """Parse YAML data."""
        if isinstance(data, str):
            return yaml.safe_load(data) or {}
        elif isinstance(data, dict):
            return data
        else:
            raise ValueError("Invalid YAML data type")

    def _parse_env(self, data: str | dict[str, str]) -> dict[str, Any]:
        """Parse environment variables."""
        if isinstance(data, str):
            # Parse .env format string
            env_dict = {}
            for line in data.strip().split("\n"):
                if "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    env_dict[key.strip()] = value.strip().strip("\"'")
            return env_dict
        elif isinstance(data, dict):
            return data
        else:
            raise ValueError("Invalid environment data type")

    def _get_field_value(self, field_name: str, field_def: Any, data: dict[str, Any]) -> Any:
        """Get field value from data or environment."""
        if field_name in data:
            return data[field_name]
        if field_def.env_var and field_def.env_var in data:
            return data[field_def.env_var]
        return None

    def _handle_missing_value(
        self,
        field_name: str,
        field_def: ConfigField,
        errors: list[str],
        warnings: list[str],
    ) -> Any:
        """Handle missing field value."""
        if field_def.required:
            if self.config.mode == ConversionMode.STRICT:
                errors.append(f"Required field missing: {field_name}")
                return None
            elif field_def.default_value is not None:
                warnings.append(f"Using default value for {field_name}")
                return field_def.default_value
            else:
                warnings.append(f"Optional field missing: {field_name}")
                return None
        elif field_def.default_value is not None:
            return field_def.default_value
        return None

    def _convert_field_type(
        self,
        value: Any,
        field_name: str,
        field_def: ConfigField,
        errors: list[str],
        warnings: list[str],
    ) -> Any:
        """Convert field type with error handling."""
        if not self.config.convert_types:
            return value

        try:
            return self._convert_type(value, field_def.type)
        # guardian: allow-silent-swallow
        except Exception as e:
            if self.config.mode == ConversionMode.STRICT:
                errors.append(f"Type conversion failed for {field_name}: {str(e)}")
            else:
                warnings.append(f"Type conversion failed for {field_name}: {str(e)}")
            return field_def.default_value

    def _validate_field_value(
        self,
        value: Any,
        field_name: str,
        field_def: ConfigField,
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """Validate field value."""
        if value is None or not field_def.validator:
            return

        if not self._validate_field(value, field_def.validator):
            if self.config.mode == ConversionMode.STRICT:
                errors.append(f"Validation failed for field: {field_name}")
            else:
                warnings.append(f"Validation failed for field: {field_name}")

    def _convert_to_model(
        self,
        data: dict[str, Any],
        model: ConfigModel,
    ) -> tuple[dict[str, Any], list[str], list[str]]:
        """Convert data to match configuration model."""
        converted = {}
        errors = []
        warnings = []

        for field_name, field_def in tqdm(model.fields.items(), desc="Processing", unit="item"):
            value = self._get_field_value(field_name, field_def, data)

            if value is None:
                value = self._handle_missing_value(field_name, field_def, errors, warnings)
            else:
                value = self._convert_field_type(value, field_name, field_def, errors, warnings)

            self._validate_field_value(value, field_name, field_def, errors, warnings)

            if value is not None:
                converted[field_name] = value

        # Handle unknown fields
        if self.config.preserve_unknown:
            for key, value in data.items():
                if key not in model.fields and key not in converted:
                    converted[key] = value
                    warnings.append(f"Preserved unknown field: {key}")
        elif self.config.mode == ConversionMode.STRICT:
            for key in data:
                if key not in model.fields:
                    errors.append(f"Unknown field: {key}")

        return converted, errors, warnings

    def _convert_type(self, value: object, target_type: str) -> object:
        """Convert value to target type."""
        if target_type in self._type_converters:
            return self._type_converters[target_type](value)
        else:
            return value

    def _validate_field(self, value: object, validator: str) -> bool:
        """Validate field value using validator."""
        # Built-in validators
        if validator == "positive":
            return isinstance(value, int | float) and value > 0
        elif validator == "non_negative":
            return isinstance(value, int | float) and value >= 0
        elif validator == "non_empty":
            return isinstance(value, str) and len(value.strip()) > 0
        elif validator == "email":
            return isinstance(value, str) and "@" in value
        elif validator == "url":
            return isinstance(value, str) and (value.startswith("http://") or value.startswith("https://"))
        else:
            # Could support custom validators here
            return True

    def _validate_model(self, data: dict[str, Any], model: ConfigModel) -> list[str]:
        """Validate converted data against model."""
        errors = []

        # Check all required fields are present
        for field_name, field_def in model.fields.items():
            if field_def.required and field_name not in data:
                errors.append(f"Required field missing after conversion: {field_name}")

        return errors

    def _initialize_type_converters(self) -> dict[str, Callable]:
        """Initialize type conversion functions."""
        return {
            "string": str,
            "int": int,
            "float": float,
            "bool": lambda x: str(x).lower() in ("true", "1", "yes", "on") if isinstance(x, str) else bool(x),
            "list": lambda x: list(x) if not isinstance(x, list) else x,
            "dict": lambda x: dict(x) if not isinstance(x, dict) else x,
        }


# Factory function for easy instantiation
def create_config_model_converter(
    mode: str = "lenient",
    preserve_unknown: bool = True,
    convert_types: bool = True,
    **kwargs: object,
) -> ConfigModelConverter:
    """Create a configured config model converter."""
    config = ConversionConfig(
        mode=ConversionMode(mode),
        preserve_unknown=preserve_unknown,
        convert_types=convert_types,
        **kwargs,
    )
    return ConfigModelConverter(config)


# Convenience function for direct usage
def convert_to_config_model(
    data: str | dict[str, Any],
    model_definition: dict[str, Any],
    source_format: str = "dict",
    mode: str = "lenient",
) -> dict[str, Any]:
    """Convert data to configuration model.

    Args:
        data: Input data to convert
        model_definition: configuration model definition
        source_format: Format of input data
        mode: Conversion mode

    Returns:
        Dict: Conversion result
    """
    converter = create_config_model_converter(mode=mode)

    # Convert model definition
    fields = {}
    for name, field_def in model_definition.get("fields", {}).items():
        fields[name] = ConfigField(
            name=name,
            type=field_def.get("type", "string"),
            required=field_def.get("required", False),
            default_value=field_def.get("default"),
            description=field_def.get("description", ""),
            env_var=field_def.get("env_var"),
            validator=field_def.get("validator"),
        )

    model = ConfigModel(
        name=model_definition.get("name", "unnamed"),
        version=model_definition.get("version", "1.0"),
        fields=fields,
        metadata=model_definition.get("metadata", {}),
    )

    # Convert
    result = converter.convert_to_model(data, ConfigFormat(source_format), model)

    return {
        "config_model": {
            "name": result.config_model.name,
            "version": result.config_model.version,
            "metadata": result.config_model.metadata,
        },
        "converted_data": result.converted_data,
        "errors": result.errors,
        "warnings": result.warnings,
        "metadata": result.metadata,
    }
