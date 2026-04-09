"""GraphDB Query Workbench - Query families for ADG graph analysis.

This package provides structured query families for analyzing projected ADG graphs:
- Structural conformance queries
- Blast-radius queries
- Historical diff queries
- Analyst investigation workflows
"""

from __future__ import annotations

from .structural import StructuralQueries
from .blast_radius import BlastRadiusQueries
from .historical import HistoricalQueries
from .analyst import AnalystQueries

__all__ = [
    "StructuralQueries",
    "BlastRadiusQueries",
    "HistoricalQueries",
    "AnalystQueries",
]
