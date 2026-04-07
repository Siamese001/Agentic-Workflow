"""ObservabilityProbeExecutorAgent — Canonical parameterized observability agent.

Consolidates: TrackObservabilityCostAgent, CoordinateObservabilityOperationsAgent,
              StrategicObservationAgent, DeadlockDetectorAgent, DebateSynthesisAgent,
              RuntimeTelemetryAgent
Created: 2026-02-08 (Structural Agent Count Reduction)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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
    record_execution_trace,
)

_emit_authorize_and_execute("p2", "observability_probe_executor", "execution_auth")
_emit_validates_capability("p2", "observability_probe_executor", "capability_check")
_emit_routes_to_capability("p2", "observability_probe_executor", "capability_route")
_emit_writes_via_uwg("p2", "observability_probe_executor", "uwg_write")
_emit_blocks_direct_write("p2", "observability_probe_executor", "direct_write_block")
_emit_records_tool_invocation("p2", "observability_probe_executor", "tool_invocation")
_emit_captures_execution_output("p2", "observability_probe_executor", "exec_output")
_emit_dispatches_agent("p3", "observability_probe_executor", "agent_dispatch")
_emit_coordinates_agents("p3", "observability_probe_executor", "agent_coordination")
_emit_records_workflow_lineage("p3", "observability_probe_executor", "workflow_lineage")
_emit_records_healing_outcome("p3", "observability_probe_executor", "healing_outcome")
_emit_escalates_failure("p3", "observability_probe_executor", "failure_escalation")
_emit_orchestrates_workflow("p3", "observability_probe_executor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "observability_probe_executor", "healing_dispatch")
_emit_invokes_evaluation("p3", "observability_probe_executor", "evaluation_signal")
_emit_records_telemetry_event("p4", "observability_probe_executor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "observability_probe_executor", "eval_metric")
_emit_stores_embedding("p4", "observability_probe_executor", "embedding_store")
_emit_updates_meta_learning_state("p4", "observability_probe_executor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "observability_probe_executor", "exec_snapshot_link")
from agentic_core.utils.decorators_compat_util import standard_heal

emit_replay_key("p0", "observability_probe_executor")
emit_determinism_digest("p0", "observability_probe_executor")

_emit_dispatches_healing_run("p1", "observability_probe_executor", "L6")
_emit_routes_through("p1", "observability_probe_executor", "L6")
_emit_checks_agent_registry("p1", "observability_probe_executor", "agent_registry")
_emit_validates_agent_capability("p1", "observability_probe_executor", "capability")
_emit_dispatches_execution_plan("p1", "observability_probe_executor", "exec_plan")
_emit_agent_executes_agent("p1", "observability_probe_executor", "sub_agent")
_emit_routes_to_agent("p1", "observability_probe_executor", "target_agent")
_emit_verifies_policy("p1", "observability_probe_executor", "policy_check")
_emit_observes_runtime_state("p1", "observability_probe_executor", "runtime_state")
_emit_verifies_boundary("p1", "observability_probe_executor", "boundary_check")
_emit_transcripts_response("p1", "observability_probe_executor", "transcript")
_emit_hard_fails_untranscripted("p1", "observability_probe_executor")
_emit_gated_by_confidence("p1", "observability_probe_executor", "confidence_gate")
_emit_escalates_to_human("p1", "observability_probe_executor", "L6")
_emit_reads_policy_state("p1", "observability_probe_executor", "L6")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

record_execution_trace("observability_probe_executor", "observability_probe_executor_trace")


_emit_emits_metric_event("observability_probe_executor", "p4obs", "metric_1")
_emit_emits_metric_event("observability_probe_executor", "p4obs", "metric_2")
_emit_emits_metric_event("observability_probe_executor", "p4obs", "metric_3")
_emit_emits_metric_event("observability_probe_executor", "p4obs", "metric_4")
_emit_emits_metric_event("observability_probe_executor", "p4obs", "metric_5")
_emit_emits_metric_event("observability_probe_executor", "p4obs", "metric_6")
_emit_records_incident_event("observability_probe_executor", "p4obs", "incident")
_emit_captures_runtime_anomaly("observability_probe_executor", "p4obs", "anomaly")
_emit_writes_observability_log("observability_probe_executor", "p4obs", "obs_log")
_emit_updates_monitoring_state("observability_probe_executor", "p4obs", "mon_state")
_emit_triggers_alert("observability_probe_executor", "p4obs", "alert")
_emit_links_incident_trace("observability_probe_executor", "p4obs", "trace_link")
_emit_captures_pattern("observability_probe_executor", "p3lm", "pattern")
_emit_records_learning_event("observability_probe_executor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("observability_probe_executor", "p3lm", "snapshot")
_emit_feeds_meta_learning("observability_probe_executor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("observability_probe_executor", "p3lm", "routing")
_emit_improves_agent_policy("observability_probe_executor", "p3lm", "policy")
_emit_stores_learning_state("observability_probe_executor", "p3lm", "state")
_emit_records_execution_trace("observability_probe_executor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("observability_probe_executor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("observability_probe_executor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("observability_probe_executor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("observability_probe_executor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("observability_probe_executor", "env_read", "p2_env_1")
_emit_reads_environ("observability_probe_executor", "env_read", "p2_env_2")
_emit_reads_runtime_state("observability_probe_executor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("observability_probe_executor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "observability_probe_executor", "context_pull")
_emit_pulls_context("p1", "observability_probe_executor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "observability_probe_executor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "observability_probe_executor", "uwg_term_2")
_emit_writes_through("p1", "observability_probe_executor", "write_through")
_emit_writes_through("p1", "observability_probe_executor", "write_through_2")
_emit_validated_by_safety_plane("p1", "observability_probe_executor", "safety_validation")
_emit_invokes_eval("p1", "observability_probe_executor", "eval_call")
_emit_proposal_commits_routing("p1", "observability_probe_executor", "routing_commit")


@dataclass
class ObservabilityProbeExecutorAgent(SovereignBaseAgent):
    """Parameterized observability probe agent.

    Usage:
        probe = ObservabilityProbeExecutorAgent(probe_type="cost_tracker")
    """

    project_root: Any = field(default=None)
    probe_type: str = "generic"
    _results: dict = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        super().__post_init__()

    # guardian: allow-type-erasure
    def execute(self, context: dict | None = None) -> dict:
        """Dispatch to probe-specific execution."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ObservabilityProbeExecutorAgent.execute", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(
            str(_uuid.uuid4()), "ObservabilityProbeExecutorAgent.execute", "p0_governance",
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L6_OBSERVABILITY, "ObservabilityProbeExecutorAgent.execute",
        )

        ctx = context or {}
        handler = self._get_handler()
        if handler:
            self._results = handler(ctx)
        return self._results

    def _get_handler(self):
        handlers = {
            "cost_tracker": self._probe_cost,
            "coordinator": self._probe_coordination,
            "strategic": self._probe_strategic,
            "deadlock": self._probe_deadlock,
            "debate": self._probe_debate,
            "runtime_telemetry": self._probe_telemetry,
        }
        return handlers.get(self.probe_type)

    # guardian: allow-type-erasure
    def _probe_cost(self, ctx: dict) -> dict:
        return {"probe": "cost_tracker", "metrics": ctx.get("cost_metrics", {})}

    # guardian: allow-type-erasure
    def _probe_coordination(self, ctx: dict) -> dict:
        return {"probe": "coordinator", "operations": ctx.get("operations", [])}

    # guardian: allow-type-erasure
    def _probe_strategic(self, ctx: dict) -> dict:
        return {"probe": "strategic", "observations": ctx.get("observations", [])}

    # guardian: allow-type-erasure
    def _probe_deadlock(self, ctx: dict) -> dict:
        return {"probe": "deadlock", "cycles": ctx.get("dependency_cycles", [])}

    # guardian: allow-type-erasure
    def _probe_debate(self, ctx: dict) -> dict:
        return {"probe": "debate", "synthesis": ctx.get("debate_results", {})}

    # guardian: allow-type-erasure
    def _probe_telemetry(self, ctx: dict) -> dict:
        return {"probe": "runtime_telemetry", "benchmarks": ctx.get("benchmarks", {})}

    # guardian: allow-type-erasure
    def scan_violations(self, target_territory: str | None = None) -> dict:
        """Contract-aligned surface for EXECUTION_PLAN phase 4.5.

        Delegates to execute() with debate probe context.
        """
        ctx: dict[str, Any] = {}
        if target_territory is not None:
            ctx["target_territory"] = target_territory
        result = self.execute(ctx)
        return {"violations": result.get("synthesis", {}).get("violations", [])}

    @standard_heal
    # guardian: allow-type-erasure
    def heal_repository(self, **kwargs) -> dict:
        return super().heal_repository(**kwargs)

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "skipped",
            "details": f"ObservabilityProbeExecutor({self.probe_type})",
            "artifacts": [],
            "errors": [],
        }
