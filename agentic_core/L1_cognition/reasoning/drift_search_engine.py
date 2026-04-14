"""DRIFT Search Engine.

Implements DRIFT (Dynamic Reasoning-Informed Fusion and Traversal) search
strategy that combines semantic, structural, and reasoning-based search.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.L4_state.types.graph_store_types import GraphEntity, IGraphStore

from agentic_core.L1_cognition.config.graphrag_config import get_config
from agentic_core.L1_cognition.types.search_types import (
    DRIFTSearchConfig,
    SearchQuery,
    SearchResponse,
    SearchResult,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_records_telemetry_event,  # noqa: E402
)
from tqdm import tqdm


class DRIFTSearchEngine:
    """Implements DRIFT search strategy for GraphRAG."""

    def __init__(
        self,
        graph_store: IGraphStore,
        config: DRIFTSearchConfig | None = None,
    ) -> None:
        """Initialize the DRIFT search engine.

        Args:
            graph_store: The graph store to search in
            config: DRIFT search configuration
        """
        self.graph_store = graph_store
        self.config = config or DRIFTSearchConfig()
        self.graphrag_config = get_config()

        # Learning feedback storage
        self._feedback_history: dict[str, list[tuple[float, datetime]]] = {}

    async def search(self, query: SearchQuery) -> SearchResponse:
        """Perform DRIFT search for the given query.

        Args:
            query: The search query

        Returns:
            SearchResponse with results and metadata
        """
        start_time = datetime.utcnow()

        try:
            # Step 1: Multi-strategy search
            semantic_results = await self._semantic_search(query)
            structural_results = await self._structural_search(query)
            reasoning_results = await self._reasoning_search(query)

            # Step 2: Dynamic fusion of results
            fused_results = await self._dynamic_fusion(
                semantic_results,
                structural_results,
                reasoning_results,
                query,
            )

            # Step 3: Apply adaptive traversal
            traversed_results = await self._adaptive_traversal(fused_results, query)

            # Step 4: Context-aware pruning
            pruned_results = self._context_aware_pruning(traversed_results, query)

            # Step 5: Apply filters and limits
            filtered_results = self._apply_filters(pruned_results, query)

            # Calculate statistics
            relevance_scores = [r.relevance_score for r in filtered_results]
            avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0

            response = SearchResponse(
                query=query,
                results=filtered_results[: query.max_results],
                total_found=len(filtered_results),
                total_returned=min(len(filtered_results), query.max_results),
                search_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                avg_relevance_score=avg_relevance,
                max_relevance_score=max(relevance_scores) if relevance_scores else 0.0,
                min_relevance_score=min(relevance_scores) if relevance_scores else 0.0,
                search_strategy="drift",
                fusion_method="dynamic_reasoning_informed",
                metadata={
                    "semantic_results": len(semantic_results),
                    "structural_results": len(structural_results),
                    "reasoning_results": len(reasoning_results),
                    "max_reasoning_depth": self.config.max_reasoning_depth,
                },
            )

            _emit_records_telemetry_event(
                "drift_search_engine",
                f"search_completed_{len(filtered_results)}_results",
            )

            return response

        except Exception as e:
            return SearchResponse(
                query=query,
                results=[],
                total_found=0,
                total_returned=0,
                search_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                avg_relevance_score=0.0,
                max_relevance_score=0.0,
                min_relevance_score=0.0,
                search_strategy="drift",
                fusion_method="dynamic_reasoning_informed",
                errors=[f"DRIFT search failed: {str(e)}"],
            )

    async def _semantic_search(self, query: SearchQuery) -> list[SearchResult]:
        """Perform semantic search using embeddings."""
        # Find entities using text search (sync call)
        search_result = self.graph_store.search_entities(
            query=query.text,
            limit=query.max_results,
        )

        results = []
        for entity in tqdm(search_result, desc="Processing", unit="item"):
            # Calculate relevance score
            score = self._calculate_text_similarity(entity, query.text)

            result = SearchResult(
                item_id=entity.id,
                item_type="entity",
                title=entity.name,
                description=entity.description,
                relevance_score=score,
                source_file=entity.metadata.get("file_path"),
                metadata={
                    "search_type": "semantic",
                    "entity_type": entity.entity_type,
                },
            )
            results.append(result)

        return results

    async def _structural_search(self, query: SearchQuery) -> list[SearchResult]:
        """Perform structural search based on graph topology."""
        # Find seed entities first (sync call)
        seed_search = self.graph_store.search_entities(
            query=query.text,
            limit=5,
        )

        results = []

        # For each seed, explore structural relationships
        for entity in tqdm(seed_search[:3], desc="Processing", unit="item"):  # Limit to top 3 seeds
            # Get traversal results (sync call)
            traversal = self.graph_store.traverse(
                start_id=entity.id,
                max_depth=2,
                relation_types=query.relation_types if hasattr(query, "relation_types") else None,
            )

            # Convert traversal results to search results
            for path in tqdm(traversal, desc="Processing", unit="item"):
                for path_entity in tqdm(path.nodes, desc="Processing", unit="item"):
                    # Calculate structural relevance
                    struct_score = self._calculate_structural_relevance(
                        path_entity,
                        entity,
                        query,
                    )

                    result = SearchResult(
                        item_id=path_entity.id,
                        item_type="entity",
                        title=path_entity.name,
                        description=path_entity.description,
                        relevance_score=struct_score,
                        path_to_root=[r.relation_type for r in path.relationships],
                        metadata={
                            "search_type": "structural",
                            "seed_entity": entity.id,
                            "path_length": len(path.relationships),
                        },
                    )
                    results.append(result)

        return results

    async def _reasoning_search(self, query: SearchQuery) -> list[SearchResult]:
        """Perform reasoning-based search with multi-hop inference."""
        # This is a simplified reasoning search
        # In practice, you'd use actual reasoning chains

        results = []

        # Find entities that match query keywords
        keywords = query.text.lower().split()

        # For each keyword, find related entities through reasoning
        for keyword in tqdm(keywords[:3], desc="Processing", unit="item"):  # Limit keywords
            # Find entities with keyword (sync call)
            keyword_search = self.graph_store.search_entities(
                query=keyword,
                limit=10,
            )

            # Apply reasoning depth
            for entity in tqdm(keyword_search, desc="Processing", unit="item"):
                reasoning_score = self._apply_reasoning_depth(entity, keyword, query)

                if reasoning_score >= self.config.reasoning_confidence_threshold:
                    result = SearchResult(
                        item_id=entity.id,
                        item_type="entity",
                        title=entity.name,
                        description=entity.description,
                        relevance_score=reasoning_score,
                        metadata={
                            "search_type": "reasoning",
                            "reasoning_keyword": keyword,
                            "reasoning_depth": 1,
                        },
                    )
                    results.append(result)

        return results

    def _calculate_structural_relevance(
        self,
        entity: GraphEntity,
        seed_entity: GraphEntity,
        query: SearchQuery,
    ) -> float:
        """Calculate structural relevance score."""
        # Base score from text similarity
        text_score = self._calculate_text_similarity(entity, query.text)

        # Structural boost based on relationship to seed
        struct_boost = 0.8 if entity.id != seed_entity.id else 1.0

        # Type compatibility
        type_boost = 1.0 if not query.entity_types or entity.entity_type in query.entity_types else 0.5

        combined_score = text_score * struct_boost * type_boost

        return min(1.0, combined_score)

    def _apply_reasoning_depth(
        self,
        entity: GraphEntity,
        keyword: str,
        query: SearchQuery,
    ) -> float:
        """Apply reasoning depth scoring."""
        # Base similarity
        similarity = self._calculate_text_similarity(entity, keyword)

        # Reasoning confidence decay
        depth_factor = self.config.feedback_decay_factor**0  # Depth 1

        return similarity * depth_factor

    async def _dynamic_fusion(
        self,
        semantic_results: list[SearchResult],
        structural_results: list[SearchResult],
        reasoning_results: list[SearchResult],
        query: SearchQuery,
    ) -> list[SearchResult]:
        """Dynamically fuse results from multiple strategies."""
        # Group results by entity ID
        entity_scores: dict[str, dict[str, float]] = {}

        # Collect scores from each strategy
        for result in semantic_results:
            entity_id = result.item_id
            if entity_id not in entity_scores:
                entity_scores[entity_id] = {}
            entity_scores[entity_id]["semantic"] = result.relevance_score

        for result in structural_results:
            entity_id = result.item_id
            if entity_id not in entity_scores:
                entity_scores[entity_id] = {}
            entity_scores[entity_id]["structural"] = result.relevance_score

        for result in reasoning_results:
            entity_id = result.item_id
            if entity_id not in entity_scores:
                entity_scores[entity_id] = {}
            entity_scores[entity_id]["reasoning"] = result.relevance_score

        # Calculate fused scores
        fused_results = []
        for entity_id, scores in tqdm(entity_scores.items(), desc="Processing", unit="item"):
            semantic_score = scores.get("semantic", 0.0)
            structural_score = scores.get("structural", 0.0)
            reasoning_score = scores.get("reasoning", 0.0)

            # Dynamic weighted fusion
            fused_score = (
                semantic_score * self.config.semantic_weight
                + structural_score * self.config.structural_weight
                + reasoning_score * self.config.reasoning_weight
            )

            # Get the best result to use as base
            best_result = None
            best_original_score = 0.0

            for result_list in [semantic_results, structural_results, reasoning_results]:
                for result in result_list:
                    if result.item_id == entity_id and result.relevance_score > best_original_score:
                        best_result = result
                        best_original_score = result.relevance_score

            if best_result:
                # Update the result with fused score
                fused_result = SearchResult(
                    item_id=best_result.item_id,
                    item_type=best_result.item_type,
                    title=best_result.title,
                    description=best_result.description,
                    relevance_score=min(1.0, fused_score),
                    context=best_result.context,
                    surrounding_entities=best_result.surrounding_entities,
                    path_to_root=best_result.path_to_root,
                    source_file=best_result.source_file,
                    confidence=best_result.confidence,
                    metadata={
                        **best_result.metadata,
                        "fused_score": fused_score,
                        "semantic_score": semantic_score,
                        "structural_score": structural_score,
                        "reasoning_score": reasoning_score,
                    },
                )
                fused_results.append(fused_result)

        # Sort by fused score
        fused_results.sort(key=lambda r: r.relevance_score, reverse=True)

        return fused_results

    async def _adaptive_traversal(
        self,
        results: list[SearchResult],
        query: SearchQuery,
    ) -> list[SearchResult]:
        """Apply adaptive traversal to expand result context."""
        if not self.config.adaptive_hop_selection:
            return results

        enhanced_results = []

        for result in tqdm(results[:20], desc="Processing", unit="item"):  # Limit traversal to top 20
            # Get additional context through traversal (sync call)
            if result.item_type == "entity":
                traversal = self.graph_store.traverse(
                    start_id=result.item_id,
                    max_depth=1,
                    relation_types=query.relation_types if hasattr(query, "relation_types") else None,
                )

                # Update result with traversal context
                if traversal:
                    # Collect surrounding entity IDs from paths
                    surrounding_ids = []
                    for path in traversal:
                        for entity in path.nodes:
                            if entity.id != result.item_id:
                                surrounding_ids.append(entity.id)
                    result.surrounding_entities = surrounding_ids[:5]
                    result.metadata["traversal_expanded"] = True

            enhanced_results.append(result)

        return enhanced_results

    def _context_aware_pruning(
        self,
        results: list[SearchResult],
        query: SearchQuery,
    ) -> list[SearchResult]:
        """Apply context-aware pruning to remove redundant results."""
        if not self.config.context_aware_pruning:
            return results

        pruned = []
        seen_entities = set()

        for result in results:
            # Check for redundancy
            entity_key = (result.item_type, result.title.lower())

            if entity_key not in seen_entities:
                seen_entities.add(entity_key)
                pruned.append(result)
            elif result.relevance_score > 0.8:  # Keep high-score duplicates
                pruned.append(result)

        return pruned

    def _apply_filters(self, results: list[SearchResult], query: SearchQuery) -> list[SearchResult]:
        """Apply final filters to results."""
        filtered = []

        for result in results:
            # Minimum relevance score
            if result.relevance_score < query.min_relevance_score:
                continue

            # Include/exclude by type
            if query.include_entities and result.item_type != "entity":
                continue

            filtered.append(result)

        return filtered

    def _calculate_text_similarity(self, entity: GraphEntity, query_text: str) -> float:
        """Calculate text similarity between entity and query."""
        query_terms = set(query_text.lower().split())
        entity_text = f"{entity.name} {entity.description}".lower()
        entity_terms = set(entity_text.split())

        if not query_terms:
            return 0.0

        intersection = query_terms & entity_terms
        union = query_terms | entity_terms

        # Jaccard similarity
        jaccard = len(intersection) / len(union) if union else 0.0

        # Boost for exact name matches
        name_boost = 1.0 if query_text.lower() == entity.name.lower() else 0.0

        return min(1.0, jaccard * 0.7 + name_boost * 0.3)

    def add_feedback(self, query_id: str, result_id: str, rating: float) -> None:
        """Add user feedback for learning."""
        if query_id not in self._feedback_history:
            self._feedback_history[query_id] = []

        self._feedback_history[query_id].append((rating, datetime.utcnow()))

        # Apply feedback decay to old entries
        if self.config.enable_feedback_learning:
            self._apply_feedback_decay(query_id)

    def _apply_feedback_decay(self, query_id: str) -> None:
        """Apply decay factor to old feedback."""
        if query_id not in self._feedback_history:
            return

        current_time = datetime.utcnow()
        decayed_feedback = []

        for rating, timestamp in self._feedback_history[query_id]:
            age_hours = (current_time - timestamp).total_seconds() / 3600
            if age_hours < 24:  # Only keep feedback from last 24 hours
                decayed_rating = rating * (self.config.feedback_decay_factor**age_hours)
                decayed_feedback.append((decayed_rating, timestamp))

        self._feedback_history[query_id] = decayed_feedback


# Factory function
def create_drift_search_engine(
    graph_store: IGraphStore,
    config: DRIFTSearchConfig | None = None,
) -> DRIFTSearchEngine:
    """Create a DRIFT search engine."""
    return DRIFTSearchEngine(graph_store, config)


__all__ = [
    "DRIFTSearchEngine",
    "create_drift_search_engine",
]
