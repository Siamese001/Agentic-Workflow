"""
ADG Precision Hardening Package

Provides execution-grade semantic graph precision for the Agentic Dependency Graph.
Transforms high-volume structural ADG into quantitatively governed precision graph.
"""

from .precision_extractor import PrecisionExtractor, PrecisionHardeningEngine
from .precision_schema import (
    NodeSpan,
    # Configuration
    PrecisionConfig,
    # Graph structure
    PrecisionGraph,
    # Metrics
    PrecisionMetrics,
    PrecisionNodeAttributes,
    # Node types
    PrecisionNodeType,
    SemanticEdgeAttributes,
    # Edge types
    SemanticEdgeType,
    # Type surfaces
    TypeSurface,
    # Validation
    ValidationReport,
    VariableAttributes,
    __all__,
)
from .precision_validator import PrecisionValidator

__all__ = [
    # Schema
    "PrecisionNodeType",
    "NodeSpan",
    "PrecisionNodeAttributes",
    "SemanticEdgeType",
    "SemanticEdgeAttributes",
    "TypeSurface",
    "VariableAttributes",
    "PrecisionGraph",
    "PrecisionConfig",
    "PrecisionMetrics",
    "ValidationReport",

    # Core components
    "PrecisionExtractor",
    "PrecisionHardeningEngine",
    "PrecisionValidator",
]
