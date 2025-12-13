"""Dataclass models for convert_to_internal_schema."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
# from .convert_to_internal_schema_enums import *  # Star import removed

@dataclass
class FieldMapping:
    """Mapping between external and internal fields."""
    external_path: str
    internal_path: str
    type_conversion: Optional[str] = None
    required: bool = False
    default_value: Any = None
    transform_func: Optional[str] = None

@dataclass
class InternalSchema:
    """Definition of internal schema format."""
    name: str
    version: str
    namespace: str
    fields: Dict[str, Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversionConfig:
    """Configuration for schema conversion."""
    strategy: ConversionStrategy = ConversionStrategy.LENIENT
    preserve_unknown: bool = False
    validate_types: bool = True
    apply_transforms: bool = True

@dataclass
class ConversionResult:
    """Result of schema conversion."""
    internal_schema: InternalSchema
    converted_data: Dict[str, Any]
    field_mappings: List[FieldMapping]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
