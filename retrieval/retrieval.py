from __future__ import annotations

"""Top-level retrieval facade module.

This re-exports the primary retrieval entrypoints from
``meta.retrieval.retrieval`` so callers can import
``meta.retrieval`` directly.
"""

from meta.retrieval.retrieval import run_rag_retrieval  # noqa: F401

__all__ = ["run_rag_retrieval"]



