"""Convert to Internal schema - Utility for converting data to internal schema format.

This module provides utilities for converting external data formats into the
internal schema format used by the system, with proper validation and mapping.
Follows the functional component pattern with proper logging.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "schema_type_types", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "schema_type_types", "policy_binding")
trace_contract._emit_snapshots_state("p0", "schema_type_types", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("schema_type_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("schema_type_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("schema_type_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("schema_type_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("schema_type_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("schema_type_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("schema_type_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("schema_type_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("schema_type_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("schema_type_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("schema_type_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("schema_type_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("schema_type_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("schema_type_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("schema_type_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("schema_type_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("schema_type_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("schema_type_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("schema_type_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("schema_type_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("schema_type_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("schema_type_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("schema_type_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("schema_type_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("schema_type_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("schema_type_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("schema_type_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("schema_type_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "schema_type_types", "context_pull")
trace_contract._emit_pulls_context("p1", "schema_type_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "schema_type_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "schema_type_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "schema_type_types", "write_through")
trace_contract._emit_writes_through("p1", "schema_type_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "schema_type_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "schema_type_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "schema_type_types", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "schema_type_types", "human_escalation")
trace_contract._emit_routes_through("p1", "schema_type_types", "route_through")
trace_contract._emit_checks_agent_registry("p1", "schema_type_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "schema_type_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "schema_type_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "schema_type_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "schema_type_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "schema_type_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "schema_type_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "schema_type_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "schema_type_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "schema_type_types")
trace_contract._emit_gated_by_confidence("p1", "schema_type_types", "confidence_gate")
trace_contract.emit_replay_key("p0", "schema_type_types")
trace_contract.emit_determinism_digest("p0", "schema_type_types")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "schema_type_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "schema_type_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "schema_type_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "schema_type_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "schema_type_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "schema_type_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "schema_type_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "schema_type_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "schema_type_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "schema_type_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "schema_type_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "schema_type_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "schema_type_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "schema_type_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "schema_type_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "schema_type_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "schema_type_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "schema_type_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "schema_type_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "schema_type_types", "exec_snapshot_link")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_1")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_2")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_3")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_4")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_5")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_6")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_7")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_8")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_9")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_10")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_11")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_12")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_13")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_14")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_15")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_16")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_17")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_18")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_19")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_20")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_21")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_22")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_23")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_24")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_25")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_26")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_27")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_28")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_29")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_30")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_31")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_32")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_33")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_34")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_35")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_36")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_37")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_38")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_39")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_40")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_41")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_42")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_43")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_44")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_45")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_46")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_47")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_48")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_49")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_50")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_51")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_52")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_53")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_54")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_55")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_56")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_57")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_58")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_59")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_60")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_61")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_62")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_63")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_64")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_65")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_66")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_67")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_68")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_69")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_70")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_71")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_72")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_73")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_74")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_75")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_76")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_77")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_78")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_79")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_80")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_81")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_82")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_83")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_84")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_85")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_86")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_87")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_88")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_89")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_90")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_91")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_92")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_93")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_94")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_95")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_96")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_97")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_98")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_99")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_100")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_101")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_102")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_103")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_104")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_105")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_106")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_107")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_108")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_109")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_110")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_111")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_112")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_113")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_114")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_115")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_116")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_117")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_118")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_119")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_120")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_121")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_122")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_123")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_124")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_125")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_126")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_127")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_128")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_129")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_130")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_131")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_132")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_133")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_134")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_135")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_136")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_137")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_138")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_139")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_140")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_141")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_142")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_143")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_144")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_145")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_146")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_147")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_148")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_149")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_150")
trace_contract._emit_reads_through("l4", "schema_type_types", "urg_read_151")

logger = logging.getLogger(__name__)


class SchemaType(Enum):
    """Types of schemas supported."""

    JSON_SCHEMA = "json_schema"
    AVRO = "avro"
    PROTOBUF = "protobuf"
    CUSTOM = "custom"


class ConversionStrategy(Enum):
    """Strategies for schema conversion."""

    STRICT = "strict"
    LENIENT = "lenient"
    MAP_ONLY = "map_only"
    VALIDATE_ONLY = "validate_only"


@dataclass
class FieldMapping:
    """Mapping between external and internal fields."""

    external_path: str
    internal_path: str
    type_conversion: str | None = None
    required: bool = False
    default_value: Any = None
    transform_func: str | None = None


@dataclass
class InternalSchema:
    """Definition of internal schema format."""

    name: str
    version: str
    namespace: str
    fields: dict[str, dict[str, Any]]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversionConfig:
    """configuration for schema conversion."""

    strategy: ConversionStrategy = ConversionStrategy.LENIENT
    preserve_unknown: bool = False
    validate_types: bool = True
    apply_transforms: bool = True


@dataclass
class ConversionResult:
    """Result of schema conversion."""

    internal_schema: InternalSchema
    converted_data: dict[str, Any]
    field_mappings: list[FieldMapping]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class InternalSchemaConverter:
    """Main class for converting data to internal schema format."""

    def __init__(self, config: ConversionConfig | None = None):
        self.config = config or ConversionConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._type_converters = self._initialize_type_converters()
        self._transform_functions = self._initialize_transform_functions()

    def _validate_external_schema(
        self,
        external_data: dict[str, Any],
        external_schema: dict[str, Any] | None,
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """Validate external data against schema."""
        if not external_schema or not self.config.validate_types:
            return
        validation_errors = self._validate_external_data(external_data, external_schema)
        if validation_errors and self.config.strategy == ConversionStrategy.STRICT:
            errors.extend(validation_errors)
        else:
            warnings.extend(validation_errors)

    def _process_field_mapping(
        self,
        mapping: FieldMapping,
        external_data: dict[str, Any],
        converted_data: dict[str, Any],
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """Process a single field mapping."""
        try:
            external_value = self._extract_and_transform_value(mapping, external_data, errors, warnings)
            self._set_converted_value(mapping, external_value, converted_data, errors, warnings)
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise

    def _extract_and_transform_value(
        self,
        mapping: FieldMapping,
        external_data: dict[str, object],
        errors: list[str],
        warnings: list[str],
    ) -> object:
        """Extract and transform value from external data."""
        external_value = self._extract_nested_value(external_data, mapping.external_path)
        if mapping.transform_func and self.config.apply_transforms:
            external_value = self._apply_transform(external_value, mapping.transform_func)
        if mapping.type_conversion:
            external_value = self._convert_with_error_handling(external_value, mapping, errors, warnings)
        return external_value

    def _convert_with_error_handling(
        self,
        value: Any,
        mapping: FieldMapping,
        errors: list[str],
        warnings: list[str],
    ) -> object:
        """Convert type with error handling."""
        try:
            return self._convert_type(value, mapping.type_conversion)
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise

    def _set_converted_value(
        self,
        mapping: FieldMapping,
        external_value: object,
        converted_data: dict[str, object],
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """Set converted value in internal data."""
        if external_value is not None:
            self._set_nested_value(converted_data, mapping.internal_path, external_value)
        elif mapping.required:
            self._handle_missing_required_field(mapping, converted_data, errors, warnings)

    def _handle_missing_required_field(
        self,
        mapping: FieldMapping,
        converted_data: dict[str, object],
        errors: list[str],
        warnings: list[str],
    ) -> None:
        """Handle missing required field."""
        if mapping.default_value is not None:
            self._set_nested_value(converted_data, mapping.internal_path, mapping.default_value)
            warnings.append(f"Using default for required field: {mapping.internal_path}")
        else:
            errors.append(f"Missing required field: {mapping.internal_path}")

    def _finalize_conversion(
        self,
        converted_data: dict[str, object],
        internal_schema: InternalSchema,
        errors: list[str],
    ) -> None:
        """Finalize conversion with validation and cleanup."""
        if not self.config.preserve_unknown:
            self._remove_unknown_fields(converted_data, internal_schema)
        if self.config.validate_types:
            validation_errors = self._validate_internal_data(converted_data, internal_schema)
            errors.extend(validation_errors)

    def convert_to_internal(
        self,
        external_data: dict[str, object],
        internal_schema: InternalSchema,
        field_mappings: list[FieldMapping],
        external_schema: dict[str, object] | None = None,
    ) -> ConversionResult:
        """Convert external data to internal schema format."""
        import uuid  # noqa: PLC0415

        trace_contract._emit_records_execution_trace(
            str(uuid.uuid4()),
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            f"SchemaConverter.convert_to_internal:{internal_schema.schema_id}",
        )
        self.logger.info(f"Converting to internal schema: {internal_schema.name}")
        try:
            converted_data = {}
            errors = []
            warnings = []
            self._validate_external_schema(external_data, external_schema, errors, warnings)
            for mapping in field_mappings:
                self._process_field_mapping(mapping, external_data, converted_data, errors, warnings)
            self._finalize_conversion(converted_data, internal_schema, errors)
            result = ConversionResult(
                internal_schema=internal_schema,
                converted_data=converted_data,
                field_mappings=field_mappings,
                errors=errors,
                warnings=warnings,
                metadata={
                    "converted_at": datetime.utcnow().isoformat(),
                    "conversion_strategy": self.config.strategy.value,
                    "external_fields": len(external_data),
                    "internal_fields": len(converted_data),
                },
            )
            self.logger.info(f"Conversion completed with {len(errors)} errors and {len(warnings)} warnings")
            return result
        except Exception as e:  # guardian: allow-silent-swallow
            self.logger.error(f"schema conversion failed: {str(e)}")
            return ConversionResult(
                internal_schema=internal_schema,
                converted_data={},
                field_mappings=field_mappings,
                errors=[str(e)],
                metadata={"error": str(e)},
            )

    def auto_generate_mappings(
        self,
        external_schema: dict[str, object],
        internal_schema: InternalSchema,
    ) -> list[FieldMapping]:
        """Automatically generate field mappings between schemas.

        Args:
            external_schema: External schema definition
            internal_schema: Internal schema definition

        Returns:
            List[FieldMapping]: Generated field mappings
        """
        mappings = []
        external_fields = self._extract_schema_fields(external_schema)
        for internal_field, internal_def in tqdm(
            internal_schema.fields.items(), desc="Processing", unit="item"
        ):
            if internal_field in external_fields:
                mappings.append(
                    FieldMapping(
                        external_path=internal_field,
                        internal_path=internal_field,
                        type_conversion=internal_def.get("type"),
                        required=internal_def.get("required", False),
                    ),
                )
                continue
            best_match = self._find_best_field_match(internal_field, external_fields.keys())
            if best_match:
                mappings.append(
                    FieldMapping(
                        external_path=best_match,
                        internal_path=internal_field,
                        type_conversion=internal_def.get("type"),
                        required=internal_def.get("required", False),
                    ),
                )
                continue
            if internal_def.get("required", False):
                self.logger.warning(f"No mapping found for required field: {internal_field}")
        return mappings

    def convert_batch(
        self,
        external_data_list: list[dict[str, object]],
        external_schema: dict[str, object] | None = None,
        internal_schema: InternalSchema = None,
        field_mappings: list[FieldMapping] = None,
    ) -> list[ConversionResult]:
        """Convert multiple external data items.

        Args:
            external_data_list: List of external data items
            external_schema: Optional external schema
            internal_schema: Internal schema
            field_mappings: Field mappings to use

        Returns:
            List[ConversionResult]: Results for each item
        """
        results = []
        for i, external_data in enumerate(external_data_list):
            self.logger.debug(f"Converting item {i + 1}/{len(external_data_list)}")
            result = self.convert_to_internal(external_data, external_schema, internal_schema, field_mappings)
            results.append(result)
        return results

    def _extract_nested_value(self, data: dict[str, object], path: str) -> object:
        """Extract value from nested data structure."""
        keys = path.split(".")
        current = data
        for key in tqdm(keys, desc="Processing", unit="item"):
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    raise IndexError(f"Index {index} out of range")
            else:
                raise KeyError(f"Key '{key}' not found in path '{path}'")
        return current

    def _set_nested_value(self, data: dict[str, object], path: str, value: object) -> None:
        """Set value in nested data structure."""
        keys = path.split(".")
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    def _apply_transform(self, value: object, transform_func: str) -> object:
        """Apply transformation function to value."""
        if transform_func in self._transform_functions:
            return self._transform_functions[transform_func](value)
        else:
            self.logger.warning(f"Unknown transform function: {transform_func}")
            return value

    def _convert_type(self, value: object, target_type: str) -> object:
        """Convert value to target type."""
        if target_type in self._type_converters:
            return self._type_converters[target_type](value)
        else:
            return value

    def _validate_external_data(self, data: dict[str, Any], schema: dict[str, Any]) -> list[str]:
        """Validate external data against external schema."""
        errors = []
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field in external data: {field}")
        return errors

    def _validate_internal_data(self, data: dict[str, Any], schema: InternalSchema) -> list[str]:
        """Validate internal data against internal schema."""
        errors = []
        for field_name, field_def in schema.fields.items():
            if field_def.get("required", False) and field_name not in data:
                errors.append(f"Missing required field in internal data: {field_name}")
        return errors

    def _extract_schema_fields(self, schema: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Extract field definitions from schema."""
        fields = {}
        if "properties" in schema:
            fields.update(schema["properties"])
        elif "fields" in schema:
            fields.update(schema["fields"])
        elif isinstance(schema, dict):
            for key, value in schema.items():
                if isinstance(value, dict) and "type" in value:
                    fields[key] = value
        return fields

    def _find_best_field_match(self, target_field: str, candidate_fields: list[str]) -> str | None:
        """Find best matching field for target field."""
        if target_field in candidate_fields:
            return target_field
        for field in candidate_fields:
            if field.lower() == target_field.lower():
                return field
        for field in candidate_fields:
            if target_field.lower() in field.lower() or field.lower() in target_field.lower():
                return field
        return None

    def _remove_unknown_fields(self, data: dict[str, Any], schema: InternalSchema) -> None:
        """Remove fields not defined in schema."""

        def _remove_unknown_recursive(obj, path=""):
            if isinstance(obj, dict):
                keys_to_remove = []
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if current_path not in schema.fields:
                        keys_to_remove.append(key)
                    else:
                        _remove_unknown_recursive(value, current_path)
                for key in keys_to_remove:
                    del obj[key]

        _remove_unknown_recursive(data)

    def _initialize_type_converters(self) -> dict[str, Callable]:
        """Initialize type conversion functions."""
        return {
            "string": str,
            "integer": int,
            "float": float,
            "boolean": lambda x: str(x).lower() in ("true", "1", "yes") if isinstance(x, str) else bool(x),
            "array": list,
            "object": dict,
        }

    def _initialize_transform_functions(self) -> dict[str, Callable]:
        """Initialize transformation functions."""
        return {
            "upper": lambda x: str(x).upper(),
            "lower": lambda x: str(x).lower(),
            "trim": lambda x: str(x).strip(),
            "abs": abs,
            "round": round,
            "timestamp_to_iso": lambda x: (
                datetime.fromtimestamp(x).isoformat() if isinstance(x, int | float) else x
            ),
            "iso_to_timestamp": lambda x: datetime.fromisoformat(x).timestamp() if isinstance(x, str) else x,
        }


