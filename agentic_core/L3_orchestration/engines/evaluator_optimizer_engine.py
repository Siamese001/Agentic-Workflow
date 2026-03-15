"""Evaluator-Optimizer Engine.

Wires the generator → evaluator → optimizer feedback loop:

  1. Generator  — produces an initial response (injected callable)
  2. Evaluator  — scores/flags the response; delegates to ContentQualityEngine
  3. Optimizer  — revises if score < threshold; delegates to ContentOptimizerEngine
  4. Gate       — loops until score >= threshold or max_iterations reached

Both ContentQualityEngine and ContentOptimizerEngine are accepted as injected
dependencies so the engine remains testable with fakes and decoupled from
the apps_rg buffer protocol.

Layer: L3_orchestration
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Logger = logging.getLogger(__name__)

_DEFAULT_THRESHOLD = 80.0
_DEFAULT_MAX_ITERATIONS = 5


class EvaluatorOptimizerEngine:
    """Generator → Evaluator → Optimizer feedback loop.

    Args:
        generator_fn:  async (task, prior_response) -> dict  (content payload)
        evaluator_fn:  async (content) -> dict  with at least ``score`` (float) and
                       ``issues`` (list[str]) and ``status`` ('passed'|'warning'|…)
        optimizer_fn:  async (content, issues) -> dict  (revised content payload)
        score_threshold: Stop when evaluator score >= this value (default 80.0).
        max_iterations:  Hard cap on revision loops (default 5).
    """

    def __init__(
        self,
        generator_fn: Callable[[str, dict[str, Any] | None], Awaitable[dict[str, Any]]],
        evaluator_fn: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]],
        optimizer_fn: Callable[[dict[str, Any], list[str]], Awaitable[dict[str, Any]]],
        score_threshold: float = _DEFAULT_THRESHOLD,
        max_iterations: int = _DEFAULT_MAX_ITERATIONS,
    ) -> None:
        self.generator_fn = generator_fn
        self.evaluator_fn = evaluator_fn
        self.optimizer_fn = optimizer_fn
        self.score_threshold = score_threshold
        self.max_iterations = max_iterations

    async def run(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run the feedback loop for a task.

        Returns:
            dict with keys:
                ``content``    — final content payload
                ``score``      — final evaluator score
                ``passed``     — whether threshold was met
                ``iterations`` — number of revision cycles
                ``history``    — list of (score, issues) per iteration
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "EvaluatorOptimizerEngine.run")

        content = await self.generator_fn(task, context)
        history: list[dict[str, Any]] = []

        for iteration in range(1, self.max_iterations + 1):
            eval_result = await self.evaluator_fn(content)
            score = float(eval_result.get("score", 0.0))
            issues = eval_result.get("issues", [])
            status = eval_result.get("status", "unknown")

            history.append({"iteration": iteration, "score": score, "issues": issues, "status": status})

            Logger.info(
                "eval_optimizer_iteration",
                extra={"iteration": iteration, "score": score, "task": task[:60]},
            )

            if score >= self.score_threshold:
                Logger.info("eval_optimizer_converged", extra={"iteration": iteration, "score": score})
                break

            content = await self.optimizer_fn(content, issues)

        final_score = history[-1]["score"] if history else 0.0
        passed = final_score >= self.score_threshold

        Logger.info(
            "eval_optimizer_complete",
            extra={"task": task[:60], "iterations": len(history), "score": final_score, "passed": passed},
        )

        return {
            "content": content,
            "score": final_score,
            "passed": passed,
            "iterations": len(history),
            "history": history,
        }

    @classmethod
    def from_rg_engines(
        cls,
        ctx: Any,
        generator_fn: Callable[[str, dict[str, Any] | None], Awaitable[dict[str, Any]]],
        score_threshold: float = _DEFAULT_THRESHOLD,
        max_iterations: int = _DEFAULT_MAX_ITERATIONS,
    ) -> EvaluatorOptimizerEngine:
        """Factory that wires ContentQualityEngine + ContentOptimizerEngine.

        Args:
            ctx: apps_rg buffer context (passed to both engines).
            generator_fn: Async callable producing the initial content dict.
            score_threshold: Quality score gate.
            max_iterations: Max revision cycles.
        """
        from apps_rg.engines.content_optimizer_engine import ContentOptimizerEngine
        from apps_rg.engines.content_quality_engine import ContentQualityEngine

        quality_engine = ContentQualityEngine(ctx)
        optimizer_engine = ContentOptimizerEngine(ctx)

        async def _evaluator_fn(content: dict[str, Any]) -> dict[str, Any]:
            ctx.buffer.write("hop2_enrichment", content, source_agent="eval_optimizer")
            return await quality_engine.execute(target_key="hop2_enrichment")

        async def _optimizer_fn(content: dict[str, Any], issues: list[str]) -> dict[str, Any]:
            ctx.buffer.write("hop2_enrichment", content, source_agent="eval_optimizer")
            sections = await optimizer_engine.execute()
            if sections:
                optimized = ctx.buffer.read("optimized_content")
                if optimized:
                    return optimized
            return content

        return cls(
            generator_fn=generator_fn,
            evaluator_fn=_evaluator_fn,
            optimizer_fn=_optimizer_fn,
            score_threshold=score_threshold,
            max_iterations=max_iterations,
        )
