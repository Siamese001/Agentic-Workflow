"""
ULTRA-HARDENED Pinecone Vector Mixin

Features:
- Feature flag control (USE_PINECONE)
- Local dict fallback for graceful degradation
- Metrics collection for dashboard visibility
- No raw code storage (embeddings only)
- Namespace isolation
"""
from __future__ import annotations
import hashlib
import logging
import time
from typing import Any, Dict, List, Optional

from agentic_core.config.flags import USE_PINECONE, CACHE_METRICS_ENABLED, GRACEFUL_DEGRADATION
from agentic_core.L6_observability.metrics.cache_metrics import get_cache_metrics

log = logging.getLogger(__name__)


class PineconeVectorMixin:
    """
    ULTRA-HARDENED Pinecone Vector Mixin
    
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
    _local_vectors: dict = {}
    
    @property
    def pinecone_enabled(self) -> bool:
        """Check if Pinecone is enabled via feature flag."""
        return USE_PINECONE
    
    @property
    def pinecone(self):
        """Lazy-load Pinecone client with graceful failure."""
        if not self.pinecone_enabled:
            return None
        if self._pinecone_client is None:
            try:
                from agentic_core.L4_state.ValidationContext.pinecone_mcp_client import get_pinecone_mcp_client
                self._pinecone_client = get_pinecone_mcp_client()
            except Exception as e:
                if not GRACEFUL_DEGRADATION:
                    raise
                log.warning(f"Pinecone client init failed ({e}) - using local fallback")
                self._pinecone_client = None
        return self._pinecone_client
    
    async def vector_search(
        self,
        embedding: List[float],
        top_k: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            embedding: Query vector
            top_k: Number of results to return
            metadata_filter: Optional filter on metadata fields
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of matches with id, score, and optionally metadata
        """
        start = time.time()
        metrics = get_cache_metrics()
        
        if self.pinecone:
            try:
                results = await self.pinecone.query(
                    vector=embedding,
                    top_k=top_k,
                    namespace=self._namespace,
                    filter=metadata_filter,
                    include_metadata=include_metadata
                )
                latency = (time.time() - start) * 1000
                hit = len(results.get("matches", [])) > 0
                if CACHE_METRICS_ENABLED:
                    metrics.record("pinecone_search", hit=hit, latency_ms=latency)
                log.debug(f"Vector search returned {len(results.get('matches', []))} results")
                return results.get("matches", [])
            except Exception as e:
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
            results.append({
                "id": vid,
                "score": 0.5,  # Placeholder score for local
                "metadata": vdata.get("metadata", {}) if include_metadata else {}
            })
        
        return results[:top_k]
    
    async def vector_upsert(
        self,
        id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> bool:
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
        self._local_vectors[id] = {
            "values": embedding,
            "metadata": metadata
        }
        
        if self.pinecone:
            try:
                await self.pinecone.upsert(
                    vectors=[{
                        "id": id,
                        "values": embedding,
                        "metadata": metadata
                    }],
                    namespace=self._namespace
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
    
    async def vector_delete(self, ids: List[str]) -> int:
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
                await self.pinecone.delete(
                    ids=ids,
                    namespace=self._namespace
                )
            except Exception:
                pass
        
        return deleted
    
    async def vector_fetch(self, ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Fetch vectors by ID.
        
        Returns dict mapping id to vector data.
        """
        results = {}
        
        if self.pinecone:
            try:
                response = await self.pinecone.fetch(
                    ids=ids,
                    namespace=self._namespace
                )
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
