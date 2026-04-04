"""Parent-Child Expansion (L4E) for Retrieval

Implements spec-compliant 4c: Parent-Child Expansion with:
- L4E Registry integration
- Recursive 3-hop expansion with confidence decay
- Parent context pulling
- Child context inclusion

Wires L4E ParentChildIndex to retrieval (spec Pipeline C Layer 3 - Step 4c).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_pulls_context,
    _emit_records_execution_trace,
)

Logger = logging.getLogger(__name__)


@dataclass
class ExpansionContext:
    """Context retrieved through parent-child expansion."""
    chunk_id: str
    content: str
    depth: int  # Hop distance from original
    relationship: str  # 'parent', 'child', 'sibling'
    confidence: float  # Decays with depth
    metadata: dict[str, Any] = field(default_factory=dict)


class ParentChildExpander:
    """Expands retrieval results using parent-child relationships.

    Implements 4c: Parent-Child Index Expansion
    - Iterative 3-hop expansion
    - Confidence decay per hop
    - Pulls context from L4E registry
    """

    def __init__(
        self,
        max_depth: int = 3,
        base_confidence: float = 1.0,
        confidence_decay: float = 0.7,
        min_confidence: float = 0.3,
        l4e_registry: Any | None = None,
    ):
        """Initialize parent-child expander.

        Args:
            max_depth: Maximum expansion hops (default 3)
            base_confidence: Starting confidence for root nodes
            confidence_decay: Multiplier per hop (0.7 = 30% decay)
            min_confidence: Minimum confidence to continue expansion
            l4e_registry: L4E ParentChildIndex registry
        """
        self.max_depth = max_depth
        self.base_confidence = base_confidence
        self.confidence_decay = confidence_decay
        self.min_confidence = min_confidence
        self.l4e_registry = l4e_registry

        self._expansion_count = 0
        self._avg_expanded_nodes = 0.0

    def expand(
        self,
        seed_chunk_id: str,
        seed_content: str | None = None,
        seed_metadata: dict[str, Any] | None = None,
    ) -> list[ExpansionContext]:
        """Expand from seed chunk using parent-child relationships.

        Args:
            seed_chunk_id: Starting chunk ID
            seed_content: Content of seed chunk
            seed_metadata: Metadata for seed chunk

        Returns:
            List of expansion contexts (includes seed at depth 0)
        """
        _trace_id = f"expand_{seed_chunk_id}_{self._expansion_count}"
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "ParentChildExpander.expand"
        )
        _emit_pulls_context(_trace_id, "ParentChildExpander", seed_chunk_id)

        results = []
        visited = {seed_chunk_id}
        queue: list[tuple[str, int, float]] = [(seed_chunk_id, 0, self.base_confidence)]

        # Add seed
        results.append(ExpansionContext(
            chunk_id=seed_chunk_id,
            content=seed_content or "",
            depth=0,
            relationship="seed",
            confidence=self.base_confidence,
            metadata=seed_metadata or {},
        ))

        while queue:
            current_id, current_depth, current_confidence = queue.pop(0)

            if current_depth >= self.max_depth:
                continue

            if current_confidence < self.min_confidence:
                continue

            # Get neighbors from L4E
            neighbors = self._get_neighbors(current_id)

            next_confidence = current_confidence * self.confidence_decay

            for neighbor in neighbors:
                neighbor_id = neighbor.get("chunk_id")
                relationship = neighbor.get("relationship", "related")

                if neighbor_id in visited:
                    continue

                visited.add(neighbor_id)

                results.append(ExpansionContext(
                    chunk_id=neighbor_id,
                    content=neighbor.get("content", ""),
                    depth=current_depth + 1,
                    relationship=relationship,
                    confidence=next_confidence,
                    metadata=neighbor.get("metadata", {}),
                ))

                queue.append((neighbor_id, current_depth + 1, next_confidence))

        # Update stats
        self._avg_expanded_nodes = (
            self._avg_expanded_nodes * self._expansion_count + len(results)
        ) / (self._expansion_count + 1)
        self._expansion_count += 1

        Logger.info(f"Expanded {seed_chunk_id}: {len(results)} nodes at depths 0-{self.max_depth}")

        return results

    def _get_neighbors(self, chunk_id: str) -> list[dict[str, Any]]:
        """Get parent and child neighbors from L4E.

        Args:
            chunk_id: Chunk ID to look up

        Returns:
            List of neighbor dicts with chunk_id, relationship, content
        """
        neighbors = []

        if self.l4e_registry is None:
            # Fallback: return empty (no expansion)
            return neighbors

        try:
            # Get parents
            parents = self.l4e_registry.get_parents(chunk_id)
            for parent in parents:
                neighbors.append({
                    "chunk_id": parent.chunk_id,
                    "relationship": "parent",
                    "content": parent.content,
                    "metadata": parent.metadata,
                })

            # Get children
            children = self.l4e_registry.get_children(chunk_id)
            for child in children:
                neighbors.append({
                    "chunk_id": child.chunk_id,
                    "relationship": "child",
                    "content": child.content,
                    "metadata": child.metadata,
                })

            # Get siblings (via shared parent)
            siblings = self.l4e_registry.get_siblings(chunk_id)
            for sibling in siblings:
                if sibling.chunk_id != chunk_id:  # Exclude self
                    neighbors.append({
                        "chunk_id": sibling.chunk_id,
                        "relationship": "sibling",
                        "content": sibling.content,
                        "metadata": sibling.metadata,
                    })

        except Exception as e:
            Logger.error(f"Failed to get neighbors for {chunk_id}: {e}")

        return neighbors

    def expand_batch(
        self,
        seed_results: list[dict[str, Any]],
        max_total_contexts: int = 50,
    ) -> list[ExpansionContext]:
        """Expand multiple seed results with deduplication.

        Args:
            seed_results: List of seed result dicts with chunk_id, content, metadata
            max_total_contexts: Maximum total contexts to return

        Returns:
            Combined list of expansion contexts
        """
        all_contexts = []
        seen_ids = set()

        for seed in seed_results:
            chunk_id = seed.get("chunk_id") or seed.get("id")
            if not chunk_id or chunk_id in seen_ids:
                continue

            contexts = self.expand(
                seed_chunk_id=chunk_id,
                seed_content=seed.get("content"),
                seed_metadata=seed.get("metadata"),
            )

            for ctx in contexts:
                if ctx.chunk_id not in seen_ids:
                    all_contexts.append(ctx)
                    seen_ids.add(ctx.chunk_id)

                    if len(all_contexts) >= max_total_contexts:
                        break

            if len(all_contexts) >= max_total_contexts:
                break

        # Sort by confidence (highest first)
        all_contexts.sort(key=lambda c: c.confidence, reverse=True)

        return all_contexts[:max_total_contexts]

    def get_stats(self) -> dict[str, Any]:
        """Get expansion statistics."""
        return {
            "expansion_count": self._expansion_count,
            "avg_expanded_nodes": self._avg_expanded_nodes,
            "max_depth": self.max_depth,
            "base_confidence": self.base_confidence,
            "confidence_decay": self.confidence_decay,
        }


class L4ERetrievalIntegrator:
    """Integrates L4E ParentChildIndex with retrieval.

    Provides the wiring between L4E registry and Pipeline C retrieval.
    """

    def __init__(
        self,
        expander: ParentChildExpander | None = None,
        enable_expansion: bool = True,
    ):
        """Initialize L4E integrator.

        Args:
            expander: Parent-child expander instance
            enable_expansion: Whether to enable expansion
        """
        self.expander = expander or ParentChildExpander()
        self.enable_expansion = enable_expansion

    def enhance_retrieval_results(
        self,
        initial_results: list[dict[str, Any]],
        expansion_depth: int = 3,
    ) -> dict[str, Any]:
        """Enhance retrieval results with parent-child expansion.

        Args:
            initial_results: Results from vector/lexical search
            expansion_depth: Max depth for expansion

        Returns:
            Enhanced results with expanded contexts
        """
        if not self.enable_expansion:
            return {
                "initial_results": initial_results,
                "expanded_contexts": [],
                "expansion_applied": False,
            }

        # Update expander depth
        self.expander.max_depth = expansion_depth

        # Expand all initial results
        expanded = self.expander.expand_batch(initial_results)

        # Convert back to result format
        expanded_results = []
        for ctx in expanded:
            if ctx.depth == 0:
                continue  # Skip seeds (already in initial_results)

            expanded_results.append({
                "id": ctx.chunk_id,
                "chunk_id": ctx.chunk_id,
                "content": ctx.content,
                "metadata": {
                    **ctx.metadata,
                    "expansion_depth": ctx.depth,
                    "expansion_relationship": ctx.relationship,
                    "expansion_confidence": ctx.confidence,
                },
                "score": ctx.confidence * 0.5,  # Expanded results get score boost
                "source": "l4e_expansion",
            })

        return {
            "initial_results": initial_results,
            "expanded_contexts": expanded_results,
            "expansion_applied": True,
            "expansion_stats": {
                "seeds": len(initial_results),
                "expanded_nodes": len(expanded_results),
                "max_depth": expansion_depth,
            },
        }

    def get_context_summary(
        self,
        contexts: list[ExpansionContext],
    ) -> dict[str, Any]:
        """Generate summary of expanded contexts.

        Args:
            contexts: List of expansion contexts

        Returns:
            Summary statistics
        """
        depth_counts = {}
        relationship_counts = {}
        confidence_sum = 0.0

        for ctx in contexts:
            depth_counts[ctx.depth] = depth_counts.get(ctx.depth, 0) + 1
            relationship_counts[ctx.relationship] = relationship_counts.get(ctx.relationship, 0) + 1
            confidence_sum += ctx.confidence

        avg_confidence = confidence_sum / len(contexts) if contexts else 0.0

        return {
            "total_contexts": len(contexts),
            "depth_distribution": depth_counts,
            "relationship_distribution": relationship_counts,
            "avg_confidence": avg_confidence,
            "max_confidence": max((c.confidence for c in contexts), default=0.0),
            "min_confidence": min((c.confidence for c in contexts), default=0.0),
        }


# Global instance
_global_expander: ParentChildExpander | None = None
_global_integrator: L4ERetrievalIntegrator | None = None


def get_global_expander() -> ParentChildExpander:
    """Get or create global expander."""
    global _global_expander
    if _global_expander is None:
        _global_expander = ParentChildExpander()
    return _global_expander


def get_global_integrator() -> L4ERetrievalIntegrator:
    """Get or create global L4E integrator."""
    global _global_integrator
    if _global_integrator is None:
        _global_integrator = L4ERetrievalIntegrator(expander=get_global_expander())
    return _global_integrator


def expand_context(
    chunk_id: str,
    content: str | None = None,
    depth: int = 3,
) -> list[ExpansionContext]:
    """Convenience function to expand a single chunk."""
    expander = get_global_expander()
    expander.max_depth = depth
    return expander.expand(chunk_id, content)


def enhance_results(
    results: list[dict[str, Any]],
    depth: int = 3,
) -> dict[str, Any]:
    """Convenience function to enhance retrieval results."""
    integrator = get_global_integrator()
    return integrator.enhance_retrieval_results(results, depth)
