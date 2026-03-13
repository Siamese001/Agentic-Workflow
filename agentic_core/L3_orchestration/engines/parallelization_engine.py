"""Parallelization Engine.

Formalises the fan-out / fan-in pattern on top of the existing DAGManager infra.

Two modes:
  SECTIONING  — split one task into N sub-tasks, run in parallel, aggregate results
  SAMPLING    — run the same task N times with different seeds, vote / synthesize

Aggregation strategies:
  majority_vote   — pick the most common result string
  llm_synthesize  — call an async synthesizer_fn on all outputs
  first_pass      — return the first result that passes a predicate
  collect_all     — return the full list of outputs (no reduction)

Layer: L3_orchestration
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import Any

Logger = logging.getLogger(__name__)


class ParallelMode(Enum):
    SECTIONING = "sectioning"
    SAMPLING = "sampling"


class AggregationStrategy(Enum):
    MAJORITY_VOTE = "majority_vote"
    LLM_SYNTHESIZE = "llm_synthesize"
    FIRST_PASS = "first_pass"
    COLLECT_ALL = "collect_all"


class ParallelizationEngine:
    """Fan-out / fan-in parallel execution engine.

    Args:
        worker_fn:     async (task: str, seed: int | None) -> Any
            Called for each parallel branch. In SECTIONING mode, ``task`` is a
            sub-task string; in SAMPLING mode, ``task`` is the same goal each time.
        mode:          ParallelMode (SECTIONING or SAMPLING).
        aggregation:   AggregationStrategy for reducing parallel outputs.
        synthesizer_fn: Required when aggregation=LLM_SYNTHESIZE.
                        async (outputs: list[Any]) -> str
        pass_predicate: Required when aggregation=FIRST_PASS.
                        sync (output: Any) -> bool
        max_concurrency: Optional semaphore cap on simultaneous workers.
    """

    def __init__(
        self,
        worker_fn: Callable[[str, int | None], Awaitable[Any]],
        mode: ParallelMode = ParallelMode.SECTIONING,
        aggregation: AggregationStrategy = AggregationStrategy.COLLECT_ALL,
        synthesizer_fn: Callable[[list[Any]], Awaitable[str]] | None = None,
        pass_predicate: Callable[[Any], bool] | None = None,
        max_concurrency: int | None = None,
    ) -> None:
        self.worker_fn = worker_fn
        self.mode = mode
        self.aggregation = aggregation
        self.synthesizer_fn = synthesizer_fn
        self.pass_predicate = pass_predicate
        self._semaphore = asyncio.Semaphore(max_concurrency) if max_concurrency else None

    async def run(
        self,
        goal: str,
        branches: list[str] | None = None,
        n_samples: int = 3,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute parallel branches and aggregate.

        Args:
            goal:     Main task / goal string.
            branches: Sub-task strings for SECTIONING mode. If None in SECTIONING
                      mode, goal is used as the only branch.
            n_samples: Number of parallel samples for SAMPLING mode (ignored in SECTIONING).
            context:  Optional metadata passed through to the result.

        Returns:
            dict with keys:
                ``result``   — aggregated output
                ``outputs``  — raw list of per-branch outputs
                ``mode``     — parallelization mode name
                ``branches`` — list of branch task strings used
        """
        if self.mode == ParallelMode.SECTIONING:
            tasks = branches if branches else [goal]
            seeds = [None] * len(tasks)
        else:
            tasks = [goal] * n_samples
            seeds = list(range(n_samples))

        Logger.info(
            "parallelization_start",
            extra={"mode": self.mode.value, "branches": len(tasks), "goal": goal[:60]},
        )

        outputs = await self._execute_parallel(tasks, seeds)

        result = await self._aggregate(outputs)

        Logger.info(
            "parallelization_complete",
            extra={"mode": self.mode.value, "branches": len(tasks), "aggregation": self.aggregation.value},
        )

        return {
            "result": result,
            "outputs": outputs,
            "mode": self.mode.value,
            "branches": tasks,
        }

    async def _execute_parallel(self, tasks: list[str], seeds: list[int | None]) -> list[Any]:
        """Run all branches concurrently, respecting optional semaphore."""

        async def _guarded(task: str, seed: int | None) -> Any:
            if self._semaphore:
                async with self._semaphore:
                    return await self.worker_fn(task, seed)
            return await self.worker_fn(task, seed)

        results = await asyncio.gather(
            *[_guarded(t, s) for t, s in zip(tasks, seeds)],
            return_exceptions=True,
        )
        outputs: list[Any] = []
        for i, r in enumerate(results):
            if isinstance(r, BaseException):
                Logger.error("parallelization_branch_error", extra={"branch": i, "error": str(r)})
                outputs.append(None)
            else:
                outputs.append(r)
        return outputs

    async def _aggregate(self, outputs: list[Any]) -> Any:
        valid = [o for o in outputs if o is not None]

        if self.aggregation == AggregationStrategy.COLLECT_ALL:
            return outputs

        if self.aggregation == AggregationStrategy.MAJORITY_VOTE:
            if not valid:
                return None
            counts: dict[str, int] = {}
            for o in valid:
                key = str(o)
                counts[key] = counts.get(key, 0) + 1
            winner = max(counts, key=counts.__getitem__)
            return winner

        if self.aggregation == AggregationStrategy.LLM_SYNTHESIZE:
            if self.synthesizer_fn is None:
                raise ValueError("synthesizer_fn required for LLM_SYNTHESIZE aggregation")
            return await self.synthesizer_fn(valid)

        if self.aggregation == AggregationStrategy.FIRST_PASS:
            if self.pass_predicate is None:
                raise ValueError("pass_predicate required for FIRST_PASS aggregation")
            for o in valid:
                if self.pass_predicate(o):
                    return o
            return valid[0] if valid else None

        return outputs
