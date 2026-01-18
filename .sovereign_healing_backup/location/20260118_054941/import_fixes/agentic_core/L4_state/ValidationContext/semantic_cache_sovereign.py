from __future__ import annotations
"""L4 State: Sovereign Semantic Cache — Redis + Pinecone Hybrid Eternal
Redis L4 local cache for lightning recall + Pinecone eternal vector store.
Full AST + metadata sovereignty with mission-isolation.
"""
import ast
import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from agentic_core.L4_state.caching.redis_mcp_client import get_redis_client
from agentic_core.L4_state.validation_context.PineconeSovereignAgent import PineconeSovereignAgent
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L4_state.validation_context.l4_subatomic_testing_mixin import L4SubatomicTestingMixin

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint_2 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin

Logger: Any = logging.getLogger(__name__)
redis_cache_ttl: Any = 60 * 60 * 24 * 7
max_redis_entry_size: Any = 1024 * 1024
redis_timeout: Any = 5

class SovereignSemanticCache(MCPHardenedMixin, HealerMixin, L4SubatomicTestingMixin):
    """Ultra-hardened hybrid semantic cache — Redis local + Pinecone eternal."""

    def __init__(self, mission_id: str, engine=None, pinecone_agent: Optional[PineconeSovereignAgent]=None):
        super().__init__()
        self.mission_id = mission_id
        self._mcp_audit('init', payload={'mission_id': mission_id})
        self.engine = engine
        self.pinecone = pinecone_agent or PineconeSovereignAgent(Path('.'))
        self.index_name = 'canon-semantic-v1'
        self.namespace = 'canon-files'
        try:
            self.redis = get_redis_client()
            Logger.info('[L4 REDIS] Sovereign MCP cache armed.')
        except Exception as e:
            Logger.critical(f'[L4 REDIS BREACH] MCP cache failed: {e}')
            mcp_authority.record_breach(f'Redis MCP Cache Failure: {str(e)}')
            self.redis = None

    def _cache_key(self, file_path: str) -> str:
        """Mission-isolated and path-hashed key for L4 sovereignty."""
        path_hash = hashlib.sha256(str(Path(file_path)).encode()).hexdigest()[:16]
        return f'semantic:{self.mission_id}:{path_hash}'

    def _extract_ast_features(self, code: str) -> Dict:
        """Parse AST for structural signals (Key 41/42)."""
        try:
            tree = ast.parse(code)
            return {'functions': len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]), 'classes': len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]), 'max_nesting': self._calculate_depth(tree), 'lines': len(code.splitlines())}
        except Exception:
            return {'lines': len(code.splitlines()), 'parse_error': True}

    def _calculate_depth(self, node, current=0) -> int:
        child_depths = [self._calculate_depth(c, current + 1) for c in ast.iter_child_nodes(node) if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.If, ast.For))]
        return max(child_depths, default=current)

    async def cache_file(self, file_path: str, code: str, metadata: Dict) -> None:
        """Embed and cache with dual-store synchronization."""
        key: Any = self._cache_key(file_path)
        if self.redis:
            try:
                cached_data: Any = await self.redis.get(key)
                if cached_data:
                    Logger.info(f'[L4 HIT] Redis MCP recall for {Path(file_path).name}')
                    return
            except Exception:
                pass
        ast_features: Any = self._extract_ast_features(code)
        embed_text: Any = f'File: {file_path}\nStructure: {json.dumps(ast_features)}\nContent: {code[:1000]}'
        try:
            vector: Any = await self.engine.get_embedding(embed_text)
            entry: Any = {'path': str(file_path), 'vector': vector, 'metadata': {**metadata, 'mission_id': self.mission_id, 'cached_at': datetime.utcnow().isoformat() + 'Z', 'ast': ast_features}}
            if self.redis:
                entry_json: Any = json.dumps(entry)
                if len(entry_json.encode()) < MAX_REDIS_ENTRY_SIZE:
                    await self.redis.set(key, entry_json, ttl=REDIS_CACHE_TTL)
            self.pinecone.upsert(index=self.index_name, vectors=[(key, vector, entry['metadata'])], namespace=self.namespace)
            Logger.info(f'[L4 STORE] Dual-sync complete for {Path(file_path).name}')
        except Exception as e:
            Logger.error(f'[L4 CACHE FAILURE] Could not cache {file_path}: {e}')

    async def invalidate(self, file_path: str) -> Any:
        """Purge both stores on fission or physical move."""
        key: Any = self._cache_key(file_path)
        if self.redis:
            try:
                await self.redis.delete(key)
            except:
                pass
        try:
            self.pinecone.delete(ids=[key], namespace=self.namespace)
            Logger.info(f'[L4 PURGE] Purged semantic trail for {Path(file_path).name}')
        except Exception:
            pass
    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
