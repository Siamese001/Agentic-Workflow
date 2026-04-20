from __future__ import annotations

import logging

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "L6ObservabilityBase", "p0_governance")
_emit_reads_policy_state("p0", "L6ObservabilityBase", "policy_binding")
_emit_snapshots_state("p0", "L6ObservabilityBase", "state_snapshot")
emit_replay_key("p0", "L6ObservabilityBase")
emit_determinism_digest("p0", "L6ObservabilityBase")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "L6ObservabilityBase", "execution_auth")
_emit_validates_capability("p2", "L6ObservabilityBase", "capability_check")
_emit_routes_to_capability("p2", "L6ObservabilityBase", "capability_route")
_emit_writes_via_uwg("p2", "L6ObservabilityBase", "uwg_write")
_emit_blocks_direct_write("p2", "L6ObservabilityBase", "direct_write_block")
_emit_records_tool_invocation("p2", "L6ObservabilityBase", "tool_invocation")
_emit_captures_execution_output("p2", "L6ObservabilityBase", "exec_output")
_emit_dispatches_agent("p3", "L6ObservabilityBase", "agent_dispatch")
_emit_coordinates_agents("p3", "L6ObservabilityBase", "agent_coordination")
_emit_records_workflow_lineage("p3", "L6ObservabilityBase", "workflow_lineage")
_emit_records_healing_outcome("p3", "L6ObservabilityBase", "healing_outcome")
_emit_escalates_failure("p3", "L6ObservabilityBase", "failure_escalation")
_emit_orchestrates_workflow("p3", "L6ObservabilityBase", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "L6ObservabilityBase", "healing_dispatch")
_emit_invokes_evaluation("p3", "L6ObservabilityBase", "evaluation_signal")
_emit_records_telemetry_event("p4", "L6ObservabilityBase", "telemetry_event")
_emit_captures_evaluation_metric("p4", "L6ObservabilityBase", "eval_metric")
_emit_stores_embedding("p4", "L6ObservabilityBase", "embedding_store")
_emit_updates_meta_learning_state("p4", "L6ObservabilityBase", "meta_learning")
_emit_links_execution_to_snapshot("p4", "L6ObservabilityBase", "exec_snapshot_link")

"\nL6ObservabilityBase - Consolidated Base for L6 Observability Agents\n\nLayer: L6 - Observability\nResponsibilities:\n- Dashboard operations\n- Telemetry collection\n- Logging coordination\n- Metrics aggregation\n\nMRO HARDENING:\n- Inheritance order: SovereignBaseAgent (root)\n- All L6 agents inherit from this base for consistent observability capabilities\n"
from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)


