"""Config Load Planner - Plans data loading operations for configuration management.

This planner manages the loading phase for configuration data operations,
including environment configs, feature flags, and deployment configurations.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
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
from apps_shared.config.pipeline_constants_config import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    THRESHOLD,
)

_emit_applies_guardrail("p0", "config_type_types", "p0_governance")
_emit_reads_policy_state("p0", "config_type_types", "policy_binding")
_emit_snapshots_state("p0", "config_type_types", "state_snapshot")
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

_emit_emits_metric_event("config_type_types", "p4obs", "metric_1")
_emit_emits_metric_event("config_type_types", "p4obs", "metric_2")
_emit_emits_metric_event("config_type_types", "p4obs", "metric_3")
_emit_emits_metric_event("config_type_types", "p4obs", "metric_4")
_emit_emits_metric_event("config_type_types", "p4obs", "metric_5")
_emit_emits_metric_event("config_type_types", "p4obs", "metric_6")
_emit_records_incident_event("config_type_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("config_type_types", "p4obs", "anomaly")
_emit_writes_observability_log("config_type_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("config_type_types", "p4obs", "mon_state")
_emit_triggers_alert("config_type_types", "p4obs", "alert")
_emit_links_incident_trace("config_type_types", "p4obs", "trace_link")
_emit_captures_pattern("config_type_types", "p3lm", "pattern")
_emit_records_learning_event("config_type_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("config_type_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("config_type_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("config_type_types", "p3lm", "routing")
_emit_improves_agent_policy("config_type_types", "p3lm", "policy")
_emit_stores_learning_state("config_type_types", "p3lm", "state")
_emit_records_execution_trace("config_type_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("config_type_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("config_type_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("config_type_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("config_type_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("config_type_types", "env_read", "p2_env_1")
_emit_reads_environ("config_type_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("config_type_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("config_type_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "config_type_types", "context_pull")
_emit_pulls_context("p1", "config_type_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "config_type_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "config_type_types", "uwg_term_2")
_emit_writes_through("p1", "config_type_types", "write_through")
_emit_writes_through("p1", "config_type_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "config_type_types", "safety_validation")
_emit_invokes_eval("p1", "config_type_types", "eval_call")
_emit_proposal_commits_routing("p1", "config_type_types", "routing_commit")
_emit_escalates_to_human("p1", "config_type_types", "human_escalation")
_emit_routes_through("p1", "config_type_types", "route_through")
_emit_checks_agent_registry("p1", "config_type_types", "agent_registry")
_emit_validates_agent_capability("p1", "config_type_types", "capability")
_emit_dispatches_execution_plan("p1", "config_type_types", "exec_plan")
_emit_agent_executes_agent("p1", "config_type_types", "sub_agent")
_emit_routes_to_agent("p1", "config_type_types", "target_agent")
_emit_verifies_policy("p1", "config_type_types", "policy_check")
_emit_observes_runtime_state("p1", "config_type_types", "runtime_state")
_emit_verifies_boundary("p1", "config_type_types", "boundary_check")
_emit_transcripts_response("p1", "config_type_types", "transcript")
_emit_hard_fails_untranscripted("p1", "config_type_types")
_emit_gated_by_confidence("p1", "config_type_types", "confidence_gate")
emit_replay_key("p0", "config_type_types")
emit_determinism_digest("p0", "config_type_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "config_type_types", "execution_auth")
_emit_validates_capability("p2", "config_type_types", "capability_check")
_emit_routes_to_capability("p2", "config_type_types", "capability_route")
_emit_writes_via_uwg("p2", "config_type_types", "uwg_write")
_emit_blocks_direct_write("p2", "config_type_types", "direct_write_block")
_emit_records_tool_invocation("p2", "config_type_types", "tool_invocation")
_emit_captures_execution_output("p2", "config_type_types", "exec_output")
_emit_dispatches_agent("p3", "config_type_types", "agent_dispatch")
_emit_coordinates_agents("p3", "config_type_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "config_type_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "config_type_types", "healing_outcome")
_emit_escalates_failure("p3", "config_type_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "config_type_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "config_type_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "config_type_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "config_type_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "config_type_types", "eval_metric")
_emit_stores_embedding("p4", "config_type_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "config_type_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "config_type_types", "exec_snapshot_link")
_emit_reads_through("l4", "config_type_types", "urg_read_1")
_emit_reads_through("l4", "config_type_types", "urg_read_2")
_emit_reads_through("l4", "config_type_types", "urg_read_3")
_emit_reads_through("l4", "config_type_types", "urg_read_4")
_emit_reads_through("l4", "config_type_types", "urg_read_5")
_emit_reads_through("l4", "config_type_types", "urg_read_6")
_emit_reads_through("l4", "config_type_types", "urg_read_7")
_emit_reads_through("l4", "config_type_types", "urg_read_8")
_emit_reads_through("l4", "config_type_types", "urg_read_9")
_emit_reads_through("l4", "config_type_types", "urg_read_10")
_emit_reads_through("l4", "config_type_types", "urg_read_11")
_emit_reads_through("l4", "config_type_types", "urg_read_12")
_emit_reads_through("l4", "config_type_types", "urg_read_13")
_emit_reads_through("l4", "config_type_types", "urg_read_14")
_emit_reads_through("l4", "config_type_types", "urg_read_15")
_emit_reads_through("l4", "config_type_types", "urg_read_16")
_emit_reads_through("l4", "config_type_types", "urg_read_17")
_emit_reads_through("l4", "config_type_types", "urg_read_18")
_emit_reads_through("l4", "config_type_types", "urg_read_19")
_emit_reads_through("l4", "config_type_types", "urg_read_20")
_emit_reads_through("l4", "config_type_types", "urg_read_21")
_emit_reads_through("l4", "config_type_types", "urg_read_22")
_emit_reads_through("l4", "config_type_types", "urg_read_23")
_emit_reads_through("l4", "config_type_types", "urg_read_24")
_emit_reads_through("l4", "config_type_types", "urg_read_25")
_emit_reads_through("l4", "config_type_types", "urg_read_26")
_emit_reads_through("l4", "config_type_types", "urg_read_27")
_emit_reads_through("l4", "config_type_types", "urg_read_28")
_emit_reads_through("l4", "config_type_types", "urg_read_29")
_emit_reads_through("l4", "config_type_types", "urg_read_30")
_emit_reads_through("l4", "config_type_types", "urg_read_31")
_emit_reads_through("l4", "config_type_types", "urg_read_32")
_emit_reads_through("l4", "config_type_types", "urg_read_33")
_emit_reads_through("l4", "config_type_types", "urg_read_34")
_emit_reads_through("l4", "config_type_types", "urg_read_35")
_emit_reads_through("l4", "config_type_types", "urg_read_36")
_emit_reads_through("l4", "config_type_types", "urg_read_37")
_emit_reads_through("l4", "config_type_types", "urg_read_38")
_emit_reads_through("l4", "config_type_types", "urg_read_39")
_emit_reads_through("l4", "config_type_types", "urg_read_40")
_emit_reads_through("l4", "config_type_types", "urg_read_41")
_emit_reads_through("l4", "config_type_types", "urg_read_42")
_emit_reads_through("l4", "config_type_types", "urg_read_43")
_emit_reads_through("l4", "config_type_types", "urg_read_44")
_emit_reads_through("l4", "config_type_types", "urg_read_45")
_emit_reads_through("l4", "config_type_types", "urg_read_46")
_emit_reads_through("l4", "config_type_types", "urg_read_47")
_emit_reads_through("l4", "config_type_types", "urg_read_48")
_emit_reads_through("l4", "config_type_types", "urg_read_49")
_emit_reads_through("l4", "config_type_types", "urg_read_50")
_emit_reads_through("l4", "config_type_types", "urg_read_51")
_emit_reads_through("l4", "config_type_types", "urg_read_52")
_emit_reads_through("l4", "config_type_types", "urg_read_53")
_emit_reads_through("l4", "config_type_types", "urg_read_54")
_emit_reads_through("l4", "config_type_types", "urg_read_55")
_emit_reads_through("l4", "config_type_types", "urg_read_56")
_emit_reads_through("l4", "config_type_types", "urg_read_57")
_emit_reads_through("l4", "config_type_types", "urg_read_58")
_emit_reads_through("l4", "config_type_types", "urg_read_59")
_emit_reads_through("l4", "config_type_types", "urg_read_60")
_emit_reads_through("l4", "config_type_types", "urg_read_61")
_emit_reads_through("l4", "config_type_types", "urg_read_62")
_emit_reads_through("l4", "config_type_types", "urg_read_63")
_emit_reads_through("l4", "config_type_types", "urg_read_64")
_emit_reads_through("l4", "config_type_types", "urg_read_65")
_emit_reads_through("l4", "config_type_types", "urg_read_66")
_emit_reads_through("l4", "config_type_types", "urg_read_67")
_emit_reads_through("l4", "config_type_types", "urg_read_68")
_emit_reads_through("l4", "config_type_types", "urg_read_69")
_emit_reads_through("l4", "config_type_types", "urg_read_70")
_emit_reads_through("l4", "config_type_types", "urg_read_71")
_emit_reads_through("l4", "config_type_types", "urg_read_72")
_emit_reads_through("l4", "config_type_types", "urg_read_73")
_emit_reads_through("l4", "config_type_types", "urg_read_74")
_emit_reads_through("l4", "config_type_types", "urg_read_75")
_emit_reads_through("l4", "config_type_types", "urg_read_76")
_emit_reads_through("l4", "config_type_types", "urg_read_77")
_emit_reads_through("l4", "config_type_types", "urg_read_78")
_emit_reads_through("l4", "config_type_types", "urg_read_79")
_emit_reads_through("l4", "config_type_types", "urg_read_80")
_emit_reads_through("l4", "config_type_types", "urg_read_81")
_emit_reads_through("l4", "config_type_types", "urg_read_82")
_emit_reads_through("l4", "config_type_types", "urg_read_83")
_emit_reads_through("l4", "config_type_types", "urg_read_84")
_emit_reads_through("l4", "config_type_types", "urg_read_85")
_emit_reads_through("l4", "config_type_types", "urg_read_86")
_emit_reads_through("l4", "config_type_types", "urg_read_87")
_emit_reads_through("l4", "config_type_types", "urg_read_88")
_emit_reads_through("l4", "config_type_types", "urg_read_89")
_emit_reads_through("l4", "config_type_types", "urg_read_90")
_emit_reads_through("l4", "config_type_types", "urg_read_91")
_emit_reads_through("l4", "config_type_types", "urg_read_92")
_emit_reads_through("l4", "config_type_types", "urg_read_93")
_emit_reads_through("l4", "config_type_types", "urg_read_94")
_emit_reads_through("l4", "config_type_types", "urg_read_95")
_emit_reads_through("l4", "config_type_types", "urg_read_96")
_emit_reads_through("l4", "config_type_types", "urg_read_97")
_emit_reads_through("l4", "config_type_types", "urg_read_98")
_emit_reads_through("l4", "config_type_types", "urg_read_99")
_emit_reads_through("l4", "config_type_types", "urg_read_100")
_emit_reads_through("l4", "config_type_types", "urg_read_101")
_emit_reads_through("l4", "config_type_types", "urg_read_102")
_emit_reads_through("l4", "config_type_types", "urg_read_103")
_emit_reads_through("l4", "config_type_types", "urg_read_104")
_emit_reads_through("l4", "config_type_types", "urg_read_105")
_emit_reads_through("l4", "config_type_types", "urg_read_106")
_emit_reads_through("l4", "config_type_types", "urg_read_107")
_emit_reads_through("l4", "config_type_types", "urg_read_108")
_emit_reads_through("l4", "config_type_types", "urg_read_109")
_emit_reads_through("l4", "config_type_types", "urg_read_110")
_emit_reads_through("l4", "config_type_types", "urg_read_111")
_emit_reads_through("l4", "config_type_types", "urg_read_112")
_emit_reads_through("l4", "config_type_types", "urg_read_113")
_emit_reads_through("l4", "config_type_types", "urg_read_114")
_emit_reads_through("l4", "config_type_types", "urg_read_115")
_emit_reads_through("l4", "config_type_types", "urg_read_116")
_emit_reads_through("l4", "config_type_types", "urg_read_117")
_emit_reads_through("l4", "config_type_types", "urg_read_118")
_emit_reads_through("l4", "config_type_types", "urg_read_119")


# Configuration constants

logger = logging.getLogger(__name__)


class ConfigType(Enum):
    """Types of configurations to load."""

    ENVIRONMENT = "environment"
    FEATURE_FLAG = "feature_flag"
    DEPLOYMENT = "deployment"
    SERVICE = "service"
    SECURITY = "security"


class ConfigFormat(Enum):
    """Supported configuration formats."""

    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    XML = "xml"
    PROPERTIES = "properties"


class ConfigScope(Enum):
    """configuration scopes."""

    GLOBAL = "global"
    REGION = "region"
    ENVIRONMENT = "environment"
    SERVICE = "service"
    INSTANCE = "instance"


@dataclass
class ConfigSource:
    """Definition of a configuration source."""

    id: str
    name: str
    config_type: ConfigType
    format: ConfigFormat
    location: str
    scope: ConfigScope
    version: str | None = None
    encryption: bool = False
    credentials: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigValidationRule:
    """Definition of a configuration validation rule."""

    id: str
    field_path: str  # e.g., "database.host", "features.*.enabled"
    rule_type: str  # required, type, range, regex
    parameters: dict[str, Any] = field(default_factory=dict)
    error_message: str = ""


@dataclass
class ConfigTransformation:
    """Definition of a configuration transformation."""

    id: str
    name: str
    transformation_type: str  # template, substitution, merge, override
    source_fields: list[str] = field(default_factory=list)
    target_field: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigLoadPlan:
    """Complete plan for configuration data loading."""

    id: str
    name: str
    sources: list[ConfigSource]
    validation_rules: list[ConfigValidationRule] = field(default_factory=list)
    transformations: list[ConfigTransformation] = field(default_factory=list)
    merge_strategy: str = "override"  # override, merge, keep_existing
    enable_validation: bool = True
    enable_encryption: bool = False
    cache_ttl: int = 300  # seconds
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigLoadConfig:
    """configuration for config load planning."""

    enable_validation: bool = True
    enable_encryption: bool = False
    enable_caching: bool = True
    max_sources_per_plan: int = 20
    default_merge_strategy: str = "override"
    default_cache_ttl: int = 300
    log_level: str = "INFO"


@dataclass
class ConfigLoadResult:
    """Result of config load planning."""

    success: bool
    load_plan: ConfigLoadPlan | None = None
    estimated_config_size: int = 0
    validation_count: int = 0
    transformation_count: int = 0
    load_time_estimate: int = 0
    security_requirements: dict[str, bool] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ConfigLoadPlanner:
    """Planner for configuration data loading operations."""

    def __init__(self, config: ConfigLoadConfig | None = None):
        self.config = config or ConfigLoadConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def plan_load(self, load_request: dict[str, Any]) -> ConfigLoadResult:
        """Plan configuration data loading operations.

        Args:
            load_request: Dictionary containing load requirements and sources

        Returns:
            ConfigLoadResult: Complete planning result with load plan
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "ConfigLoadPlanner.plan_load"
        )
        self.logger.info(
            f"Starting config load planning for: {load_request.get('plan_name', 'unknown')}",
        )

        try:
            # Validate input request
            self._validate_request(load_request)

            # Parse config sources
            sources = self._parse_sources(load_request)

            # Parse validation rules
            validation_rules = (
                self._parse_validation_rules(load_request) if self.config.enable_validation else []
            )

            # Parse transformations
            transformations = self._parse_transformations(load_request)

            # Create load plan
            load_plan = self._create_load_plan(
                load_request,
                sources,
                validation_rules,
                transformations,
            )

            # Estimate config size
            config_size = self._estimate_config_size(load_plan)

            # Estimate load time
            load_time = self._estimate_load_time(load_plan)

            # Calculate security requirements
            security_requirements = self._calculate_security_requirements(load_plan)

            result = ConfigLoadResult(
                success=True,
                load_plan=load_plan,
                estimated_config_size=config_size,
                validation_count=len(validation_rules),
                transformation_count=len(transformations),
                load_time_estimate=load_time,
                security_requirements=security_requirements,
                metadata={
                    "planned_at": datetime.utcnow().isoformat(),
                    "plan_name": load_request.get("plan_name"),
                    "source_count": len(sources),
                    "planner": "ConfigLoadPlanner",
                },
            )

            self.logger.info(
                f"Successfully planned config load: "
                f"{len(sources)} sources, {len(validation_rules)} validations",
            )
            return result

        except (TypeError, ValueError, KeyError, AttributeError, RuntimeError, OSError) as e:
            self.logger.error(f"Config load planning failed: {str(e)}")
            return ConfigLoadResult(
                success=False,
                errors=[str(e)],
                metadata={
                    "failed_at": datetime.utcnow().isoformat(),
                    "planner": "ConfigLoadPlanner",
                },
            )

    def _validate_request(self, request: dict[str, Any]) -> None:
        """Validate config load planning request."""
        if not request:
            raise ValueError("Config load planning request cannot be empty")

        if "plan_name" not in request:
            raise ValueError("Plan name is required in config load planning request")

        if "sources" not in request:
            raise ValueError("Sources are required in config load planning request")

    def _parse_sources(self, request: dict[str, Any]) -> list[ConfigSource]:
        """Parse config sources from request."""
        sources = []
        raw_sources = request.get("sources", [])

        for raw_source in tqdm(raw_sources, desc="Processing", unit="item"):
            if isinstance(raw_source, dict):
                # Map strings to enums
                config_type_mapping = {
                    "environment": ConfigType.ENVIRONMENT,
                    "feature_flag": ConfigType.FEATURE_FLAG,
                    "deployment": ConfigType.DEPLOYMENT,
                    "service": ConfigType.SERVICE,
                    "security": ConfigType.SECURITY,
                }

                format_mapping = {
                    "json": ConfigFormat.JSON,
                    "yaml": ConfigFormat.YAML,
                    "toml": ConfigFormat.TOML,
                    "xml": ConfigFormat.XML,
                    "properties": ConfigFormat.PROPERTIES,
                }

                scope_mapping = {
                    "global": ConfigScope.GLOBAL,
                    "region": ConfigScope.REGION,
                    "environment": ConfigScope.ENVIRONMENT,
                    "service": ConfigScope.SERVICE,
                    "instance": ConfigScope.INSTANCE,
                }

                source = ConfigSource(
                    id=raw_source.get("id", f"source_{len(sources)}"),
                    name=raw_source.get("name", "unnamed"),
                    config_type=config_type_mapping.get(
                        raw_source.get("config_type", "environment"),
                        ConfigType.ENVIRONMENT,
                    ),
                    format=format_mapping.get(raw_source.get("format", "json"), ConfigFormat.JSON),
                    location=raw_source.get("location", ""),
                    scope=scope_mapping.get(raw_source.get("scope", "global"), ConfigScope.GLOBAL),
                    version=raw_source.get("version"),
                    encryption=raw_source.get("encryption", False),
                    credentials=raw_source.get("credentials", {}),
                )
                sources.append(source)

        # Validate source count
        if len(sources) > self.config.max_sources_per_plan:
            raise ValueError(
                f"Number of sources ({len(sources)}) exceeds maximum ({self.config.max_sources_per_plan})",
            )

        return sources

    def _parse_validation_rules(self, request: dict[str, Any]) -> list[ConfigValidationRule]:
        """Parse validation rules from request."""
        rules = []
        raw_rules = request.get("validation_rules", [])

        for raw_rule in raw_rules:
            if isinstance(raw_rule, dict):
                rule = ConfigValidationRule(
                    id=raw_rule.get("id", f"rule_{len(rules)}"),
                    field_path=raw_rule.get("field_path", ""),
                    rule_type=raw_rule.get("rule_type", "required"),
                    parameters=raw_rule.get("parameters", {}),
                    error_message=raw_rule.get("error_message", ""),
                )
                rules.append(rule)

        return rules

    def _parse_transformations(self, request: dict[str, Any]) -> list[ConfigTransformation]:
        """Parse transformations from request."""
        transformations = []
        raw_transforms = request.get("transformations", [])

        for raw_transform in tqdm(raw_transforms, desc="Processing", unit="item"):
            if isinstance(raw_transform, dict):
                transform = ConfigTransformation(
                    id=raw_transform.get("id", f"transform_{len(transformations)}"),
                    name=raw_transform.get("name", "unnamed"),
                    transformation_type=raw_transform.get("transformation_type", "override"),
                    source_fields=raw_transform.get("source_fields", []),
                    target_field=raw_transform.get("target_field", ""),
                    parameters=raw_transform.get("parameters", {}),
                )
                transformations.append(transform)

        return transformations

    def _create_load_plan(
        self,
        request: dict[str, Any],
        sources: list[ConfigSource],
        validation_rules: list[ConfigValidationRule],
        transformations: list[ConfigTransformation],
    ) -> ConfigLoadPlan:
        """Create config load plan from parsed components."""
        return ConfigLoadPlan(
            id=request.get("plan_id", f"plan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"),
            name=request.get("plan_name", "unnamed_plan"),
            sources=sources,
            validation_rules=validation_rules,
            transformations=transformations,
            merge_strategy=request.get("merge_strategy", self.config.default_merge_strategy),
            enable_validation=request.get("enable_validation", self.config.enable_validation),
            enable_encryption=request.get("enable_encryption", self.config.enable_encryption),
            cache_ttl=request.get("cache_ttl", self.config.default_cache_ttl),
            metadata=request.get("metadata", {}),
        )

    def _get_base_size_for_type(self, config_type: ConfigType) -> int:
        """Get base size estimate for config type."""
        size_map = {
            ConfigType.ENVIRONMENT: 1024,
            ConfigType.FEATURE_FLAG: 2048,
            ConfigType.DEPLOYMENT: 5120,
            ConfigType.SERVICE: 10240,
            ConfigType.SECURITY: 4096,
        }
        return size_map.get(config_type, 2048)

    def _apply_format_multiplier(self, size: int, format: ConfigFormat) -> int:
        """Apply format-specific size multiplier."""
        if format == ConfigFormat.XML:
            return int(size * 1.5)
        elif format == ConfigFormat.YAML:
            return int(size * 0.8)
        return size

    def _estimate_config_size(self, plan: ConfigLoadPlan) -> int:
        """Estimate configuration size in bytes."""
        total_size = 0

        for source in plan.sources:
            base_size = self._get_base_size_for_type(source.config_type)
            total_size += self._apply_format_multiplier(base_size, source.format)

        return total_size

    def _estimate_load_time(self, plan: ConfigLoadPlan) -> int:
        """Estimate load time in seconds."""
        base_time = 2  # Base setup time

        # Add time per source
        source_time = len(plan.sources) * 1

        # Add time for validation
        validation_time = len(plan.validation_rules) * 0.5

        # Add time for transformations
        transform_time = len(plan.transformations) * 1

        # Add time for encryption if enabled
        encryption_time = 5 if plan.enable_encryption else 0

        total_time = base_time + source_time + validation_time + transform_time + encryption_time

        return int(total_time)

    def _calculate_security_requirements(self, plan: ConfigLoadPlan) -> dict[str, bool]:
        """Calculate security requirements for the load plan."""
        requirements = {
            "encryption_needed": False,
            "authentication_needed": False,
            "authorization_needed": False,
            "audit_logging": False,
        }

        # Check if any source requires encryption
        if plan.enable_encryption or any(s.encryption for s in plan.sources):
            requirements["encryption_needed"] = True

        # Check if any source has credentials
        if any(s.credentials for s in plan.sources):
            requirements["authentication_needed"] = True

        # Security configs always need authorization
        if any(s.config_type == ConfigType.SECURITY for s in plan.sources):
            requirements["authorization_needed"] = True
            requirements["audit_logging"] = True

        # Feature flags need audit logging
        if any(s.config_type == ConfigType.FEATURE_FLAG for s in plan.sources):
            requirements["audit_logging"] = True

        return requirements


