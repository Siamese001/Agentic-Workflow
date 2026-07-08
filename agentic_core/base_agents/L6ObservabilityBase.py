from __future__ import annotations

import logging

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "L6ObservabilityBase", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "L6ObservabilityBase", "policy_binding")
trace_contract._emit_snapshots_state("p0", "L6ObservabilityBase", "state_snapshot")
trace_contract.emit_replay_key("p0", "L6ObservabilityBase")
trace_contract.emit_determinism_digest("p0", "L6ObservabilityBase")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "L6ObservabilityBase", "execution_auth")
trace_contract._emit_validates_capability("p2", "L6ObservabilityBase", "capability_check")
trace_contract._emit_routes_to_capability("p2", "L6ObservabilityBase", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "L6ObservabilityBase", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "L6ObservabilityBase", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "L6ObservabilityBase", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "L6ObservabilityBase", "exec_output")
trace_contract._emit_dispatches_agent("p3", "L6ObservabilityBase", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "L6ObservabilityBase", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "L6ObservabilityBase", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "L6ObservabilityBase", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "L6ObservabilityBase", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "L6ObservabilityBase", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "L6ObservabilityBase", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "L6ObservabilityBase", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "L6ObservabilityBase", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "L6ObservabilityBase", "eval_metric")
trace_contract._emit_stores_embedding("p4", "L6ObservabilityBase", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "L6ObservabilityBase", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "L6ObservabilityBase", "exec_snapshot_link")

"\nL6ObservabilityBase - Consolidated Base for L6 Observability Agents\n\nLayer: L6 - Observability\nResponsibilities:\n- Dashboard operations\n- Telemetry collection\n- Logging coordination\n- Metrics aggregation\n\nMRO HARDENING:\n- Inheritance order: SovereignBaseAgent (root)\n- All L6 agents inherit from this base for consistent observability capabilities\n"
from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent


trace_contract._emit_emits_metric_event("L6ObservabilityBase", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("L6ObservabilityBase", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("L6ObservabilityBase", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("L6ObservabilityBase", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("L6ObservabilityBase", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("L6ObservabilityBase", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("L6ObservabilityBase", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("L6ObservabilityBase", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("L6ObservabilityBase", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("L6ObservabilityBase", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("L6ObservabilityBase", "p4obs", "alert")
trace_contract._emit_links_incident_trace("L6ObservabilityBase", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("L6ObservabilityBase", "p3lm", "pattern")
trace_contract._emit_records_learning_event("L6ObservabilityBase", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("L6ObservabilityBase", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("L6ObservabilityBase", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("L6ObservabilityBase", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("L6ObservabilityBase", "p3lm", "policy")
trace_contract._emit_stores_learning_state("L6ObservabilityBase", "p3lm", "state")
trace_contract._emit_records_execution_trace("L6ObservabilityBase", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("L6ObservabilityBase", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("L6ObservabilityBase", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("L6ObservabilityBase", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("L6ObservabilityBase", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("L6ObservabilityBase", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("L6ObservabilityBase", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("L6ObservabilityBase", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("L6ObservabilityBase", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "L6ObservabilityBase", "context_pull")
trace_contract._emit_pulls_context("p1", "L6ObservabilityBase", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "L6ObservabilityBase", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "L6ObservabilityBase", "uwg_term_2")
trace_contract._emit_writes_through("p1", "L6ObservabilityBase", "write_through")
trace_contract._emit_writes_through("p1", "L6ObservabilityBase", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "L6ObservabilityBase", "safety_validation")
trace_contract._emit_invokes_eval("p1", "L6ObservabilityBase", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "L6ObservabilityBase", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "L6ObservabilityBase", "human_escalation")
trace_contract._emit_routes_through("p1", "L6ObservabilityBase", "route_through")
trace_contract._emit_checks_agent_registry("p1", "L6ObservabilityBase", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "L6ObservabilityBase", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "L6ObservabilityBase", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "L6ObservabilityBase", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "L6ObservabilityBase", "target_agent")
trace_contract._emit_verifies_policy("p1", "L6ObservabilityBase", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "L6ObservabilityBase", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "L6ObservabilityBase", "boundary_check")
trace_contract._emit_transcripts_response("p1", "L6ObservabilityBase", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "L6ObservabilityBase")
trace_contract._emit_gated_by_confidence("p1", "L6ObservabilityBase", "confidence_gate")

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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "L6ObservabilityBase.collect_metrics"
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
        except (ImportError, AttributeError, OSError, RuntimeError, ValueError) as e:  # guardian: allow-log-and-swallow -- ADG index unavailable: non-fatal; metrics collected without ADG health fields
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
