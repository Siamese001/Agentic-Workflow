"""Context Assembler.

Assembles and formats context from search results for RAG generation,
including filtering, ranking, and truncation strategies.
"""

from __future__ import annotations

from datetime import datetime

from agentic_core.L1_cognition.config.graphrag_config import get_config
from agentic_core.L1_cognition.reasoning.search_fusion_engine import SearchFusionEngine
from agentic_core.L1_cognition.types.rag_types import (
    ContextItem,
    RAGConfig,
    RAGContext,
    RAGQuery,
)
from agentic_core.L1_cognition.types.search_types import SearchResponse
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_records_telemetry_event,  # noqa: E402
)
from tqdm import tqdm


class ContextAssembler:
    """Assembles context from search results for RAG generation."""

    def __init__(
        self,
        search_engine: SearchFusionEngine,
        config: RAGConfig | None = None,
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
        self._assembly_stats: dict[str, list[float]] = {
            "assembly_time": [],
            "context_length": [],
            "item_count": [],
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
                filtered_items,
                query,
            )

            # Step 5: Calculate statistics
            context = self._create_context(
                query,
                final_items,
                truncation_applied,
                start_time,
            )

            # Update statistics
            assembly_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._assembly_stats["assembly_time"].append(assembly_time)
            self._assembly_stats["context_length"].append(context.total_length)
            self._assembly_stats["item_count"].append(context.total_items)

            _emit_records_telemetry_event(
                "context_assembler",
                f"context_assembled_{context.total_items}_items_{context.total_length}_chars",
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
                warnings=[f"Context assembly failed: {str(e)}"],
            )

    async def _search_for_context(self, query: RAGQuery) -> SearchResponse:
        """Search for relevant context items."""
        # Convert RAG query to search query
        search_query = query.search_response if hasattr(query, "search_response") else None

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
                relation_types=query.search_filters.get("relation_types"),
            )

        # Execute search
        search_response = await self.search_engine.search(search_query)

        return search_response

    def _convert_to_context_items(
        self,
        search_response: SearchResponse,
        query: RAGQuery,
    ) -> list[ContextItem]:
        """Convert search results to context items."""
        context_items = []

        for result in tqdm(search_response.results, desc="Processing", unit="item"):
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
                line_number=getattr(result, "line_number", None),
                confidence=result.confidence,
                context_type=context_type,
                hierarchy_level=result.metadata.get("community_level"),
                surrounding_context=result.context,
                formatted_content=None,  # Will be formatted later
            )

            context_items.append(item)

        return context_items

    def _filter_and_rank_items(
        self,
        items: list[ContextItem],
        query: RAGQuery,
    ) -> list[ContextItem]:
        """Filter and rank context items."""
        # Apply filters
        filtered_items = []

        for item in tqdm(items, desc="Processing", unit="item"):
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
        items: list[ContextItem],
        query: RAGQuery,
    ) -> list[ContextItem]:
        """Apply diversity filtering to avoid redundant items."""
        if len(items) <= query.min_context_items:
            return items

        diverse_items = [items[0]]  # Always include the top item
        seen_sources = set()

        if items[0].source_file:
            seen_sources.add(items[0].source_file)

        for item in tqdm(items[1:], desc="Processing", unit="item"):
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

    def _is_too_similar(self, item: ContextItem, existing_items: list[ContextItem]) -> bool:
        """Check if an item is too similar to existing items."""
        # Simple text similarity check
        item_words = set(item.content.lower().split())

        for existing in tqdm(existing_items, desc="Processing", unit="item"):
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
        items: list[ContextItem],
        query: RAGQuery,
    ) -> tuple[list[ContextItem], bool]:
        """Apply length constraints to context items."""
        total_length = sum(len(item.content) for item in items)

        if total_length <= query.max_context_length:
            return items, False

        # Need to truncate
        truncated_items = []
        current_length = 0
        truncation_applied = True

        for item in tqdm(items, desc="Processing", unit="item"):
            item_length = len(item.content)

            if current_length + item_length <= query.max_context_length:
                truncated_items.append(item)
                current_length += item_length
            else:
                # Try to add a truncated version
                remaining_space = query.max_context_length - current_length
                if remaining_space > 100:  # Only add if meaningful space remains
                    # Truncate the content
                    truncated_content = item.content[: remaining_space - 3] + "..."
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
                        formatted_content=None,
                    )
                    truncated_items.append(truncated_item)
                break

        return truncated_items, truncation_applied

    def _create_context(
        self,
        query: RAGQuery,
        items: list[ContextItem],
        truncation_applied: bool,
        start_time: datetime,
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
            warnings.append(
                f"Only {len(items)} context items found, below minimum of {query.min_context_items}"
            )

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
            warnings=warnings,
        )

    def _estimate_tokens(self, text_length: int) -> int:
        """Estimate token count from text length."""
        # Rough estimate: ~4 characters per token
        return max(1, text_length // 4)

    def get_assembly_stats(self) -> dict[str, dict[str, float]]:
        """Get context assembly statistics."""
        stats = {}

        for metric, values in tqdm(self._assembly_stats.items(), desc="Processing", unit="item"):
            if values:
                stats[metric] = {
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values),
                }
            else:
                stats[metric] = {
                    "avg": 0.0,
                    "min": 0.0,
                    "max": 0.0,
                    "count": 0,
                }

        return stats


# Factory function
def create_context_assembler(
    search_engine: SearchFusionEngine,
    config: RAGConfig | None = None,
) -> ContextAssembler:
    """Create a context assembler."""
    return ContextAssembler(search_engine, config)


__all__ = [
    "ContextAssembler",
    "create_context_assembler",
]
