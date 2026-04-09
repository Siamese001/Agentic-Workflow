"""Sparse/Hybrid Indexing - Sparse lexical and hybrid merge retrieval.

Implements 10C GAP-10C-002:
- Sparse index build (normalize, extract, tokenize, weight, inverted index)
- Hybrid merge query-time (sparse + dense combination)
- BM25 weighting
"""

from .sparse_index import SparseIndex
from .hybrid_merger import HybridMerger
from .bm25_scorer import BM25Scorer

__all__ = [
    "SparseIndex",
    "HybridMerger",
    "BM25Scorer",
]
