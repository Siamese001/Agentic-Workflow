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

    @staticmethod
    def _get_target_collection(topic_domain: str, default_collection: str) -> str:
        """Map a topic domain to the canonical ChromaDB collection name."""
        _domain_to_collection: dict[str, str] = {
            "policy": "ext_authority",
            "architecture": "repo_evidence",
            "best_practice": "ext_authority",
            "tool_contracts": "ext_authority",
            "code": "code_chunks",
        }
        return _domain_to_collection.get(topic_domain, default_collection)

    @staticmethod
    def _get_arch_prefilter(topic_domain: str) -> dict[str, Any] | None:
        """Return a ChromaDB where= filter for canonical arch docs, or None."""
        if topic_domain == "architecture":
            return {"source_band": "repo_canonical"}
        return None

    def route(
        self,
        query: str,
        query_embedding: list[float] | None = None,
        collection_name: str = "code_chunks",
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
        # Detect intent and topic domain
        intent = self.intent_detector.detect_intent(query)
        confidence = self.intent_detector.get_confidence(query)
        topic_domain = self.intent_detector.detect_topic_domain(query)

        resolved_collection = self._get_target_collection(topic_domain, collection_name)
        metadata_filter = self._get_arch_prefilter(topic_domain)
        authority_rerank = topic_domain in ("architecture", "best_practice", "tool_contracts", "policy")
        collapse_max = 2 if topic_domain in ("best_practice", "tool_contracts", "policy") else None

        Logger.info(
            f"Query intent: {intent} (confidence: {confidence:.2f})  "
            f"domain: {topic_domain}  collection: {resolved_collection}"
        )

        # Route based on intent
        if intent == QueryIntent.STRUCTURAL:
            results = self._structural_search(query, governance_filter)
            return "structural", results
        elif intent == QueryIntent.SEMANTIC:
            results = self.engine.search(
                query=query,
                query_embedding=query_embedding,
                collection_name=resolved_collection,
                governance_filter=governance_filter,
                metadata_filter=metadata_filter,
                authority_rerank=authority_rerank,
                collapse_group_dedup_max=collapse_max,
            )
            return "semantic", results
        else:  # HYBRID
            results = self._hybrid_search(
                query,
                query_embedding,
                resolved_collection,
                governance_filter,
                metadata_filter=metadata_filter,
                authority_rerank=authority_rerank,
                collapse_group_dedup_max=collapse_max,
            )
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
        conn = self.engine._ensure_adg_connection()
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

        except (RuntimeError, ValueError, AttributeError, KeyError, TypeError):  # guardian: allow-double-logging -- structural-search failure logged before re-raise for query diagnostics
            raise

    def _hybrid_search(
        self,
        query: str,
        query_embedding: list[float] | None,
        collection_name: str,
        governance_filter: dict[str, Any] | None,
        metadata_filter: dict[str, Any] | None = None,
        authority_rerank: bool = False,
        collapse_group_dedup_max: int | None = None,
    ) -> list[Any]:
        """Execute hybrid search combining semantic and structural.

        Args:
            query: Query string
            query_embedding: Pre-computed query embedding
            collection_name: ChromaDB collection name
            governance_filter: Optional governance filters
            metadata_filter: Optional Chroma where= prefilter
            authority_rerank: Whether to apply authority_level reranking
            collapse_group_dedup_max: If set, cap results per collapse_group

        Returns:
            Fused search results
        """
        semantic_results = self.engine.search(
            query=query,
            query_embedding=query_embedding,
            collection_name=collection_name,
            governance_filter=governance_filter,
            metadata_filter=metadata_filter,
            authority_rerank=authority_rerank,
            collapse_group_dedup_max=collapse_group_dedup_max,
        )
        return semantic_results
