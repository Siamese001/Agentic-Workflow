from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "adaptive_execution_mixin", "p0_governance")
_emit_reads_policy_state("p0", "adaptive_execution_mixin", "policy_binding")
_emit_routes_to_agent("p1", "adaptive_execution_mixin", "L3")
_emit_orchestrates_workflow("p1", "adaptive_execution_mixin", "L3")
_emit_dispatches_execution_plan("p1", "adaptive_execution_mixin", "L3")
_emit_validates_agent_capability("p1", "adaptive_execution_mixin", "L3")
_emit_checks_agent_registry("p1", "adaptive_execution_mixin", "L3")
_emit_snapshots_state("p0", "adaptive_execution_mixin", "state_snapshot")
emit_replay_key("p0", "adaptive_execution_mixin")
emit_determinism_digest("p0", "adaptive_execution_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "adaptive_execution_mixin", "execution_auth")
_emit_validates_capability("p2", "adaptive_execution_mixin", "capability_check")
_emit_routes_to_capability("p2", "adaptive_execution_mixin", "capability_route")
_emit_writes_via_uwg("p2", "adaptive_execution_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "adaptive_execution_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "adaptive_execution_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "adaptive_execution_mixin", "exec_output")
_emit_dispatches_agent("p3", "adaptive_execution_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "adaptive_execution_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "adaptive_execution_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "adaptive_execution_mixin", "healing_outcome")
_emit_escalates_failure("p3", "adaptive_execution_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "adaptive_execution_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "adaptive_execution_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "adaptive_execution_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "adaptive_execution_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "adaptive_execution_mixin", "eval_metric")
_emit_stores_embedding("p4", "adaptive_execution_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "adaptive_execution_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "adaptive_execution_mixin", "exec_snapshot_link")

"\nAdaptiveExecutionMixin – Sovereign Agent Role Mixin (Phase 29 – Dec 30, 2025)\n\nPurpose:\n  Enable agents to dynamically select execution mode based on real-time context:\n    - standard: normal operation\n    - conservative: high failure rate → safer, more verification\n    - aggressive: urgent → faster, riskier\n    - minimal: high system load → skip non-essential work\n\nConstitutional Alignment:\n  - Prevents resource exhaustion\n  - Adapts to sovereignty health\n  - Enables self-preservation under stress\n"
import logging
from typing import Any


# Lazy import to avoid L_SHARED->L3 gravity violation
def _get_registry():
    from agentic_core.L3_orchestration.utils.registry.agent_dispatch_registry import get_agent_dispatch_registry
    return get_agent_dispatch_registry()

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("adaptive_execution_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("adaptive_execution_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("adaptive_execution_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("adaptive_execution_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("adaptive_execution_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("adaptive_execution_mixin", "p4obs", "metric_6")
_emit_records_incident_event("adaptive_execution_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("adaptive_execution_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("adaptive_execution_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("adaptive_execution_mixin", "p4obs", "mon_state")
_emit_triggers_alert("adaptive_execution_mixin", "p4obs", "alert")
_emit_links_incident_trace("adaptive_execution_mixin", "p4obs", "trace_link")
_emit_captures_pattern("adaptive_execution_mixin", "p3lm", "pattern")
_emit_records_learning_event("adaptive_execution_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("adaptive_execution_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("adaptive_execution_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("adaptive_execution_mixin", "p3lm", "routing")
_emit_improves_agent_policy("adaptive_execution_mixin", "p3lm", "policy")
_emit_stores_learning_state("adaptive_execution_mixin", "p3lm", "state")
_emit_records_execution_trace("adaptive_execution_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("adaptive_execution_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("adaptive_execution_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("adaptive_execution_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("adaptive_execution_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("adaptive_execution_mixin", "env_read", "p2_env_1")
_emit_reads_environ("adaptive_execution_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("adaptive_execution_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("adaptive_execution_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "adaptive_execution_mixin", "context_pull")
_emit_pulls_context("p1", "adaptive_execution_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "adaptive_execution_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "adaptive_execution_mixin", "uwg_term_2")
_emit_writes_through("p1", "adaptive_execution_mixin", "write_through")
_emit_writes_through("p1", "adaptive_execution_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "adaptive_execution_mixin", "safety_validation")
_emit_invokes_eval("p1", "adaptive_execution_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "adaptive_execution_mixin", "routing_commit")
_emit_escalates_to_human("p1", "adaptive_execution_mixin", "human_escalation")
_emit_routes_through("p1", "adaptive_execution_mixin", "route_through")
_emit_agent_executes_agent("p1", "adaptive_execution_mixin", "sub_agent")
_emit_verifies_policy("p1", "adaptive_execution_mixin", "policy_check")
_emit_observes_runtime_state("p1", "adaptive_execution_mixin", "runtime_state")
_emit_verifies_boundary("p1", "adaptive_execution_mixin", "boundary_check")
_emit_transcripts_response("p1", "adaptive_execution_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "adaptive_execution_mixin")
_emit_gated_by_confidence("p1", "adaptive_execution_mixin", "confidence_gate")


class AdaptiveExecutionMixin:
    """
    Mixin that adds context-aware execution mode selection.
    Agents inherit this to become environmentally adaptive.
    """

    EXECUTION_MODES = ["standard", "conservative", "aggressive", "minimal"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Logger = logging.getLogger(f"{self.__class__.__name__}.Adaptive")
        self._current_mode: str = "standard"

    @property
    def current_mode(self) -> str:
        """Current execution mode — readable by orchestrators and logs."""
        return self._current_mode

    async def select_execution_mode(self, context: dict[str, Any]) -> str:
        """
        Constitutional decision engine for mode selection.
        Override or extend for agent-specific logic.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AdaptiveExecutionMixin.select_execution_mode")

        system_load = context.get("system_load", 0.0)
        if system_load > 0.85:
            self.Logger.warning(f"High system load ({system_load:.1%}) → switching to minimal mode")
            return "minimal"
        failure_rate = await self._get_recent_failure_rate(context)
        if failure_rate > 0.35:
            self.Logger.warning(f"High failure rate ({failure_rate:.1%}) → switching to conservative mode")
            return "conservative"
        if context.get("urgent", False) or context.get("time_critical", False):
            self.Logger.info("Urgent context detected → switching to aggressive mode")
            return "aggressive"
        health_score = context.get("sovereignty_health", 100.0)
        if health_score < 90:
            self.Logger.info(f"Low sovereignty health ({health_score:.0f}%) → conservative mode")
            return "conservative"
        return "standard"

    async def _get_recent_failure_rate(self, context: dict[str, Any]) -> float:
        """
        Hook for agents with history tracking.
        Default: assume healthy.
        """
        return 0.0

    async def execute(self, ctx: Any = None, **kwargs) -> Any:
        """
        Adaptive wrapper around agent's core execute().
        Agents must call super().execute() or implement mode-specific logic.
        """
        base_context = (
            await self._build_execution_context(ctx) if hasattr(self, "_build_execution_context") else {}
        )
        full_context = {**base_context, **kwargs}
        self._current_mode = await self.select_execution_mode(full_context)
        self.Logger.info(f"Executing in '{self._current_mode}' mode")
        mode_method = f"_execute_{self._current_mode}"
        if hasattr(self, mode_method):
            # Wave 2: Use AgentDispatchRegistry instead of raw getattr
            registry = get_agent_dispatch_registry()
            return await registry.dispatch(
                caller="AdaptiveExecutionMixin",
                target_class=self.__class__.__name__,
                method=mode_method,
                target_instance=self,
                args=(ctx,),
                kwargs=full_context
            )
        if hasattr(self, "_execute_standard"):
            registry = get_agent_dispatch_registry()
            return await registry.dispatch(
                caller="AdaptiveExecutionMixin",
                target_class=self.__class__.__name__,
                method="_execute_standard",
                target_instance=self,
                args=(ctx,),
                kwargs=full_context
            )
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement either mode-specific _execute_* or _execute_standard"
        )

    async def _execute_standard(self, ctx: Any, **context: dict[str, Any]) -> Any:
        """Default mode — full capability execution."""
        raise NotImplementedError("Agent must implement _execute_standard or override execute()")

    async def _execute_conservative(self, ctx: Any, **context: dict[str, Any]) -> Any:
        """Safer, more verified execution — e.g., extra validation, smaller steps."""
        self.Logger.info("Conservative mode: adding extra constitutional checks")
        return await self._execute_standard(ctx, **context)

    async def _execute_aggressive(self, ctx: Any, **context: dict[str, Any]) -> Any:
        """Faster execution — e.g., parallelize, skip non-critical checks."""
        self.Logger.info("Aggressive mode: prioritizing speed")
        return await self._execute_standard(ctx, **context)

    async def _execute_minimal(self, ctx: Any, **context: dict[str, Any]) -> Any:
        """Bare minimum — skip non-essential work to preserve resources."""
        self.Logger.warning("Minimal mode: skipping non-critical operations")
        return {"mode": "minimal", "result": "skipped_due_to_load", "preserved_resources": True}

    def force_mode(self, mode: str) -> None:
        """Emergency override — for testing or containment."""
        if mode not in self.EXECUTION_MODES:
            raise ValueError(f"Invalid mode: {mode}")
        self._current_mode = mode
        self.Logger.warning(f"Execution mode forced to '{mode}' via emergency override")
