"""Dataclass models for convert_to_config_model."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .convert_to_config_model_enums import *

@dataclass
class ConfigField:
    """Definition of a configuration field."""
    name: str
    type: str
    required: bool = False
    default_value: object = None
    description: str = ''
    env_var: Optional[str] = None
    validator: Optional[str] = None

@dataclass
class ConfigModel:
    """Configuration model definition."""
    name: str
    version: str
    fields: Dict[str, ConfigField]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversionConfig:
    """Configuration for conversion operations."""
    mode: ConversionMode = ConversionMode.LENIENT
    preserve_unknown: bool = True
    convert_types: bool = True
    validate_after: bool = True

@dataclass
class ConversionResult:
    """Result of configuration conversion."""
    config_model: ConfigModel
    converted_data: Dict[str, Any]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

