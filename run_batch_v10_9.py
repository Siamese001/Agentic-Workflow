# FILE: run_batch_v10_9.py
"""
Batch Runner — v10_9 Agentic Workflow (ENTERPRISE REFACTOR)

This module provides an enterprise-grade, architecture-compliant batch
runner for the v10_9 agentic workflow.

It lives strictly ABOVE L1–L5 as a META-UTILITY and therefore:

    • DOES NOT perform cognition (no L1 planning).
    • DOES NOT execute tools/LLMs directly (no L2 logic).
    • DOES NOT orchestrate phases/DAGs (no L3 internals).
    • DOES NOT mutate state (no L4 StateAdapter usage).
    • DOES NOT make safety/policy decisions (no L5 logic).

Instead, it:

    • Invokes run_workflow_v10_9(initial_state) per job.
    • Applies batch-level resilience via a CircuitBreaker.
    • Limits concurrency (backpressure).
    • Aggregates per-job results into a batch summary.
    • Optionally calls a meta-learning callback after batch completion.

This design satisfies the Agentic Ecosystem constraints while providing
high-level batch orchestration.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from main_v10_9 import run_workflow_v10_9


# ============================================================================
# 1. CIRCUIT BREAKER (BATCH-LEVEL RESILIENCE)
# ============================================================================


@dataclass
class CircuitBreaker:
    """
    Simple batch-level circuit breaker for resilience.

    This is deliberately batch-scoped and NOT part of L1–L5. It protects
    infrastructure by halting additional job executions when too many
    failures occur in a single batch.

    Semantics:
        • record_success() resets failure count.
        • record_failure() increments failure count.
        • check() raises CircuitBreakerOpenError when open.
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
                f"Circuit breaker OPEN after {self.failure_count} failures"
            )


class CircuitBreakerOpenError(RuntimeError):
    """Raised when the batch-level circuit breaker is open."""


# ============================================================================
# 2. BATCH FEEDBACK AGGREGATOR
# ============================================================================


@dataclass
class BatchFeedbackAggregator:
    """
    Aggregates results across a batch of workflow runs.

    Fields:
        • results: list of per-job results (full run_workflow_v10_9 outputs)
        • failed: count of jobs that raised exceptions at the batch level
        • breaker_open: whether the CircuitBreaker opened during the batch

    Derived properties:
        • total_jobs: # results + # failures
        • successful: # results (jobs that completed, regardless of phase)
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
        # All completed runs are counted as "successful" at the batch level;
        # domain-specific success criteria (e.g., phase == COMPLETE, safety
        # passed) are up to the caller.
        return len(self.results)

    def summary(self) -> Dict[str, Any]:
        return {
            "total_jobs": self.total_jobs,
            "successful": self.successful,
            "failed": self.failed,
            "breaker_open": self.breaker_open,
        }


# ============================================================================
# 3. BATCH RUNNER APIs
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
    Execute a batch of v10_9 workflows asynchronously.

    Args:
        job_inputs:
            list[dict]; each dict is an initial_state to pass to
            run_workflow_v10_9.

        max_concurrency:
            Optional limit on concurrent tasks; if None, all jobs are
            launched concurrently. This provides basic backpressure.

        failure_threshold:
            Number of failures allowed before the batch-level
            CircuitBreaker opens and halts further job processing.

        max_jobs:
            Optional cap on the number of jobs to process from job_inputs.
            If provided, only the first max_jobs entries are processed.
            This is an additional safety/backpressure knob.

        meta_learning_callback:
            Optional callable invoked AFTER all jobs complete (or the
            breaker opens). It receives the list of per-job results
            (aggregator.results). Typical usage: run a meta-learning
            pass over feedback/preference logs.

        compat_mode:
            Optional compat flag forwarded to run_workflow_v10_9. It is
            stored in state["metadata"]["compat_mode"] and may adjust
            behavior of underlying agents.

        debug_mode:
            When True, forwarded to run_workflow_v10_9 to enable extra
            debug metadata in the per-job state.

    Returns:
        dict:
            {
                "jobs": [... per-job results ...],
                "batch_summary": {
                    "total_jobs": int,
                    "successful": int,
                    "failed": int,
                    "breaker_open": bool,
                },
            }
    """
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

    # Apply max_jobs backpressure if requested
    if max_jobs is not None and max_jobs >= 0:
        job_inputs = job_inputs[: max_jobs]

    aggregator = BatchFeedbackAggregator()
    breaker = CircuitBreaker(failure_threshold=failure_threshold)

    semaphore = (
        asyncio.Semaphore(max_concurrency)
        if max_concurrency is not None and max_concurrency > 0
        else None
    )

    async def _run_single(initial_state: Dict[str, Any]) -> None:
        # Check breaker BEFORE starting the job
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
            # Batch-level failure; record and update breaker.
            aggregator.add_failure()
            breaker.record_failure()

    # Schedule jobs with circuit-breaker awareness
    tasks: List[asyncio.Task[None]] = []
    for job in job_inputs:
        if breaker.is_open:
            aggregator.breaker_open = True
            break
        tasks.append(asyncio.create_task(_run_single(job)))

    if tasks:
        await asyncio.gather(*tasks, return_exceptions=False)

    # Optional meta-learning hook (above L1–L5, non-critical path)
    if meta_learning_callback is not None:
        try:
            meta_learning_callback(aggregator.results)
        except Exception:
            # Meta-learning failures must never break the batch itself.
            pass

    return {
        "jobs": aggregator.results,
        "batch_summary": aggregator.summary(),
    }


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
    Synchronous wrapper around run_batch_async for convenient use in
    CLI scripts or non-async contexts.

    This function is META-only and must not be called from inside the
    core L1–L5 runtime loops (it is for outer service/CLI boundaries).
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
# 4. OPTIONAL CLI ENTRYPOINT
# ============================================================================

if __name__ == "__main__":
    # Example: simple inline batch for demonstration / smoke tests.
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

    def _example_meta_learning_callback(results: List[Dict[str, Any]]) -> None:
        # Minimal stub: in a real system this would trigger a meta-learning pass.
        print(f"[meta-learning] Received {len(results)} completed results.")

    result = run_batch_sync(
        example_jobs,
        max_concurrency=2,
        failure_threshold=2,
        meta_learning_callback=_example_meta_learning_callback,
        compat_mode=None,
        debug_mode=True,
    )
    print("=== v10_9 Batch Runner Output ===")
    print("Batch Summary:", result["batch_summary"])
    print("Jobs:", result["jobs"])
