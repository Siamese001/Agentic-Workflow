"""Query Router for Hybrid Search.

Routes queries to appropriate search mode based on intent.
"""

import logging
from typing import Any, Literal

from agentic_core.L3_orchestration.reasoning.engines.query_intent_detector import (
    QueryIntent,
    QueryIntentDetector,
)

Logger = logging.getLogger(__name__)


class QueryRouter:
    """Routes queries to appropriate search mode based on intent."""

    def __init__(self, hybrid_search_engine: Any):
        """Initialize query router.

        Args:
            hybrid_search_engine: HybridSearchEngine instance
        """
        self.engine = hybrid_search_engine
        self.intent_detector = QueryIntentDetector()

    def route(
        self,
        query: str,
        query_embedding: list[float] | None = None,
        collection_name: str = "repo_code_chunks",
        governance_filter: dict[str, Any] | None = None,
    ) -> tuple[Literal["semantic", "structural", "hybrid"], list[Any]]:
        """Route query to appropriate search mode.

        Args:
            query: Query string
            query_embedding: Pre-computed query embedding
            collection_name: ChromaDB collection name
            governance_filter: Optional governance filters

        Returns:
            Tuple of (mode, results)
        """
        # Detect intent
        intent = self.intent_detector.detect_intent(query)
        confidence = self.intent_detector.get_confidence(query)

        Logger.info(f"Query intent: {intent} (confidence: {confidence:.2f})")

        # Route based on intent
        if intent == QueryIntent.STRUCTURAL:
            results = self._structural_search(query, governance_filter)
            return "structural", results
        elif intent == QueryIntent.SEMANTIC:
            results = self.engine.search(
                query=query,
                query_embedding=query_embedding,
                collection_name=collection_name,
                governance_filter=governance_filter,
            )
            return "semantic", results
        else:  # HYBRID
            results = self._hybrid_search(query, query_embedding, collection_name, governance_filter)
            return "hybrid", results

    def _structural_search(self, query: str, governance_filter: dict[str, Any] | None = None) -> list[Any]:
        """Execute structural search using ADG.

        Args:
            query: Query string (should contain structural patterns)
            governance_filter: Optional governance filters

        Returns:
            Search results
        """
        # Extract entity name from query (simple heuristic)
        # This is a placeholder - full implementation would parse the query
        words = query.split()
        entity_name = None
        for word in words:
            # Allow underscores (common in Python identifiers)
            if word.replace("_", "").isalpha() and len(word) > 2:
                entity_name = word
                break

        if not entity_name:
            Logger.warning("Could not extract entity name from structural query")
            return []

        # Try to find node by name in ADG
        conn = self.engine._get_adg_connection()
        if not conn:
            Logger.warning("ADG connection not available for structural search")
            return []

        try:
            cur = conn.execute(
                "SELECT id FROM nodes WHERE adg_name LIKE ? LIMIT 1",
                (f"%{entity_name}%",),
            )
            row = cur.fetchone()
            if not row:
                Logger.warning(f"Node '{entity_name}' not found in ADG")
                return []

            node_id = row[0]
            Logger.info(f"Found ADG node {node_id} for entity '{entity_name}'")

            # Get chunks for this node
            chunks = self.engine.get_chunks_by_adg_node(node_id)

            # Apply governance filter if provided
            if governance_filter and chunks:
                chunks = self.engine._apply_governance_filters(chunks, governance_filter)

            return chunks

        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            Logger.error(f"Structural search failed: {e}")
            raise  # Re-raise to surface errors to caller

    def _hybrid_search(
        self,
        query: str,
        query_embedding: list[float] | None,
        collection_name: str,
        governance_filter: dict[str, Any] | None,
    ) -> list[Any]:
        """Execute hybrid search combining semantic and structural.

        Args:
            query: Query string
            query_embedding: Pre-computed query embedding
            collection_name: ChromaDB collection name
            governance_filter: Optional governance filters

        Returns:
            Fused search results
        """
        # First run semantic search
        semantic_results = self.engine.search(
            query=query,
            query_embedding=query_embedding,
            collection_name=collection_name,
            governance_filter=governance_filter,
        )

        # Then try to augment with structural results
        # For now, just return semantic results
        # Full implementation would merge and re-rank
        return semantic_results
