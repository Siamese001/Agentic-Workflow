"""GraphDB Enhancement - Graph projection layer for ADG analysis.

This package provides a NetworkX-based graph projection layer that reads from
canonical ADG SQLite artifacts and enables advanced structural analysis,
blast-radius exploration, and historical diffing.

Architecture:
    Canonical ADG SQLite → NetworkX Projection → Query Workbench

Key Features:
    - Deterministic projection from canonical artifacts
    - Rich structural conformance queries
    - Blast-radius and impact analysis
    - Historical graph diffing
    - Analyst investigation workflows
"""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "GraphDB Enhancement Team"

# Core exports
from .projection import GraphProjector
from .schema import NODE_TYPE_MAPPING, EDGE_TYPE_MAPPING
from .snapshot import SnapshotManager

__all__ = [
    "GraphProjector",
    "SnapshotManager",
    "NODE_TYPE_MAPPING",
    "EDGE_TYPE_MAPPING",
]
