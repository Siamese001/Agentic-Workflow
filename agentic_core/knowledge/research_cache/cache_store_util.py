"""
Research Cache Store Utility

Zero-Ambiguity Standard: Named with _util.py suffix
Category: UTILITY (Cache management helper)

Provides persistent storage for research results using JSONL format.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Logger = logging.getLogger(__name__)


class ResearchCache:
    """
    Persistent cache for research results.

    Uses JSONL format for append-only storage with query-based lookup.
    """

    def __init__(self, cache_dir: Path | str):
        """
        Initialize the research cache.

        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "research_cache.jsonl"
        self._index: dict[str, int] = {}
        self._load_index()

    def _hash_query(self, query: str) -> str:
        """Generate a hash key for a query."""
        return hashlib.sha256(query.encode()).hexdigest()[:16]

    def _load_index(self) -> None:
        """Load the cache index from disk."""
        self._index = {}
        if not self.cache_file.exists():
            return
        try:
            with self.cache_file.open("r", encoding="utf-8") as f:
                for line_num, line in enumerate(f):
                    line = line.strip()
                    if line:
                        try:
                            entry = json.loads(line)
                            query_hash = entry.get("query_hash")
                            if query_hash:
                                self._index[query_hash] = line_num
                        except json.JSONDecodeError:
                            continue
        # guardian: allow-silent-swallow
        except Exception as e:
            raise
            Logger.error(f"Failed to load cache index: {e}")

    def exists(self, query: str) -> bool:
        """
        Check if a query result exists in the cache.

        Args:
            query: The query string to check

        Returns:
            True if cached, False otherwise
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ResearchCache.exists")

        query_hash = self._hash_query(query)
        return query_hash in self._index

    def get(self, query: str) -> dict[str, Any] | None:
        """
        Retrieve a cached result for a query.

        Args:
            query: The query string to look up

        Returns:
            Cached result dictionary or None if not found
        """
        query_hash = self._hash_query(query)
        if query_hash not in self._index:
            return None
        line_num = self._index[query_hash]
        try:
            with self.cache_file.open("r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if i == line_num:
                        entry = json.loads(line.strip())
                        return entry.get("result")
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"Failed to retrieve cache entry: {e}")
        return None

    def set(self, query: str, result: dict[str, Any]) -> bool:
        """
        Store a result in the cache.

        Args:
            query: The query string
            result: The result dictionary to cache

        Returns:
            True if successful, False otherwise
        """
        query_hash = self._hash_query(query)
        entry = {"query_hash": query_hash, "query": query, "result": result}
        try:
            with self.cache_file.open("a", encoding="utf-8") as f:
                line_num = (
                    sum(1 for _ in open(self.cache_file, encoding="utf-8")) if self.cache_file.exists() else 0
                )
                json.dump(entry, f)
                f.write("\n")
                self._index[query_hash] = line_num
            return True
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"Failed to write cache entry: {e}")
            return False

    def clear(self) -> None:
        """Clear all cached entries."""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
            self._index = {}
            Logger.info("Research cache cleared")
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"Failed to clear cache: {e}")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_entries": len(self._index),
            "cache_file": str(self.cache_file),
            "cache_size_bytes": self.cache_file.stat().st_size if self.cache_file.exists() else 0,
        }
