# FILE: 10_10/run_batch_v10_10.py
"""
Batch Runner — v10_10 Agentic Workflow (META-LAYER)
===================================================

This is the v10_10 refactor of the v10_9 batch runner. It preserves the
META-only orchestration capabilities:

    • High-throughput batch execution of v10_10 workflows
    • Concurrency control (async semaphore)
    • CircuitBreaker for batch resilience
    • Batch-level result aggregation
    • Optional meta-learning callback hook
    • Async + sync entrypoints
    • ZERO L1–L5 logic inside this file

Important:
    ✔ No planning logic (L1)
    ✔ No execution logic (L2)
    ✔ No DAG logic (L3)
    ✔ No state mutation (L4)
    ✔ No safety policy decisions (L5)

This module sits *entirely above* the agentic runtime.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from main_v10_10 import run_workflow_v10_10


# ======================================================================
# 1. Circuit Breaker
# ======================================================================

@dataclass
class CircuitBreaker:
    """
    Batch-level circuit breaker.

    Trigger:
        • When failures >= failure_threshold → breaker opens

    Behaviors:
        record_success()
        record_failure()
        check() → raises CircuitBreakerOpenError
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
    """Raised when circuit breaker is open."""
    pass


# ======================================================================
# 2. Aggregator
# ======================================================================

@dataclass
class BatchFeedbackAggregator:
    """
    Aggregates results across a batch.

    Fields:
        results     — list of successful workflow outputs
        failed      — number of failed jobs
        breaker_open — whether breaker opened

    Derived:
        total_jobs
        successful
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


# ======================================================================
# 3. ASYNC Batch Runner
# ======================================================================

async def run_batch_async_v10_10(
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
    High-level async batch execution for v10_10 workflows.

    Each job_input is a v10_9-style initial_state dict, passed to
    run_workflow_v10_10() which handles translation to v10_10 typed inputs.
    """

    # Edge case: no jobs
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

    # Apply max_jobs cap
    if max_jobs is not None and max_jobs >= 0:
        job_inputs = job_inputs[: max_jobs]

    aggregator = BatchFeedbackAggregator()
    breaker = CircuitBreaker(failure_threshold=failure_threshold)

    # Concurrency (None → unlimited)
    semaphore = (
        asyncio.Semaphore(max_concurrency)
        if max_concurrency is not None and max_concurrency > 0
        else None
    )

    # -------------------------
    # Inner job runner
    # -------------------------
    async def _run_single_job(initial_state: Dict[str, Any]) -> None:
        try:
            breaker.check()
        except CircuitBreakerOpenError:
            aggregator.breaker_open = True
            return

        try:
            if semaphore:
                async with semaphore:
                    result = await run_workflow_v10_10(
                        initial_state,
                        compat_mode=compat_mode,
                        debug_mode=debug_mode,
                        stream_callback=None,
                    )
            else:
                result = await run_workflow_v10_10(
                    initial_state,
                    compat_mode=compat_mode,
                    debug_mode=debug_mode,
                    stream_callback=None,
                )

            aggregator.add_result(result)
            breaker.record_success()

        except Exception:
            aggregator.add_failure()
            breaker.record_failure()

    # -------------------------
    # Schedule batch jobs
    # -------------------------
    tasks: List[asyncio.Task] = []
    for job_state in job_inputs:
        if breaker.is_open:
            aggregator.breaker_open = True
            break
        tasks.append(asyncio.create_task(_run_single_job(job_state)))

    if tasks:
        await asyncio.gather(*tasks, return_exceptions=False)

    # META-learning hook (cannot break batch)
    if meta_learning_callback:
        try:
            meta_learning_callback(aggregator.results)
        except Exception:
            pass

    return {
        "jobs": aggregator.results,
        "batch_summary": aggregator.summary(),
    }


# ======================================================================
# 4. SYNC Wrapper
# ======================================================================

def run_batch_sync_v10_10(
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
    Synchronous wrapper around run_batch_async_v10_10().
    Suitable for CLI, scripts, notebooks.
    """
    return asyncio.run(
        run_batch_async_v10_10(
            job_inputs,
            max_concurrency=max_concurrency,
            failure_threshold=failure_threshold,
            max_jobs=max_jobs,
            meta_learning_callback=meta_learning_callback,
            compat_mode=compat_mode,
            debug_mode=debug_mode,
        )
    )


# ======================================================================
# 5. Optional CLI
# ======================================================================

if __name__ == "__main__":
    # Minimal smoke test
    example_jobs = [
        {
            "objective": "draft a concise summary",
            "messages": [{"role": "user", "content": "Summarize my background."}],
        },
        {
            "objective": "test QA",
            "messages": [{"role": "user", "content": "Check this text."}],
        },
    ]

    def _callback(results: List[Dict[str, Any]]) -> None:
        print(f"[META CALLBACK] {len(results)} results processed.")

    out = run_batch_sync_v10_10(
        example_jobs,
        max_concurrency=2,
        failure_threshold=2,
        meta_learning_callback=_callback,
        debug_mode=True,
    )

    print("=== v10_10 Batch Summary ===")
    print(out["batch_summary"])
