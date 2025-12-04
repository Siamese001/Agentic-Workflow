"""
Schema definitions for extracting parameters from schema definitions.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ParameterType(Enum):
    """Schema parameter data types."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class SchemaParameter:
    """Schema for individual parameter definition."""
    name: str
    param_type: ParameterType
    required: bool = True
    default_value: Optional[Union[str, int, float, bool]] = None
    description: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None


@dataclass
class ParameterConstraints:
    """Schema for parameter validation constraints."""
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Union[str, int, float]]] = None


@dataclass
class ExtractedParameters:
    """Schema for extracted parameter collection."""
    schema_id: str
    parameters: List[SchemaParameter]
    metadata: Optional[Dict[str, Any]] = None
    version: Optional[str] = None