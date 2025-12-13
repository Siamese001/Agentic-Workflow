"""Dataclass models for orchestrate_config_planning."""

from typing import Any, Dict, List, Optional
# from .orchestrate_config_planning_enums import *  # Star import removed

@dataclass
class ConfigDefinition:
    """Definition of a configuration item."""
    name: str
    format: ConfigFormat
    environment: ConfigEnvironment
    content: Dict[str, Any]
    version: str = '1.0.0'
    namespace: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class ConfigValidationRule:
    """Rule for validating configuration."""
    name: str
    path: str
    rule_type: str
    constraint: Any
    message: str
    severity: str = 'error'

@dataclass
class DeploymentPlan:
    """Plan for configuration deployment."""
    strategy: DeploymentStrategy
    target_environments: List[ConfigEnvironment]
    rollout_percentage: float = 100.0
    validation_steps: List[str] = field(default_factory=list)
    rollback_plan: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)

@dataclass
class ConfigPlanningConfig:
    """Configuration for config planning orchestrator."""
    enable_validation: bool = True
    enable_versioning: bool = True
    enable_encryption: bool = False
    auto_backup: bool = True
    max_config_size: int = 1048576
    log_level: str = 'INFO'

@dataclass
class ConfigPlanningResult:
    """Result of config planning orchestration."""
    success: bool
    validated_configs: List[ConfigDefinition] = field(default_factory=list)
    deployment_plan: Optional[DeploymentPlan] = None
    validation_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
