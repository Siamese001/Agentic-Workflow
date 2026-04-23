"""Shim — re-exports from agentic_core.utils.workflow_engines.interfaces for backward compatibility."""

from agentic_core.utils.workflow_engines.interfaces import (  # noqa: F401
    Document,
    ICandidateFusion,
    IReranker,
    IRetrieverLexical,
    IRetrieverVector,
)

__all__ = [
    "Document",
    "ICandidateFusion",
    "IReranker",
    "IRetrieverLexical",
    "IRetrieverVector",
]
