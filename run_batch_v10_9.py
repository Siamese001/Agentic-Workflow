# FILE: run_batch_v10_9.py
"""
Batch Runner — v10_9 Agentic Workflow (REFINED)

This module provides a simple, architecture-compliant batch runner for
the v10_9 agentic workflow.

Responsibilities:
    • Accept a list of initial_state dicts (job inputs).
    • Execute each via main_v10_9.run_workflow_v10_9.
    • Aggregate results and basic telemetry at the batch level.

Non-responsibilities:
    • NO L1 cognition (planning).
    • NO L2 execution/tool calls (beyond invoking run_workflow_v10_9).
    • NO L3 orchestration logic (delegated to Orchestrator in l3.py).
    • NO L4 state mutation logic (delegated to StateAdapter).
    • NO L5 safety/policy decisions (delegated to l5.py).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from main_v10_9 import run_workflow_v10_9


# ============================================================================
# 1. BATCH FEEDBACK AGGREGATOR
# ============================================================================


@dataclass
class BatchFeedbackAggregator:
    """
    Aggregates results across a batch of workflow runs.

    Fields:
        • results: list of per-job results (full run_workflow_v10_9 outputs)
        • total_jobs: count of jobs processed
        • successful: count of jobs that completed without raising
                      (does not inspect safety outcomes; that is per-job)
    """

    results: List[Dict[str, Any]] = field(default_factory=list)

    def add_result(self, result: Dict[str, Any]) -> None:
        self.results.append(result)

    @property
    def total_jobs(self) -> int:
        return len(self.results)

    @property
    def successful(self) -> int:
        # For now, treat all completed runs as "successful"; domain-specific
        # success criteria (e.g., phase == COMPLETE, safety passed) can be
        # layered on top by callers.
        return len(self.results)

    def summary(self) -> Dict[str, Any]:
        return {
            "total_jobs": self.total_jobs,
            "successful": self.successful,
        }


# ============================================================================
# 2. BATCH RUNNER APIs
# ============================================================================


async def run_batch_async(
    job_inputs: List[Dict[str, Any]],
    *,
    max_concurrency: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Execute a batch of v10_9 workflows asynchronously.

    Args:
        job_inputs: list[dict]; each dict is an initial_state to pass to
                    run_workflow_v10_9.
        max_concurrency: optional limit on concurrent tasks; if None, all
                         jobs are launched concurrently.

    Returns:
        dict:
            {
                "jobs": [... per-job results ...],
                "batch_summary": {
                    "total_jobs": int,
                    "successful": int,
                },
            }
    """
    if not job_inputs:
        return {"jobs": [], "batch_summary": {"total_jobs": 0, "successful": 0}}

    aggregator = BatchFeedbackAggregator()

    semaphore = (
        asyncio.Semaphore(max_concurrency)
        if max_concurrency is not None and max_concurrency > 0
        else None
    )

    async def _run_single(initial_state: Dict[str, Any]) -> None:
        if semaphore:
            async with semaphore:
                result = await run_workflow_v10_9(initial_state)
        else:
            result = await run_workflow_v10_9(initial_state)
        aggregator.add_result(result)

    tasks = [asyncio.create_task(_run_single(job)) for job in job_inputs]
    await asyncio.gather(*tasks, return_exceptions=False)

    return {
        "jobs": aggregator.results,
        "batch_summary": aggregator.summary(),
    }


def run_batch_sync(
    job_inputs: List[Dict[str, Any]],
    *,
    max_concurrency: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Synchronous wrapper around run_batch_async for convenient use in
    CLI scripts or non-async contexts.
    """
    return asyncio.run(run_batch_async(job_inputs, max_concurrency=max_concurrency))


# ============================================================================
# 3. OPTIONAL CLI ENTRYPOINT
# ============================================================================

if __name__ == "__main__":
    # Example: simple inline batch for demonstration.
    example_jobs = [
        {
            "objective": "draft a concise professional summary",
            "messages": [{"role": "user", "content": "Summarize my profile."}],
        },
        {
            "objective": "qa validate this summary",
            "messages": [{"role": "user", "content": "Check quality of this text."}],
            "draft_result": {"draft": ["This is a clean, logically structured sentence."]},
        },
    ]

    result = run_batch_sync(example_jobs, max_concurrency=2)
    print("=== v10_9 Batch Runner Output ===")
    print("Batch Summary:", result["batch_summary"])
    print("Jobs:", result["jobs"])
