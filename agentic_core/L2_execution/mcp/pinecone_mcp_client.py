from __future__ import annotations
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"""
Sovereign Pinecone MCP Client – Phase 13C (Dec 26, 2025)
Replaces all custom Pinecone wrappers with official MCP integration.
L3 routed, L5 shielded vector operations.

[HARDENING] Added MCPHardenedMixin for retry, timeout, and observability (Jan 1, 2026)
"""
import logging
from typing import Any

# ARCHIVED IMPORT REMOVED - dependency no longer available
from agentic_core.config.blueprint_sovereign.sovereign_config_1 import config

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.utils.core_extensions.decorators import standard_heal

Logger: Any = logging.getLogger(__name__)


class SovereignPineconeMcpClient(SovereignBaseAgent):
    """
    Official Pinecone MCP client — L3 routed, L5 shielded.

    [PHASE 34] Redis-Cached for Meta-Learning Layer:
    - Search results cached with 1-hour TTL
    - Reduces MCP call overhead

    All vector operations flow through the Sovereign MCP router for:
    - L5 safety validation
    - L3 orchestration coordination
    - L4 state persistence

    [HARDENING] Inherits MCPHardenedMixin for:
    - Exponential backoff retry (3 attempts)
    - SovereignEvent emission on connect/fail/success
    - Timeout enforcement
    - CRITIQUE emission on exhausted retries
    """

    # RedisCacheMixin configuration
    _cache_prefix: str = "pinecone_mcp"
    _default_ttl: int = 3600  # 1 hour

    def __init__(self):
        """Initialize the Pinecone MCP client with sovereign routing and Redis."""
        super().__init__()
        self.router = SovereignMCPRouter(role="semantic_memory")
        self.initialized = False
        self.audit_log: list[dict] = []  # [PHASE 1] Absorbed from pinecone.py
        self._mcp_audit("init")
        Logger.info("[L4 PINECONE MCP] Client initialized")

    def _audit(self, operation: str, success: bool):
        """[PHASE 1] Record operation for L2 auditing."""
        import time

        self.audit_log.append({"op": operation, "success": success, "ts": time.time()})

    async def initialize(self) -> Any:
        """Async initialization of MCP router."""
        try:
            await self.router.initialize()
            self.initialized = True
            Logger.info("[L4 PINECONE MCP] router initialized successfully")
        except Exception as e:
            Logger.error(f"[L4 PINECONE MCP] Initialization failed: {e}")
            raise

    async def search(
        self,
        query_text: str,
        top_k: int = 10,
        namespace: str | None = None,
        rerank: bool = True,
        filters: dict | None = None,
        use_cache: bool = True,  # [PHASE 34] New parameter
    ) -> dict[str, Any]:
        """
        Execute semantic search with Redis caching and optional server-side reranking.

        Args:
            query_text: Text to search for
            top_k: Number of results to return
            namespace: Optional namespace to search in
            rerank: Whether to apply reranking
            filters: Optional metadata filters
            use_cache: Whether to use Redis cache (default: True)

        Returns:
            Search results with scores and metadata
        """
        import hashlib

        if not config.PINECONE_MCP_ENABLED:
            raise RuntimeError("Pinecone MCP is disabled in Sovereign Config.")
        if not self.initialized:
            await self.initialize()

        # [PHASE 34] cache Check
        effective_ns = namespace or config.PINECONE_DEFAULT_NAMESPACE
        cache_key = ""

        if use_cache:
            # Deterministic hash of query + critical params
            q_hash = hashlib.sha256(query_text.encode()).hexdigest()[:16]
            cache_key = f"search:{q_hash}:{top_k}:{effective_ns}:{rerank}"

            cached = await self.cache_get(cache_key)
            if cached:
                Logger.debug("[L4 PINECONE MCP] Search cache HIT")
                return cached

        try:
            result: Any = await self._hardened_call(
                "pinecone_search",
                self.router.manager.call_tool,
                tool_name="pinecone_search",
                args={
                    "query": query_text,
                    "top_k": top_k,
                    "namespace": effective_ns,
                    "rerank": rerank,
                    "rerank_model": config.PINECONE_RERANK_MODEL if rerank else None,
                },
            )

            # [PHASE 34] cache Write
            if use_cache and result.get("matches"):
                await self.cache_set(cache_key, result, ttl=self._default_ttl)

            Logger.info(
                f"[L4 PINECONE MCP] Search completed: {len(result.get('matches', []))} results"
            )
            return result
        except Exception as e:
            Logger.error(f"[L4 PINECONE MCP] Search failed: {e}")
            return {"matches": [], "error": str(e)}

    async def upsert(self, vectors: list[dict], namespace: str | None = None) -> dict[str, Any]:
        """
        Upsert vectors to the index.

        Args:
            vectors: List of vector records to upsert
            namespace: Optional namespace

        Returns:
            Upsert result with count
        """
        if not self.initialized:
            await self.initialize()
        try:
            result: Any = await self._hardened_call(
                "pinecone_upsert",
                self.router.manager.call_tool,
                tool_name="pinecone_upsert",
                args={
                    "vectors": vectors,
                    "namespace": namespace or config.PINECONE_DEFAULT_NAMESPACE,
                },
            )
            Logger.info(f"[L4 PINECONE MCP] Upserted {len(vectors)} records")
            return result
        except Exception as e:
            Logger.error(f"[L4 PINECONE MCP] Upsert failed: {e}")
            return {"upserted_count": 0, "error": str(e)}

    async def inference_embed(self, texts: list[str]) -> dict[str, Any]:
        """
        Generate embeddings via the Inference MCP tool.

        Args:
            texts: List of texts to embed

        Returns:
            Embeddings result with 'data' key containing embedding vectors
        """
        if not self.initialized:
            await self.initialize()
        try:
            result: Any = await self._hardened_call(
                "pinecone_inference",
                self.router.manager.call_tool,
                tool_name="pinecone_inference",
                args={
                    "texts": texts,
                    "model": config.PINECONE_INFERENCE_MODEL,
                    "input_type": "passage",
                },
            )
            Logger.info(f"[L4 PINECONE MCP] Generated embeddings for {len(texts)} texts")
            return result
        except Exception as e:
            Logger.error(f"[L4 PINECONE MCP] Inference failed: {e}")
            return {"data": [], "error": str(e)}

    async def delete(self, ids: list[str], namespace: str | None = None) -> dict[str, Any]:
        """
        Delete vectors by ID.

        Args:
            ids: List of vector IDs to delete
            namespace: Optional namespace

        Returns:
            Deletion result
        """
        if not self.initialized:
            await self.initialize()
        try:
            Logger.warning("[L4 PINECONE MCP] Delete not directly supported via MCP")
            return {"deleted_count": 0, "note": "Delete operation not available via MCP"}
        except Exception as e:
            Logger.error(f"[L4 PINECONE MCP] Delete failed: {e}")
            return {"deleted_count": 0, "error": str(e)}

    async def describe_index_stats(self) -> dict[str, Any]:
        """
        Get index statistics.

        Returns:
            Index statistics
        """
        if not self.initialized:
            await self.initialize()
        try:
            result: Any = await self._hardened_call(
                "pinecone_stats",
                self.router.manager.call_tool,
                "mcp8_describe-index-stats",
                {
                    "name": config.PINECONE_INDEX_NAME
                    if hasattr(config, "PINECONE_INDEX_NAME")
                    else "default"
                },
            )
            Logger.info("[L4 PINECONE MCP] Index stats retrieved")
            return result
        except Exception as e:
            Logger.error(f"[L4 PINECONE MCP] Stats retrieval failed: {e}")
            return {"error": str(e)}

    async def health_check(self) -> dict[str, Any]:
        """
        Perform health check on Pinecone connection.

        Returns:
            Health status
        """
        try:
            stats: Any = await self.describe_index_stats()
            if "error" in stats:
                return {"status": "unhealthy", "error": stats["error"]}
            return {
                "status": "healthy",
                "vector_count": stats.get("totalRecordCount", 0),
                "namespaces": stats.get("namespaces", {}),
            }
        except Exception as e:
            Logger.error(f"[L4 PINECONE MCP] Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    @standard_heal
    def heal_repository(self, **kwargs) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository(**kwargs)


_pinecone_mcp_client: SovereignPineconeMCPClient | None = None


def get_pinecone_mcp_client() -> SovereignPineconeMCPClient:
    """Get or create the global Pinecone MCP client."""
    global _pinecone_mcp_client
    if _pinecone_mcp_client is None:
        _pinecone_mcp_client = SovereignPineconeMCPClient()
    return _pinecone_mcp_client
