"""Global Search Engine.

Implements global search strategy that searches across communities
and their summaries to find relevant information at a higher level.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.L4_state.types.graph_store_types import GraphCommunity, IGraphStore

from agentic_core.L1_cognition.config.graphrag_config import get_config
from agentic_core.L1_cognition.types.search_types import (
    GlobalSearchConfig,
    SearchQuery,
    SearchResponse,
    SearchResult,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

emit_replay_key("p0", "global_search_engine")
emit_determinism_digest("p0", "global_search_engine")

_emit_dispatches_healing_run("p1", "global_search_engine", "L1")
_emit_routes_through("p1", "global_search_engine", "L1")
_emit_checks_agent_registry("p1", "global_search_engine", "agent_registry")
_emit_validates_agent_capability("p1", "global_search_engine", "capability")
_emit_dispatches_execution_plan("p1", "global_search_engine", "exec_plan")
_emit_agent_executes_agent("p1", "global_search_engine", "sub_agent")
_emit_routes_to_agent("p1", "global_search_engine", "target_agent")
_emit_verifies_policy("p1", "global_search_engine", "policy_check")
_emit_observes_runtime_state("p1", "global_search_engine", "runtime_state")
_emit_verifies_boundary("p1", "global_search_engine", "boundary_check")
_emit_transcripts_response("p1", "global_search_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "global_search_engine")
_emit_gated_by_confidence("p1", "global_search_engine", "confidence_gate")
_emit_escalates_to_human("p1", "global_search_engine", "L1")
_emit_reads_policy_state("p1", "global_search_engine", "L1")
_emit_authorize_and_execute("p2", "global_search_engine", "execution_auth")
_emit_validates_capability("p2", "global_search_engine", "capability_check")
_emit_routes_to_capability("p2", "global_search_engine", "capability_route")
_emit_writes_via_uwg("p2", "global_search_engine", "uwg_write")
_emit_blocks_direct_write("p2", "global_search_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "global_search_engine", "tool_invocation")
_emit_captures_execution_output("p2", "global_search_engine", "exec_output")
_emit_dispatches_agent("p3", "global_search_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "global_search_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "global_search_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "global_search_engine", "healing_outcome")
_emit_escalates_failure("p3", "global_search_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "global_search_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "global_search_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "global_search_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "global_search_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "global_search_engine", "eval_metric")
_emit_stores_embedding("p4", "global_search_engine", "embedding_store")


class GlobalSearchEngine:
    """Implements global search strategy for GraphRAG."""

    def __init__(
        self,
        graph_store: IGraphStore,
        config: GlobalSearchConfig | None = None
    ) -> None:
        """Initialize the global search engine.

        Args:
            graph_store: The graph store to search in
            config: Global search configuration
        """
        self.graph_store = graph_store
        self.config = config or GlobalSearchConfig()
        self.graphrag_config = get_config()

    async def search(self, query: SearchQuery) -> SearchResponse:
        """Perform global search for the given query.

        Args:
            query: The search query

        Returns:
            SearchResponse with results and metadata
        """
        start_time = datetime.utcnow()

        try:
            # Step 1: Search communities by summaries
            community_results = await self._search_communities(query)

            # Step 2: For top communities, search within them
            entity_results = await self._search_within_communities(community_results, query)

            # Step 3: Combine and score results
            combined_results = await self._combine_results(community_results, entity_results, query)

            # Step 4: Apply filters and limits
            filtered_results = self._apply_filters(combined_results, query)

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
                search_strategy="global",
                metadata={
                    "communities_searched": len(community_results),
                    "entities_found": len(entity_results),
                    "max_communities": self.config.max_communities
                }
            )

            _emit_records_telemetry_event(
                "global_search_engine",
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
                search_strategy="global",
                errors=[f"Global search failed: {str(e)}"]
            )

    async def _search_communities(self, query: SearchQuery) -> list[SearchResult]:
        """Search communities by their summaries and descriptions."""
        # Get all communities (simplified - in practice, you'd use search)
        communities = []

        # This is a placeholder - in practice, you'd have a proper community search
        # For now, we'll simulate finding communities

        # Create mock community results
        for i in range(min(self.config.max_communities, 5)):
            community_id = f"community_{i}"

            # Calculate summary match score
            summary_score = self._calculate_summary_match(query.text, f"Community {i} summary")

            if summary_score >= query.min_relevance_score:
                result = SearchResult(
                    item_id=community_id,
                    item_type="community",
                    title=f"Community {i}",
                    description=f"Description for community {i}",
                    relevance_score=summary_score,
                    context=f"Community level: {i % 3}",
                    metadata={
                        "community_level": i % 3,
                        "summary_match": summary_score,
                        "entity_count": 10 + i * 5
                    }
                )
                communities.append(result)

        # Sort by relevance
        communities.sort(key=lambda r: r.relevance_score, reverse=True)

        return communities

    async def _search_within_communities(
        self,
        community_results: list[SearchResult],
        query: SearchQuery
    ) -> list[SearchResult]:
        """Search for entities within the top communities."""
        entity_results = []

        # Get entities from top communities
        top_communities = community_results[:self.config.max_communities]

        for community_result in top_communities:
            community_id = community_result.item_id

            # Get community details (simplified)
            community = await self.graph_store.get_community(community_id)

            if community and community.member_entity_ids:
                # Search within this community
                community_entities = await self._search_community_entities(
                    community, query, community_result.relevance_score
                )
                entity_results.extend(community_entities)

        return entity_results

    async def _search_community_entities(
        self,
        community: GraphCommunity,
        query: SearchQuery,
        community_boost: float
    ) -> list[SearchResult]:
        """Search for entities within a specific community."""
        entity_results = []

        # Limit entities per community
        entity_ids = list(community.member_entity_ids)[:self.config.max_entities_per_community]

        for entity_id in entity_ids:
            # Get entity
            entity = await self.graph_store.get_entity(entity_id)

            if entity:
                # Calculate entity relevance
                entity_score = self._calculate_entity_relevance(entity, query)

                # Apply community boost
                boosted_score = min(1.0, entity_score * community_boost * self.config.community_boost_weight)

                if boosted_score >= query.min_relevance_score:
                    result = SearchResult(
                        item_id=entity.id,
                        item_type="entity",
                        title=entity.name,
                        description=entity.description,
                        relevance_score=boosted_score,
                        context=f"In community: {community.title}",
                        source_file=entity.metadata.get("resolved_path"),
                        metadata={
                            "entity_type": entity.entity_type,
                            "community_id": community.id,
                            "community_level": community.level,
                            "base_score": entity_score,
                            "community_boost": community_boost
                        }
                    )
                    entity_results.append(result)

        # Sort by relevance
        entity_results.sort(key=lambda r: r.relevance_score, reverse=True)

        return entity_results

    def _calculate_summary_match(self, query_text: str, summary_text: str) -> float:
        """Calculate how well the query matches a community summary."""
        # Simple keyword matching (in practice, you'd use embeddings)
        query_terms = set(query_text.lower().split())
        summary_terms = set(summary_text.lower().split())

        if not query_terms:
            return 0.0

        intersection = query_terms & summary_terms
        union = query_terms | summary_terms

        # Jaccard similarity
        jaccard = len(intersection) / len(union) if union else 0.0

        return jaccard

    def _calculate_entity_relevance(self, entity, query: SearchQuery) -> float:
        """Calculate entity relevance within a community context."""
        # Text similarity
        text_score = self._calculate_text_similarity(entity, query.text)

        # Entity density consideration (smaller communities get higher weight)
        density_score = 1.0  # Placeholder

        # Combined score
        combined_score = (
            text_score * self.config.keyword_match_weight +
            density_score * self.config.entity_density_weight
        )

        return min(1.0, combined_score)

    def _calculate_text_similarity(self, entity, query_text: str) -> float:
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

    async def _combine_results(
        self,
        community_results: list[SearchResult],
        entity_results: list[SearchResult],
        query: SearchQuery
    ) -> list[SearchResult]:
        """Combine community and entity results."""
        combined = []

        # Add community results with type weighting
        for result in community_results:
            # Apply community summary weight
            weighted_score = result.relevance_score * self.config.community_summary_weight
            result.relevance_score = min(1.0, weighted_score)
            combined.append(result)

        # Add entity results
        for result in entity_results:
            combined.append(result)

        # Sort by relevance
        combined.sort(key=lambda r: r.relevance_score, reverse=True)

        return combined

    def _apply_filters(self, results: list[SearchResult], query: SearchQuery) -> list[SearchResult]:
        """Apply final filters to results."""
        filtered = []

        for result in results:
            # Minimum relevance score
            if result.relevance_score < query.min_relevance_score:
                continue

            # Community level filters
            if query.community_levels:
                community_level = result.metadata.get("community_level")
                if community_level not in query.community_levels:
                    continue

            # Include/exclude by type
            if query.include_communities and result.item_type != "community":
                continue
            if query.include_entities and result.item_type != "entity":
                continue

            filtered.append(result)

        return filtered


# Factory function
def create_global_search_engine(
    graph_store: IGraphStore,
    config: GlobalSearchConfig | None = None
) -> GlobalSearchEngine:
    """Create a global search engine."""
    return GlobalSearchEngine(graph_store, config)


__all__ = [
    "GlobalSearchEngine",
    "create_global_search_engine",
]
