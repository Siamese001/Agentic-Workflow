"""Architecture Dependency Graph (ADG) package.

Provides commit-scoped static analysis, MCP-backed graph persistence,
and policy enforcement across the five governance applications.
"""

__all__ = [
    "ADG_NS",
    "EntityType",
    "RelationType",
    "EdgeKind",
    "canonical_name",
    "schema",
]


def __getattr__(name: str):
    if name == "schema":
        from agentic_core.adg import schema_util
        return schema_util
    if name in ("ADG_NS", "EdgeKind", "EntityType", "RelationType", "canonical_name"):
        from agentic_core.adg.schema_util import ADG_NS, EdgeKind, EntityType, RelationType, canonical_name
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
