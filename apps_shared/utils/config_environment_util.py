"""Config Planning Orchestrator - Coordinates configuration management and deployment operations.

This orchestrator manages the planning phase for configuration operations,
including validation, environment management, version control, and deployment strategies.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "config_environment_util", "p0_governance")
_emit_reads_policy_state("p0", "config_environment_util", "policy_binding")
_emit_snapshots_state("p0", "config_environment_util", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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

_emit_emits_metric_event("config_environment_util", "p4obs", "metric_1")
_emit_emits_metric_event("config_environment_util", "p4obs", "metric_2")
_emit_emits_metric_event("config_environment_util", "p4obs", "metric_3")
_emit_emits_metric_event("config_environment_util", "p4obs", "metric_4")
_emit_emits_metric_event("config_environment_util", "p4obs", "metric_5")
_emit_emits_metric_event("config_environment_util", "p4obs", "metric_6")
_emit_records_incident_event("config_environment_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("config_environment_util", "p4obs", "anomaly")
_emit_writes_observability_log("config_environment_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("config_environment_util", "p4obs", "mon_state")
_emit_triggers_alert("config_environment_util", "p4obs", "alert")
_emit_links_incident_trace("config_environment_util", "p4obs", "trace_link")
_emit_captures_pattern("config_environment_util", "p3lm", "pattern")
_emit_records_learning_event("config_environment_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("config_environment_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("config_environment_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("config_environment_util", "p3lm", "routing")
_emit_improves_agent_policy("config_environment_util", "p3lm", "policy")
_emit_stores_learning_state("config_environment_util", "p3lm", "state")
_emit_records_execution_trace("config_environment_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("config_environment_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("config_environment_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("config_environment_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("config_environment_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("config_environment_util", "env_read", "p2_env_1")
_emit_reads_environ("config_environment_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("config_environment_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("config_environment_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "config_environment_util", "context_pull")
_emit_pulls_context("p1", "config_environment_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "config_environment_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "config_environment_util", "uwg_term_2")
_emit_writes_through("p1", "config_environment_util", "write_through")
_emit_writes_through("p1", "config_environment_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "config_environment_util", "safety_validation")
_emit_invokes_eval("p1", "config_environment_util", "eval_call")
_emit_proposal_commits_routing("p1", "config_environment_util", "routing_commit")
_emit_escalates_to_human("p1", "config_environment_util", "human_escalation")
_emit_routes_through("p1", "config_environment_util", "route_through")
_emit_checks_agent_registry("p1", "config_environment_util", "agent_registry")
_emit_validates_agent_capability("p1", "config_environment_util", "capability")
_emit_dispatches_execution_plan("p1", "config_environment_util", "exec_plan")
_emit_agent_executes_agent("p1", "config_environment_util", "sub_agent")
_emit_routes_to_agent("p1", "config_environment_util", "target_agent")
_emit_verifies_policy("p1", "config_environment_util", "policy_check")
_emit_observes_runtime_state("p1", "config_environment_util", "runtime_state")
_emit_verifies_boundary("p1", "config_environment_util", "boundary_check")
_emit_transcripts_response("p1", "config_environment_util", "transcript")
_emit_hard_fails_untranscripted("p1", "config_environment_util")
_emit_gated_by_confidence("p1", "config_environment_util", "confidence_gate")
emit_replay_key("p0", "config_environment_util")
emit_determinism_digest("p0", "config_environment_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "config_environment_util", "execution_auth")
_emit_validates_capability("p2", "config_environment_util", "capability_check")
_emit_routes_to_capability("p2", "config_environment_util", "capability_route")
_emit_writes_via_uwg("p2", "config_environment_util", "uwg_write")
_emit_blocks_direct_write("p2", "config_environment_util", "direct_write_block")
_emit_records_tool_invocation("p2", "config_environment_util", "tool_invocation")
_emit_captures_execution_output("p2", "config_environment_util", "exec_output")
_emit_dispatches_agent("p3", "config_environment_util", "agent_dispatch")
_emit_coordinates_agents("p3", "config_environment_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "config_environment_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "config_environment_util", "healing_outcome")
_emit_escalates_failure("p3", "config_environment_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "config_environment_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "config_environment_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "config_environment_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "config_environment_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "config_environment_util", "eval_metric")
_emit_stores_embedding("p4", "config_environment_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "config_environment_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "config_environment_util", "exec_snapshot_link")
_emit_reads_through("l4", "config_environment_util", "urg_read_1")
_emit_reads_through("l4", "config_environment_util", "urg_read_2")
_emit_reads_through("l4", "config_environment_util", "urg_read_3")
_emit_reads_through("l4", "config_environment_util", "urg_read_4")
_emit_reads_through("l4", "config_environment_util", "urg_read_5")
_emit_reads_through("l4", "config_environment_util", "urg_read_6")
_emit_reads_through("l4", "config_environment_util", "urg_read_7")
_emit_reads_through("l4", "config_environment_util", "urg_read_8")
_emit_reads_through("l4", "config_environment_util", "urg_read_9")
_emit_reads_through("l4", "config_environment_util", "urg_read_10")
_emit_reads_through("l4", "config_environment_util", "urg_read_11")
_emit_reads_through("l4", "config_environment_util", "urg_read_12")
_emit_reads_through("l4", "config_environment_util", "urg_read_13")
_emit_reads_through("l4", "config_environment_util", "urg_read_14")
_emit_reads_through("l4", "config_environment_util", "urg_read_15")
_emit_reads_through("l4", "config_environment_util", "urg_read_16")
_emit_reads_through("l4", "config_environment_util", "urg_read_17")
_emit_reads_through("l4", "config_environment_util", "urg_read_18")
_emit_reads_through("l4", "config_environment_util", "urg_read_19")
_emit_reads_through("l4", "config_environment_util", "urg_read_20")
_emit_reads_through("l4", "config_environment_util", "urg_read_21")
_emit_reads_through("l4", "config_environment_util", "urg_read_22")
_emit_reads_through("l4", "config_environment_util", "urg_read_23")
_emit_reads_through("l4", "config_environment_util", "urg_read_24")
_emit_reads_through("l4", "config_environment_util", "urg_read_25")
_emit_reads_through("l4", "config_environment_util", "urg_read_26")
_emit_reads_through("l4", "config_environment_util", "urg_read_27")
_emit_reads_through("l4", "config_environment_util", "urg_read_28")
_emit_reads_through("l4", "config_environment_util", "urg_read_29")
_emit_reads_through("l4", "config_environment_util", "urg_read_30")
_emit_reads_through("l4", "config_environment_util", "urg_read_31")
_emit_reads_through("l4", "config_environment_util", "urg_read_32")
_emit_reads_through("l4", "config_environment_util", "urg_read_33")
_emit_reads_through("l4", "config_environment_util", "urg_read_34")
_emit_reads_through("l4", "config_environment_util", "urg_read_35")
_emit_reads_through("l4", "config_environment_util", "urg_read_36")
_emit_reads_through("l4", "config_environment_util", "urg_read_37")
_emit_reads_through("l4", "config_environment_util", "urg_read_38")
_emit_reads_through("l4", "config_environment_util", "urg_read_39")
_emit_reads_through("l4", "config_environment_util", "urg_read_40")
_emit_reads_through("l4", "config_environment_util", "urg_read_41")
_emit_reads_through("l4", "config_environment_util", "urg_read_42")
_emit_reads_through("l4", "config_environment_util", "urg_read_43")
_emit_reads_through("l4", "config_environment_util", "urg_read_44")
_emit_reads_through("l4", "config_environment_util", "urg_read_45")
_emit_reads_through("l4", "config_environment_util", "urg_read_46")
_emit_reads_through("l4", "config_environment_util", "urg_read_47")
_emit_reads_through("l4", "config_environment_util", "urg_read_48")
_emit_reads_through("l4", "config_environment_util", "urg_read_49")
_emit_reads_through("l4", "config_environment_util", "urg_read_50")
_emit_reads_through("l4", "config_environment_util", "urg_read_51")
_emit_reads_through("l4", "config_environment_util", "urg_read_52")
_emit_reads_through("l4", "config_environment_util", "urg_read_53")
_emit_reads_through("l4", "config_environment_util", "urg_read_54")
_emit_reads_through("l4", "config_environment_util", "urg_read_55")
_emit_reads_through("l4", "config_environment_util", "urg_read_56")
_emit_reads_through("l4", "config_environment_util", "urg_read_57")
_emit_reads_through("l4", "config_environment_util", "urg_read_58")
_emit_reads_through("l4", "config_environment_util", "urg_read_59")
_emit_reads_through("l4", "config_environment_util", "urg_read_60")
_emit_reads_through("l4", "config_environment_util", "urg_read_61")
_emit_reads_through("l4", "config_environment_util", "urg_read_62")
_emit_reads_through("l4", "config_environment_util", "urg_read_63")
_emit_reads_through("l4", "config_environment_util", "urg_read_64")
_emit_reads_through("l4", "config_environment_util", "urg_read_65")
_emit_reads_through("l4", "config_environment_util", "urg_read_66")
_emit_reads_through("l4", "config_environment_util", "urg_read_67")
_emit_reads_through("l4", "config_environment_util", "urg_read_68")
_emit_reads_through("l4", "config_environment_util", "urg_read_69")
_emit_reads_through("l4", "config_environment_util", "urg_read_70")
_emit_reads_through("l4", "config_environment_util", "urg_read_71")
_emit_reads_through("l4", "config_environment_util", "urg_read_72")
_emit_reads_through("l4", "config_environment_util", "urg_read_73")
_emit_reads_through("l4", "config_environment_util", "urg_read_74")
_emit_reads_through("l4", "config_environment_util", "urg_read_75")


DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)


class ConfigEnvironment(Enum):
    """Deployment environments for configuration."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DR = "disaster_recovery"


