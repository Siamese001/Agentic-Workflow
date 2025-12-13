"""Dataclass models for understand_request_load_planning."""

from typing import Any, Dict, List, Optional
# from .understand_request_load_planning_enums import *  # Star import removed

@dataclass
class ConfigParameter:
    """Information about a configuration parameter."""
    key: str
    value: Any
    type: str
    required: bool = False
    default_value: Optional[Any] = None
    description: str = ''
    validation_rules: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConfigSection:
    """Information about a configuration section."""
    name: str
    parameters: List[ConfigParameter] = field(default_factory=list)
    subsections: List['ConfigSection'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationRule:
    """Information about a validation rule."""
    name: str
    type: str
    condition: str
    error_message: str
    severity: str = 'error'
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConfigLoadPlan:
    """Complete plan for configuration loading."""
    id: str
    name: str
    config_type: ConfigType
    scope: ConfigScope
    sections: List[ConfigSection] = field(default_factory=list)
    validation_rules: List[ValidationRule] = field(default_factory=list)
    validation_level: ValidationLevel = ValidationLevel.BASIC
    enable_caching: bool = True
    cache_ttl: int = 600
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConfigLoadConfig:
    """Configuration for config load planning."""
    enable_validation: bool = True
    enable_type_checking: bool = True
    enable_default_values: bool = True
    max_parameters_per_config: int = 500
    default_validation_level: str = 'basic'
    log_level: str = 'INFO'
