"""Top-level retrieval facade module.

Re-exports META retrieval orchestration entrypoints so that callers can import
from the project root directly. All retrieval logic is centralized in
``meta.retrieval.retrieval`` following L2 execution-layer conventions.
"""
from __future__ import annotations

from meta.retrieval.retrieval import orchestrate_retrieval  # noqa: F401
from meta.retrieval.retrieval import run_rag_retrieval  # noqa: F401

__all__ = ["orchestrate_retrieval", "run_rag_retrieval"]
