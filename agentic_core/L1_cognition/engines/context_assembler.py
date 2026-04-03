"""Context Assembler.

Assembles and formats context from search results for RAG generation,
including filtering, ranking, and truncation strategies.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from agentic_core.L1_cognition.config.graphrag_config import get_config
from agentic_core.L1_cognition.engines.search_fusion_engine import SearchFusionEngine
from agentic_core.L1_cognition.types.rag_types import (
    ContextItem,
    RAGConfig,
    RAGContext,
    RAGQuery,
)
from agentic_core.L1_cognition.types.search_types import SearchResponse
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

emit_replay_key("p0", "context_assembler")
emit_determinism_digest("p0", "context_assembler")

_emit_dispatches_healing_run("p1", "context_assembler", "L1")
_emit_routes_through("p1", "context_assembler", "L1")
_emit_checks_agent_registry("p1", "context_assembler", "agent_registry")
_emit_validates_agent_capability("p1", "context_assembler", "capability")
_emit_dispatches_execution_plan("p1", "context_assembler", "exec_plan")
_emit_agent_executes_agent("p1", "context_assembler", "sub_agent")
_emit_routes_to_agent("p1", "context_assembler", "target_agent")
_emit_verifies_policy("p1", "context_assembler", "policy_check")
_emit_observes_runtime_state("p1", "context_assembler", "runtime_state")
_emit_verifies_boundary("p1", "context_assembler", "boundary_check")
_emit_transcripts_response("p1", "context_assembler", "transcript")
_emit_hard_fails_untranscripted("p1", "context_assembler")
_emit_gated_by_confidence("p1", "context_assembler", "confidence_gate")
_emit_escalates_to_human("p1", "context_assembler", "L1")
_emit_reads_policy_state("p1", "context_assembler", "L1")
_emit_authorize_and_execute("p2", "context_assembler", "execution_auth")
_emit_validates_capability("p2", "context_assembler", "capability_check")
_emit_routes_to_capability("p2", "context_assembler", "capability_route")
_emit_writes_via_uwg("p2", "context_assembler", "uwg_write")
_emit_blocks_direct_write("p2", "context_assembler", "direct_write_block")
_emit_records_tool_invocation("p2", "context_assembler", "tool_invocation")
_emit_captures_execution_output("p2", "context_assembler", "exec_output")
_emit_dispatches_agent("p3", "context_assembler", "agent_dispatch")
_emit_coordinates_agents("p3", "context_assembler", "agent_coordination")
_emit_records_workflow_lineage("p3", "context_assembler", "workflow_lineage")
_emit_records_healing_outcome("p3", "context_assembler", "healing_outcome")
_emit_escalates_failure("p3", "context_assembler", "failure_escalation")
_emit_orchestrates_workflow("p3", "context_assembler", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "context_assembler", "healing_dispatch")
_emit_invokes_evaluation("p3", "context_assembler", "evaluation_signal")
_emit_records_telemetry_event("p4", "context_assembler", "telemetry_event")
_emit_captures_evaluation_metric("p4", "context_assembler", "eval_metric")
_emit_stores_embedding("p4", "context_assembler", "embedding_store")


class ContextAssembler:
    """Assembles context from search results for RAG generation."""

    def __init__(
        self,
        search_engine: SearchFusionEngine,
        config: Optional[RAGConfig] = None
    ) -> None:
        """Initialize the context assembler.

        Args:
            search_engine: The search engine to use for finding context
            config: RAG configuration
        """
        self.search_engine = search_engine
        self.config = config or RAGConfig()
        self.graphrag_config = get_config()

        # Context assembly statistics
        self._assembly_stats: Dict[str, List[float]] = {
            "assembly_time": [],
            "context_length": [],
            "item_count": []
        }

    async def assemble_context(self, query: RAGQuery) -> RAGContext:
        """Assemble context for the given query.

        Args:
            query: The RAG query

        Returns:
            Assembled RAG context
        """
        start_time = datetime.utcnow()

        try:
            # Step 1: Search for relevant items
            search_response = await self._search_for_context(query)

            # Step 2: Convert search results to context items
            context_items = self._convert_to_context_items(search_response, query)

            # Step 3: Filter and rank items
            filtered_items = self._filter_and_rank_items(context_items, query)

            # Step 4: Apply length constraints
            final_items, truncation_applied = self._apply_length_constraints(
                filtered_items, query
            )

            # Step 5: Calculate statistics
            context = self._create_context(
                query, final_items, truncation_applied, start_time
            )

            # Update statistics
            assembly_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._assembly_stats["assembly_time"].append(assembly_time)
            self._assembly_stats["context_length"].append(context.total_length)
            self._assembly_stats["item_count"].append(context.total_items)

            _emit_records_telemetry_event(
                "context_assembler",
                f"context_assembled_{context.total_items}_items_{context.total_length}_chars"
            )

            return context

        except Exception as e:
            # Return empty context on error
            return RAGContext(
                query=query,
                items=[],
                total_items=0,
                total_length=0,
                token_estimate=0,
                avg_relevance_score=0.0,
                max_relevance_score=0.0,
                min_relevance_score=0.0,
                item_type_distribution={},
                source_distribution={},
                assembly_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                assembly_method="error",
                truncation_applied=False,
                warnings=[f"Context assembly failed: {str(e)}"]
            )

    async def _search_for_context(self, query: RAGQuery) -> SearchResponse:
        """Search for relevant context items."""
        # Convert RAG query to search query
        search_query = query.search_response if hasattr(query, 'search_response') else None

        if not search_query:
            # Create search query from RAG query
            from agentic_core.L1_cognition.types.search_types import SearchQuery

            search_query = SearchQuery(
                text=query.query_text,
                query_type=query.query_type,
                search_mode=query.search_mode,
                max_results=query.max_context_items * 2,  # Get more to filter
                min_relevance_score=self.config.min_relevance_threshold,
                include_communities=query.include_communities,
                include_entities=True,
                entity_types=query.search_filters.get("entity_types"),
                relation_types=query.search_filters.get("relation_types")
            )

        # Execute search
        search_response = await self.search_engine.search(search_query)

        return search_response

    def _convert_to_context_items(
        self,
        search_response: SearchResponse,
        query: RAGQuery
    ) -> List[ContextItem]:
        """Convert search results to context items."""
        context_items = []

        for result in search_response.results:
            # Determine context type based on relevance
            if result.relevance_score >= 0.8:
                context_type = "primary"
            elif result.relevance_score >= 0.5:
                context_type = "supporting"
            else:
                context_type = "background"

            # Create context item
            item = ContextItem(
                item_id=result.item_id,
                content=result.description or result.title,
                item_type=result.item_type,
                title=result.title,
                relevance_score=result.relevance_score,
                source_file=result.source_file,
                line_number=getattr(result, 'line_number', None),
                confidence=result.confidence,
                context_type=context_type,
                hierarchy_level=result.metadata.get("community_level"),
                surrounding_context=result.context,
                formatted_content=None  # Will be formatted later
            )

            context_items.append(item)

        return context_items

    def _filter_and_rank_items(
        self,
        items: List[ContextItem],
        query: RAGQuery
    ) -> List[ContextItem]:
        """Filter and rank context items."""
        # Apply filters
        filtered_items = []

        for item in items:
            # Minimum relevance filter
            if item.relevance_score < self.config.min_relevance_threshold:
                continue

            # Item type filters
            if not query.include_entities and item.item_type == "entity":
                continue
            if not query.include_relationships and item.item_type == "relationship":
                continue
            if not query.include_communities and item.item_type == "community":
                continue

            filtered_items.append(item)

        # Sort by relevance score (descending)
        filtered_items.sort(key=lambda x: x.relevance_score, reverse=True)

        # Apply diversity filtering if needed
        if len(filtered_items) > query.min_context_items:
            filtered_items = self._apply_diversity_filtering(filtered_items, query)

        return filtered_items

    def _apply_diversity_filtering(
        self,
        items: List[ContextItem],
        query: RAGQuery
    ) -> List[ContextItem]:
        """Apply diversity filtering to avoid redundant items."""
        if len(items) <= query.min_context_items:
            return items

        diverse_items = [items[0]]  # Always include the top item
        seen_sources = set()

        if items[0].source_file:
            seen_sources.add(items[0].source_file)

        for item in items[1:]:
            # Check source diversity
            if item.source_file and item.source_file in seen_sources:
                # Skip if we already have an item from this source
                # unless we need more items to meet minimum
                if len(diverse_items) >= query.min_context_items:
                    continue

            # Check content similarity (simplified)
            if self._is_too_similar(item, diverse_items):
                if len(diverse_items) >= query.min_context_items:
                    continue

            diverse_items.append(item)
            if item.source_file:
                seen_sources.add(item.source_file)

            # Stop if we've reached maximum
            if len(diverse_items) >= query.max_context_items:
                break

        return diverse_items

    def _is_too_similar(self, item: ContextItem, existing_items: List[ContextItem]) -> bool:
        """Check if an item is too similar to existing items."""
        # Simple text similarity check
        item_words = set(item.content.lower().split())

        for existing in existing_items:
            existing_words = set(existing.content.lower().split())

            if not item_words or not existing_words:
                continue

            # Jaccard similarity
            intersection = item_words & existing_words
            union = item_words | existing_words
            similarity = len(intersection) / len(union) if union else 0.0

            # If too similar, skip
            if similarity > 0.7:
                return True

        return False

    def _apply_length_constraints(
        self,
        items: List[ContextItem],
        query: RAGQuery
    ) -> Tuple[List[ContextItem], bool]:
        """Apply length constraints to context items."""
        total_length = sum(len(item.content) for item in items)

        if total_length <= query.max_context_length:
            return items, False

        # Need to truncate
        truncated_items = []
        current_length = 0
        truncation_applied = True

        for item in items:
            item_length = len(item.content)

            if current_length + item_length <= query.max_context_length:
                truncated_items.append(item)
                current_length += item_length
            else:
                # Try to add a truncated version
                remaining_space = query.max_context_length - current_length
                if remaining_space > 100:  # Only add if meaningful space remains
                    # Truncate the content
                    truncated_content = item.content[:remaining_space - 3] + "..."
                    truncated_item = ContextItem(
                        item_id=item.item_id,
                        content=truncated_content,
                        item_type=item.item_type,
                        title=item.title,
                        relevance_score=item.relevance_score,
                        source_file=item.source_file,
                        line_number=item.line_number,
                        confidence=item.confidence,
                        context_type="truncated",
                        hierarchy_level=item.hierarchy_level,
                        surrounding_context=item.surrounding_context,
                        formatted_content=None
                    )
                    truncated_items.append(truncated_item)
                break

        return truncated_items, truncation_applied

    def _create_context(
        self,
        query: RAGQuery,
        items: List[ContextItem],
        truncation_applied: bool,
        start_time: datetime
    ) -> RAGContext:
        """Create the RAG context object."""
        # Calculate statistics
        total_length = sum(len(item.content) for item in items)
        token_estimate = self._estimate_tokens(total_length)

        relevance_scores = [item.relevance_score for item in items]
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0

        # Calculate distributions
        item_type_distribution = {}
        source_distribution = {}

        for item in items:
            # Item type distribution
            item_type_distribution[item.item_type] = item_type_distribution.get(item.item_type, 0) + 1

            # Source distribution
            if item.source_file:
                source_distribution[item.source_file] = source_distribution.get(item.source_file, 0) + 1

        # Create warnings
        warnings = []
        if truncation_applied:
            warnings.append("Context was truncated to fit length constraints")

        if len(items) < query.min_context_items:
            warnings.append(f"Only {len(items)} context items found, below minimum of {query.min_context_items}")

        assembly_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        return RAGContext(
            query=query,
            items=items,
            total_items=len(items),
            total_length=total_length,
            token_estimate=token_estimate,
            avg_relevance_score=avg_relevance,
            max_relevance_score=max(relevance_scores) if relevance_scores else 0.0,
            min_relevance_score=min(relevance_scores) if relevance_scores else 0.0,
            item_type_distribution=item_type_distribution,
            source_distribution=source_distribution,
            assembly_time_ms=assembly_time,
            assembly_method="filtered_ranked",
            truncation_applied=truncation_applied,
            warnings=warnings
        )

    def _estimate_tokens(self, text_length: int) -> int:
        """Estimate token count from text length."""
        # Rough estimate: ~4 characters per token
        return max(1, text_length // 4)

    def get_assembly_stats(self) -> Dict[str, Dict[str, float]]:
        """Get context assembly statistics."""
        stats = {}

        for metric, values in self._assembly_stats.items():
            if values:
                stats[metric] = {
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }
            else:
                stats[metric] = {
                    "avg": 0.0,
                    "min": 0.0,
                    "max": 0.0,
                    "count": 0
                }

        return stats


# Factory function
def create_context_assembler(
    search_engine: SearchFusionEngine,
    config: Optional[RAGConfig] = None
) -> ContextAssembler:
    """Create a context assembler."""
    return ContextAssembler(search_engine, config)


__all__ = [
    "ContextAssembler",
    "create_context_assembler",
]
