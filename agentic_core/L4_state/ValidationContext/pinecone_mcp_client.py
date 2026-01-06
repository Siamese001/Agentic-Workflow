from __future__ import annotations
"""
Sovereign Pinecone MCP Client – Phase 13C (Dec 26, 2025)
Replaces all custom Pinecone wrappers with official MCP integration.
L3 routed, L5 shielded vector operations.

[HARDENING] Added MCPHardenedMixin for retry, timeout, and observability (Jan 1, 2026)
"""
import logging
from typing import Optional, List, Dict, Any
from agentic_core.L3_orchestration.workflow_engines.mcp_router_sovereign import SovereignMCPRouter
from agentic_core.config.blueprint_sovereign.sovereign_config import config
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L4_state.validation_context.l4_subatomic_testing_mixin import L4SubatomicTestingMixin

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

Logger: Any = logging.getLogger(__name__)

class SovereignPineconeMcpClient(MCPHardenedMixin, HealerMixin, L4SubatomicTestingMixin):
    """
    Official Pinecone MCP client — L3 routed, L5 shielded.
    
    All vector operations flow through the Sovereign MCP Router for:
    - L5 safety validation
    - L3 orchestration coordination
    - L4 state persistence
    
    [HARDENING] Inherits MCPHardenedMixin for:
    - Exponential backoff retry (3 attempts)
    - SovereignEvent emission on connect/fail/success
    - Timeout enforcement
    - CRITIQUE emission on exhausted retries
    """

    def __init__(self):
        """Initialize the Pinecone MCP client with sovereign routing."""
        super().__init__()
        self.router = SovereignMCPRouter(role='semantic_memory')
        self.initialized = False
        self._mcp_audit('init')
        Logger.info('[L4 PINECONE MCP] Client initialized')

    async def initialize(self) -> Any:
        """Async initialization of MCP router."""
        try:
            await self.router.initialize()
            self.initialized = True
            Logger.info('[L4 PINECONE MCP] Router initialized successfully')
        except Exception as e:
            Logger.error(f'[L4 PINECONE MCP] Initialization failed: {e}')
            raise

    async def search(self, query_text: str, top_k: int=10, namespace: Optional[str]=None, rerank: bool=True, filters: Optional[Dict]=None) -> Dict[str, Any]:
        """
        Execute semantic search with optional server-side reranking.
        
        Args:
            query_text: Text to search for
            top_k: Number of results to return
            namespace: Optional namespace to search in
            rerank: Whether to apply reranking
            filters: Optional metadata filters
            
        Returns:
            Search results with scores and metadata
        """
        if not config.PINECONE_MCP_ENABLED:
            raise RuntimeError('Pinecone MCP is disabled in Sovereign Config.')
        if not self.initialized:
            await self.initialize()
        try:
            result: Any = await self._hardened_call(
                'pinecone_search',
                self.router.manager.call_tool,
                tool_name='pinecone_search',
                args={'query': query_text, 'top_k': top_k, 'namespace': namespace or config.PINECONE_DEFAULT_NAMESPACE, 'rerank': rerank, 'rerank_model': config.PINECONE_RERANK_MODEL if rerank else None}
            )
            Logger.info(f"[L4 PINECONE MCP] Search completed: {len(result.get('matches', []))} results")
            return result
        except Exception as e:
            Logger.error(f'[L4 PINECONE MCP] Search failed: {e}')
            return {'matches': [], 'error': str(e)}

    async def upsert(self, vectors: List[Dict], namespace: Optional[str]=None) -> Dict[str, Any]:
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
                'pinecone_upsert',
                self.router.manager.call_tool,
                tool_name='pinecone_upsert',
                args={'vectors': vectors, 'namespace': namespace or config.PINECONE_DEFAULT_NAMESPACE}
            )
            Logger.info(f'[L4 PINECONE MCP] Upserted {len(vectors)} records')
            return result
        except Exception as e:
            Logger.error(f'[L4 PINECONE MCP] Upsert failed: {e}')
            return {'upserted_count': 0, 'error': str(e)}

    async def inference_embed(self, texts: List[str]) -> Dict[str, Any]:
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
                'pinecone_inference',
                self.router.manager.call_tool,
                tool_name='pinecone_inference',
                args={'texts': texts, 'model': config.PINECONE_INFERENCE_MODEL, 'input_type': 'passage'}
            )
            Logger.info(f'[L4 PINECONE MCP] Generated embeddings for {len(texts)} texts')
            return result
        except Exception as e:
            Logger.error(f'[L4 PINECONE MCP] Inference failed: {e}')
            return {'data': [], 'error': str(e)}

    async def delete(self, ids: List[str], namespace: Optional[str]=None) -> Dict[str, Any]:
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
            Logger.warning(f'[L4 PINECONE MCP] Delete not directly supported via MCP')
            return {'deleted_count': 0, 'note': 'Delete operation not available via MCP'}
        except Exception as e:
            Logger.error(f'[L4 PINECONE MCP] Delete failed: {e}')
            return {'deleted_count': 0, 'error': str(e)}

    async def describe_index_stats(self) -> Dict[str, Any]:
        """
        Get index statistics.
        
        Returns:
            Index statistics
        """
        if not self.initialized:
            await self.initialize()
        try:
            result: Any = await self._hardened_call(
                'pinecone_stats',
                self.router.manager.call_tool,
                'mcp8_describe-index-stats',
                {'name': config.PINECONE_INDEX_NAME if hasattr(config, 'PINECONE_INDEX_NAME') else 'default'}
            )
            Logger.info(f'[L4 PINECONE MCP] Index stats retrieved')
            return result
        except Exception as e:
            Logger.error(f'[L4 PINECONE MCP] Stats retrieval failed: {e}')
            return {'error': str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Pinecone connection.
        
        Returns:
            Health status
        """
        try:
            stats: Any = await self.describe_index_stats()
            if 'error' in stats:
                return {'status': 'unhealthy', 'error': stats['error']}
            return {'status': 'healthy', 'vector_count': stats.get('totalRecordCount', 0), 'namespaces': stats.get('namespaces', {})}
        except Exception as e:
            Logger.error(f'[L4 PINECONE MCP] Health check failed: {e}')
            return {'status': 'unhealthy', 'error': str(e)}

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
_pinecone_mcp_client: Optional[SovereignPineconeMCPClient] = None

def get_pinecone_mcp_client() -> SovereignPineconeMCPClient:
    """Get or create the global Pinecone MCP client."""
    global _pinecone_mcp_client
    if _pinecone_mcp_client is None:
        _pinecone_mcp_client = SovereignPineconeMCPClient()
    return _pinecone_mcp_client