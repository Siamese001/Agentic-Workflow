from __future__ import annotations

"""Batch Embedding Service - Parallel embedding generation for 5-10x speedup.

Optimized for i7-10750H (6 cores/12 threads) with 32GB RAM allocation.
Uses ThreadPoolExecutor to process embeddings in parallel batches.
"""
import asyncio
import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import numpy as np

Logger: Any = logging.getLogger(__name__)


class BatchEmbeddingService:
    """Service for parallel batch embedding generation.

    Optimized for i7-10750H (6 cores/12 threads).
    Keeps workers low to prevent context switching overhead.
    """

    def __init__(self, batch_size: int = 32, max_workers: int = 4):
        """Initialize the batch embedding service.

        Args:
            batch_size: Number of texts to embed in a single batch (default: 32)
            max_workers: Number of parallel workers (default: 4 for i7-10750H)
        """
        self.batch_size = batch_size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        Logger.info(f"Initialized BatchEmbeddingService: batch_size={batch_size}, max_workers={max_workers}")

    async def embed_batch(
        self,
        texts: list[str],
        model_func: Callable[[list[str]], list[np.ndarray]],
    ) -> list[np.ndarray]:
        """Embed a list of texts in parallel batches.

        Args:
            texts: List of strings to embed
            model_func: Sync function that takes a list of strings and returns embeddings

        Returns:
            List of embeddings as numpy arrays

        Example:
            >>> service = BatchEmbeddingService(batch_size=32, max_workers=4)
            >>> embeddings = await service.embed_batch(
            ...     texts=["text1", "text2", ...],
            ...     model_func=my_embedding_model.embed
            ... )
        """
        if not texts:
            Logger.warning("Empty text list provided to embed_batch")
            return []
        batches: Any = [texts[i : i + self.batch_size] for i in range(0, len(texts), self.batch_size)]
        Logger.debug(f"Processing {len(texts)} texts in {len(batches)} batches of size {self.batch_size}")
        loop: Any = asyncio.get_event_loop()
        tasks: Any = [loop.run_in_executor(self.executor, model_func, batch) for batch in batches]
        try:
            results: Any = await asyncio.gather(*tasks)
            embeddings: Any = [emb for batch_result in results for emb in batch_result]
            Logger.info(f"Successfully generated {len(embeddings)} embeddings from {len(texts)} texts")
            return embeddings
        except Exception as e:
            Logger.error(f"Failed to generate embeddings: {e}")
            raise

    async def embed_single(
        self,
        text: str,
        model_func: Callable[[list[str]], list[np.ndarray]],
    ) -> np.ndarray:
        """Embed a single text (convenience method).

        Args:
            text: Single string to embed
            model_func: Sync function that takes a list of strings and returns embeddings

        Returns:
            Single embedding as numpy array
        """
        embeddings: Any = await self.embed_batch([text], model_func)
        return embeddings[0] if embeddings else None

    def shutdown(self) -> Any:
        """Shutdown the thread pool executor."""
        Logger.info("Shutting down BatchEmbeddingService executor")
        self.executor.shutdown(wait=True)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()


def create_batch_embedding_service(batch_size: int = 32, max_workers: int = 4) -> BatchEmbeddingService:
    """Create a BatchEmbeddingService instance.

    Args:
        batch_size: Number of texts to embed in a single batch
        max_workers: Number of parallel workers

    Returns:
        Configured BatchEmbeddingService instance
    """
    return BatchEmbeddingService(batch_size=batch_size, max_workers=max_workers)
