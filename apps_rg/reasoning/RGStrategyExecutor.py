"""RGStrategyExecutor — Canonical parameterized RG strategy agent.

Consolidates: ContentStrategyAgent, RgStrategicPlannerAgent, RgTemplateOptimizerAgent
Created: 2026-02-08 (Structural Agent Count Reduction)
"""

from __future__ import annotations

from dataclasses import dataclass

from apps_rg.utils.RGAgentBase import RGAgentBase

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "RGStrategyExecutor", "p0_governance")
_emit_reads_policy_state("p0", "RGStrategyExecutor", "policy_binding")
_emit_snapshots_state("p0", "RGStrategyExecutor", "state_snapshot")
emit_replay_key("p0", "RGStrategyExecutor")
emit_determinism_digest("p0", "RGStrategyExecutor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass
class RGStrategyExecutor(RGAgentBase):
    """Parameterized RG strategy agent.

    Usage:
        strategy = RGStrategyExecutor(strategy_type="content")
    """

    strategy_type: str = "generic"

    def execute(self, data: dict | None = None, **kwargs) -> dict:
        """Dispatch to strategy-specific execution."""
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"RGStrategyExecutor.execute:{self.strategy_type}")
        ctx = data or {}
        handler = {
            "content": self._strategy_content,
            "strategic_planner": self._strategy_planner,
            "template_optimizer": self._strategy_optimizer,
        }.get(self.strategy_type, self._strategy_default)
        return handler(ctx)

    def _strategy_content(self, ctx: dict) -> dict:
        topic = ctx.get("topic", "")
        return {"strategy": "content", "topic": topic, "recommendations": []}

    def _strategy_planner(self, ctx: dict) -> dict:
        goals = ctx.get("goals", [])
        return {"strategy": "strategic_planner", "goals": goals, "plan": []}

    def _strategy_optimizer(self, ctx: dict) -> dict:
        template = ctx.get("template", "")
        return {"strategy": "template_optimizer", "template": template, "optimizations": []}

    def _strategy_default(self, ctx: dict) -> dict:
        return {"strategy": self.strategy_type, "status": "no_handler"}
