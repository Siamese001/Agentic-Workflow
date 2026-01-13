import asyncio
import logging
import time
from typing import Any, List, Dict, Callable, Coroutine, Optional

class BatchOperationMixin:
    """
    Phase 2 Observability Infrastructure: Batch Operations (Report 4.6).
    
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

    async def batch_execute(self, 
                            tasks: List[Coroutine], 
                            max_workers: int = 5, 
                            sequential: bool = False) -> List[Any]:
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

        async def _sem_task(task_coro, index):
            async with semaphore:
                try:
                    return await task_coro
                except Exception as e:
                    self._bo_logger.error(f"Parallel task {index} failed: {e}")
                    return e

        # Wrap tasks with semaphore logic
        wrapped_tasks = [_sem_task(t, i) for i, t in enumerate(tasks)]
        
        # Execute all tasks and maintain order
        results = await asyncio.gather(*wrapped_tasks)
        
        duration = time.time() - start_time
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        self._bo_logger.info(
            f"Batch completed: {success_count}/{total_tasks} successful in {duration:.2f}s"
        )
        
        return results
