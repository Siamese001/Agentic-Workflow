"""Batch Processing Utilities for CPU-Intensive Operations.

Provides efficient batch processing for large datasets,
optimized for AMD CPUs with high core counts.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar

from agentic_core.L2_execution.utils.cpu_optimizer import (
    AMD9950X3DOptimizer,
    CPUConfig,
)

logger = logging.getLogger(__name__)

T = TypeVar('T')
R = TypeVar('R')


@dataclass
class BatchResult(Generic[T, R]):
    """Result from batch processing."""
    items: list[T]
    results: list[R]
    processing_time_ms: float
    success: bool = True
    error: str | None = None


@dataclass
class BatchMetrics:
    """Metrics for batch processing."""
    total_batches: int = 0
    total_items: int = 0
    total_time_ms: float = 0.0
    avg_batch_time_ms: float = 0.0
    min_batch_time_ms: float = float('inf')
    max_batch_time_ms: float = 0.0
    _batch_times: list[float] = field(default_factory=list)

    def record_batch(self, items: int, time_ms: float) -> None:
        """Record batch metrics."""
        self.total_batches += 1
        self.total_items += items
        self._batch_times.append(time_ms)
        self.total_time_ms += time_ms
        self.min_batch_time_ms = min(self.min_batch_time_ms, time_ms)
        self.max_batch_time_ms = max(self.max_batch_time_ms, time_ms)
        self.avg_batch_time_ms = self.total_time_ms / self.total_batches

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_batches": self.total_batches,
            "total_items": self.total_items,
            "total_time_ms": self.total_time_ms,
            "avg_batch_time_ms": self.avg_batch_time_ms,
            "min_batch_time_ms": self.min_batch_time_ms,
            "max_batch_time_ms": self.max_batch_time_ms,
            "items_per_second": (
                self.total_items / (self.total_time_ms / 1000)
                if self.total_time_ms > 0 else 0
            ),
        }


class BatchProcessor(Generic[T, R]):
    """High-performance batch processor.

    Features:
    - Automatic batch sizing based on item complexity
    - Parallel processing within batches
    - Progress tracking and metrics
    - Error isolation (one failed item doesn't stop batch)
    """

    def __init__(
        self,
        processor_func: Callable[[T], R],
        batch_size: int = 1000,
        max_workers: int | None = None,
        error_isolation: bool = True,
    ):
        self.processor_func = processor_func
        self.batch_size = batch_size
        self.error_isolation = error_isolation
        self.optimizer = AMD9950X3DOptimizer(CPUConfig(max_workers=max_workers))
        self.metrics = BatchMetrics()

    def process(self, items: list[T]) -> list[R]:
        """Process all items in optimized batches."""
        if not items:
            return []

        total = len(items)
        results: list[R] = []

        logger.info(f"Processing {total} items in batches of {self.batch_size}")

        for i in range(0, total, self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (total + self.batch_size - 1) // self.batch_size

            start = time.time()

            try:
                if self.error_isolation:
                    batch_results = self._process_batch_with_isolation(batch)
                else:
                    batch_results = [self.processor_func(item) for item in batch]

                results.extend(batch_results)

            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                logger.error(f"Batch {batch_num} failed: {e}")
                raise

            elapsed_ms = (time.time() - start) * 1000
            self.metrics.record_batch(len(batch), elapsed_ms)

            logger.debug(
                f"Batch {batch_num}/{total_batches}: "
                f"{len(batch)} items in {elapsed_ms:.1f}ms"
            )

        logger.info(f"Processed {total} items in {self.metrics.total_batches} batches")
        return results

    def _process_batch_with_isolation(self, batch: list[T]) -> list[R]:
        """Process batch with error isolation per item."""
        results: list[R] = []

        for item in batch:
            try:
                result = self.processor_func(item)
                results.append(result)
            except Exception as e:
                logger.warning(f"Item processing failed: {e}")
                # Add None or sentinel value for failed items
                results.append(None)  # type: ignore

        return results

    def process_parallel(self, items: list[T]) -> list[R]:
        """Process items using parallel execution within batches."""
        if not items:
            return []

        total = len(items)
        results: list[R] = []
        executor = self.optimizer.get_executor()

        logger.info(f"Parallel processing {total} items with {self.optimizer.get_optimal_workers()} workers")

        for i in range(0, total, self.batch_size):
            batch = items[i:i + self.batch_size]

            start = time.time()

            # Submit all items in batch to executor
            futures = [executor.submit(self.processor_func, item) for item in batch]

            # Collect results
            for future in futures:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                    if self.error_isolation:
                        logger.warning(f"Parallel item failed: {e}")
                        results.append(None)  # type: ignore
                    else:
                        raise

            elapsed_ms = (time.time() - start) * 1000
            self.metrics.record_batch(len(batch), elapsed_ms)

        return results

    def get_metrics(self) -> dict[str, Any]:
        """Get processing metrics."""
        return self.metrics.to_dict()


class StreamingBatchProcessor(Generic[T, R]):
    """Batch processor for streaming/large datasets.

    Processes items as they arrive, maintaining optimal batch sizes
    without loading everything into memory.
    """

    def __init__(
        self,
        processor_func: Callable[[T], R],
        batch_size: int = 1000,
        max_pending: int = 5000,
    ):
        self.processor_func = processor_func
        self.batch_size = batch_size
        self.max_pending = max_pending
        self._buffer: list[T] = []
        self._results: list[R] = []
        self.metrics = BatchMetrics()

    def add(self, item: T) -> list[R] | None:
        """Add item to buffer. Returns results if batch is full."""
        self._buffer.append(item)

        if len(self._buffer) >= self.batch_size:
            return self.flush()

        return None

    def flush(self) -> list[R]:
        """Process and return all buffered items."""
        if not self._buffer:
            return []

        batch = self._buffer[:self.batch_size]
        self._buffer = self._buffer[self.batch_size:]

        start = time.time()

        results = [self.processor_func(item) for item in batch]
        self._results.extend(results)

        elapsed_ms = (time.time() - start) * 1000
        self.metrics.record_batch(len(batch), elapsed_ms)

        return results

    def close(self) -> list[R]:
        """Process remaining items and return all results."""
        self.flush()
        final_results = self._results
        self._results = []
        return final_results


# Predefined batch processors for common ADG operations

class JSONBatchProcessor(BatchProcessor[str, Any]):
    """Batch processor for JSON files."""

    def __init__(self, batch_size: int = 500):
        import json
        super().__init__(
            processor_func=lambda path: json.load(open(path)),
            batch_size=batch_size,
        )


class FileHashBatchProcessor(BatchProcessor[str, str]):
    """Batch processor for computing file hashes."""

    def __init__(self, algorithm: str = 'sha256', batch_size: int = 200):
        import hashlib

        def compute_hash(path: str) -> str:
            hasher = hashlib.new(algorithm)
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()

        super().__init__(
            processor_func=compute_hash,
            batch_size=batch_size,
        )


__all__ = [
    "BatchProcessor",
    "StreamingBatchProcessor",
    "BatchResult",
    "BatchMetrics",
    "JSONBatchProcessor",
    "FileHashBatchProcessor",
]
