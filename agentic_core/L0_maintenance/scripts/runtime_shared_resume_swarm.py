"""Resume Swarm - Multi-process resume generation for CPU-intensive tasks.

Utilizes multiprocessing.Pool to distribute CPU-intensive resume generation tasks
(PDF generation, heavy parsing, formatting) across multiple worker processes.
Optimized for i7-10750H (6 cores/12 threads) with 32GB RAM.
"""

import logging
import multiprocessing
import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Protocol
from typing import Any, Optional, Protocol, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class ResumeResult:
    """Result from a single resume generation task."""
    job_id: str
    status: str  # "success", "failed"
    result: Optional[Any] = None
    error: Optional[str] = None
    worker_pid: int = 0
    execution_time: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class SwarmMetrics:
    """Metrics for resume swarm execution."""
    total_jobs: int = 0
    successful: int = 0
    failed: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    max_execution_time: float = 0.0
    min_execution_time: float = float('inf')
    throughput: float = 0.0  # Jobs per second
    start_time: Optional[float] = None
    end_time: Optional[float] = None


def _worker_generate_resume(payload: Dict) -> ResumeResult:
    """Worker function for resume generation (must be at module level for pickling).

    This function runs in a separate process and handles CPU-intensive tasks:
    - PDF generation
    - Heavy text parsing
    - Document formatting
    - Template rendering

    Args:
        payload: Dictionary containing job data and configuration

    Returns:
        ResumeResult with generation status and result/error
    """
    job_id = payload.get('job_id', 'unknown')
    start_time = time.time()
    worker_pid = os.getpid()

    try:
        logger.debug(f"Worker {worker_pid} processing job {job_id}")

        # Extract payload data
        job_description = payload.get('job_description', '')
        payload.get('user_profile', {})
        output_format = payload.get('output_format', 'pdf')

        # Simulate or call actual heavy generation logic
        # Option 1: Import and call real resume generator
        # from apps_rg.resume_engine import generate_single_resume
        # result = generate_single_resume(payload)

        # Option 2: Simulate CPU-intensive work (for testing)
        # Simulate PDF generation, parsing, etc.
        time.sleep(0.5)  # Simulate work

        result = {
            "job_id": job_id,
            "status": "completed",
            "output_path": f"/output/resume_{job_id}.{output_format}",
            "worker_pid": worker_pid,
            "job_description": job_description[:50] + "..." if len(job_description) > 50 else job_description
        }

        execution_time = time.time() - start_time

        logger.info(
            f"Worker {worker_pid} completed job {job_id} "
            f"in {execution_time:.2f}s"
        )

        return ResumeResult(
            job_id=job_id,
            status="success",
            result=result,
            worker_pid=worker_pid,
            execution_time=execution_time
        )

    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Worker {worker_pid} failed job {job_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)

        return ResumeResult(
            job_id=job_id,
            status="failed",
            error=error_msg,
            worker_pid=worker_pid,
            execution_time=execution_time
        )


