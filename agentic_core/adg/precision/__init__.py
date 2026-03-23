"""
ADG Precision Hardening Package

Provides execution-grade semantic graph precision for the Agentic Dependency Graph.
Transforms high-volume structural ADG into quantitatively governed precision graph.
"""

from .precision_schema import (
    # Node types
    PrecisionNodeType,
    NodeSpan,
    PrecisionNodeAttributes,

    # Edge types
    SemanticEdgeType,
    SemanticEdgeAttributes,

    # Type surfaces
    TypeSurface,
    VariableAttributes,

    # Graph structure
    PrecisionGraph,

    # Configuration
    PrecisionConfig,

    # Metrics
    PrecisionMetrics,

    # Validation
    ValidationReport,

    __all__
)

from .precision_extractor import PrecisionExtractor, PrecisionHardeningEngine
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