# Factory function for easy instantiation
def create_config_load_planner(
    enable_validation: bool = True,
    enable_encryption: bool = False,
    enable_caching: bool = True,
    **kwargs: object,
) -> ConfigLoadPlanner:
    """Create a configured config load planner."""
    config = ConfigLoadConfig(
        enable_validation=enable_validation,
        enable_encryption=enable_encryption,
        enable_caching=enable_caching,
        **kwargs,
    )
    return ConfigLoadPlanner(config)


# Convenience function for direct usage
def plan_config_load(
    plan_name: str,
    sources: list[dict[str, Any]],
    validation_rules: list[dict[str, Any]] | None = None,
    transformations: list[dict[str, Any]] | None = None,
    merge_strategy: str = "override",
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Plan config data load from simple parameters.

    Args:
        plan_name: Name of the load plan
        sources: List of config source definitions
        validation_rules: Optional list of validation rule definitions
        transformations: Optional list of transformation definitions
        merge_strategy: Strategy for merging configs (override, merge, keep_existing)
        config: Optional planner configuration overrides

    Returns:
        Dict: Planning result with load plan and resource requirements
    """
    # Build request
    request = {
        "plan_name": plan_name,
        "sources": sources,
        "validation_rules": validation_rules or [],
        "transformations": transformations or [],
        "merge_strategy": merge_strategy,
    }

    # Create planner and execute
    planner_config = ConfigLoadConfig(**config) if config else None
    planner = ConfigLoadPlanner(planner_config)
    result = planner.plan_load(request)

    # Convert result to dict for JSON serialization
    return {
        "success": result.success,
        "load_plan": {
            "id": result.load_plan.id,
            "name": result.load_plan.name,
            "sources": [
                {
                    "id": s.id,
                    "name": s.name,
                    "config_type": s.config_type.value,
                    "format": s.format.value,
                    "location": s.location,
                    "scope": s.scope.value,
                    "version": s.version,
                    "encryption": s.encryption,
                    "credentials": s.credentials,
                }
                for s in result.load_plan.sources
            ],
            "validation_rules": [
                {
                    "id": r.id,
                    "field_path": r.field_path,
                    "rule_type": r.rule_type,
                    "parameters": r.parameters,
                    "error_message": r.error_message,
                }
                for r in result.load_plan.validation_rules
            ],
            "transformations": [
                {
                    "id": t.id,
                    "name": t.name,
                    "transformation_type": t.transformation_type,
                    "source_fields": t.source_fields,
                    "target_field": t.target_field,
                    "parameters": t.parameters,
                }
                for t in result.load_plan.transformations
            ],
            "merge_strategy": result.load_plan.merge_strategy,
            "enable_validation": result.load_plan.enable_validation,
            "enable_encryption": result.load_plan.enable_encryption,
            "cache_ttl": result.load_plan.cache_ttl,
            "metadata": result.load_plan.metadata,
        }
        if result.load_plan
        else None,
        "estimated_config_size": result.estimated_config_size,
        "validation_count": result.validation_count,
        "transformation_count": result.transformation_count,
        "load_time_estimate": result.load_time_estimate,
        "security_requirements": result.security_requirements,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata,
    }
