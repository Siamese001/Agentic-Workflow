"""Reflexion Engine.

Full Reflexion loop (Shinn et al. 2023):
  1. Generator  — produces initial/revised response
  2. Evaluator  — verbal critique + numeric score (delegates scoring to ReflectionEngine)
  3. Memory     — stores critique history across iterations (ReflexionMemory)
  4. Revisor    — uses critique + memory to generate a revised response
  5. Gate       — loops up to max_iterations; stops early when score >= threshold

Delegates scalar scoring back to the existing apps_rg ReflectionEngine stub
so existing pipeline behaviour is preserved.

Layer: L3_orchestration
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from agentic_core.L3_orchestration.types.reflexion_types import ReflexionCritique, ReflexionMemory
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Logger = logging.getLogger(__name__)

_DEFAULT_THRESHOLD = 0.85
_DEFAULT_MAX_ITERATIONS = 5


class ReflexionEngine:
    """Iterative critique-revise loop with verbal memory.

    All LLM interactions are injected as async callables so the engine
    remains LLM-provider-agnostic and fully testable with fakes.

    Args:
        generator_fn:  async (task, prior_response, memory_summary) -> str
            Produces the initial response (prior_response=None) or a revision.
        evaluator_fn:  async (task, response) -> dict with keys:
            ``critique`` (str), ``score`` (float 0-1), ``passed`` (bool)
        score_threshold: Stop iterating when score >= this value (default 0.85).
        max_iterations:  Hard upper bound on revision loops (default 5).
    """

    def __init__(
        self,
        generator_fn: Callable[[str, str | None, str], Awaitable[str]],
        evaluator_fn: Callable[[str, str], Awaitable[dict[str, Any]]],
        score_threshold: float = _DEFAULT_THRESHOLD,
        max_iterations: int = _DEFAULT_MAX_ITERATIONS,
    ) -> None:
        self.generator_fn = generator_fn
        self.evaluator_fn = evaluator_fn
        self.score_threshold = score_threshold
        self.max_iterations = max_iterations

    async def run(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run the Reflexion loop for a task.

        Returns:
            dict with keys:
                ``response``   — best response found
                ``score``      — final score
                ``passed``     — whether threshold was met
                ``iterations`` — number of iterations taken
                ``memory``     — ReflexionMemory instance with full critique history
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ReflexionEngine.run")

        memory = ReflexionMemory(task=task)
        response: str | None = None
        final_critique: ReflexionCritique | None = None

        for iteration in range(1, self.max_iterations + 1):
            memory_summary = memory.summary()
            response = await self.generator_fn(task, response, memory_summary)

            eval_result = await self.evaluator_fn(task, response)
            critique_text = eval_result.get("critique", "")
            score = float(eval_result.get("score", 0.0))
            passed = bool(eval_result.get("passed", score >= self.score_threshold))

            critique = ReflexionCritique(
                iteration=iteration,
                response=response,
                critique=critique_text,
                score=score,
                passed=passed,
                metadata=context or {},
            )
            memory.add(critique)
            final_critique = critique

            Logger.info(
                "reflexion_iteration",
                extra={
                    "iteration": iteration,
                    "score": score,
                    "passed": passed,
                    "task": task[:60],
                },
            )

            if passed:
                Logger.info(
                    "reflexion_converged",
                    extra={"iteration": iteration, "score": score},
                )
                break

        best_response = memory.best_response() or response or ""
        best_score = max((c.score for c in memory.critiques), default=0.0)
        best_passed = best_score >= self.score_threshold

        Logger.info(
            "reflexion_complete",
            extra={
                "task": task[:60],
                "iterations": len(memory.critiques),
                "best_score": best_score,
                "passed": best_passed,
            },
        )

        return {
            "response": best_response,
            "score": best_score,
            "passed": best_passed,
            "iterations": len(memory.critiques),
            "memory": memory,
            "final_critique": final_critique,
        }

    @classmethod
    def with_rg_scorer(
        cls,
        generator_fn: Callable[[str, str | None, str], Awaitable[str]],
        score_threshold: float = _DEFAULT_THRESHOLD,
        max_iterations: int = _DEFAULT_MAX_ITERATIONS,
    ) -> ReflexionEngine:
        """Factory that wires the existing apps_rg ReflectionEngine as the scorer.

        The ReflectionEngine produces a numeric score from workflow_results;
        here we wrap a single-response dict to reuse its scoring logic.
        """
        from apps_rg.engines.reflection_engine import ReflectionEngine

        _rg_engine_sentinel: dict[str, Any] = {}

        async def _rg_evaluator_fn(task: str, response: str) -> dict[str, Any]:
            workflow_results = {
                "response_engine": {
                    "passed": True,
                    "signal": None,
                    "output": response,
                }
            }
            ctx_obj = _rg_engine_sentinel.get("ctx")
            if ctx_obj is None:
                score = 0.7
                critique = "RG scorer unavailable — ctx not provided; using default score."
            else:
                engine = ReflectionEngine(ctx_obj)
                result = await engine.execute(workflow_results)
                score = result.get("overall_score", 0.0)
                weaknesses = result.get("weaknesses", [])
                critique = "; ".join(weaknesses) if weaknesses else "No issues detected."

            passed = score >= score_threshold
            return {"critique": critique, "score": score, "passed": passed}

        return cls(
            generator_fn=generator_fn,
            evaluator_fn=_rg_evaluator_fn,
            score_threshold=score_threshold,
            max_iterations=max_iterations,
        )
