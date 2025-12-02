"""
Schema definitions for schema dependency management and resolution.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class DependencyType(Enum):
    """Types of schema dependencies."""
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    BEHAVIORAL = "behavioral"
    VERSION = "version"


class ResolutionStrategy(Enum):
    """Dependency resolution strategies."""
    LATEST_VERSION = "latest_version"
    COMPATIBLE_VERSION = "compatible_version"
    EXACT_VERSION = "exact_version"
    MINIMUM_VERSION = "minimum_version"


@dataclass
class SchemaDependency:
    """Schema for individual schema dependency."""
    dependency_id: str
    dependent_schema_id: str
    required_schema_id: str
    dependency_type: DependencyType
    version_constraint: str
    optional: bool = False


@dataclass
class DependencyGraph:
    """Schema for dependency graph representation."""
    graph_id: str
    nodes: List[str]
    edges: List[SchemaDependency]
    circular_dependencies: List[List[str]]
    orphaned_schemas: List[str]


@dataclass
class DependencyResolutionResult:
    """Schema for dependency resolution results."""
    resolution_id: str
    strategy: ResolutionStrategy
    resolved_dependencies: List[SchemaDependency]
    conflicts: List[Dict[str, Any]]
    resolution_timestamp: str
