"""Dataclass models for load_schema_planning."""

from typing import Any, Dict, List, Optional
# from .load_schema_planning_enums import *  # Star import removed

@dataclass
class SchemaDefinition:
    """Definition of a schema to be loaded."""
    name: str
    type: SchemaType
    version: str
    content: str
    file_path: Optional[str] = None
    url: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    scope: SchemaScope = SchemaScope.DATA

@dataclass
class ValidationRule:
    """Definition of a validation rule."""
    name: str
    type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    severity: str = 'error'
    message: Optional[str] = None

@dataclass
class SchemaTransform:
    """Definition of a schema transformation."""
    source_type: SchemaType
    target_type: SchemaType
    transform_function: str
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SchemaLoadPlan:
    """Complete plan for schema loading."""
    id: str
    name: str
    schemas: List[SchemaDefinition] = field(default_factory=list)
    validation_mode: ValidationMode = ValidationMode.STRICT
    validation_rules: List[ValidationRule] = field(default_factory=list)
    transforms: List[SchemaTransform] = field(default_factory=list)
    resolve_dependencies: bool = True
    enable_caching: bool = True
    cache_ttl: int = 3600
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SchemaLoadConfig:
    """Configuration for schema load planning."""
    enable_validation: bool = True
    enable_transforms: bool = True
    max_schemas_per_plan: int = 50
    max_dependencies: int = 100
    default_validation_mode: str = 'strict'
    log_level: str = 'INFO'

@dataclass
class SchemaLoadResult:
    """Result of schema load planning."""
    success: bool
    load_plan: Optional[SchemaLoadPlan] = None
    schema_count: int = 0
    dependency_count: int = 0
    validation_rule_count: int = 0
    transform_count: int = 0
    load_time_estimate: int = 0
    memory_estimate: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
