"""Architecture Dependency Graph (ADG) package.

Provides commit-scoped static analysis, MCP-backed graph persistence,
and policy enforcement across the five governance applications.
"""

from agentic_core.adg import schema_util as schema  # backward-compat alias
from agentic_core.adg.schema_util import (
    ADG_NS,
    EdgeKind,
    EntityType,
    RelationType,
    canonical_name,
)

__all__ = [
    "ADG_NS",
    "EntityType",
    "RelationType",
    "EdgeKind",
    "canonical_name",
    "schema",
]
