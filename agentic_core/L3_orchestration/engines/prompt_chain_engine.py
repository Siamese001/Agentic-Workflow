"""Prompt Chain Engine.

Formalises the implicit chaining in ResumeOrchestratorEngine into a
first-class PromptChainEngine with explicit Gate nodes.

Chain execution:
  step_1 → [Gate] → step_2 → [Gate] → ... → step_n

Each step is an async callable: async (input_context: dict) -> dict
A Gate is an optional async callable: async (output: dict) -> bool
  - True  → advance to next step
  - False → take the fail_branch (or raise if none)

Each step's output is injected as context into the next step's input.

Layer: L3_orchestration
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "prompt_chain_engine")
emit_determinism_digest("p0", "prompt_chain_engine")

_emit_dispatches_healing_run("p1", "prompt_chain_engine", "L3")
_emit_routes_through("p1", "prompt_chain_engine", "L3")
_emit_escalates_to_human("p1", "prompt_chain_engine", "L3")
_emit_reads_policy_state("p1", "prompt_chain_engine", "L3")

Logger = logging.getLogger(__name__)


@dataclass
class ChainStep:
    """A single step in the prompt chain."""

    name: str
    fn: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]
    gate: Callable[[dict[str, Any]], Awaitable[bool]] | None = None
    fail_branch: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]] | None = None
    description: str = ""


@dataclass
class ChainResult:
    """Result of running the full prompt chain."""

    success: bool
    output: dict[str, Any]
    steps_completed: list[str] = field(default_factory=list)
    steps_failed: list[str] = field(default_factory=list)
    gate_failures: list[str] = field(default_factory=list)
    error: str | None = None


class PromptChainEngine:
    """Sequential prompt chain with per-step Gate nodes.

    Usage::

        chain = PromptChainEngine()
        chain.add_step("enrich",    enrich_fn,    gate=quality_gate)
        chain.add_step("optimise",  optimise_fn)
        chain.add_step("finalise",  finalise_fn,  gate=final_gate, fail_branch=fallback_fn)
        result = await chain.run(initial_context={"resume": raw_resume})

    Args:
        stop_on_gate_failure: If True, abort chain when a gate returns False and
                              no fail_branch is configured (default True).
    """

    def __init__(self, stop_on_gate_failure: bool = True) -> None:
        self._steps: list[ChainStep] = []
        self.stop_on_gate_failure = stop_on_gate_failure

    def add_step(
        self,
        name: str,
        fn: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]],
        gate: Callable[[dict[str, Any]], Awaitable[bool]] | None = None,
        fail_branch: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]] | None = None,
        description: str = "",
    ) -> PromptChainEngine:
        """Append a step to the chain.

        Args:
            name:        Unique step identifier.
            fn:          Async step function: (context) -> updated_context
            gate:        Optional async gate: (output) -> bool.  True = proceed.
            fail_branch: Async fallback used when gate returns False.
            description: Human-readable step description.

        Returns:
            self (fluent API).
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "PromptChainEngine.add_step", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "PromptChainEngine.add_step", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PromptChainEngine.add_step")

        self._steps.append(
            ChainStep(name=name, fn=fn, gate=gate, fail_branch=fail_branch, description=description)
        )
        return self

    async def run(
        self,
        initial_context: dict[str, Any] | None = None,
    ) -> ChainResult:
        """Execute the chain, injecting each step's output into the next.

        Args:
            initial_context: Seed context for the first step.

        Returns:
            ChainResult with final output and execution trace.
        """
        context: dict[str, Any] = initial_context or {}
        result = ChainResult(success=False, output=context)

        Logger.info("prompt_chain_start", extra={"steps": len(self._steps)})

        for step in self._steps:
            Logger.debug("prompt_chain_step", extra={"step": step.name})
            try:
                output = await step.fn(context)
            except Exception as exc:
                result.error = f"Step '{step.name}' raised: {exc}"
                result.steps_failed.append(step.name)
                Logger.error("prompt_chain_step_error", extra={"step": step.name, "error": str(exc)})
                return result

            if step.gate is not None:
                gate_passed = await step.gate(output)
                if not gate_passed:
                    result.gate_failures.append(step.name)
                    Logger.info("prompt_chain_gate_fail", extra={"step": step.name})
                    if step.fail_branch is not None:
                        output = await step.fail_branch(context)
                    elif self.stop_on_gate_failure:
                        result.error = f"Gate failed at step '{step.name}' — no fail_branch configured"
                        result.steps_failed.append(step.name)
                        result.output = output
                        return result

            context = {**context, **output}
            result.steps_completed.append(step.name)

        result.success = True
        result.output = context
        Logger.info(
            "prompt_chain_complete",
            extra={
                "steps_completed": len(result.steps_completed),
                "gate_failures": len(result.gate_failures),
            },
        )
        return result

    @classmethod
    def from_rg_orchestrator(cls, ctx: Any) -> PromptChainEngine:
        """Factory that wires the standard apps_rg resume pipeline as a chain.

        Extracts the implicit chaining from ResumeOrchestratorEngine into
        explicit steps with quality gates.
        """
        from apps_rg.engines.content_optimizer_engine import ContentOptimizerEngine
        from apps_rg.engines.content_quality_engine import ContentQualityEngine
        from apps_rg.engines.reflection_engine import ReflectionEngine

        quality_engine = ContentQualityEngine(ctx)
        optimizer_engine = ContentOptimizerEngine(ctx)
        reflection_engine = ReflectionEngine(ctx)

        async def _quality_step(context: dict[str, Any]) -> dict[str, Any]:
            ctx.buffer.write("hop2_enrichment", context.get("content", {}), source_agent="chain")
            report = await quality_engine.execute()
            return {"quality_report": report}

        async def _optimize_step(context: dict[str, Any]) -> dict[str, Any]:
            sections = await optimizer_engine.execute()
            return {"optimized_sections": sections}

        async def _reflect_step(context: dict[str, Any]) -> dict[str, Any]:
            result = await reflection_engine.execute(context)
            return {"reflection": result}

        async def _quality_gate(output: dict[str, Any]) -> bool:
            report = output.get("quality_report", {})
            return float(report.get("score", 0)) >= 70

        chain = cls(stop_on_gate_failure=False)
        chain.add_step("quality_check", _quality_step, gate=_quality_gate)
        chain.add_step("optimize", _optimize_step)
        chain.add_step("reflect", _reflect_step)
        return chain
