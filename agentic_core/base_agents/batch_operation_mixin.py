import asyncio
import logging
import time
from collections.abc import Coroutine
from typing import Any


class BatchOperationMixin:
    """
    Phase 2 observability Infrastructure: Batch Operations (Report 4.6).

    Enables safe parallelization and batch execution for high-volume tasks.
    Features:
    - Concurrency limiting via Semaphores
    - Parallel vs Sequential execution modes
    - Partial failure handling (atomic results)
    - Progress tracking and timing
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._bo_logger = logging.getLogger(self.__class__.__name__)

    async def batch_execute(
        self, tasks: list[Coroutine], max_workers: int = 5, sequential: bool = False
    ) -> list[Any]:
        # Hardened: overall batch timeout + better failure classification
        """
        Executes a collection of tasks with controlled concurrency.

        Args:
            tasks: A list of coroutines to execute.
            max_workers: Maximum number of concurrent tasks (semaphore limit).
            sequential: If True, ignores max_workers and runs one by one.

        Returns:
            List[Any]: A list of results in the same order as tasks.
        """
        if not tasks:
            return []

        start_time = time.time()
        total_tasks = len(tasks)
        self._bo_logger.info(f"Starting batch: {total_tasks} tasks (sequential={sequential})")

        if sequential:
            results = []
            for i, task in enumerate(tasks):
                try:
                    results.append(await task)
                except Exception as e:
                    self._bo_logger.error(f"Sequential task {i} failed: {e}")
                    results.append(e)
            return results

        # Parallel execution with Semaphore to prevent resource exhaustion
        semaphore = asyncio.Semaphore(max_workers)

        BATCH_TIMEOUT = 120.0
        TIMEOUT_PER_TASK = 45.0

        async def _sem_task(task_coro, index):
            async with semaphore:
                try:
                    return await asyncio.wait_for(task_coro, timeout=TIMEOUT_PER_TASK)
                except asyncio.TimeoutError:
                    self._bo_logger.error(f"Task {index} timed out individually")
                    return asyncio.TimeoutError(f"Task {index} timeout")
                except Exception as e:
                    self._bo_logger.error(f"Parallel task {index} failed: {e}")
                    return e

        # Wrap tasks with semaphore logic
        wrapped_tasks = [_sem_task(t, i) for i, t in enumerate(tasks)]

        # Execute all tasks and maintain order
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*wrapped_tasks, return_exceptions=True),
                timeout=BATCH_TIMEOUT,
            )
        except asyncio.TimeoutError:
            self._bo_logger.critical(f"Entire batch timed out after {BATCH_TIMEOUT}s")
            results = [asyncio.TimeoutError("Batch level timeout")] * len(tasks)

        duration = time.time() - start_time
        timeout_count = sum(1 for r in results if isinstance(r, asyncio.TimeoutError))
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        error_types = {type(r).__name__ for r in results if isinstance(r, Exception)}
        self._bo_logger.info(
            f"Batch completed: {success_count}/{total_tasks} successful "
            f"({timeout_count} timeouts) in {duration:.2f}s | "
            f"Error types: {', '.join(sorted(error_types)) or 'none'}"
        )

        return results
