"""Top-level retrieval facade module.

Re-exports META retrieval orchestration entrypoints so that callers can import
from the project root directly. All retrieval logic is centralized in
``meta.retrieval.retrieval`` following L2 execution-layer conventions.
"""
from __future__ import annotations

from archives.legacy_root_folders.meta.retrieval.retrieval import orchestrate_retrieval
from archives.legacy_root_folders.meta.retrieval.retrieval import run_rag_retrieval

__all__ = ["orchestrate_retrieval", "run_rag_retrieval"]
