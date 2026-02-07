"""
semantic_cache_mixin - Unified Semantic cache Access

[PHASE 3 MIGRATION] Provides single interface to canonical SemanticCacheManager.
"""

from typing import Any


class SemanticCacheMixin:
    """
    Mixin providing unified semantic cache access.

    [PHASE 3 MIGRATION] Routes to canonical L4 implementation.

    Usage:
        class MyAgent(semantic_cache_mixin, SovereignBaseAgent):
            async def process(self, query: str):
                cached = await self.semantic_recall(query)
                if cached:
                    return cached
                result = await self._compute(query)
                await self.semantic_learn(query, result)
                return result
    """

    _semantic_cache = None

    @property
    def semantic_cache(self):
        """Lazy-load canonical SemanticCacheManager singleton."""
        if self._semantic_cache is None:
            from agentic_core.L4_state.memory.semantic_cache_manager_config import (
                SemanticCacheManager,
            )

            self._semantic_cache = SemanticCacheManager()
        return self._semantic_cache

    async def semantic_recall(self, query: str, threshold: float = 0.85) -> Any:
        """Recall from semantic cache (L1 Redis + L2 Pinecone)."""
        return await self.semantic_cache.recall(query, threshold=threshold)

    async def semantic_learn(self, query: str, response: Any, metadata: dict = None) -> None:
        """Store in semantic cache with optional metadata."""
        await self.semantic_cache.learn(query, response, metadata=metadata)

    async def semantic_promote(self, query: str) -> None:
        """Promote high-value memory from Redis (L1) to Pinecone (L2)."""
        await self.semantic_cache.promote_to_long_term(query)


# Backward compatibility alias
semantic_cache_mixin = SemanticCacheMixin
