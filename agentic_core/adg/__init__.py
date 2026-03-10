"""Architecture Dependency Graph (ADG) package.

Provides commit-scoped static analysis, MCP-backed graph persistence,
and policy enforcement across the five governance applications.
"""

from agentic_core.adg.schema import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
]
