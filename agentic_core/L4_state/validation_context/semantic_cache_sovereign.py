"""L4 State: Sovereign Semantic Cache — Redis + Pinecone Hybrid Eternal
Redis L4 local cache for lightning recall + Pinecone eternal vector store.
Full AST + metadata sovereignty with mission-isolation.
"""
import ast
import json
import logging
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import redis
from agentic_core.L4_state.vector.pinecone_sovereign_agent import PineconeSovereignAgent
from agentic_core.L5_safety.policy.mcp_sovereign import mcp_authority

logger = logging.getLogger(__name__)

# Sovereign limits for L5 stability
REDIS_CACHE_TTL = 60 * 60 * 24 * 7  # 7 days
MAX_REDIS_ENTRY_SIZE = 1024 * 1024  # 1MB shielding
REDIS_TIMEOUT = 5

class SovereignSemanticCache:
    """Ultra-hardened hybrid semantic cache — Redis local + Pinecone eternal."""
    
    def __init__(self, mission_id: str, engine=None, pinecone_agent: Optional[PineconeSovereignAgent] = None):
        self.mission_id = mission_id
        self.engine = engine
        self.pinecone = pinecone_agent or PineconeSovereignAgent(Path("."))
        self.index_name = "canon-semantic-v1"
        self.namespace = "canon-files"
        
        # L4 Hardened Redis Connection Pool
        try:
            url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_pool = redis.ConnectionPool.from_url(
                url,
                max_connections=10,
                socket_connect_timeout=REDIS_TIMEOUT,
                socket_timeout=REDIS_TIMEOUT,
                retry_on_timeout=True
            )
            self.redis = redis.Redis(connection_pool=self.redis_pool)
            self.redis.ping()
            logger.info("[L4 REDIS] Sovereign local cache armed.")
        except Exception as e:
            logger.critical(f"[L4 REDIS BREACH] Local cache failed: {e}")
            mcp_authority.record_breach(f"Redis Cache Failure: {str(e)}")
            self.redis = None

    def _cache_key(self, file_path: str) -> str:
        """Mission-isolated and path-hashed key for L4 sovereignty."""
        path_hash = hashlib.sha256(str(Path(file_path)).encode()).hexdigest()[:16]
        return f"semantic:{self.mission_id}:{path_hash}"
    
    def _extract_ast_features(self, code: str) -> Dict:
        """Parse AST for structural signals (Key 41/42)."""
        try:
            tree = ast.parse(code)
            return {
                "functions": len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                "classes": len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
                "max_nesting": self._calculate_depth(tree),
                "lines": len(code.splitlines())
            }
        except Exception:
            return {"lines": len(code.splitlines()), "parse_error": True}

    def _calculate_depth(self, node, current=0) -> int:
        child_depths = [self._calculate_depth(c, current + 1) 
                        for c in ast.iter_child_nodes(node) 
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.If, ast.For))]
        return max(child_depths, default=current)

    async def cache_file(self, file_path: str, code: str, metadata: Dict) -> None:
        """Embed and cache with dual-store synchronization."""
        key = self._cache_key(file_path)
        
        # [L5 SHIELD] Check Redis local first for fast hit
        if self.redis:
            try:
                cached_data = self.redis.get(key)
                if cached_data:
                    logger.info(f"[L4 HIT] Redis recall for {Path(file_path).name}")
                    return # Already synced
            except Exception: pass

        # Fresh Embedding path
        ast_features = self._extract_ast_features(code)
        embed_text = f"File: {file_path}\nStructure: {json.dumps(ast_features)}\nContent: {code[:1000]}"
        
        try:
            vector = await self.engine.get_embedding(embed_text)
            
            entry = {
                "path": str(file_path),
                "vector": vector,
                "metadata": {
                    **metadata,
                    "mission_id": self.mission_id,
                    "cached_at": datetime.utcnow().isoformat() + "Z",
                    "ast": ast_features
                }
            }

            # 1. Local Redis Persistence (Fast Access)
            if self.redis:
                entry_json = json.dumps(entry)
                if len(entry_json.encode()) < MAX_REDIS_ENTRY_SIZE:
                    self.redis.set(key, entry_json, ex=REDIS_CACHE_TTL)
            
            # 2. Remote Pinecone Persistence (Eternal Truth)
            self.pinecone.upsert(
                index=self.index_name,
                vectors=[(key, vector, entry["metadata"])],
                namespace=self.namespace
            )
            logger.info(f"[L4 STORE] Dual-sync complete for {Path(file_path).name}")

        except Exception as e:
            logger.error(f"[L4 CACHE FAILURE] Could not cache {file_path}: {e}")

    async def invalidate(self, file_path: str):
        """Purge both stores on fission or physical move."""
        key = self._cache_key(file_path)
        if self.redis:
            try: self.redis.delete(key)
            except: pass
        try:
            self.pinecone.delete(ids=[key], namespace=self.namespace)
            logger.info(f"[L4 PURGE] Purged semantic trail for {Path(file_path).name}")
        except Exception: pass
