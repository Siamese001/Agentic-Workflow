"""Schema Planning Models - Configuration and result models.


logger = logging.getLogger(__name__)
This module contains dataclass models for schema planning configuration
and result structures.
"""

from typing import Dict, List, Any
import logging

@dataclass
class TransformationPlan:
    """Plan for schema transformation."""
    transformation_type: TransformationType
    source_schema: str
    target_schema: str
    mapping_rules: Dict[str, Any] = field(default_factory=dict)
    validation_rules: List[ValidationRule] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

@dataclass
class SchemaPlanningConfig:
    """Configuration for schema planning orchestrator."""
    enable_validation: bool = True
    enable_transformation: bool = True
    enable_compatibility_check: bool = True
    max_schema_depth: int = 10
    strict_validation: bool = True
    log_level: str = "INFO"

@dataclass
class SchemaPlanningResult:
    """Result of schema planning orchestration."""
    success: bool
    validated_schemas: List[SchemaDefinition] = field(default_factory=list)
    transformation_plans: List[TransformationPlan] = field(default_factory=list)
    compatibility_report: Dict[str, Any] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