class ResumeSwarm:
    """Multi-process resume generation swarm.

    Distributes CPU-intensive resume generation tasks across multiple worker
    processes to maximize throughput on multi-core systems.
    """

    def __init__(
        self,
        num_workers: int = 6,
        enable_metrics: bool = True,
        worker_function: Optional[Callable] = None
    ):
        """Initialize the ResumeSwarm.

        Args:
            num_workers: Number of worker processes (default: 6 for i7-10750H)
            enable_metrics: Enable metrics collection (default: True)
            worker_function: Custom worker function (default: _worker_generate_resume)
        """
        self.num_workers = num_workers
        self.enable_metrics = enable_metrics
        self.worker_function = worker_function or _worker_generate_resume
        self.metrics = SwarmMetrics()

        logger.info(
            f"Initialized ResumeSwarm: "
            f"num_workers={num_workers}, "
            f"available_cpus={multiprocessing.cpu_count()}"
        )

    def generate_batch(
        self,
        job_payloads: List[Dict[str, Any]],
        chunksize: Optional[int] = None
    ) -> List[ResumeResult]:
        """Distribute resume generation tasks across worker processes.

        Args:
            job_payloads: List of job dictionaries to process
            chunksize: Number of jobs per worker chunk (default: auto-calculated)

        Returns:
            List of ResumeResult objects

        Example:
            >>> swarm = ResumeSwarm(num_workers=6)
            >>> jobs = [
            ...     {"job_id": "1", "job_description": "Senior Python Dev"},
            ...     {"job_id": "2", "job_description": "Data Scientist"},
            ... ]
            >>> results = swarm.generate_batch(jobs)
        """
        if not job_payloads:
            logger.warning("Empty job_payloads provided to generate_batch")
            return []

        # Initialize metrics
        if self.enable_metrics:
            self.metrics = SwarmMetrics(
                total_jobs=len(job_payloads),
                start_time=time.time()
            )

        logger.info(
            f"Starting batch generation: {len(job_payloads)} jobs "
            f"across {self.num_workers} workers"
        )

        # Calculate optimal chunksize if not provided
        if chunksize is None:
            chunksize = max(1, len(job_payloads) // (self.num_workers * 4))

        try:
            with multiprocessing.Pool(processes=self.num_workers) as pool:
                # Map inputs to workers
                results = pool.map(
                    self.worker_function,
                    job_payloads,
                    chunksize=chunksize
                )

            # Update metrics
            if self.enable_metrics:
                self._update_metrics(results)

            logger.info(
                f"Batch generation complete: "
                f"{self.metrics.successful}/{self.metrics.total_jobs} successful, "
                f"{self.metrics.failed} failed"
            )

            return results

        except Exception as e:
            logger.error(f"Batch generation failed: {e}", exc_info=True)
            raise

    def generate_batch_async(
        self,
        job_payloads: List[Dict[str, Any]],
        callback: Optional[Callable[[ResumeResult], None]] = None,
        chunksize: Optional[int] = None
    ) -> List[ResumeResult]:
        """Asynchronous batch generation with optional callback.

        Args:
            job_payloads: List of job dictionaries to process
            callback: Optional callback function called for each completed job
            chunksize: Number of jobs per worker chunk

        Returns:
            List of ResumeResult objects
        """
        if not job_payloads:
            return []

        # Initialize metrics
        if self.enable_metrics:
            self.metrics = SwarmMetrics(
                total_jobs=len(job_payloads),
                start_time=time.time()
            )

        logger.info(
            f"Starting async batch generation: {len(job_payloads)} jobs"
        )

        if chunksize is None:
            chunksize = max(1, len(job_payloads) // (self.num_workers * 4))

        try:
            with multiprocessing.Pool(processes=self.num_workers) as pool:
                # Use map_async for non-blocking execution
                async_result = pool.map_async(
                    self.worker_function,
                    job_payloads,
                    chunksize=chunksize,
                    callback=callback
                )

                # Wait for completion
                results = async_result.get()

            # Update metrics
            if self.enable_metrics:
                self._update_metrics(results)

            return results

        except Exception as e:
            logger.error(f"Async batch generation failed: {e}", exc_info=True)
            raise

    def generate_streaming(
        self,
        job_payloads: List[Dict[str, Any]],
        chunksize: int = 1
    ):
        """Stream results as they complete (generator).

        Args:
            job_payloads: List of job dictionaries to process
            chunksize: Number of jobs per worker chunk

        Yields:
            ResumeResult objects as they complete

        Example:
            >>> swarm = ResumeSwarm(num_workers=6)
            >>> for result in swarm.generate_streaming(jobs):
            ...     print(f"Completed: {result.job_id}")
        """
        if not job_payloads:
            return

        # Initialize metrics
        if self.enable_metrics:
            self.metrics = SwarmMetrics(
                total_jobs=len(job_payloads),
                start_time=time.time()
            )

        logger.info(
            f"Starting streaming generation: {len(job_payloads)} jobs"
        )

        try:
            with multiprocessing.Pool(processes=self.num_workers) as pool:
                # Use imap for streaming results
                for result in pool.imap(
                    self.worker_function,
                    job_payloads,
                    chunksize=chunksize
                ):
                    yield result

            # Update metrics after all results
            if self.enable_metrics:
                self.metrics.end_time = time.time()

        except Exception as e:
            logger.error(f"Streaming generation failed: {e}", exc_info=True)
            raise

    def _update_metrics(self, results: List[ResumeResult]) -> None:
        """Update swarm metrics based on results.

        Args:
            results: List of ResumeResult objects
        """
        self.metrics.end_time = time.time()

        for result in results:
            if result.status == "success":
                self.metrics.successful += 1
            elif result.status == "failed":
                self.metrics.failed += 1

            # Update execution time stats
            self.metrics.total_execution_time += result.execution_time
            self.metrics.max_execution_time = max(
                self.metrics.max_execution_time,
                result.execution_time
            )
            self.metrics.min_execution_time = min(
                self.metrics.min_execution_time,
                result.execution_time
            )

        # Calculate average and throughput
        if self.metrics.total_jobs > 0:
            self.metrics.average_execution_time = (
                self.metrics.total_execution_time / self.metrics.total_jobs
            )

            wall_time = self.metrics.end_time - self.metrics.start_time
            if wall_time > 0:
                self.metrics.throughput = self.metrics.total_jobs / wall_time

    def get_metrics(self) -> SwarmMetrics:
        """Get current swarm metrics.

        Returns:
            SwarmMetrics object with execution statistics
        """
        return self.metrics

    def get_success_rate(self) -> float:
        """Get success rate as a percentage.

        Returns:
            Success rate (0.0 to 100.0)
        """
        if self.metrics.total_jobs == 0:
            return 0.0
        return (self.metrics.successful / self.metrics.total_jobs) * 100

    def reset_metrics(self) -> None:
        """Reset metrics for a new batch."""
        self.metrics = SwarmMetrics()


# Factory function
def create_resume_swarm(
    num_workers: int = 6,
    enable_metrics: bool = True,
    worker_function: Optional[Callable] = None
) -> ResumeSwarm:
    """Create a ResumeSwarm instance.

    Args:
        num_workers: Number of worker processes
        enable_metrics: Enable metrics collection
        worker_function: Custom worker function

    Returns:
        Configured ResumeSwarm instance
    """
    return ResumeSwarm(
        num_workers=num_workers,
        enable_metrics=enable_metrics,
        worker_function=worker_function
    )