# FILE: run_batch_v10_10.py
"""
Unified Batch Runner (v10_10) — HIGH THROUGHPUT ORCHESTRATION (REFACTORED)

This module acts as the "Factory Floor" (Pillar 11).
It manages parallel execution, concurrency limits, and resilience.

Responsibilities:
    1. Concurrency Control: Semaphore-based throttling.
    2. Resilience: Circuit Breaker pattern (Pillar 8).
    3. Aggregation: Compiles `BatchResult` from individual `WorkflowState`s.

Refactor Highlights (v10_10):
    • Typed Aggregation: Returns Pydantic `BatchResult` models.
    • Engine Integration: Uses the `AgenticWorkflow` class directly.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional
from pydantic import Field

from models import (
    AgenticBaseModel,
    WorkflowState,
    WorkflowPhase
)
from main_v10_10 import AgenticWorkflow
from runtime_utils import record_event

# =============================================================================
# DATA MODELS (Batch Specific)
# =============================================================================

class BatchSummary(AgenticBaseModel):
    total_jobs: int = 0
    successful: int = 0
    failed: int = 0
    breaker_open: bool = False
    duration_ms: float = 0.0

class BatchResult(AgenticBaseModel):
    jobs: List[WorkflowState] = Field(default_factory=list)
    summary: BatchSummary = Field(default_factory=BatchSummary)


# =============================================================================
# CIRCUIT BREAKER
# =============================================================================

class CircuitBreaker:
    """
    Protects the batch from cascading failures (Pillar 8).
    """
    def __init__(self, threshold: int = 5):
        self.threshold = threshold
        self.failures = 0
        self.is_open = False

    def record_failure(self):
        self.failures += 1
        if self.failures >= self.threshold:
            self.is_open = True
            record_event("circuit_breaker_open", {"failures": self.failures})

    def record_success(self):
        self.failures = 0 
        self.is_open = False

    def check(self):
        if self.is_open:
            raise RuntimeError("Circuit Breaker Open")


# =============================================================================
# BATCH RUNNER
# =============================================================================

async def run_batch_async(
    job_inputs: List[Dict[str, Any]],
    max_concurrency: int = 5,
    failure_threshold: int = 3
) -> BatchResult:
    """
    Execute workflows in parallel with safety limits.
    """
    import time
    start_time = time.perf_counter()
    
    breaker = CircuitBreaker(threshold=failure_threshold)
    semaphore = asyncio.Semaphore(max_concurrency)
    engine = AgenticWorkflow()
    
    results: List[WorkflowState] = []
    failures = 0

    async def _worker(state: Dict[str, Any]) -> Optional[WorkflowState]:
        nonlocal failures
        
        # Fail Fast (Pillar 8)
        if breaker.is_open:
            return None

        async with semaphore:
            try:
                # Execute Main Workflow
                result = await engine.run(state)
                
                if result.phase == WorkflowPhase.FAILED:
                    breaker.record_failure()
                    failures += 1
                else:
                    breaker.record_success()
                
                return result

            except Exception as e:
                breaker.record_failure()
                failures += 1
                # Return a shell failure state for accounting
                return WorkflowState(
                    workflow_id=str(state.get("workflow_id", "unknown")),
                    phase=WorkflowPhase.FAILED,
                    node_statuses={},
                    summary="Batch Worker Exception",
                    result={},
                    errors=[str(e)]
                )

    # Schedule all jobs
    tasks = [asyncio.create_task(_worker(job)) for job in job_inputs]
    completed = await asyncio.gather(*tasks)
    
    # Filter out skipped jobs (due to breaker)
    valid_results = [r for r in completed if r is not None]

    duration = (time.perf_counter() - start_time) * 1000

    summary = BatchSummary(
        total_jobs=len(job_inputs),
        successful=len(valid_results) - failures,
        failed=failures,
        breaker_open=breaker.is_open,
        duration_ms=duration
    )

    return BatchResult(
        jobs=valid_results,
        summary=summary
    )

# =============================================================================
# SYNC WRAPPER
# =============================================================================

def run_batch_sync(job_inputs: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
    """
    Blocking wrapper for scripts. Returns dict for easy JSON dumping.
    """
    result_obj = asyncio.run(run_batch_async(job_inputs, **kwargs))
    return result_obj.model_dump()

if __name__ == "__main__":
    # Simple Load Test
    jobs = [{"objective": f"Test Job {i}"} for i in range(3)]
    res = run_batch_sync(jobs, max_concurrency=2)
    print(f"Batch Completed: {res['summary']}")
