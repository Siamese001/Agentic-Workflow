"""RAG Reranker Boundary Shim.

This module isolates torch and FlagEmbedding imports outside L0-L6.
L5 code calls this shim via a narrow interface to obtain a reranker
instance without importing model libraries directly.

Boundary contract:
- torch and FlagEmbedding are imported ONLY in this file.
- L0-L6 must NEVER import this module directly; it is called only
  at application wiring time (composition root) or via dependency
  injection.
"""

from __future__ import annotations

from typing import Any


def create_bge_reranker() -> tuple[Any | None, bool, str]:
    """Create a BGE reranker instance with device detection.

    Returns:
        Tuple of (reranker_instance_or_None, is_available, status_message).
        If torch or FlagEmbedding are not installed, returns (None, False, ...).
    """
    try:
        import torch
    except ImportError:
        return (None, False, "torch not installed")

    try:
        from FlagEmbedding import FlagReranker
    except ImportError:
        return (
            None,
            False,
            "FlagEmbedding not installed — falling back to RRF only",
        )

    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    model_name = "BAAI/bge-reranker-v2-m3"
    reranker = FlagReranker(model_name, use_fp16=device != "cpu")
    return (
        reranker,
        True,
        f"BGE Reranker armed on {device}: {model_name}",
    )
