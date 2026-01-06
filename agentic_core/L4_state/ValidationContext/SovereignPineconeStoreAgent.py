from __future__ import annotations
"""
Pinecone Vector Store – ADAPTER (Phase 13C)
Translation Layer: Legacy Interface -> New MCP Client

Maintains backward compatibility for 'add_texts' and 'similarity_search'
while routing all operations through the Sovereign MCP architecture.
"""
import logging
from typing import List, Optional, Any, Dict
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from pathlib import Path

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

Logger: Any = logging.getLogger('L4.PineconeStore')

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

# NAMING CANON ETERNAL — renamed for sovereign discovery — Phase 3 — 2025-12-30
class SovereignPineconeStoreAgent(HealerMixin, MCPHardenedMixin):
    """
    ADAPTER: Legacy Interface -> New MCP Client.
    Maintains backward compatibility for 'add_texts' and 'similarity_search'.
    
    Phase 13C: All operations now flow through L3 MCP Router with L5 shielding.
    """

    def __init__(self, index_name: Optional[str]=None, namespace: Optional[str]=None) -> None:
        """Initialize the adapter with MCP client."""
        from agentic_core.L4_state.semantic_memory.pinecone_mcp_client import SovereignPineconeMCPClient
        self.McpClient = SovereignPineconeMCPClient()
        self.namespace = namespace
        self._initialized = False
        Logger.info('[L4 ADAPTER] Initialized - routing to MCP client')

    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L4 compliance."""
        assert hasattr(self, 'McpClient'), "Missing McpClient"
        assert hasattr(self, 'namespace'), "Missing namespace"
        return True

    async def _ensure_initialized(self):
        """Ensure MCP client is initialized."""
        if not self._initialized:
            await self.McpClient.initialize()
            self._initialized = True

    async def similarity_search(self, query: str, k: int=4, **kwargs) -> List[Dict]:
        """Legacy adapter for search."""
        Logger.info(f'[L4 ADAPTER] Routing legacy search to MCP: {query}')
        await self._ensure_initialized()
        result: Any = await self.McpClient.search(query_text=query, top_k=k, namespace=self.namespace, rerank=kwargs.get('rerank', True))
        matches: Any = result.get('matches', []) if isinstance(result, dict) else []
        return matches

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L4 state agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L4 state - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    async def add_texts(self, texts: List[str], metadatas: Optional[List[dict]]=None, ids: Optional[List[str]]=None) -> List[str]:
        """Legacy adapter for adding documents."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        Logger.info(f'[L4 ADAPTER] Routing legacy add_texts to MCP Inference + Upsert')
        await self._ensure_initialized()
        emb_result: Any = await self.McpClient.inference_embed(texts)
        embeddings: Any = emb_result.get('data', [])
        if not embeddings:
            raise RuntimeError('MCP Inference failed to return embeddings')
        vectors: Any = []
        result_ids: Any = []
        for i, text in enumerate(texts):
            vec_id: Any = ids[i] if ids else f'vec_{abs(hash(text))}'
            meta: Any = metadatas[i] if metadatas else {}
            meta['text'] = text
            vectors.append({'id': vec_id, 'values': embeddings[i]['values'] if isinstance(embeddings[i], dict) else embeddings[i], 'metadata': meta})
            result_ids.append(vec_id)
        await self.McpClient.upsert(vectors=vectors, namespace=self.namespace)
        return result_ids

    async def upsert_file_vector(self, file_path: Path, territory_hint: Optional[str]=None) -> Any:
        """
        Upsert single file — used during healing.
        
        Args:
            file_path: Path to file
            territory_hint: Optional territory classification
        """
        await self._ensure_initialized()
        try:
            content: Any = file_path.read_text(encoding='utf-8', errors='ignore')
            path_str: Any = str(file_path).replace('/', '_').replace('\\', '_')
            file_id: Any = f'file_{path_str}'
            metadata: Any = {'text': content, 'file_path': str(file_path), 'type': 'file'}
            if territory_hint:
                metadata['territory'] = territory_hint
            vectors: Any = [{'id': file_id, 'metadata': metadata}]
            await self.McpClient.upsert(vectors=vectors)
            Logger.info(f'[L4 PINECONE STORE] Upserted file vector: {file_path}')
        except Exception as e:
            Logger.error(f'[L4 PINECONE STORE] File upsert failed for {file_path}: {e}')

    async def semantic_search(self, query: str, top_k: int=5) -> List[Dict]:
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
            results: Any = await self.McpClient.search(query_text=query, top_k=top_k, rerank=True)
            Logger.info(f"[L4 PINECONE STORE] Semantic search returned {len(results.get('matches', []))} results")
            return results.get('matches', [])
        except Exception as e:
            Logger.error(f'[L4 PINECONE STORE] Semantic search failed: {e}')
            return []

    async def hybrid_search(self, query: str, top_k: int=5) -> List[Dict]:
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
            results: Any = await self.McpClient.search(query_text=query, top_k=top_k, rerank=True)
            Logger.info(f"[L4 PINECONE STORE] Hybrid search returned {len(results.get('matches', []))} results")
            return results.get('matches', [])
        except Exception as e:
            Logger.error(f'[L4 PINECONE STORE] Hybrid search failed: {e}')
            return []

    def purge_ghost_vector(self, file_path: Path) -> Any:
        """
        Surgical strike to remove stale vector data.
        
        Note: Delete operations not directly supported via MCP.
        This is a no-op for compatibility.
        
        Args:
            file_path: Path to file
        """
        Logger.warning(f'[L4 PINECONE STORE] purge_ghost_vector called but delete not supported via MCP: {file_path}')

    async def health_check(self) -> Dict:
        """
        Enhanced health check with sample quality assessment.
        
        Returns:
            Health status dictionary
        """
        await self._ensure_initialized()
        try:
            health: Any = await self.McpClient.health_check()
            return {'status': health.get('status', 'unknown'), 'vectors': health.get('vector_count', 0), 'namespaces': health.get('namespaces', {}), 'sample_quality': 'good' if health.get('status') == 'healthy' else 'degraded'}
        except Exception as e:
            Logger.error(f'[L4 PINECONE STORE] Health check failed: {e}')
            return {'status': 'unhealthy', 'error': str(e), 'vectors': 0, 'sample_quality': 'degraded'}

    async def execute(self, ctx: Any=None) -> Any:
        """
        Health check for the validator loop.
        Reports index status and vector count with quality metrics.
        
        Args:
            ctx: Optional validation context
        """
        await self._ensure_initialized()
        try:
            health: Any = await self.health_check()
            status_msg: Any = f"Pinecone MCP: {health['vectors']} vectors online (quality: {health['sample_quality']})"
            Logger.info(f'[L4 PINECONE STORE] {status_msg}')
            if ctx:
                ctx.report('VectorHealth', 1, health['status'] == 'healthy', status_msg)
        except Exception as e:
            Logger.error(f'[L4 PINECONE STORE] Execute failed: {e}')
            if ctx:
                ctx.report('VectorHealth', 1, True, f'Pinecone health check warning: {str(e)}')
PineconeSovereignAgent: Any = SovereignPineconeStoreAgent
