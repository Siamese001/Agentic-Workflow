from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "batch_embedding_service", "L2")
_emit_routes_through("p1", "batch_embedding_service", "L2")
_emit_escalates_to_human("p1", "batch_embedding_service", "L2")
_emit_reads_policy_state("p1", "batch_embedding_service", "L2")

_emit_applies_guardrail("p0", "batch_embedding_service", "p0_governance")
_emit_snapshots_state("p0", "batch_embedding_service", "state_snapshot")

"Batch Embedding Service - Parallel embedding generation for 5-10x speedup.\n\nOptimized for i7-10750H (6 cores/12 threads) with 32GB RAM allocation.\nUses ThreadPoolExecutor to process embeddings in parallel batches.\n"
import asyncio
import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)

Logger: Any = logging.getLogger(__name__)


class BatchEmbeddingService:
    """Service for parallel batch embedding generation.

    Optimized for i7-10750H (6 cores/12 threads).
    Keeps workers low to prevent context switching overhead.
    """

    # guardian: allow-magic-config
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
        self, texts: list[str], model_func: Callable[[list[str]], list[np.ndarray]]
    ) -> list[np.ndarray]:
        """Embed a list of texts in parallel batches.

        Args:
            texts: List of strings to embed
            model_func: Sync function that takes a list of strings and returns embeddings

        Returns:
            List of embeddings as numpy arrays

        Example:
            >>> service = BatchEmbeddingService(batch_size=BATCH_SIZE, max_workers=4)
            >>> embeddings = await service.embed_batch(
            ...     texts=["text1", "text2", ...],
            ...     model_func=my_embedding_model.embed
            ... )
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "BatchEmbeddingService.embed_batch"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:BatchEmbeddingService.embed_batch".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        self, text: str, model_func: Callable[[list[str]], list[np.ndarray]]
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


# guardian: allow-magic-config
def create_batch_embedding_service(batch_size: int = 32, max_workers: int = 4) -> BatchEmbeddingService:
    """Create a BatchEmbeddingService instance.

    Args:
        batch_size: Number of texts to embed in a single batch
        max_workers: Number of parallel workers

    Returns:
        Configured BatchEmbeddingService instance
    """
    return BatchEmbeddingService(batch_size=batch_size, max_workers=max_workers)
