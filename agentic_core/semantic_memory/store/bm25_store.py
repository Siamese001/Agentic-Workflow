# Sovereign BM25 Keyword Store
# Territory: agentic_core/semantic_memory/store
# Canon Key 9 - Sparse keyword retrieval (BM25)
# Requires: pip install rank_bm25

from rank_bm25 import BM25Okapi
from typing import List, Dict, Optional
import json
from pathlib import Path


class BM25Store:
    """In-memory BM25 index for fast keyword retrieval."""

    def __init__(self):
        self.documents: List[Dict] = []  # {"id": str, "text": str, "metadata": dict}
        self.bm25: Optional[BM25Okapi] = None
        self._build_index()

    def add_documents(self, docs: List[Dict]) -> None:
        """Add or update documents."""
        self.documents.extend(docs)
        self._build_index()

    def _build_index(self) -> None:
        if not self.documents:
            self.bm25 = None
            return
        tokenized = [doc["text"].lower().split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized)

    def query(self, query: str, top_k: int = 5) -> List[Dict]:
        """BM25 keyword search."""
        if not self.bm25 or not self.documents:
            return []

        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)

        # Get top_k with scores
        ranked = sorted(
            enumerate(scores),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

        results = []
        for idx, score in ranked:
            if score == 0:
                continue
            doc = self.documents[idx]
            results.append({
                "source": "bm25",
                "content": doc["text"],
                "score": float(score),
                "id": doc["id"],
                "metadata": doc.get("metadata", {})
            })

        return results


# Global singleton
bm25_store = BM25Store()

def get_bm25_store() -> BM25Store:
    return bm25_store
