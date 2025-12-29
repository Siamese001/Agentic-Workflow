# Research Cache Store
# Territory: agentic_core/knowledge/research_cache
# Purpose: Persist successful external research results to accelerate convergence.

import json
from pathlib import Path
from typing import List, Optional

class ResearchCache:
    """Simple file-based cache for RAG results, optimized for agentic retrieval."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = cache_dir / "research_cache.jsonl"

    def store(self, query: str, content: str, metadata: Optional[dict] = None) -> None:
        """Atomically store a research result with metadata."""
        entry = {
            "query": query.lower(),
            "content": content,
            "metadata": metadata or {},
            "timestamp": "2025-12-29",
        }
        with self.cache_file.open("a", encoding="utf-8") as f:
            json.dump(entry, f)
            f.write("\n")

    def query(self, query: str, top_k: int = 3) -> List[str]:
        """Performs simple keyword-matching retrieval from the research cache."""
        query_lower = query.lower()
        results = []

        if not self.cache_file.exists():
            return results

        with self.cache_file.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    # Simple contains check for v1; v2 will use embeddings
                    if query_lower in entry["query"]:
                        results.append(entry["content"])
                except json.JSONDecodeError:
                    continue
                if len(results) >= top_k:
                    break

        return results
