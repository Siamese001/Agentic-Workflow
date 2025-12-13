"""Dataclass models for load_planning."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .load_planning_enums import *

@dataclass
class ConfigSource:
    """Definition of a configuration source."""
    id: str
    name: str
    config_type: ConfigType
    format: ConfigFormat
    location: str
    scope: ConfigScope
    version: Optional[str] = None
    encryption: bool = False
    credentials: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConfigValidationRule:
    """Definition of a configuration validation rule."""
    id: str
    field_path: str
    rule_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ''

@dataclass
class ConfigTransformation:
    """Definition of a configuration transformation."""
    id: str
    name: str
    transformation_type: str
    source_fields: List[str] = field(default_factory=list)
    target_field: str = ''
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConfigLoadPlan:
    """Complete plan for configuration data loading."""
    id: str
    name: str
    sources: List[ConfigSource]
    validation_rules: List[ConfigValidationRule] = field(default_factory=list)
    transformations: List[ConfigTransformation] = field(default_factory=list)
    merge_strategy: str = 'override'
    enable_validation: bool = True
    enable_encryption: bool = False
    cache_ttl: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConfigLoadConfig:
    """Configuration for config load planning."""
    enable_validation: bool = True
    enable_encryption: bool = False
    enable_caching: bool = True
    max_sources_per_plan: int = 20
    default_merge_strategy: str = 'override'
    default_cache_ttl: int = 300
    log_level: str = 'INFO'


# ============================================
# Merged from: config/logic/data_access/get_info/load_planning_models_2.py
# ============================================
"""Dataclass models for load_planning."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .load_planning_enums import *

@dataclass
class ConfigLoadResult:
    """Result of config load planning."""
    success: bool
    load_plan: Optional[ConfigLoadPlan] = None
    estimated_config_size: int = 0
    validation_count: int = 0
    transformation_count: int = 0
    load_time_estimate: int = 0
    security_requirements: Dict[str, bool] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

