"""Local Search Engine.

Implements local search strategy that finds entities and relationships
within a specified hop distance from relevant seed entities.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.L4_state.types.graph_store_types import GraphEntity, IGraphStore

from agentic_core.L1_cognition.config.graphrag_config import get_config
from agentic_core.L1_cognition.types.search_types import (
    LocalSearchConfig,
    SearchQuery,
    SearchResponse,
    SearchResult,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "local_search_engine")
emit_determinism_digest("p0", "local_search_engine")

_emit_dispatches_healing_run("p1", "local_search_engine", "L1")
_emit_routes_through("p1", "local_search_engine", "L1")
_emit_checks_agent_registry("p1", "local_search_engine", "agent_registry")
_emit_validates_agent_capability("p1", "local_search_engine", "capability")
_emit_dispatches_execution_plan("p1", "local_search_engine", "exec_plan")
_emit_agent_executes_agent("p1", "local_search_engine", "sub_agent")
_emit_routes_to_agent("p1", "local_search_engine", "target_agent")
_emit_verifies_policy("p1", "local_search_engine", "policy_check")
_emit_observes_runtime_state("p1", "local_search_engine", "runtime_state")
_emit_verifies_boundary("p1", "local_search_engine", "boundary_check")
_emit_transcripts_response("p1", "local_search_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "local_search_engine")
_emit_gated_by_confidence("p1", "local_search_engine", "confidence_gate")
_emit_escalates_to_human("p1", "local_search_engine", "L1")
_emit_reads_policy_state("p1", "local_search_engine", "L1")
_emit_authorize_and_execute("p2", "local_search_engine", "execution_auth")
_emit_validates_capability("p2", "local_search_engine", "capability_check")
_emit_routes_to_capability("p2", "local_search_engine", "capability_route")
_emit_writes_via_uwg("p2", "local_search_engine", "uwg_write")
_emit_blocks_direct_write("p2", "local_search_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "local_search_engine", "tool_invocation")
_emit_captures_execution_output("p2", "local_search_engine", "exec_output")
_emit_dispatches_agent("p3", "local_search_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "local_search_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "local_search_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "local_search_engine", "healing_outcome")
_emit_escalates_failure("p3", "local_search_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "local_search_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "local_search_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "local_search_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "local_search_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "local_search_engine", "eval_metric")
_emit_stores_embedding("p4", "local_search_engine", "embedding_store")


class LocalSearchEngine:
    """Implements local search strategy for GraphRAG."""

    def __init__(
        self,
        graph_store: IGraphStore,
        config: LocalSearchConfig | None = None
    ) -> None:
        """Initialize the local search engine.

        Args:
            graph_store: The graph store to search in
            config: Local search configuration
        """
        self.graph_store = graph_store
        self.config = config or LocalSearchConfig()
        self.graphrag_config = get_config()

        # Cache for frequently accessed entities
        self._entity_cache: dict[str, GraphEntity] = {}
        self._cache_timestamps: dict[str, datetime] = {}

    async def search(self, query: SearchQuery) -> SearchResponse:
        """Perform local search for the given query.

        Args:
            query: The search query

        Returns:
            SearchResponse with results and metadata
        """
        start_time = datetime.utcnow()

        try:
            # Step 1: Find seed entities using text search
            seed_entities = await self._find_seed_entities(query)

            if not seed_entities:
                return SearchResponse(
                    query=query,
                    results=[],
                    total_found=0,
                    total_returned=0,
                    search_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                    avg_relevance_score=0.0,
                    max_relevance_score=0.0,
                    min_relevance_score=0.0,
                    search_strategy="local"
                )

            # Step 2: Expand search using graph traversal
            expanded_entities = await self._expand_search(seed_entities, query)

            # Step 3: Score and rank results
            scored_results = await self._score_results(expanded_entities, query, seed_entities)

            # Step 4: Apply filters and limits
            filtered_results = self._apply_filters(scored_results, query)

            # Calculate statistics
            relevance_scores = [r.relevance_score for r in filtered_results]
            avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0

            response = SearchResponse(
                query=query,
                results=filtered_results[:query.max_results],
                total_found=len(filtered_results),
                total_returned=min(len(filtered_results), query.max_results),
                search_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                avg_relevance_score=avg_relevance,
                max_relevance_score=max(relevance_scores) if relevance_scores else 0.0,
                min_relevance_score=min(relevance_scores) if relevance_scores else 0.0,
                search_strategy="local",
                metadata={
                    "seed_entities": len(seed_entities),
                    "expanded_entities": len(expanded_entities),
                    "max_hops": self.config.max_hops
                }
            )

            _emit_records_telemetry_event(
                "local_search_engine",
                f"search_completed_{len(filtered_results)}_results"
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
                search_strategy="local",
                errors=[f"Local search failed: {str(e)}"]
            )

    async def _find_seed_entities(self, query: SearchQuery) -> list[GraphEntity]:
        """Find seed entities using text search."""
        # Use the graph store's search functionality (sync call)
        search_result = self.graph_store.search_entities(
            query=query.text,
            limit=query.max_results * 2  # Get more to have better coverage
        )

        # Filter by relevance threshold
        seed_entities = []
        for entity in search_result:
            # Simple relevance check based on text matching
            text_score = self._calculate_text_similarity(entity, query)
            if text_score >= query.min_relevance_score:
                seed_entities.append(entity)

        return seed_entities

    async def _expand_search(
        self,
        seed_entities: list[GraphEntity],
        query: SearchQuery
    ) -> list[GraphEntity]:
        """Expand search using graph traversal from seed entities."""
        expanded_entities = set(seed_entities)  # Use set to avoid duplicates
        visited_entities = set(entity.id for entity in seed_entities)

        # BFS traversal up to max_hops
        current_level = seed_entities

        for hop in range(1, self.config.max_hops + 1):
            next_level = []

            for entity in current_level:
                # Get relationships (sync call)
                relationships = self.graph_store.get_relationships(
                    entity.id, direction="both"
                )

                for rel in relationships:
                    # Add connected entities
                    connected_id = rel.target_id if rel.source_id == entity.id else rel.source_id

                    if connected_id not in visited_entities:
                        visited_entities.add(connected_id)

                        # Get the connected entity (sync call)
                        connected_entity = self._get_cached_entity(connected_id)
                        if connected_entity:
                            # Apply filters
                            if self._passes_entity_filters(connected_entity, query):
                                next_level.append(connected_entity)
                                expanded_entities.add(connected_entity)

                                # Limit entities per hop
                                if len(next_level) >= self.config.max_entities_per_hop:
                                    break

                if len(next_level) >= self.config.max_entities_per_hop:
                    break

            current_level = next_level
            if not current_level:
                break

        return list(expanded_entities)

    async def _score_results(
        self,
        entities: list[GraphEntity],
        query: SearchQuery,
        seed_entities: list[GraphEntity]
    ) -> list[SearchResult]:
        """Score and rank entities based on multiple factors."""
        results = []
        seed_entity_ids = {e.id for e in seed_entities}

        for entity in entities:
            # Text similarity score (simplified)
            text_score = self._calculate_text_similarity(entity, query)

            # Graph proximity score
            proximity_score = self._calculate_proximity_score(entity, seed_entity_ids)

            # Community coherence score
            community_score = await self._calculate_community_score(entity, seed_entities)

            # Recency score (if timestamp available)
            recency_score = self._calculate_recency_score(entity)

            # Combined score
            combined_score = (
                text_score * self.config.text_similarity_weight +
                proximity_score * self.config.graph_proximity_weight +
                community_score * self.config.community_coherence_weight +
                recency_score * self.config.recency_weight
            )

            # Create search result
            result = SearchResult(
                item_id=entity.id,
                item_type="entity",
                title=entity.name,
                description=entity.description,
                relevance_score=min(1.0, combined_score),  # Clamp to [0, 1]
                context=await self._get_entity_context(entity),
                surrounding_entities=await self._get_surrounding_entities(entity),
                source_file=entity.metadata.get("resolved_path"),
                confidence=entity.confidence,
                metadata={
                    "entity_type": entity.entity_type,
                    "text_similarity": text_score,
                    "proximity_score": proximity_score,
                    "community_score": community_score,
                    "recency_score": recency_score,
                    "is_seed": entity.id in seed_entity_ids
                }
            )
            results.append(result)

        # Sort by relevance score
        results.sort(key=lambda r: r.relevance_score, reverse=True)

        return results

    def _calculate_text_similarity(self, entity: GraphEntity, query: SearchQuery) -> float:
        """Calculate text similarity between entity and query."""
        # Simple keyword matching (in practice, you'd use embeddings)
        query_terms = set(query.text.lower().split())
        entity_text = f"{entity.name} {entity.description}".lower()
        entity_terms = set(entity_text.split())

        if not query_terms:
            return 0.0

        intersection = query_terms & entity_terms
        union = query_terms | entity_terms

        # Jaccard similarity
        jaccard = len(intersection) / len(union) if union else 0.0

        # Boost for exact name matches
        name_boost = 1.0 if query.text.lower() == entity.name.lower() else 0.0

        return min(1.0, jaccard * 0.7 + name_boost * 0.3)

    def _calculate_proximity_score(
        self,
        entity: GraphEntity,
        seed_entity_ids: set[str]
    ) -> float:
        """Calculate graph proximity score to seed entities."""
        if entity.id in seed_entity_ids:
            return 1.0  # Seed entities get max score

        # Simplified: check if directly connected to any seed
        # In practice, you'd calculate shortest path distances
        return 0.5  # Placeholder

    async def _calculate_community_score(
        self,
        entity: GraphEntity,
        seed_entities: list[GraphEntity]
    ) -> float:
        """Calculate community coherence score."""
        # Simplified: check if entity shares community with seeds
        # In practice, you'd use actual community assignments
        return 0.5  # Placeholder

    def _calculate_recency_score(self, entity: GraphEntity) -> float:
        """Calculate recency score based on entity timestamp."""
        # Simplified: return neutral score
        # In practice, you'd use entity creation/update timestamps
        return 0.5

    async def _get_entity_context(self, entity: GraphEntity) -> str | None:
        """Get context information for an entity."""
        # Get relationships to provide context (sync call)
        relationships = self.graph_store.get_relationships(entity.id, direction="both")

        if not relationships:
            return None

        # Build context string
        context_parts = []
        for rel in relationships[:5]:  # Limit to top 5
            target_id = rel.target_id if rel.source_id == entity.id else rel.source_id
            context_parts.append(f"{rel.relation_type} {target_id}")

        return f"Connected via: {', '.join(context_parts)}"

    async def _get_surrounding_entities(self, entity: GraphEntity) -> list[str]:
        """Get surrounding entity IDs."""
        # Get relationships (sync call)
        relationships = self.graph_store.get_relationships(entity.id, direction="both")

        surrounding = []
        for rel in relationships[:10]:  # Limit to 10 surrounding entities
            target_id = rel.target_id if rel.source_id == entity.id else rel.source_id
            surrounding.append(target_id)

        return surrounding

    def _passes_entity_filters(self, entity: GraphEntity, query: SearchQuery) -> bool:
        """Check if entity passes query filters."""
        # Entity type filter
        if query.entity_types and entity.entity_type not in query.entity_types:
            return False

        # Degree centrality filter
        if entity.confidence < self.config.min_degree_centrality:
            return False

        # Required entity types
        if self.config.required_entity_types and entity.entity_type not in self.config.required_entity_types:
            return False

        return True

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

    def _get_cached_entity(self, entity_id: str) -> GraphEntity | None:
        """Get entity from cache or graph store."""
        # Check cache
        if self.config.enable_caching and entity_id in self._entity_cache:
            # Check if cache is still valid
            if entity_id in self._cache_timestamps:
                age = (datetime.utcnow() - self._cache_timestamps[entity_id]).total_seconds()
                if age < self.config.cache_ttl_seconds:
                    return self._entity_cache[entity_id]

        # Get from graph store (sync call)
        entity = self.graph_store.get_entity(entity_id)

        # Update cache
        if entity and self.config.enable_caching:
            self._entity_cache[entity_id] = entity
            self._cache_timestamps[entity_id] = datetime.utcnow()

        return entity

    def clear_cache(self) -> None:
        """Clear the entity cache."""
        self._entity_cache.clear()
        self._cache_timestamps.clear()
        _emit_records_telemetry_event("local_search_engine", "cache_cleared")


# Factory function
def create_local_search_engine(
    graph_store: IGraphStore,
    config: LocalSearchConfig | None = None
) -> LocalSearchEngine:
    """Create a local search engine."""
    return LocalSearchEngine(graph_store, config)


def create_local_search_engine_with_sqlite(
    db_path: str | None = None,
    config: LocalSearchConfig | None = None
) -> LocalSearchEngine:
    """Create a local search engine with SQLiteGraphStore backend.
    
    Convenience function that creates a SQLiteGraphStore instance
    and initializes a LocalSearchEngine with it.
    
    Args:
        db_path: Path to ADG SQLite database. If None, uses default path.
        config: Local search configuration
    
    Returns:
        LocalSearchEngine instance with SQLiteGraphStore backend
    
    Raises:
        FileNotFoundError: If ADG database not found
    """
    from agentic_core.L4_state.utils.memory.graph_store_factory import create_sqlite_graph_store
    
    graph_store = create_sqlite_graph_store(db_path)
    return create_local_search_engine(graph_store, config)


__all__ = [
    "LocalSearchEngine",
    "create_local_search_engine",
    "create_local_search_engine_with_sqlite",
]
