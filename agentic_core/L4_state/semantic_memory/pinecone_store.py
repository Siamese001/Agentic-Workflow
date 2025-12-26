"""
Pinecone Vector Store – DEPRECATED (Phase 13C)
Refactored as an Adapter to SovereignPineconeMCPClient.

This module maintains backward compatibility with legacy code
while routing actual logic to the new MCP Client.
"""
import logging
from typing import List, Optional, Any, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class SovereignPineconeStore:
    """
    Adapter class to maintain backward compatibility with legacy code
    while routing actual logic to the new MCP Client.
    
    Phase 13C: All operations now flow through L3 MCP Router with L5 shielding.
    """
    
    def __init__(self):
        """Initialize the adapter with MCP client."""
        from agentic_core.L4_state.semantic_memory.pinecone_mcp_client import get_pinecone_mcp_client
        
        self.mcp_client = get_pinecone_mcp_client()
        self._initialized = False
        logger.info("[L4 PINECONE STORE] Adapter initialized - routing to MCP client")
    
    async def _ensure_initialized(self):
        """Ensure MCP client is initialized."""
        if not self._initialized:
            await self.mcp_client.initialize()
            self._initialized = True
    
    async def similarity_search(
        self, 
        query: str, 
        k: int = 4, 
        namespace: Optional[str] = None,
        **kwargs
    ) -> List[Any]:
        """
        Legacy interface adapter for search.
        
        Args:
            query: Search query text
            k: Number of results to return
            namespace: Optional namespace
            **kwargs: Additional arguments (e.g., rerank, filters)
            
        Returns:
            List of search results
        """
        await self._ensure_initialized()
        
        try:
            results = await self.mcp_client.search(
                query_text=query,
                top_k=k,
                namespace=namespace,
                rerank=kwargs.get('rerank', True),
                filters=kwargs.get('filters')
            )
            
            # Transform MCP results back to legacy format
            matches = results.get('matches', [])
            
            # Convert to legacy result format
            legacy_results = []
            for match in matches:
                legacy_results.append({
                    'id': match.get('id'),
                    'score': match.get('score', 0.0),
                    'metadata': match.get('metadata', {}),
                    'values': match.get('values', [])
                })
            
            logger.info(f"[L4 PINECONE STORE] Similarity search returned {len(legacy_results)} results")
            return legacy_results
            
        except Exception as e:
            logger.error(f"[L4 PINECONE STORE] Similarity search failed: {e}")
            return []
    
    async def add_texts(
        self, 
        texts: List[str], 
        metadatas: Optional[List[dict]] = None, 
        namespace: Optional[str] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Legacy interface adapter for adding documents (via embedding + upsert).
        
        Args:
            texts: List of texts to add
            metadatas: Optional metadata for each text
            namespace: Optional namespace
            ids: Optional IDs for each text
            
        Returns:
            List of IDs for added texts
        """
        await self._ensure_initialized()
        
        try:
            # Generate IDs if not provided
            if ids is None:
                import hashlib
                ids = [f"vec_{hashlib.sha256(text.encode()).hexdigest()[:16]}" for text in texts]
            
            # Construct vectors for upsert
            vectors = []
            for i, text in enumerate(texts):
                vector = {
                    "id": ids[i],
                    "metadata": {
                        "text": text,
                        **(metadatas[i] if metadatas and i < len(metadatas) else {})
                    }
                }
                vectors.append(vector)
            
            # Upsert via MCP (embeddings generated automatically)
            result = await self.mcp_client.upsert(vectors=vectors, namespace=namespace)
            
            logger.info(f"[L4 PINECONE STORE] Added {len(texts)} texts")
            return ids
            
        except Exception as e:
            logger.error(f"[L4 PINECONE STORE] Add texts failed: {e}")
            return []
    
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
            file_id = f"file_{str(file_path).replace('/', '_').replace('\\', '_')}"
            
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