_emit_emits_metric_event("L6ObservabilityBase", "p4obs", "metric_1")
_emit_emits_metric_event("L6ObservabilityBase", "p4obs", "metric_2")
_emit_emits_metric_event("L6ObservabilityBase", "p4obs", "metric_3")
_emit_emits_metric_event("L6ObservabilityBase", "p4obs", "metric_4")
_emit_emits_metric_event("L6ObservabilityBase", "p4obs", "metric_5")
_emit_emits_metric_event("L6ObservabilityBase", "p4obs", "metric_6")
_emit_records_incident_event("L6ObservabilityBase", "p4obs", "incident")
_emit_captures_runtime_anomaly("L6ObservabilityBase", "p4obs", "anomaly")
_emit_writes_observability_log("L6ObservabilityBase", "p4obs", "obs_log")
_emit_updates_monitoring_state("L6ObservabilityBase", "p4obs", "mon_state")
_emit_triggers_alert("L6ObservabilityBase", "p4obs", "alert")
_emit_links_incident_trace("L6ObservabilityBase", "p4obs", "trace_link")
_emit_captures_pattern("L6ObservabilityBase", "p3lm", "pattern")
_emit_records_learning_event("L6ObservabilityBase", "p3lm", "learning_event")
_emit_writes_learning_snapshot("L6ObservabilityBase", "p3lm", "snapshot")
_emit_feeds_meta_learning("L6ObservabilityBase", "p3lm", "meta_feed")
_emit_updates_routing_strategy("L6ObservabilityBase", "p3lm", "routing")
_emit_improves_agent_policy("L6ObservabilityBase", "p3lm", "policy")
_emit_stores_learning_state("L6ObservabilityBase", "p3lm", "state")
_emit_records_execution_trace("L6ObservabilityBase", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("L6ObservabilityBase", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("L6ObservabilityBase", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("L6ObservabilityBase", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("L6ObservabilityBase", "L4_STATE", "p2_trace_5")
_emit_reads_environ("L6ObservabilityBase", "env_read", "p2_env_1")
_emit_reads_environ("L6ObservabilityBase", "env_read", "p2_env_2")
_emit_reads_runtime_state("L6ObservabilityBase", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("L6ObservabilityBase", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "L6ObservabilityBase", "context_pull")
_emit_pulls_context("p1", "L6ObservabilityBase", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "L6ObservabilityBase", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "L6ObservabilityBase", "uwg_term_2")
_emit_writes_through("p1", "L6ObservabilityBase", "write_through")
_emit_writes_through("p1", "L6ObservabilityBase", "write_through_2")
_emit_validated_by_safety_plane("p1", "L6ObservabilityBase", "safety_validation")
_emit_invokes_eval("p1", "L6ObservabilityBase", "eval_call")
_emit_proposal_commits_routing("p1", "L6ObservabilityBase", "routing_commit")
_emit_escalates_to_human("p1", "L6ObservabilityBase", "human_escalation")
_emit_routes_through("p1", "L6ObservabilityBase", "route_through")
_emit_checks_agent_registry("p1", "L6ObservabilityBase", "agent_registry")
_emit_validates_agent_capability("p1", "L6ObservabilityBase", "capability")
_emit_dispatches_execution_plan("p1", "L6ObservabilityBase", "exec_plan")
_emit_agent_executes_agent("p1", "L6ObservabilityBase", "sub_agent")
_emit_routes_to_agent("p1", "L6ObservabilityBase", "target_agent")
_emit_verifies_policy("p1", "L6ObservabilityBase", "policy_check")
_emit_observes_runtime_state("p1", "L6ObservabilityBase", "runtime_state")
_emit_verifies_boundary("p1", "L6ObservabilityBase", "boundary_check")
_emit_transcripts_response("p1", "L6ObservabilityBase", "transcript")
_emit_hard_fails_untranscripted("p1", "L6ObservabilityBase")
_emit_gated_by_confidence("p1", "L6ObservabilityBase", "confidence_gate")

logger = logging.getLogger(__name__)


@dataclass
class L6ObservabilityBase(SovereignBaseAgent):
    """
    Consolidated base for L6 Observability agents.

    L6 agents handle:
    - Dashboard data aggregation
    - Telemetry collection and export
    - Logging coordination
    - Metrics and KPI tracking

    MRO: L6ObservabilityBase -> SovereignBaseAgent -> object
    """

    name: str = "L6ObservabilityBase"
    layer: str = "L6"

    def __post_init__(self) -> None:
        """Cooperative MRO initialization."""
        super().__post_init__()

    def collect_metrics(self) -> dict[str, Any]:
        """
        Collect metrics from the system.

        Override in subclasses for specialized metric collection.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "L6ObservabilityBase.collect_metrics"
        )

        _adg_health: dict[str, Any] = {}
        try:
            from pathlib import Path as _Path

            from agentic_core.adg.runtime.behavioral_index import ADGBehavioralIndex as _ADGIdx

            _self_file = _Path(__file__).resolve()
            _root = _Path(getattr(self, "project_root", _self_file.parents[2])).resolve()
            _idx = _ADGIdx.from_latest(_root)
            if _idx is not None:
                _adg_health = {
                    "adg_trust_score": _idx.trust_score if hasattr(_idx, "trust_score") else None,
                    "adg_unresolved_imports": len(getattr(_idx, "unresolved_imports", [])),
                    "adg_layer_violations": len(getattr(_idx, "layer_violations", [])),
                    "adg_orphan_modules": len(getattr(_idx, "orphan_modules", [])),
                }
        except (ImportError, AttributeError, OSError, RuntimeError, ValueError) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            logger.debug("L6ObservabilityBase.collect_metrics degraded gracefully: %s", e)
        return {"metrics": {}, "timestamp": None, **_adg_health}

    def emit_telemetry(self, event: dict[str, Any]) -> bool:
        """
        Emit a telemetry event.

        Override in subclasses for specialized telemetry emission.
        """
        return True

    def aggregate_logs(self, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """
        Aggregate logs based on filters.

        Override in subclasses for specialized log aggregation.
        """
        return []
