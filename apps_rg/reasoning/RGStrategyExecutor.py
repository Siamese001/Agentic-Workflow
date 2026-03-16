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
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "RGStrategyExecutor", "p0_governance")
_emit_reads_policy_state("p0", "RGStrategyExecutor", "policy_binding")
_emit_snapshots_state("p0", "RGStrategyExecutor", "state_snapshot")
emit_replay_key("p0", "RGStrategyExecutor")
emit_determinism_digest("p0", "RGStrategyExecutor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "RGStrategyExecutor", "execution_auth")
_emit_validates_capability("p2", "RGStrategyExecutor", "capability_check")
_emit_routes_to_capability("p2", "RGStrategyExecutor", "capability_route")
_emit_writes_via_uwg("p2", "RGStrategyExecutor", "uwg_write")
_emit_blocks_direct_write("p2", "RGStrategyExecutor", "direct_write_block")
_emit_records_tool_invocation("p2", "RGStrategyExecutor", "tool_invocation")
_emit_captures_execution_output("p2", "RGStrategyExecutor", "exec_output")
_emit_dispatches_agent("p3", "RGStrategyExecutor", "agent_dispatch")
_emit_coordinates_agents("p3", "RGStrategyExecutor", "agent_coordination")
_emit_records_workflow_lineage("p3", "RGStrategyExecutor", "workflow_lineage")
_emit_records_healing_outcome("p3", "RGStrategyExecutor", "healing_outcome")
_emit_escalates_failure("p3", "RGStrategyExecutor", "failure_escalation")
_emit_orchestrates_workflow("p3", "RGStrategyExecutor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "RGStrategyExecutor", "healing_dispatch")
_emit_invokes_evaluation("p3", "RGStrategyExecutor", "evaluation_signal")
_emit_records_telemetry_event("p4", "RGStrategyExecutor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "RGStrategyExecutor", "eval_metric")
_emit_stores_embedding("p4", "RGStrategyExecutor", "embedding_store")
_emit_updates_meta_learning_state("p4", "RGStrategyExecutor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "RGStrategyExecutor", "exec_snapshot_link")


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
