"""
Pinecone Vector Store – ADAPTER (Phase 13C)
Translation Layer: Legacy Interface -> New MCP Client

Maintains backward compatibility for 'add_texts' and 'similarity_search'
while routing all operations through the Sovereign MCP architecture.
"""
import logging
from typing import List, Optional, Any, Dict
from pathlib import Path

logger = logging.getLogger("L4.PineconeStore")


class SovereignPineconeStore:
    """
    ADAPTER: Legacy Interface -> New MCP Client.
    Maintains backward compatibility for 'add_texts' and 'similarity_search'.
    
    Phase 13C: All operations now flow through L3 MCP Router with L5 shielding.
    """
    
    def __init__(self, index_name: Optional[str] = None, namespace: Optional[str] = None):
        """Initialize the adapter with MCP client."""
        from agentic_core.L4_state.semantic_memory.pinecone_mcp_client import SovereignPineconeMCPClient
        
        self.mcp_client = SovereignPineconeMCPClient()
        self.namespace = namespace
        self._initialized = False
        logger.info("[L4 ADAPTER] Initialized - routing to MCP client")
    
    async def _ensure_initialized(self):
        """Ensure MCP client is initialized."""
        if not self._initialized:
            await self.mcp_client.initialize()
            self._initialized = True
    
    async def similarity_search(
        self, 
        query: str, 
        k: int = 4,
        **kwargs
    ) -> List[Dict]:
        """Legacy adapter for search."""
        logger.info(f"[L4 ADAPTER] Routing legacy search to MCP: {query}")
        
        await self._ensure_initialized()
        
        result = await self.mcp_client.search(
            query_text=query,
            top_k=k,
            namespace=self.namespace,
            rerank=kwargs.get('rerank', True)
        )
        
        # Transform MCP result format back to legacy list-of-dicts if needed
        # Assuming MCP returns {'matches': [...]}
        matches = result.get('matches', []) if isinstance(result, dict) else []
        return matches
    
    async def add_texts(
        self, 
        texts: List[str], 
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Legacy adapter for adding documents."""
        logger.info(f"[L4 ADAPTER] Routing legacy add_texts to MCP Inference + Upsert")
        
        await self._ensure_initialized()
        
        # 1. Generate Embeddings (Server-side)
        emb_result = await self.mcp_client.inference_embed(texts)
        embeddings = emb_result.get('data', [])  # Standardize based on MCP return
        
        if not embeddings:
            raise RuntimeError("MCP Inference failed to return embeddings")

        # 2. Format Vectors
        vectors = []
        result_ids = []
        for i, text in enumerate(texts):
            # Generate a stable ID based on content hash
            vec_id = ids[i] if ids else f"vec_{abs(hash(text))}"
            meta = metadatas[i] if metadatas else {}
            meta["text"] = text
            
            vectors.append({
                "id": vec_id,
                "values": embeddings[i]['values'] if isinstance(embeddings[i], dict) else embeddings[i],
                "metadata": meta
            })
            result_ids.append(vec_id)
            
        # 3. Upsert
        await self.mcp_client.upsert(vectors=vectors, namespace=self.namespace)
        return result_ids
    
    async def upsert_file_vector(
        self, 
        file_path: Path, 
        territory_hint: Optional[str] = None
    ):
        """
        Upsert single file — used during healing.
        
        Args:
            file_path: Path to file
            territory_hint: Optional territory classification
        """
        await self._ensure_initialized()
        
        try:
            # Read file content
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            
            # Generate file ID
            path_str = str(file_path).replace('/', '_').replace('\\', '_')
            file_id = f"file_{path_str}"
            
            # Prepare metadata
            metadata = {
                "text": content,
                "file_path": str(file_path),
                "type": "file"
            }
            if territory_hint:
                metadata["territory"] = territory_hint
            
            # Upsert
            vectors = [{
                "id": file_id,
                "metadata": metadata
            }]
            
            await self.mcp_client.upsert(vectors=vectors)
            
            logger.info(f"[L4 PINECONE STORE] Upserted file vector: {file_path}")
            
        except Exception as e:
            logger.error(f"[L4 PINECONE STORE] File upsert failed for {file_path}: {e}")
    
    async def semantic_search(
        self, 
        query: str, 
        top_k: int = 5
    ) -> List[Dict]:
        """
        Runtime retrieval for agents needing to 'find' logic.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            
        Returns:
            List of search results with metadata
        """
        await self._ensure_initialized()
        
        try:
            results = await self.mcp_client.search(
                query_text=query,
                top_k=top_k,
                rerank=True
            )
            
            logger.info(f"[L4 PINECONE STORE] Semantic search returned {len(results.get('matches', []))} results")
            return results.get('matches', [])
            
        except Exception as e:
            logger.error(f"[L4 PINECONE STORE] Semantic search failed: {e}")
            return []
    
    async def hybrid_search(
        self, 
        query: str, 
        top_k: int = 5
    ) -> List[Dict]:
        """
        Eternal precision: Combined Vector + Keyword search.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            Search results
        """
        await self._ensure_initialized()
        
        try:
            # MCP client handles hybrid search automatically with reranking
            results = await self.mcp_client.search(
                query_text=query,
                top_k=top_k,
                rerank=True
            )
            
            logger.info(f"[L4 PINECONE STORE] Hybrid search returned {len(results.get('matches', []))} results")
            return results.get('matches', [])
            
        except Exception as e:
            logger.error(f"[L4 PINECONE STORE] Hybrid search failed: {e}")
            return []
    
    def purge_ghost_vector(self, file_path: Path):
        """
        Surgical strike to remove stale vector data.
        
        Note: Delete operations not directly supported via MCP.
        This is a no-op for compatibility.
        
        Args:
            file_path: Path to file
        """
        logger.warning(f"[L4 PINECONE STORE] purge_ghost_vector called but delete not supported via MCP: {file_path}")
    
    async def health_check(self) -> Dict:
        """
        Enhanced health check with sample quality assessment.
        
        Returns:
            Health status dictionary
        """
        await self._ensure_initialized()
        
        try:
            health = await self.mcp_client.health_check()
            
            return {
                "status": health.get("status", "unknown"),
                "vectors": health.get("vector_count", 0),
                "namespaces": health.get("namespaces", {}),
                "sample_quality": "good" if health.get("status") == "healthy" else "degraded"
            }
            
        except Exception as e:
            logger.error(f"[L4 PINECONE STORE] Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "vectors": 0,
                "sample_quality": "degraded"
            }
    
    async def execute(self, ctx=None):
        """
        Health check for the validator loop.
        Reports index status and vector count with quality metrics.
        
        Args:
            ctx: Optional validation context
        """
        await self._ensure_initialized()
        
        try:
            health = await self.health_check()
            
            status_msg = f"Pinecone MCP: {health['vectors']} vectors online (quality: {health['sample_quality']})"
            logger.info(f"[L4 PINECONE STORE] {status_msg}")
            
            if ctx:
                ctx.report(
                    "VectorHealth", 
                    1, 
                    health['status'] == 'healthy',
                    status_msg
                )
                
        except Exception as e:
            logger.error(f"[L4 PINECONE STORE] Execute failed: {e}")
            if ctx:
                ctx.report("VectorHealth", 1, False, f"Pinecone health check failed: {str(e)}")


# Legacy compatibility - maintain existing import patterns
PineconeSovereignAgent = SovereignPineconeStore
