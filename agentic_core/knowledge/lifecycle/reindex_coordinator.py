"""Reindex Coordinator.

Coordinates batch reindexing operations, manages index consistency,
and handles background reindexing jobs for the ingestion pipeline.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import Any, Callable

from agentic_core.knowledge.canonical.canonical_store import CanonicalStore
from agentic_core.knowledge.ingestion.intake_clerk import IntakeClerk
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)
from tqdm import tqdm

log = logging.getLogger(__name__)


@dataclass
class ReindexJob:
    """A reindexing job."""

    job_id: str
    file_paths: list[str]
    status: str = "pending"  # pending, running, completed, failed
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    completed_at: float | None = None
    results: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    progress: float = 0.0


@dataclass
class ReindexResult:
    """Result of reindexing a single file."""

    file_path: str
    success: bool
    unit_id: str | None = None
    error_message: str | None = None
    processing_time_ms: float = 0.0


class ReindexCoordinator:
    """Coordinates batch reindexing operations.

    The ReindexCoordinator manages the reindexing workflow for multiple
    files, ensuring index consistency and supporting both synchronous
    and asynchronous reindexing operations.
    """

    def __init__(
        self,
        canonical_store: CanonicalStore | None = None,
        intake_clerk: IntakeClerk | None = None,
        max_workers: int = 4,
    ):
        """Initialize the reindex coordinator.

        Args:
            canonical_store: Store for canonical units
            intake_clerk: Intake clerk for document processing
            max_workers: Maximum number of parallel workers
        """
        self.store = canonical_store or CanonicalStore()
        self.intake_clerk = intake_clerk or IntakeClerk()
        self.max_workers = max_workers

        # Job tracking
        self._jobs: dict[str, ReindexJob] = {}
        self._jobs_lock = Lock()

        # Callbacks
        self._on_complete_callbacks: list[Callable[[ReindexJob], None]] = []
        self._on_progress_callbacks: list[Callable[[str, float], None]] = []

        log.info(f"ReindexCoordinator initialized (max_workers={max_workers})")

    def submit_job(
        self,
        file_paths: list[str | Path],
        sync: bool = False,
    ) -> ReindexJob:
        """Submit a reindexing job.

        Args:
            file_paths: List of file paths to reindex
            sync: If True, wait for completion; if False, run async

        Returns:
            ReindexJob tracking the operation
        """
        job_id = f"reindex_{int(time.time())}_{len(file_paths)}"

        job = ReindexJob(
            job_id=job_id,
            file_paths=[str(p) for p in file_paths],
        )

        with self._jobs_lock:
            self._jobs[job_id] = job

        if sync:
            self._execute_job(job)
        else:
            # Run async
            import threading

            thread = threading.Thread(target=self._execute_job, args=(job,))
            thread.daemon = True
            thread.start()

        log.info(f"Submitted reindex job {job_id} ({len(file_paths)} files, sync={sync})")
        return job

    def get_job(self, job_id: str) -> ReindexJob | None:
        """Get a job by ID.

        Args:
            job_id: Job ID to lookup

        Returns:
            ReindexJob if found, None otherwise
        """
        with self._jobs_lock:
            return self._jobs.get(job_id)

    def get_all_jobs(self) -> list[ReindexJob]:
        """Get all jobs.

        Returns:
            List of all ReindexJob objects
        """
        with self._jobs_lock:
            return list(self._jobs.values())

    def reindex_file(self, file_path: str | Path) -> ReindexResult:
        """Reindex a single file.

        Args:
            file_path: Path to the file to reindex

        Returns:
            ReindexResult with outcome
        """
        trace_id = f"reindex_{Path(file_path).name}"
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L4_STATE,
            "ReindexCoordinator.reindex_file",
        )

        start_time = time.time()

        try:
            # Use intake clerk to process the file
            ingestion_result = self.intake_clerk.ingest_document(file_path)

            processing_time = (time.time() - start_time) * 1000

            if ingestion_result.success:
                _emit_records_telemetry_event(
                    "reindex",
                    f"success_{Path(file_path).name}",
                )

                return ReindexResult(
                    file_path=str(file_path),
                    success=True,
                    unit_id=ingestion_result.metadata.checksum if ingestion_result.metadata else None,
                    processing_time_ms=processing_time,
                )
            else:
                _emit_records_telemetry_event(
                    "reindex",
                    f"failed_{Path(file_path).name}",
                )

                return ReindexResult(
                    file_path=str(file_path),
                    success=False,
                    error_message=ingestion_result.error_message,
                    processing_time_ms=processing_time,
                )

        except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as e:
            processing_time = (time.time() - start_time) * 1000
            log.error(f"Error reindexing {file_path}: {e}")

            return ReindexResult(
                file_path=str(file_path),
                success=False,
                error_message=str(e),
                processing_time_ms=processing_time,
            )

    def reindex_batch(
        self,
        file_paths: list[str | Path],
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> list[ReindexResult]:
        """Reindex multiple files in batch.

        Args:
            file_paths: List of file paths to reindex
            progress_callback: Optional callback(current, total)

        Returns:
            List of ReindexResult for all files
        """
        trace_id = f"batch_{int(time.time())}"
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L4_STATE,
            "ReindexCoordinator.reindex_batch",
        )

        results = []
        total = len(file_paths)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_path = {executor.submit(self.reindex_file, path): path for path in file_paths}

            # Collect results as they complete
            completed = 0
            for future in tqdm(as_completed(future_to_path), desc="Processing", unit="item"):
                path = future_to_path[future]
                try:
                    result = future.result()
                    results.append(result)
                except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as e:
                    results.append(
                        ReindexResult(
                            file_path=str(path),
                            success=False,
                            error_message=str(e),
                        )
                    )

                completed += 1
                if progress_callback:
                    progress_callback(completed, total)

                self._notify_progress(trace_id, completed / total)

        success_count = sum(1 for r in results if r.success)
        log.info(f"Batch reindex complete: {success_count}/{total} succeeded")

        return results

    def _execute_job(self, job: ReindexJob) -> None:
        """Execute a reindex job."""
        job.status = "running"
        job.started_at = time.time()

        log.info(f"Executing reindex job {job.job_id} ({len(job.file_paths)} files)")

        def progress_callback(current: int, total: int):
            job.progress = current / total
            self._notify_progress(job.job_id, job.progress)

        results = self.reindex_batch(job.file_paths, progress_callback)

        # Update job
        job.results = [
            {
                "file_path": r.file_path,
                "success": r.success,
                "unit_id": r.unit_id,
                "error_message": r.error_message,
            }
            for r in results
        ]
        job.errors = [r.error_message for r in results if not r.success and r.error_message]
        job.completed_at = time.time()
        job.status = "completed" if all(r.success for r in results) else "failed"
        job.progress = 1.0

        # Notify completion
        self._notify_complete(job)

        log.info(f"Reindex job {job.job_id} completed with status {job.status}")

    def on_complete(self, callback: Callable[[ReindexJob], None]) -> None:
        """Register a callback for job completion.

        Args:
            callback: Function to call when job completes
        """
        self._on_complete_callbacks.append(callback)

    def on_progress(self, callback: Callable[[str, float], None]) -> None:
        """Register a callback for job progress updates.

        Args:
            callback: Function(job_id, progress) to call on progress
        """
        self._on_progress_callbacks.append(callback)

    def _notify_complete(self, job: ReindexJob) -> None:
        """Notify completion callbacks."""
        for callback in self._on_complete_callbacks:
            try:
                callback(job)
            except (AttributeError, RuntimeError, TypeError, ValueError) as e:
                log.warning(f"Complete callback error: {e}")

    def _notify_progress(self, job_id: str, progress: float) -> None:
        """Notify progress callbacks."""
        for callback in self._on_progress_callbacks:
            try:
                callback(job_id, progress)
            except (AttributeError, RuntimeError, TypeError, ValueError) as e:
                log.warning(f"Progress callback error: {e}")


# Global instance
_global_coordinator: ReindexCoordinator | None = None


def get_reindex_coordinator() -> ReindexCoordinator:
    """Get or create the global reindex coordinator."""
    global _global_coordinator
    if _global_coordinator is None:
        _global_coordinator = ReindexCoordinator()
    return _global_coordinator