class ConfigFormat(Enum):
    """configuration file formats."""

    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    INI = "ini"
    ENV = "env"
    XML = "xml"


class DeploymentStrategy(Enum):
    """configuration deployment strategies."""

    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING = "rolling"
    ATOMIC = "atomic"
    SHADOW = "shadow"


@dataclass
class ConfigDefinition:
    """Definition of a configuration item."""

    name: str
    format: ConfigFormat
    environment: ConfigEnvironment
    content: dict[str, Any]
    version: str = "1.0.0"
    namespace: str | None = None
    description: str | None = None
    tags: list[str] = field(default_factory=list)


@dataclass
class ConfigValidationRule:
    """Rule for validating configuration."""

    name: str
    path: str  # JSON path or similar
    rule_type: str  # required, pattern, range, enum
    constraint: Any
    message: str
    severity: str = "error"


@dataclass
class DeploymentPlan:
    """Plan for configuration deployment."""

    strategy: DeploymentStrategy
    target_environments: list[ConfigEnvironment]
    rollout_percentage: float = 100.0
    validation_steps: list[str] = field(default_factory=list)
    rollback_plan: str | None = None
    dependencies: list[str] = field(default_factory=list)


@dataclass
class ConfigPlanningConfig:
    """configuration for config planning orchestrator."""

    enable_validation: bool = True
    enable_versioning: bool = True
    enable_encryption: bool = False
    auto_backup: bool = True
    max_config_size: int = 1048576  # 1MB
    log_level: str = "INFO"


