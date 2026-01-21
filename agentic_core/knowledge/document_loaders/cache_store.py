"""
Research Cache - File-based cache for RAG results.

Restored: 2026-01-13 | Version: 2.0.0
Original: archives/unmapped_drift/20260107/agentic_core/knowledge/document_loaders/cache_store.py
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ResearchCache:
    """Simple file-based cache for RAG results, optimized for agentic retrieval."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / 'ResearchCache.jsonl'

    def store(self, query: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Atomically store a research result with metadata."""
        entry: Dict[str, Any] = {
            'query': query.lower(),
            'content': content,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
        with self.cache_file.open('a', encoding='utf-8') as f:
            json.dump(entry, f)
            f.write('\n')

    def query(self, query: str, top_k: int = 3) -> List[str]:
        """Performs simple keyword-matching retrieval from the research cache."""
        query_lower: str = query.lower()
        results: List[str] = []

        if not self.cache_file.exists():
            return results

        with self.cache_file.open('r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry: Dict[str, Any] = json.loads(line)
                    if query_lower in entry['query']:
                        results.append(entry['content'])
                except json.JSONDecodeError:
                    continue
                if len(results) >= top_k:
                    break

        return results

    def get_all_entries(self) -> List[Dict[str, Any]]:
        """Retrieve all cache entries."""
        entries: List[Dict[str, Any]] = []

        if not self.cache_file.exists():
            return entries

        with self.cache_file.open('r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        return entries

    def clear(self) -> None:
        """Clear all cache entries."""
        if self.cache_file.exists():
            self.cache_file.unlink()
