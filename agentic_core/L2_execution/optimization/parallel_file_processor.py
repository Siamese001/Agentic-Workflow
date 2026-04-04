"""Parallel File Processing for CPU-Intensive ADG Operations.

Provides parallel file reading/processing for ADG tools and other
file-intensive operations. Uses ProcessPoolExecutor for true parallelism.
"""

from __future__ import annotations

import concurrent.futures
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, TypeVar

from agentic_core.L2_execution.optimization.cpu_optimizer import (
    AMD9950X3DOptimizer,
    CPUConfig,
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass(frozen=True)
class FileTask:
    """File processing task specification."""
    file_path: str
    task_id: str
    metadata: dict[str, Any] | None = None


@dataclass
class FileResult:
    """Result from file processing."""
    task_id: str
    file_path: str
    success: bool
    data: Any = None
    error: str | None = None
    processing_time_ms: float = 0.0


class ParallelFileProcessor:
    """Parallel file processor for CPU-intensive operations."""

    def __init__(
        self,
        max_workers: int | None = None,
        chunk_size: int = 50,
        use_processes: bool = False,  # Default to threads for file I/O
    ):
        self.config = CPUConfig(
            max_workers=max_workers,
            chunk_size=chunk_size,
            use_processes=use_processes,
        )
        self.optimizer = AMD9950X3DOptimizer(self.config)
        self._executor: concurrent.futures.Executor | None = None

    def _get_executor(self) -> concurrent.futures.Executor:
        """Get or create executor."""
        if self._executor is None:
            workers = self.optimizer.get_optimal_workers()

            if self.config.use_processes:
                self._executor = concurrent.futures.ProcessPoolExecutor(
                    max_workers=workers,
                )
            else:
                self._executor = concurrent.futures.ThreadPoolExecutor(
                    max_workers=workers,
                )

        return self._executor

    def process_files(
        self,
        file_paths: list[str],
        processor_func: Callable[[str], T],
        on_progress: Callable[[int, int], None] | None = None,
    ) -> list[FileResult]:
        """Process multiple files in parallel."""
        if not file_paths:
            return []

        total = len(file_paths)
        results: list[FileResult] = []

        tasks = [
            FileTask(file_path=fp, task_id=f"task_{i}")
            for i, fp in enumerate(file_paths)
        ]

        executor = self._get_executor()
        futures = {
            executor.submit(self._process_single, task, processor_func): task
            for task in tasks
        }

        completed = 0
        for future in concurrent.futures.as_completed(futures):
            task = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append(FileResult(
                    task_id=task.task_id,
                    file_path=task.file_path,
                    success=False,
                    error=str(e),
                ))

            completed += 1
            if on_progress and completed % 10 == 0:
                on_progress(completed, total)

        if on_progress:
            on_progress(completed, total)

        return results

    def _process_single(
        self,
        task: FileTask,
        processor_func: Callable[[str], T],
    ) -> FileResult:
        """Process a single file."""
        start = time.time()

        try:
            if not os.path.exists(task.file_path):
                return FileResult(
                    task_id=task.task_id,
                    file_path=task.file_path,
                    success=False,
                    error="File not found",
                    processing_time_ms=0.0,
                )

            result_data = processor_func(task.file_path)
            elapsed_ms = (time.time() - start) * 1000

            return FileResult(
                task_id=task.task_id,
                file_path=task.file_path,
                success=True,
                data=result_data,
                processing_time_ms=elapsed_ms,
            )

        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            return FileResult(
                task_id=task.task_id,
                file_path=task.file_path,
                success=False,
                error=str(e),
                processing_time_ms=elapsed_ms,
            )

    def process_directory(
        self,
        directory: str,
        pattern: str,
        processor_func: Callable[[str], T],
        recursive: bool = True,
    ) -> list[FileResult]:
        """Process all files matching pattern in directory."""
        path = Path(directory)

        if recursive and "**" not in pattern:
            pattern = f"**/{pattern}"

        file_paths = [str(p) for p in path.glob(pattern) if p.is_file()]

        logger.info(f"Found {len(file_paths)} files matching '{pattern}' in {directory}")

        return self.process_files(file_paths, processor_func)

    def get_statistics(self, results: list[FileResult]) -> dict[str, Any]:
        """Calculate statistics from processing results."""
        if not results:
            return {"total": 0}

        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        total_time = sum(r.processing_time_ms for r in results)
        avg_time = total_time / len(results) if results else 0

        return {
            "total": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(results) if results else 0,
            "total_time_ms": total_time,
            "avg_time_ms": avg_time,
            "workers_used": self.optimizer.get_optimal_workers(),
        }

    def shutdown(self) -> None:
        """Shutdown the processor."""
        if self._executor:
            self._executor.shutdown(wait=True)
            self._executor = None


# Utility functions

def read_file_utf8(file_path: str) -> str:
    """Read file as UTF-8 text."""
    with open(file_path, encoding='utf-8', errors='ignore') as f:
        return f.read()


def parse_json_file(file_path: str) -> Any:
    """Parse JSON file."""
    import json
    with open(file_path, encoding='utf-8') as f:
        return json.load(f)


def compute_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
    """Compute file hash."""
    import hashlib

    hasher = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)

    return hasher.hexdigest()


# Singleton instance
_file_processor: ParallelFileProcessor | None = None


def get_file_processor(
    max_workers: int | None = None,
    chunk_size: int = 50,
) -> ParallelFileProcessor:
    """Get or create singleton file processor."""
    global _file_processor
    if _file_processor is None:
        _file_processor = ParallelFileProcessor(
            max_workers=max_workers,
            chunk_size=chunk_size,
        )
    return _file_processor


def shutdown_file_processor() -> None:
    """Shutdown singleton file processor."""
    global _file_processor
    if _file_processor:
        _file_processor.shutdown()
        _file_processor = None


__all__ = [
    "ParallelFileProcessor",
    "FileTask",
    "FileResult",
    "get_file_processor",
    "shutdown_file_processor",
    "read_file_utf8",
    "parse_json_file",
    "compute_file_hash",
]
