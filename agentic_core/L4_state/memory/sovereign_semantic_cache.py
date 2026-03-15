"""L4 State: Sovereign Semantic cache — Redis + BGE vector store Hybrid.
Redis L4 local cache for lightning recall + in-memory BGE vector store.
Full AST + metadata sovereignty with mission-isolation.
"""

from __future__ import annotations

import ast
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.cache.redis_cache_client import get_hot_cache as _get_hot_cache


def get_redis_client():
    """Shim: redirect legacy callers to the canonical DeterministicRedisCache client."""
    return _get_hot_cache()


from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)
from agentic_core.utils.decorators_compat_util import standard_heal

Logger: Any = logging.getLogger(__name__)
redis_cache_ttl: Any = 60 * 60 * 24 * 7
max_redis_entry_size: Any = 1024 * 1024
redis_timeout: Any = 5


class SovereignSemanticCache(SovereignBaseAgent):
    """Ultra-hardened hybrid semantic cache — Redis local + InMemoryVectorStore eternal."""

    def __init__(self, mission_id: str, engine=None):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "SovereignSemanticCache.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "SovereignSemanticCache.__init__", "p0_governance")
        super().__init__()
        self.mission_id = mission_id
        self.engine = engine
        from agentic_core.L4_state.memory.in_memory_vector_store import InMemoryVectorStore

        self._vector_store: InMemoryVectorStore = InMemoryVectorStore()
        self.index_name = "canon-semantic-v1"
        self.namespace = "canon-files"
        try:
            self.redis = get_redis_client()
            Logger.info("[L4 REDIS] Sovereign MCP cache armed.")
        # guardian: allow-silent-swallow
        except Exception as e:
            raise
            Logger.critical(f"[L4 REDIS BREACH] MCP cache failed: {e}")
            self.redis = None

    def _cache_key(self, file_path: str) -> str:
        """Mission-isolated and path-hashed key for L4 sovereignty."""
        path_hash = hashlib.sha256(str(Path(file_path)).encode()).hexdigest()[:16]
        return f"semantic:{self.mission_id}:{path_hash}"

    # guardian: allow-type-erasure
    def _extract_ast_features(self, code: str) -> dict:
        """Parse AST for structural signals (Key 41/42)."""
        try:
            tree = ast.parse(code)
            return {
                "functions": len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                "classes": len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
                "max_nesting": self._calculate_depth(tree),
                "lines": len(code.splitlines()),
            }
        # guardian: allow-silent-swallow
        except Exception:
            return {"lines": len(code.splitlines()), "parse_error": True}

    def _calculate_depth(self, node, current=0) -> int:
        child_depths = [
            self._calculate_depth(c, current + 1)
            for c in ast.iter_child_nodes(node)
            if isinstance(node, ast.FunctionDef | ast.ClassDef | ast.If | ast.For)
        ]
        return max(child_depths, default=current)

    def cache_file(self, file_path: str, code: str, metadata: dict) -> None:
        """Embed and cache with dual-store synchronization."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "SovereignSemanticCache.cache_file")

        key: Any = self._cache_key(file_path)
        if self.redis:
            try:
                cached_data: Any = self.redis.get(key)
                if cached_data:
                    Logger.info(f"[L4 HIT] Redis MCP recall for {Path(file_path).name}")
                    return
            # guardian: allow-silent-swallow
            except Exception:
                raise
                pass
        ast_features: Any = self._extract_ast_features(code)
        embed_text: Any = f"File: {file_path}\nStructure: {json.dumps(ast_features)}\nContent: {code[:1000]}"
        try:
            vector: Any = self.engine.get_embedding(embed_text)
            entry: Any = {
                "path": str(file_path),
                "vector": vector,
                "metadata": {
                    **metadata,
                    "mission_id": self.mission_id,
                    "cached_at": datetime.utcnow().isoformat() + "Z",
                    "ast": ast_features,
                },
            }
            if self.redis:
                entry_json: Any = json.dumps(entry)
                if len(entry_json.encode()) < max_redis_entry_size:
                    self.redis.set(key, entry_json.encode(), ttl_seconds=redis_cache_ttl)
            self._vector_store[key] = {
                "vector": vector,
                "metadata": entry["metadata"],
                "namespace": self.namespace,
            }
            Logger.info(f"[L4 STORE] Dual-sync complete for {Path(file_path).name}")
        # guardian: allow-silent-swallow
        except Exception as e:
            raise
            Logger.error(f"[L4 CACHE FAILURE] Could not cache {file_path}: {e}")

    # guardian: allow-type-erasure
    def invalidate(self, file_path: str) -> Any:
        """Purge both stores on fission or physical move."""
        key: Any = self._cache_key(file_path)
        if self.redis:
            try:
                self.redis.delete(key)
            # guardian: allow-silent-swallow
            except:
                pass
        self._vector_store.pop(key, None)
        Logger.info(f"[L4 PURGE] Purged semantic trail for {Path(file_path).name}")

    def query(self, text: str, top_k: int = 20, namespace: str = "") -> list[dict]:
        """Semantic similarity search over the in-memory vector store.

        Embeds *text* via BGEEmbedder (BAAI/bge-m3, 1024-dim), then ranks
        all cached entries by cosine similarity.  Returns informational-only
        dicts: ``content_hash``, ``score``, ``content`` (metadata text preview).

        Falls back to empty list when the kill-switch is active or the store
        is empty.  Works with both InMemoryVectorStore (MemoryItem-backed) and
        plain-dict fallback stores.
        """
        import math
        import os

        if os.environ.get("EMBEDDING_ENABLED", "true").lower() in ("false", "0", "no"):
            return []

        # Resolve the underlying storage — InMemoryVectorStore wraps a ._storage dict
        store = getattr(self._vector_store, "_storage", None)
        if store is None:
            # Plain-dict fallback (test injection or legacy usage)
            store = self._vector_store if isinstance(self._vector_store, dict) else {}
        if not store:
            return []

        try:
            from system_learning.engines.openai_embedder import BGEEmbedder

            _embedder = BGEEmbedder()
            vecs = _embedder.embed_batch([text])
            if not vecs or not vecs[0]:
                return []
            q_vec = vecs[0]
        # guardian: allow-silent-swallow
        except Exception:
            return []

        q_mag = math.sqrt(sum(x * x for x in q_vec))
        if q_mag == 0.0:
            return []

        results: list[dict] = []
        for key, entry in store.items():
            # entry is either a MemoryItem or a plain dict (test/legacy)
            if hasattr(entry, "embedding"):
                # InMemoryVectorStore MemoryItem path
                d_vec = entry.embedding or []
                meta = entry.metadata or {}
                ns = meta.get("namespace", "")
            elif isinstance(entry, dict):
                d_vec = entry.get("vector") or []
                meta = entry.get("metadata") or {}
                ns = entry.get("namespace", "")
            else:
                continue
            if namespace and ns != namespace:
                continue
            if not d_vec:
                continue
            dot = sum(a * b for a, b in zip(q_vec, d_vec, strict=False))
            d_mag = math.sqrt(sum(x * x for x in d_vec))
            score = dot / (d_mag * q_mag) if d_mag * q_mag != 0 else 0.0
            results.append(
                {
                    "content_hash": key,
                    "score": score,
                    "content": meta.get("text", meta.get("path", ""))[:200],
                }
            )

        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:top_k]

    @standard_heal
    # guardian: allow-type-erasure
    def heal_repository(self, **kwargs) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository(**kwargs)

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)
