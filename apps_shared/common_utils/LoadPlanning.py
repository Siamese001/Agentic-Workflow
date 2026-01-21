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
    """Configuration scopes."""
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
    """Configuration for config load planning."""
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
        self.logger.info(f"Starting config load planning for: {load_request.get('plan_name', 'unknown')}")

        try:
            # Validate input request
            self._validate_request(load_request)

            # Parse config sources
            sources = self._parse_sources(load_request)

            # Parse validation rules
            validation_rules = (
                self._parse_validation_rules(load_request)
                if self.config.enable_validation else []
            )

            # Parse transformations
            transformations = self._parse_transformations(load_request)

            # Create load plan
            load_plan = self._create_load_plan(
                load_request, sources, validation_rules, transformations
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
                    "planner": "ConfigLoadPlanner"
                }
            )

            self.logger.info(
                f"Successfully planned config load: "
                f"{len(sources)} sources, {len(validation_rules)} validations"
            )
            return result

        except Exception as e:
            self.logger.error(f"Config load planning failed: {str(e)}")
            return ConfigLoadResult(
                success=False,
                errors=[str(e)],
                metadata={
                    "failed_at": datetime.utcnow().isoformat(),
                    "planner": "ConfigLoadPlanner"
                }
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

        for raw_source in raw_sources:
            if isinstance(raw_source, dict):
                # Map strings to enums
                config_type_mapping = {
                    "environment": ConfigType.ENVIRONMENT,
                    "feature_flag": ConfigType.FEATURE_FLAG,
                    "deployment": ConfigType.DEPLOYMENT,
                    "service": ConfigType.SERVICE,
                    "security": ConfigType.SECURITY
                }

                format_mapping = {
                    "json": ConfigFormat.JSON,
                    "yaml": ConfigFormat.YAML,
                    "toml": ConfigFormat.TOML,
                    "xml": ConfigFormat.XML,
                    "properties": ConfigFormat.PROPERTIES
                }

                scope_mapping = {
                    "global": ConfigScope.GLOBAL,
                    "region": ConfigScope.REGION,
                    "environment": ConfigScope.ENVIRONMENT,
                    "service": ConfigScope.SERVICE,
                    "instance": ConfigScope.INSTANCE
                }

                source = ConfigSource(
                    id=raw_source.get("id", f"source_{len(sources)}"),
                    name=raw_source.get("name", "unnamed"),
                    config_type=config_type_mapping.get(
                        raw_source.get("config_type", "environment"),
                        ConfigType.ENVIRONMENT
                    ),
                    format=format_mapping.get(
                        raw_source.get("format", "json"),
                        ConfigFormat.JSON
                    ),
                    location=raw_source.get("location", ""),
                    scope=scope_mapping.get(
                        raw_source.get("scope", "global"),
                        ConfigScope.GLOBAL
                    ),
                    version=raw_source.get("version"),
                    encryption=raw_source.get("encryption", False),
                    credentials=raw_source.get("credentials", {})
                )
                sources.append(source)

        # Validate source count
        if len(sources) > self.config.max_sources_per_plan:
            raise ValueError(
                f"Number of sources ({len(sources)}) exceeds maximum "
                f"({self.config.max_sources_per_plan})"
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
                    error_message=raw_rule.get("error_message", "")
                )
                rules.append(rule)

        return rules

    def _parse_transformations(self, request: dict[str, Any]) -> list[ConfigTransformation]:
        """Parse transformations from request."""
        transformations = []
        raw_transforms = request.get("transformations", [])

        for raw_transform in raw_transforms:
            if isinstance(raw_transform, dict):
                transform = ConfigTransformation(
                    id=raw_transform.get("id", f"transform_{len(transformations)}"),
                    name=raw_transform.get("name", "unnamed"),
                    transformation_type=raw_transform.get("transformation_type", "override"),
                    source_fields=raw_transform.get("source_fields", []),
                    target_field=raw_transform.get("target_field", ""),
                    parameters=raw_transform.get("parameters", {})
                )
                transformations.append(transform)

        return transformations

    def _create_load_plan(
        self,
        request: dict[str, Any],
        sources: list[ConfigSource],
        validation_rules: list[ConfigValidationRule],
        transformations: list[ConfigTransformation]
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
            metadata=request.get("metadata", {})
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
            "audit_logging": False
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
    **kwargs: object
) -> ConfigLoadPlanner:
    """Create a configured config load planner."""
    config = ConfigLoadConfig(
        enable_validation=enable_validation,
        enable_encryption=enable_encryption,
        enable_caching=enable_caching,
        **kwargs
    )
    return ConfigLoadPlanner(config)


# Convenience function for direct usage
def plan_config_load(
    plan_name: str,
    sources: list[dict[str, Any]],
    validation_rules: list[dict[str, Any]] | None = None,
    transformations: list[dict[str, Any]] | None = None,
    merge_strategy: str = "override",
    config: dict[str, Any] | None = None
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
        "merge_strategy": merge_strategy
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
                    "credentials": s.credentials
                }
                for s in result.load_plan.sources
            ],
            "validation_rules": [
                {
                    "id": r.id,
                    "field_path": r.field_path,
                    "rule_type": r.rule_type,
                    "parameters": r.parameters,
                    "error_message": r.error_message
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
                    "parameters": t.parameters
                }
                for t in result.load_plan.transformations
            ],
            "merge_strategy": result.load_plan.merge_strategy,
            "enable_validation": result.load_plan.enable_validation,
            "enable_encryption": result.load_plan.enable_encryption,
            "cache_ttl": result.load_plan.cache_ttl,
            "metadata": result.load_plan.metadata
        } if result.load_plan else None,
        "estimated_config_size": result.estimated_config_size,
        "validation_count": result.validation_count,
        "transformation_count": result.transformation_count,
        "load_time_estimate": result.load_time_estimate,
        "security_requirements": result.security_requirements,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata
    }
