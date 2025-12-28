"""
Sovereign Pinecone MCP Client – Phase 13C (Dec 26, 2025)
Replaces all custom Pinecone wrappers with official MCP integration.
L3 routed, L5 shielded vector operations.
"""
import logging
from typing import Optional, List, Dict, Any
from agentic_core.L3_orchestration.workflow_engines.mcp_router_sovereign import SovereignMCPRouter
from agentic_core.config.blueprint_sovereign.sovereign_config import config

logger = logging.getLogger(__name__)


class SovereignPineconeMCPClient:
    """
    Official Pinecone MCP client — L3 routed, L5 shielded.
    
    All vector operations flow through the Sovereign MCP Router for:
    - L5 safety validation
    - L3 orchestration coordination
    - L4 state persistence
    """
    
    def __init__(self):
        """Initialize the Pinecone MCP client with sovereign routing."""
        self.router = SovereignMCPRouter(role="semantic_memory")
        self.initialized = False
        logger.info("[L4 PINECONE MCP] Client initialized")
    
    async def initialize(self):
        """Async initialization of MCP router."""
        try:
            await self.router.initialize()
            self.initialized = True
            logger.info("[L4 PINECONE MCP] Router initialized successfully")
        except Exception as e:
            logger.error(f"[L4 PINECONE MCP] Initialization failed: {e}")
            raise
    
    async def search(
        self, 
        query_text: str, 
        top_k: int = 10, 
        namespace: Optional[str] = None, 
        rerank: bool = True,
        filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
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
            raise RuntimeError("Pinecone MCP is disabled in Sovereign Config.")
        
        if not self.initialized:
            await self.initialize()
        
        try:
            result = await self.router.manager.call_tool(
                tool_name="pinecone_search",
                args={
                    "query": query_text,
                    "top_k": top_k,
                    "namespace": namespace or config.PINECONE_DEFAULT_NAMESPACE,
                    "rerank": rerank,
                    "rerank_model": config.PINECONE_RERANK_MODEL if rerank else None
                }
            )
            
            logger.info(f"[L4 PINECONE MCP] Search completed: {len(result.get('matches', []))} results")
            return result
            
        except Exception as e:
            logger.error(f"[L4 PINECONE MCP] Search failed: {e}")
            return {"matches": [], "error": str(e)}
    
    async def upsert(
        self, 
        vectors: List[Dict], 
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
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
            result = await self.router.manager.call_tool(
                tool_name="pinecone_upsert",
                args={
                    "vectors": vectors,
                    "namespace": namespace or config.PINECONE_DEFAULT_NAMESPACE
                }
            )
            
            logger.info(f"[L4 PINECONE MCP] Upserted {len(vectors)} records")
            return result
            
        except Exception as e:
            logger.error(f"[L4 PINECONE MCP] Upsert failed: {e}")
            return {"upserted_count": 0, "error": str(e)}
    
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
            result = await self.router.manager.call_tool(
                tool_name="pinecone_inference",
                args={
                    "texts": texts,
                    "model": config.PINECONE_INFERENCE_MODEL,
                    "input_type": "passage"
                }
            )
            
            logger.info(f"[L4 PINECONE MCP] Generated embeddings for {len(texts)} texts")
            return result
            
        except Exception as e:
            logger.error(f"[L4 PINECONE MCP] Inference failed: {e}")
            return {"data": [], "error": str(e)}
    
    async def delete(
        self, 
        ids: List[str], 
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
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
            # Note: Pinecone MCP doesn't expose delete directly
            # This is a placeholder for compatibility
            logger.warning(f"[L4 PINECONE MCP] Delete not directly supported via MCP")
            return {"deleted_count": 0, "note": "Delete operation not available via MCP"}
            
        except Exception as e:
            logger.error(f"[L4 PINECONE MCP] Delete failed: {e}")
            return {"deleted_count": 0, "error": str(e)}
    
    async def describe_index_stats(self) -> Dict[str, Any]:
        """
        Get index statistics.
        
        Returns:
            Index statistics
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            result = await self.router.manager.call_tool(
                "mcp8_describe-index-stats",
                {
                    "name": config.PINECONE_INDEX_NAME if hasattr(config, 'PINECONE_INDEX_NAME') else "default"
                }
            )
            
            logger.info(f"[L4 PINECONE MCP] Index stats retrieved")
            return result
            
        except Exception as e:
            logger.error(f"[L4 PINECONE MCP] Stats retrieval failed: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Pinecone connection.
        
        Returns:
            Health status
        """
        try:
            stats = await self.describe_index_stats()
            
            if "error" in stats:
                return {
                    "status": "unhealthy",
                    "error": stats["error"]
                }
            
            return {
                "status": "healthy",
                "vector_count": stats.get("totalRecordCount", 0),
                "namespaces": stats.get("namespaces", {})
            }
            
        except Exception as e:
            logger.error(f"[L4 PINECONE MCP] Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Singleton instance
_pinecone_mcp_client: Optional[SovereignPineconeMCPClient] = None


def get_pinecone_mcp_client() -> SovereignPineconeMCPClient:
    """Get or create the global Pinecone MCP client."""
    global _pinecone_mcp_client
    if _pinecone_mcp_client is None:
        _pinecone_mcp_client = SovereignPineconeMCPClient()
    return _pinecone_mcp_client
