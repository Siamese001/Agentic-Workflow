"""
Schema definitions for schema state inspection and monitoring.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class InspectionType(Enum):
    """Types of schema inspections."""
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"


class InspectionScope(Enum):
    """Schema inspection scopes."""
    SINGLE_SCHEMA = "single_schema"
    SCHEMA_COLLECTION = "schema_collection"
    DEPENDENCY_GRAPH = "dependency_graph"
    ENTIRE_REGISTRY = "entire_registry"


@dataclass
class InspectionParameters:
    """Schema for inspection parameters."""
    inspection_type: InspectionType
    scope: InspectionScope
    target_schema_ids: Optional[List[str]] = None
    depth_limit: int = 10
    include_metadata: bool = True


@dataclass
class InspectionFinding:
    """Schema for individual inspection finding."""
    finding_id: str
    category: str
    severity: str
    description: str
    location: Optional[str] = None
    recommendation: Optional[str] = None


@dataclass
class InspectionResult:
    """Schema for complete inspection results."""
    inspection_id: str
    inspection_timestamp: str
    total_schemas_inspected: int
    findings: List[InspectionFinding]
    summary_statistics: Dict[str, int]