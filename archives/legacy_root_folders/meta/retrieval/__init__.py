"""Retrieval META package for v10_10.

Canonical entrypoints:
- meta.retrieval.retrieval
- meta.retrieval.hybrid_ranker

The package-level surface also exposes ``run_rag_retrieval`` so callers can
import it directly from ``meta.retrieval``.
"""

from archives.legacy_root_folders.retrievers.retrieval import orchestrate_retrieval, run_rag_retrieval
from archives.legacy_root_folders.meta.retrieval.hybrid_ranker import fuse_and_rank

__all__ = ["orchestrate_retrieval", "run_rag_retrieval", "fuse_and_rank"]