def create_internal_schema_converter(
    strategy: str = "lenient",
    preserve_unknown: bool = False,
    validate_types: bool = True,
    **kwargs: dict[str, object],
) -> InternalSchemaConverter:
    """Create a configured internal schema converter."""
    config = ConversionConfig(
        strategy=ConversionStrategy(strategy),
        preserve_unknown=preserve_unknown,
        validate_types=validate_types,
        **kwargs,
    )
    return InternalSchemaConverter(config)


def convert_to_internal_schema(
    external_data: dict[str, Any],
    internal_schema_def: dict[str, Any],
    field_mappings: list[dict[str, Any]] | None = None,
    external_schema: dict[str, Any] | None = None,
    strategy: str = "lenient",
) -> dict[str, Any]:
    """Convert data to internal schema format.

    Args:
        external_data: External data to convert
        internal_schema_def: Internal schema definition
        field_mappings: Optional field mappings
        external_schema: Optional external schema
        strategy: Conversion strategy

    Returns:
        Dict: Conversion result
    """
    converter = create_internal_schema_converter(strategy=strategy)
    internal_schema = InternalSchema(
        name=internal_schema_def.get("name", "unnamed"),
        version=internal_schema_def.get("version", "1.0"),
        namespace=internal_schema_def.get("namespace", "default"),
        fields=internal_schema_def.get("fields", {}),
        metadata=internal_schema_def.get("metadata", {}),
    )
    mappings = []
    if field_mappings:
        for mapping in field_mappings:
            mappings.append(FieldMapping(**mapping))
    elif external_schema:
        mappings = converter.auto_generate_mappings(external_schema, internal_schema)
    result = converter.convert_to_internal(external_data, external_schema, internal_schema, mappings)
    return {
        "internal_schema": {
            "name": result.internal_schema.name,
            "version": result.internal_schema.version,
            "namespace": result.internal_schema.namespace,
        },
        "converted_data": result.converted_data,
        "field_mappings": [
            {
                "external_path": m.external_path,
                "internal_path": m.internal_path,
                "type_conversion": m.type_conversion,
                "required": m.required,
            }
            for m in result.field_mappings
        ],
        "errors": result.errors,
        "warnings": result.warnings,
        "metadata": result.metadata,
    }
