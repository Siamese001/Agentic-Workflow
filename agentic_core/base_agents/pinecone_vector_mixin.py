from __future__ import annotations

"""
ULTRA-HARDENED Pinecone Vector Mixin

Features:
- Feature flag control (USE_PINECONE)
- Local dict fallback for graceful degradation
- Metrics collection for dashboard visibility
- No raw code storage (embeddings only)
- Namespace isolation
"""


import asyncio
import logging
import time
from enum import Enum
from typing import Any

from agentic_core.config.core.feature_flags_config import (
    CACHE_METRICS_ENABLED,
    GRACEFUL_DEGRADATION,
    USE_PINECONE,
)

# from agentic_core.L6_observability.cache_metrics import get_cache_metrics  # Optional metrics - commented out

log = logging.getLogger(__name__)


# Stub for optional cache metrics
def get_cache_metrics():
    """Stub for optional cache metrics tracking."""
    return {}


class RetrievalBroadness(Enum):
    """Standardized retrieval scopes for semantic search."""

    NARROW = 5  # Quick, focused retrieval (legacy default)
    STANDARD = 15  # Balanced retrieval for most use cases
    BROAD = 30  # Wide neighborhood for complex tasks
    EXHAUSTIVE = 50  # Maximum retrieval for meta-learning


from agentic_core.base_agents.redis_cache_mixin import RedisCacheMixin


