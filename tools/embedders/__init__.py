"""Embedder tools for vector indexing.

Exports:
    BgeM3Embedder: BGE-M3 embedder with 1024-dim output
    get_embedder: Get singleton embedder instance
    embed_text: Convenience function for single text embedding
    embed_texts: Convenience function for batch embedding
"""

from .bge_m3_embedder import (
    BgeM3Embedder,
    embed_text,
    embed_texts,
    get_embedder,
)

__all__ = [
    "BgeM3Embedder",
    "embed_text",
    "embed_texts",
    "get_embedder",
]
