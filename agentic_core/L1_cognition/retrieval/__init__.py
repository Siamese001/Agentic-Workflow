"""
L1 Cognition — Retrieval Bridge Module

Provides QueryRetrievalBridge for wiring L1 query intent expansion
to the retrieval pipeline across all apps_* packages.
"""

from __future__ import annotations

from typing import Any

from agentic_core.L1_cognition.config.graphrag_config import GraphRAGConfig
from agentic_core.L1_cognition.query_intent_expansion import QueryIntentExpander

__all__ = [
    "QueryRetrievalBridge",
]


class QueryRetrievalBridge:
    """Bridge L1 query intent expansion to retrieval pipeline.

    This class is imported by apps_* execution adapters to establish
    ADG edges from apps to L1_cognition retrieval components.

    Minimal implementation: re-exports L1 retrieval functionality.
    """

    # Re-export core L1 retrieval classes for apps_* import
    QueryIntentExpander = QueryIntentExpander
    GraphRAGConfig = GraphRAGConfig

    @staticmethod
    def get_intent_expander() -> type[QueryIntentExpander]:
        """Return the QueryIntentExpander class."""
        return QueryIntentExpander

    @staticmethod
    def get_graphrag_config() -> type[GraphRAGConfig]:
        """Return the GraphRAGConfig class."""
        return GraphRAGConfig