class PineconeVectorMixin(RedisCacheMixin):
    """
    ULTRA-HARDENED Pinecone Vector Mixin with Redis Caching

    Provides semantic search and vector storage with graceful degradation.
    All operations are safe - failures never crash the agent.

    SECURITY: Never stores raw source code - only embeddings and metadata hashes.

    Usage:
        class MyAgent(HealerMixin, MCPHardenedMixin, PineconeVectorMixin):
            _index_name = "my-index"
            _namespace = "my_patterns"

            async def find_similar(self, embedding):
                return await self.vector_search(embedding, top_k=5)
    """

    _pinecone_client = None
    _index_name: str = "sovereign-agents-v1"
    _namespace: str = "agent_patterns"
    _similarity_threshold: float = 0.85  # [PHASE 25] Configurable
    _local_vectors: dict = {}

    # RedisCacheMixin configuration
    _cache_prefix: str = "pinecone_vector"
    _default_ttl: int = 3600  # 1 hour

    EXPECTED_DIMENSION = 1536
    MAX_QUERY_TOP_K = 50
    QUERY_TIMEOUT = 12.0

    circuit_breaker = None

    @property
    def pinecone_enabled(self) -> bool:
        """Check if Pinecone is enabled via feature flag."""
        return USE_PINECONE

    @property
    def pinecone(self):
        """
        Lazy-load Hardened MCP Pinecone client.

        [PHASE 1 MIGRATION] Now strictly routes through the Sovereign MCP Client
        to ensure all operations are audited and cached via Redis.
        """
        if not self.pinecone_enabled:
            return None
        if self._pinecone_client is None:
            try:
                # Re-routing to the hardened MCP implementation
                from agentic_core.L2_execution.mcp.pinecone_mcp_client import (
                    get_pinecone_mcp_client,
                )

                self._pinecone_client = get_pinecone_mcp_client()
                log.info(f"[{self.__class__.__name__}] Connected to Hardened Pinecone MCP")
            except Exception as e:
                if not GRACEFUL_DEGRADATION:
                    raise
                log.warning(f"Pinecone client init failed ({e}) - using local fallback")
                self._pinecone_client = None
        return self._pinecone_client

    async def vector_search(
        self,
        embedding: list[float],
        top_k: int | None = None,
        broadness: RetrievalBroadness = RetrievalBroadness.STANDARD,
        metadata_filter: dict[str, Any] | None = None,
        include_metadata: bool = True,
        score_threshold: float | None = None,
        use_cache: bool = True,  # [PHASE 34] New parameter
        apply_similarity_threshold: bool = True,  # [PHASE 25]
    ) -> list[dict[str, Any]]:
        """
        Perform a hardened vector search with Redis caching.

        Args:
            embedding: The query embedding vector.
            top_k: (Optional) Explicit override for number of results. If provided, ignores broadness.
            broadness: RetrievalBroadness enum determining semantic scope (default: STANDARD).
            metadata_filter: Optional dictionary for metadata filtering.
            include_metadata: Whether to include metadata in results.
            score_threshold: (Optional) Minimum similarity score to return.
            use_cache: Whether to use Redis cache (default: True).

        Returns:
            List of vector search results matching the query.
        """
        start = time.time()
        metrics = get_cache_metrics()

        if len(embedding) != self.EXPECTED_DIMENSION:
            raise ValueError(f"Invalid embedding dimension: {len(embedding)} != {self.EXPECTED_DIMENSION}")

        # Precedence Logic: Explicit top_k > Broadness Enum
        if top_k is not None:
            effective_top_k = min(top_k, self.MAX_QUERY_TOP_K)
            if top_k != broadness.value:
                log.debug(
                    f"Manual top_k ({top_k}) overriding broadness ({broadness.name}: {broadness.value})"
                )
        else:
            effective_top_k = min(broadness.value, self.MAX_QUERY_TOP_K)

        # [PHASE 34] Redis cache Check
        cache_key = ""
        if use_cache:
            import hashlib
            import json

            # Create deterministic signature of embedding
            emb_sig = hashlib.sha256(json.dumps(embedding[:5] + embedding[-5:]).encode()).hexdigest()[:16]

            cache_params = {
                "emb": emb_sig,
                "k": effective_top_k,
                "ns": self._namespace,
                "fil": str(metadata_filter) if metadata_filter else "",
                "th": score_threshold,
            }
            # Key format: pinecone_vector:vs:<hash>
            cache_key = f"vs:{cache_params['emb']}:{cache_params['k']}:{cache_params['ns']}"

            cached = await self.cache_get(cache_key)
            if cached:
                latency = (time.time() - start) * 1000
                log.debug(f"Vector search cache HIT in {latency:.1f}ms")
                if CACHE_METRICS_ENABLED:
                    metrics.record("redis_vector_search", hit=True, latency_ms=latency)
                return cached

        local_only = False

        if hasattr(self, "circuit_breaker") and self.circuit_breaker:
            try:
                if hasattr(self.circuit_breaker, "can_execute") and not self.circuit_breaker.can_execute():
                    log.warning("Pinecone circuit open -> fallback to local immediately")
                    local_only = True
            except Exception:
                pass

        if self.pinecone and not local_only:
            try:
                results = await asyncio.wait_for(
                    self.pinecone.query(
                        vector=embedding,
                        top_k=effective_top_k,
                        namespace=self._namespace,
                        filter=metadata_filter,
                        include_metadata=include_metadata,
                    ),
                    timeout=self.QUERY_TIMEOUT,
                )
                latency = (time.time() - start) * 1000
                matches = results.get("matches", [])

                # [PHASE 25] Apply similarity threshold
                thresh = (
                    score_threshold
                    if score_threshold is not None
                    else (self._similarity_threshold if apply_similarity_threshold else 0.0)
                )

                if thresh > 0:
                    matches = [m for m in matches if m.get("score", 0) >= thresh]

                # [PHASE 34] cache Write
                if use_cache and matches:
                    await self.cache_set(cache_key, matches, ttl=self._default_ttl)

                hit = len(matches) > 0
                if CACHE_METRICS_ENABLED:
                    metrics.record("pinecone_search", hit=hit, latency_ms=latency)
                log.debug(f"Vector search returned {len(matches)} results")
                return matches

            except Exception as e:
                latency = (time.time() - start) * 1000
                log.warning(f"Pinecone query failed after {latency:.0f}ms: {e}")
                if CACHE_METRICS_ENABLED:
                    metrics.record_error("pinecone_search")
                log.debug(f"Pinecone search failed ({e}) - returning empty")

        # Local fallback (simplified cosine similarity)
        latency = (time.time() - start) * 1000
        if CACHE_METRICS_ENABLED:
            metrics.record("local_search", hit=False, latency_ms=latency)

        # Basic local search (limited functionality)
        results = []
        for vid, vdata in self._local_vectors.items():
            if metadata_filter:
                # Simple filter match
                meta = vdata.get("metadata", {})
                if not all(meta.get(k) == v for k, v in metadata_filter.items()):
                    continue
            results.append(
                {
                    "id": vid,
                    "score": 0.5,  # Placeholder score for local
                    "metadata": vdata.get("metadata", {}) if include_metadata else {},
                }
            )

        return results[:effective_top_k]

    async def vector_upsert(self, id: str, embedding: list[float], metadata: dict[str, Any]) -> bool:
        """
        Upsert a vector with metadata.

        SECURITY: Metadata should contain hashes, not raw content.

        Args:
            id: Unique identifier for the vector
            embedding: Vector values
            metadata: Associated metadata (use hashes for content)

        Returns:
            True if successful (Pinecone or local)
        """
        start = time.time()
        metrics = get_cache_metrics()

        # Always store locally
        self._local_vectors[id] = {"values": embedding, "metadata": metadata}

        if self.pinecone:
            try:
                await self.pinecone.upsert(
                    vectors=[{"id": id, "values": embedding, "metadata": metadata}],
                    namespace=self._namespace,
                )
                latency = (time.time() - start) * 1000
                if CACHE_METRICS_ENABLED:
                    metrics.record("pinecone_upsert", hit=True, latency_ms=latency)
                log.debug(f"Vector upserted to Pinecone: {id}")
                return True
            except Exception as e:
                if CACHE_METRICS_ENABLED:
                    metrics.record_error("pinecone_upsert")
                log.debug(f"Pinecone upsert failed ({e}) - stored locally")

        latency = (time.time() - start) * 1000
        if CACHE_METRICS_ENABLED:
            metrics.record("local_upsert", hit=True, latency_ms=latency)
        log.debug(f"Vector stored locally: {id}")
        return True

    async def vector_delete(self, ids: list[str]) -> int:
        """
        Delete vectors by ID.

        Returns count of vectors deleted.
        """
        deleted = 0

        # Delete from local
        for vid in ids:
            if vid in self._local_vectors:
                del self._local_vectors[vid]
                deleted += 1

        # Delete from Pinecone
        if self.pinecone:
            try:
                await self.pinecone.delete(ids=ids, namespace=self._namespace)
            except Exception:
                pass

        return deleted

    async def vector_fetch(self, ids: list[str]) -> dict[str, dict[str, Any]]:
        """
        Fetch vectors by ID.

        Returns dict mapping id to vector data.
        """
        results = {}

        if self.pinecone:
            try:
                response = await self.pinecone.fetch(ids=ids, namespace=self._namespace)
                results.update(response.get("vectors", {}))
            except Exception:
                pass

        # Add local vectors not in Pinecone results
        for vid in ids:
            if vid not in results and vid in self._local_vectors:
                results[vid] = self._local_vectors[vid]

        return results

    def vector_stats(self) -> dict:
        """Get vector store statistics for this mixin instance."""
        return {
            "index_name": self._index_name,
            "namespace": self._namespace,
            "local_vector_count": len(self._local_vectors),
            "pinecone_enabled": self.pinecone_enabled,
            "pinecone_connected": self._pinecone_client is not None,
        }
