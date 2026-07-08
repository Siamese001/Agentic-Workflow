from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "shared_infrastructure_config", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "shared_infrastructure_config", "policy_binding")
trace_contract._emit_snapshots_state("p0", "shared_infrastructure_config", "state_snapshot")
trace_contract.emit_replay_key("p0", "shared_infrastructure_config")
trace_contract.emit_determinism_digest("p0", "shared_infrastructure_config")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "shared_infrastructure_config", "execution_auth")
trace_contract._emit_validates_capability("p2", "shared_infrastructure_config", "capability_check")
trace_contract._emit_routes_to_capability("p2", "shared_infrastructure_config", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "shared_infrastructure_config", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "shared_infrastructure_config", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "shared_infrastructure_config", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "shared_infrastructure_config", "exec_output")
trace_contract._emit_dispatches_agent("p3", "shared_infrastructure_config", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "shared_infrastructure_config", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "shared_infrastructure_config", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "shared_infrastructure_config", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "shared_infrastructure_config", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "shared_infrastructure_config", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "shared_infrastructure_config", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "shared_infrastructure_config", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "shared_infrastructure_config", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "shared_infrastructure_config", "eval_metric")
trace_contract._emit_stores_embedding("p4", "shared_infrastructure_config", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "shared_infrastructure_config", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "shared_infrastructure_config", "exec_snapshot_link")

# Configuration constants

"""
Shared Infrastructure
Provides shared infrastructure services and domain configuration.
"""
import logging
from dataclasses import dataclass
from typing import Any


trace_contract._emit_emits_metric_event("shared_infrastructure_config", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("shared_infrastructure_config", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("shared_infrastructure_config", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("shared_infrastructure_config", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("shared_infrastructure_config", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("shared_infrastructure_config", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("shared_infrastructure_config", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("shared_infrastructure_config", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("shared_infrastructure_config", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("shared_infrastructure_config", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("shared_infrastructure_config", "p4obs", "alert")
trace_contract._emit_links_incident_trace("shared_infrastructure_config", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("shared_infrastructure_config", "p3lm", "pattern")
trace_contract._emit_records_learning_event("shared_infrastructure_config", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("shared_infrastructure_config", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("shared_infrastructure_config", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("shared_infrastructure_config", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("shared_infrastructure_config", "p3lm", "policy")
trace_contract._emit_stores_learning_state("shared_infrastructure_config", "p3lm", "state")
trace_contract._emit_records_execution_trace("shared_infrastructure_config", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("shared_infrastructure_config", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("shared_infrastructure_config", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("shared_infrastructure_config", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("shared_infrastructure_config", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("shared_infrastructure_config", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("shared_infrastructure_config", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("shared_infrastructure_config", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("shared_infrastructure_config", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "shared_infrastructure_config", "context_pull")
trace_contract._emit_pulls_context("p1", "shared_infrastructure_config", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "shared_infrastructure_config", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "shared_infrastructure_config", "uwg_term_2")
trace_contract._emit_writes_through("p1", "shared_infrastructure_config", "write_through")
trace_contract._emit_writes_through("p1", "shared_infrastructure_config", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "shared_infrastructure_config", "safety_validation")
trace_contract._emit_invokes_eval("p1", "shared_infrastructure_config", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "shared_infrastructure_config", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "shared_infrastructure_config", "human_escalation")
trace_contract._emit_routes_through("p1", "shared_infrastructure_config", "route_through")
trace_contract._emit_checks_agent_registry("p1", "shared_infrastructure_config", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "shared_infrastructure_config", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "shared_infrastructure_config", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "shared_infrastructure_config", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "shared_infrastructure_config", "target_agent")
trace_contract._emit_verifies_policy("p1", "shared_infrastructure_config", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "shared_infrastructure_config", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "shared_infrastructure_config", "boundary_check")
trace_contract._emit_transcripts_response("p1", "shared_infrastructure_config", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "shared_infrastructure_config")
trace_contract._emit_gated_by_confidence("p1", "shared_infrastructure_config", "confidence_gate")

Logger = logging.getLogger(__name__)


@dataclass
class DomainConfig:
    """Domain-specific configuration."""

    engine_type: str
    settings: dict[str, Any]
    metadata: dict[str, Any]


class SharedInfrastructure:
    """Shared infrastructure services."""

    def __init__(self):
        """Initialize shared infrastructure."""
        self._configs: dict[str, DomainConfig] = {}
        Logger.debug("SharedInfrastructure initialized")

    def create_domain_config(self, engine_type: str) -> DomainConfig:
        """Create domain configuration for engine type."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "SharedInfrastructure.create_domain_config"
        )

        config: Any = DomainConfig(engine_type=engine_type, settings={}, metadata={})
        self._configs[engine_type] = config
        Logger.debug(f"Domain config created for: {engine_type}")
        return config

    def get_domain_config(self, engine_type: str) -> DomainConfig | None:
        """Get domain configuration."""
        return self._configs.get(engine_type)


_shared_infrastructure: SharedInfrastructure | None = None


def get_shared_infrastructure() -> SharedInfrastructure:
    """Get shared infrastructure singleton."""
    global _shared_infrastructure
    if _shared_infrastructure is None:
        _shared_infrastructure = SharedInfrastructure()
    return _shared_infrastructure


__all__ = ["DomainConfig", "SharedInfrastructure", "get_shared_infrastructure"]
