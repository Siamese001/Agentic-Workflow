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
        from agentic_core.adg.contracts import schema_util
        return schema_util
    if name == "ADG_NS":
        from agentic_core.adg.contracts.schema_util import ADG_NS
        return ADG_NS
    if name == "EdgeKind":
        from agentic_core.adg.contracts.schema_util import EdgeKind
        return EdgeKind
    if name == "EntityType":
        from agentic_core.adg.contracts.schema_util import EntityType
        return EntityType
    if name == "RelationType":
        from agentic_core.adg.contracts.schema_util import RelationType
        return RelationType
    if name == "canonical_name":
        from agentic_core.adg.contracts.schema_util import canonical_name
        return canonical_name
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
