"""Retrieval META package for v10_10.

Canonical entrypoints:
- meta.retrieval.retrieval
- meta.retrieval.hybrid_ranker

The package-level surface also exposes ``run_rag_retrieval`` so callers can
import it directly from ``meta.retrieval``.
"""

from .retrieval import orchestrate_retrieval, run_rag_retrieval  # noqa: F401
from .hybrid_ranker import fuse_and_rank  # noqa: F401

__all__ = ["orchestrate_retrieval", "run_rag_retrieval", "fuse_and_rank"]