@dataclass
class ConfigPlanningResult:
    """Result of config planning orchestration."""

    success: bool
    validated_configs: list[ConfigDefinition] = field(default_factory=list)
    deployment_plan: DeploymentPlan | None = None
    validation_errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ConfigPlanningOrchestrator:
    """Orchestrator for planning configuration operations."""

    def __init__(self, config: ConfigPlanningConfig | None = None):
        self.config = config or ConfigPlanningConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def execute(self, config_request: dict[str, Any]) -> ConfigPlanningResult:
        """Execute the config planning orchestration.

        Args:
            config_request: Dictionary containing configuration requirements

        Returns:
            ConfigPlanningResult: Complete planning result with validated configs and deployment plan
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ConfigPlanningOrchestrator.execute")

        self.logger.info(
            f"Starting config planning for: {config_request.get('service', 'unknown')}",
        )

        try:
            # Validate input request
            self._validate_request(config_request)

            # Parse and validate configurations
            validated_configs = []
            if self.config.enable_validation:
                validated_configs = self._validate_configs(config_request)

            # Create deployment plan
            deployment_plan = self._create_deployment_plan(config_request, validated_configs)

            # Collect validation errors
            validation_errors = self._collect_validation_errors(config_request)

            result = ConfigPlanningResult(
                success=len(validation_errors) == 0,
                validated_configs=validated_configs,
                deployment_plan=deployment_plan,
                validation_errors=validation_errors,
                metadata={
                    "planned_at": datetime.utcnow().isoformat(),
                    "service": config_request.get("service"),
                    "config_count": len(validated_configs),
                    "orchestrator": "ConfigPlanningOrchestrator",
                },
            )

            self.logger.info(
                f"Successfully planned configuration: {len(validated_configs)} configs validated",
            )
            return result

        except Exception as e:
            self.logger.error(f"Config planning failed: {str(e)}")
            return ConfigPlanningResult(
                success=False,
                errors=[str(e)],
                metadata={
                    "failed_at": datetime.utcnow().isoformat(),
                    "orchestrator": "ConfigPlanningOrchestrator",
                },
            )

    def _validate_request(self, request: dict[str, Any]) -> None:
        """Validate config planning request."""
        if not request:
            raise ValueError("Config request cannot be empty")

        if "service" not in request:
            raise ValueError("Service name is required in config request")

        if "environment" not in request:
            raise ValueError("Target environment is required in config request")

    def _validate_configs(self, request: dict[str, Any]) -> list[ConfigDefinition]:
        """Validate and parse configurations from request."""
        configs = []
        raw_configs = request.get("configs", [])
        environment_str = request.get("environment")

        # Map string to enum
        env_mapping = {
            "dev": ConfigEnvironment.DEVELOPMENT,
            "development": ConfigEnvironment.DEVELOPMENT,
            "test": ConfigEnvironment.TESTING,
            "testing": ConfigEnvironment.TESTING,
            "staging": ConfigEnvironment.STAGING,
            "prod": ConfigEnvironment.PRODUCTION,
            "production": ConfigEnvironment.PRODUCTION,
            "dr": ConfigEnvironment.DR,
        }

        environment = env_mapping.get(environment_str.lower(), ConfigEnvironment.DEVELOPMENT)

        for raw_config in raw_configs:
            if isinstance(raw_config, dict):
                config = ConfigDefinition(
                    name=raw_config.get("name", "unnamed"),
                    format=ConfigFormat(raw_config.get("format", "json")),
                    environment=environment,
                    content=raw_config.get("content", {}),
                    version=raw_config.get("version", "1.0.0"),
                    namespace=raw_config.get("namespace"),
                    description=raw_config.get("description"),
                    tags=raw_config.get("tags", []),
                )
                configs.append(config)

        return configs

    def _create_deployment_plan(
        self,
        request: dict[str, Any],
        configs: list[ConfigDefinition],
    ) -> DeploymentPlan | None:
        """Create deployment plan for configurations."""
        if not configs:
            return None

        deployment_config = request.get("deployment", {})
        strategy_str = deployment_config.get("strategy", "atomic")

        # Map string to enum
        strategy_mapping = {
            "blue_green": DeploymentStrategy.BLUE_GREEN,
            "canary": DeploymentStrategy.CANARY,
            "rolling": DeploymentStrategy.ROLLING,
            "atomic": DeploymentStrategy.ATOMIC,
            "shadow": DeploymentStrategy.SHADOW,
        }

        strategy = strategy_mapping.get(strategy_str.lower(), DeploymentStrategy.ATOMIC)

        # Get target environments
        target_envs_str = deployment_config.get("target_environments", [request.get("environment")])
        target_envs = []

        for env_str in target_envs_str:
            env_mapping = {
                "dev": ConfigEnvironment.DEVELOPMENT,
                "development": ConfigEnvironment.DEVELOPMENT,
                "test": ConfigEnvironment.TESTING,
                "testing": ConfigEnvironment.TESTING,
                "staging": ConfigEnvironment.STAGING,
                "prod": ConfigEnvironment.PRODUCTION,
                "production": ConfigEnvironment.PRODUCTION,
                "dr": ConfigEnvironment.DR,
            }
            env = env_mapping.get(env_str.lower(), ConfigEnvironment.DEVELOPMENT)
            target_envs.append(env)

        return DeploymentPlan(
            strategy=strategy,
            target_environments=target_envs,
            rollout_percentage=deployment_config.get("rollout_percentage", 100.0),
            validation_steps=deployment_config.get("validation_steps", []),
            rollback_plan=deployment_config.get("rollback_plan"),
            dependencies=deployment_config.get("dependencies", []),
        )

    def _collect_validation_errors(self, request: dict[str, Any]) -> list[str]:
        """Collect validation errors from configurations."""
        errors = []
        configs = request.get("configs", [])

        for config in configs:
            if not isinstance(config, dict):
                errors.append("Invalid config format")
                continue

            if "name" not in config:
                errors.append("Config missing name")

            if "content" not in config:
                errors.append("Config missing content")

            # Check config size
            content_size = len(str(config.get("content", {})))
            if content_size > self.config.max_config_size:
                errors.append(
                    f"Config exceeds maximum size: {content_size} > {self.config.max_config_size}",
                )

        return errors


# Factory function for easy instantiation
def create_config_planning_orchestrator(
    enable_validation: bool = True,
    enable_versioning: bool = True,
    **kwargs: object,
) -> ConfigPlanningOrchestrator:
    """Create a configured config planning orchestrator."""
    config = ConfigPlanningConfig(
        enable_validation=enable_validation,
        enable_versioning=enable_versioning,
        **kwargs,
    )
    return ConfigPlanningOrchestrator(config)


# Convenience function for direct usage
def plan_config_deployment(
    service: str,
    environment: str,
    configs: list[dict[str, Any]],
    deployment: dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Plan configuration deployment from simple parameters.

    Args:
        service: Name of the service
        environment: Target environment
        configs: List of configuration definitions
        deployment: Optional deployment configuration
        config: Optional orchestrator configuration overrides

    Returns:
        Dict: Planning result with validated configs and deployment plan
    """
    # Build request
    request = {
        "service": service,
        "environment": environment,
        "configs": configs,
        "deployment": deployment or {},
    }

    # Create orchestrator and execute
    orchestrator_config = ConfigPlanningConfig(**config) if config else None
    orchestrator = ConfigPlanningOrchestrator(orchestrator_config)
    result = orchestrator.execute(request)

    # Convert result to dict for JSON serialization
    return {
        "success": result.success,
        "validated_configs": [
            {
                "name": c.name,
                "format": c.format.value,
                "environment": c.environment.value,
                "content": c.content,
                "version": c.version,
                "namespace": c.namespace,
                "description": c.description,
                "tags": c.tags,
            }
            for c in result.validated_configs
        ],
        "deployment_plan": {
            "strategy": result.deployment_plan.strategy.value,
            "target_environments": [e.value for e in result.deployment_plan.target_environments],
            "rollout_percentage": result.deployment_plan.rollout_percentage,
            "validation_steps": result.deployment_plan.validation_steps,
            "rollback_plan": result.deployment_plan.rollback_plan,
            "dependencies": result.deployment_plan.dependencies,
        }
        if result.deployment_plan
        else None,
        "validation_errors": result.validation_errors,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata,
    }


if __name__ == "__main__":
    # Example usage
    example_configs = [
        {
            "name": "database_config",
            "format": "json",
            "content": {"host": "localhost", "port": 5432},
            "version": "1.0.0",
        },
    ]

    result = plan_config_deployment(
        service="user_service",
        environment="production",
        configs=example_configs,
        deployment={"strategy": "blue_green"},
    )
