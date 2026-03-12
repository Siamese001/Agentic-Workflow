"""
semantic_cache_mixin - Unified Semantic cache Access

[PHASE 3 MIGRATION] Provides single interface to canonical SemanticCacheManager.
"""
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class SemanticCacheMixin:
    """
    Mixin providing unified semantic cache access.

    [PHASE 3 MIGRATION] Routes to canonical L4 implementation.

    Usage:
        class MyAgent(SemanticCacheMixin, SovereignBaseAgent):
            def process(self, query: str):
                namespace = self.__class__.__name__
                cached = self.semantic_recall(query, namespace)
                if cached:
                    return cached
                result = self._compute(query)
                self.semantic_learn(query, namespace, result)
                return result

    Note: `semantic_cache` always delegates to `SemanticCacheManager.get_instance()`.
    No stale references — every call returns the live singleton.
    """

    @property
    def semantic_cache(self):
        """Return canonical SemanticCacheManager singleton (no instance caching)."""
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager
        return SemanticCacheManager.get_instance()

    def semantic_recall(self, context: str, namespace: str) -> Any:
        """Recall from semantic cache (L1 Redis + L2 BGE vector store)."""
        return self.semantic_cache.recall(context, namespace)

    def semantic_learn(self, context: str, namespace: str, result: dict[str, Any], feedback_score: float | None=None) -> None:
        """Store in semantic cache working memory (Redis, 24h TTL)."""
        self.semantic_cache.learn(context, namespace, result, feedback_score)

    def semantic_promote(self, context: str, namespace: str, result: dict[str, Any], feedback_score: float) -> bool:
        """Promote high-value memory to long-term vector store."""
        return self.semantic_cache.promote_to_long_term(context, namespace, result, feedback_score)

    def semantic_update_feedback(self, context: str, namespace: str, feedback_score: float) -> bool:
        """Update feedback score for existing memory; auto-promotes if above threshold."""
        return self.semantic_cache.update_feedback_score(context, namespace, feedback_score)

    def semantic_stats(self) -> dict[str, Any]:
        """Return cache hit/miss statistics."""
        return self.semantic_cache.get_statistics()
semantic_cache_mixin = SemanticCacheMixin
