# FILE: run_batch_v10_9.py
"""
Batch Runner — v10_9 Agentic Workflow (ENTERPRISE REFACTOR, META-ONLY)

This module is a META-layer utility ABOVE L1–L5. It provides:

    • High-throughput batch execution of v10_9 agentic workflows.
    • Concurrency control (basic backpressure).
    • Batch-level resilience (CircuitBreaker).
    • Batch-level aggregations (summary, counts, failures).
    • Optional meta-learning callback.
    • Fully asynchronous execution path + sync wrapper.
    • Strict agentic-layer separation and safety constraints.

Guarantees:
    ✔ NO L1 logic (planning)
    ✔ NO L2 logic (tools/LLMs/retrieval/drafting/etc.)
    ✔ NO L3 orchestration logic (DAG execution is in main_v10_9)
    ✔ NO L4 state mutation (only passes initial_state)
    ✔ NO L5 policy/safety decisions (handled inside main_v10_9)
    ✔ Pure META-level orchestration

This file is the correct layer for:
    • external service orchestration
    • CLI batch jobs
    • long-running background jobs
    • ETL-style batch transformations
    • offline meta-learning / signal extraction
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from main_v10_9 import run_workflow_v10_9


# ============================================================================
# 1. CIRCUIT BREAKER (Batch-Level Resilience)
# ============================================================================

@dataclass
class CircuitBreaker:
    """
    Batch-level circuit breaker.

    Behavior:
        • record_success(): resets failure count
        • record_failure(): increments failure count
        • check(): raises CircuitBreakerOpenError if breaker is "open"

    Trigger:
        - When failures >= failure_threshold

    This is NOT part of the agentic runtime (L1–L5).
    It is META-only resilience infrastructure.
    """

    failure_threshold: int = 3
    failure_count: int = field(default=0, init=False)
    is_open: bool = field(default=False, init=False)

    def record_success(self) -> None:
        self.failure_count = 0
        self.is_open = False

    def record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.is_open = True

    def check(self) -> None:
        if self.is_open:
            raise CircuitBreakerOpenError(
                f"Circuit breaker OPEN — {self.failure_count} failures"
            )


class CircuitBreakerOpenError(RuntimeError):
    """Raised when the batch-level circuit breaker is open."""
    pass


# ============================================================================
# 2. BATCH FEEDBACK AGGREGATOR
# ============================================================================

@dataclass
class BatchFeedbackAggregator:
    """
    Aggregates results across a batch.

    Fields:
        • results: list of successful workflow outputs
        • failed:  # of jobs that raised exceptions at batch level
        • breaker_open: True if breaker opened during processing

    Derived properties:
        • total_jobs: results + failed
        • successful: len(results)
    """

    results: List[Dict[str, Any]] = field(default_factory=list)
    failed: int = 0
    breaker_open: bool = False

    def add_result(self, result: Dict[str, Any]) -> None:
        self.results.append(result)

    def add_failure(self) -> None:
        self.failed += 1

    @property
    def total_jobs(self) -> int:
        return len(self.results) + self.failed

    @property
    def successful(self) -> int:
        return len(self.results)

    def summary(self) -> Dict[str, Any]:
        return {
            "total_jobs": self.total_jobs,
            "successful": self.successful,
            "failed": self.failed,
            "breaker_open": self.breaker_open,
        }


# ============================================================================
# 3. ASYNC BATCH EXECUTION API
# ============================================================================

async def run_batch_async(
    job_inputs: List[Dict[str, Any]],
    *,
    max_concurrency: Optional[int] = None,
    failure_threshold: int = 3,
    max_jobs: Optional[int] = None,
    meta_learning_callback: Optional[Callable[[List[Dict[str, Any]]], Any]] = None,
    compat_mode: Optional[str] = None,
    debug_mode: bool = False,
) -> Dict[str, Any]:
    """
    Execute a batch of v10_9 agentic workflows asynchronously.

    Args:
        job_inputs:
            List of initial_state dicts for run_workflow_v10_9

        max_concurrency:
            Maximum concurrent jobs (optional). If None → no limit.

        failure_threshold:
            # of failures allowed before the CircuitBreaker trips.

        max_jobs:
            Optional cap on how many jobs to process from job_inputs.

        meta_learning_callback:
            Optional callable that receives aggregator.results after batch is complete.
            This is strictly META-level; failures must NOT affect the batch.

        compat_mode:
            Passed through to run_workflow_v10_9

        debug_mode:
            Enables debug metadata on run_workflow_v10_9

    Returns:
        {
            "jobs": <list of per-job workflow outputs>,
            "batch_summary": {...}
        }
    """

    # No jobs → trivial batch
    if not job_inputs:
        return {
            "jobs": [],
            "batch_summary": {
                "total_jobs": 0,
                "successful": 0,
                "failed": 0,
                "breaker_open": False,
            },
        }

    # Apply job cap via max_jobs
    if max_jobs is not None and max_jobs >= 0:
        job_inputs = job_inputs[: max_jobs]

    aggregator = BatchFeedbackAggregator()
    breaker = CircuitBreaker(failure_threshold=failure_threshold)

    # Establish concurrency semaphore
    semaphore = (
        asyncio.Semaphore(max_concurrency)
        if max_concurrency is not None and max_concurrency > 0
        else None
    )

    async def _run_single_job(initial_state: Dict[str, Any]) -> None:
        """Execute one job with circuit-breaker protection + concurrency control."""
        try:
            breaker.check()
        except CircuitBreakerOpenError:
            aggregator.breaker_open = True
            return

        try:
            if semaphore:
                async with semaphore:
                    result = await run_workflow_v10_9(
                        initial_state,
                        compat_mode=compat_mode,
                        debug_mode=debug_mode,
                        stream_callback=None,
                    )
            else:
                result = await run_workflow_v10_9(
                    initial_state,
                    compat_mode=compat_mode,
                    debug_mode=debug_mode,
                    stream_callback=None,
                )

            aggregator.add_result(result)
            breaker.record_success()

        except Exception:
            # Any job-level exception counts as a batch-level failure
            aggregator.add_failure()
            breaker.record_failure()

    # Schedule jobs
    tasks: List[asyncio.Task] = []
    for job_state in job_inputs:
        if breaker.is_open:
            aggregator.breaker_open = True
            break
        tasks.append(asyncio.create_task(_run_single_job(job_state)))

    if tasks:
        await asyncio.gather(*tasks, return_exceptions=False)

    # Optional meta-learning callback (never allowed to break batch)
    if meta_learning_callback:
        try:
            meta_learning_callback(aggregator.results)
        except Exception:
            pass  # must not break batch

    return {
        "jobs": aggregator.results,
        "batch_summary": aggregator.summary(),
    }


# ============================================================================
# 4. SYNC WRAPPER
# ============================================================================

def run_batch_sync(
    job_inputs: List[Dict[str, Any]],
    *,
    max_concurrency: Optional[int] = None,
    failure_threshold: int = 3,
    max_jobs: Optional[int] = None,
    meta_learning_callback: Optional[Callable[[List[Dict[str, Any]]], Any]] = None,
    compat_mode: Optional[str] = None,
    debug_mode: bool = False,
) -> Dict[str, Any]:
    """
    Synchronous wrapper around run_batch_async — for CLI, scripts,
    notebooks, or local developer runs.
    """
    return asyncio.run(
        run_batch_async(
            job_inputs,
            max_concurrency=max_concurrency,
            failure_threshold=failure_threshold,
            max_jobs=max_jobs,
            meta_learning_callback=meta_learning_callback,
            compat_mode=compat_mode,
            debug_mode=debug_mode,
        )
    )


# ============================================================================
# 5. OPTIONAL CLI ENTRYPOINT
# ============================================================================

if __name__ == "__main__":
    # Example smoke-test batch
    example_jobs = [
        {
            "objective": "draft a concise professional summary",
            "messages": [{"role": "user", "content": "Summarize my profile."}],
        },
        {
            "objective": "qa validate this summary",
            "messages": [{"role": "user", "content": "Check quality of this text."}],
            "draft_result": {
                "draft": ["This is a clean, logically structured sentence."]
            },
        },
    ]

    def _example_meta_callback(results: List[Dict[str, Any]]) -> None:
        print(f"[META LEARNING] Completed {len(results)} workflow results.")

    print("=== Running v10_9 Batch (example) ===")
    result = run_batch_sync(
        example_jobs,
        max_concurrency=2,
        failure_threshold=2,
        meta_learning_callback=_example_meta_callback,
        debug_mode=True,
    )
    print("Batch Summary:", result["batch_summary"])
    print("Jobs:", result["jobs"])
