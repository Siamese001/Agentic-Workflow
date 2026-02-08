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
