from __future__ import annotations
from rank_bm25 import BM25Okapi
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from typing import Any, List, Dict, Optional
import json
from pathlib import Path

class Bm25Store:
    """In-memory BM25 index for fast keyword retrieval."""

    def __init__(self):
        self.documents: List[Dict] = []
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
        tokenized = [doc['text'].lower().split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized)

    def query(self, query: str, top_k: int=5) -> List[Dict]:
        """BM25 keyword search."""
        if not self.bm25 or not self.documents:
            return []
        tokenized_query: Any = query.lower().split()
        scores: Any = self.bm25.get_scores(tokenized_query)
        ranked: Any = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        results: Any = []
        for idx, score in ranked:
            if score == 0:
                continue
            doc: Any = self.documents[idx]
            results.append({'source': 'bm25', 'content': doc['text'], 'score': float(score), 'id': doc['id'], 'metadata': doc.get('metadata', {})})
        return results

_bm25_store: Any = Bm25Store()

def get_bm25_store() -> BM25Store:
    """Brief description of functionality and purpose."""
    return _bm25_store
