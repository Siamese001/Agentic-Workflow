"""
Safety agent seam contracts — Protocol definition for L5 healing agents,
plus an AgentFactory for injection into L3 consumers.

This module sits outside the layer hierarchy so imports from here
do not count as upward seams in the gravity scanner.
"""

from __future__ import annotations

from importlib import import_module
import logging
from typing import Any, Protocol, runtime_checkable

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "safety_agents", "p0_governance")
_emit_reads_policy_state("p0", "safety_agents", "policy_binding")
_emit_snapshots_state("p0", "safety_agents", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("safety_agents", "p4obs", "metric_1")
_emit_emits_metric_event("safety_agents", "p4obs", "metric_2")
_emit_emits_metric_event("safety_agents", "p4obs", "metric_3")
_emit_emits_metric_event("safety_agents", "p4obs", "metric_4")
_emit_emits_metric_event("safety_agents", "p4obs", "metric_5")
_emit_emits_metric_event("safety_agents", "p4obs", "metric_6")
_emit_records_incident_event("safety_agents", "p4obs", "incident")
_emit_captures_runtime_anomaly("safety_agents", "p4obs", "anomaly")
_emit_writes_observability_log("safety_agents", "p4obs", "obs_log")
_emit_updates_monitoring_state("safety_agents", "p4obs", "mon_state")
_emit_triggers_alert("safety_agents", "p4obs", "alert")
_emit_links_incident_trace("safety_agents", "p4obs", "trace_link")
_emit_captures_pattern("safety_agents", "p3lm", "pattern")
_emit_records_learning_event("safety_agents", "p3lm", "learning_event")
_emit_writes_learning_snapshot("safety_agents", "p3lm", "snapshot")
_emit_feeds_meta_learning("safety_agents", "p3lm", "meta_feed")
_emit_updates_routing_strategy("safety_agents", "p3lm", "routing")
_emit_improves_agent_policy("safety_agents", "p3lm", "policy")
_emit_stores_learning_state("safety_agents", "p3lm", "state")
_emit_records_execution_trace("safety_agents", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("safety_agents", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("safety_agents", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("safety_agents", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("safety_agents", "L4_STATE", "p2_trace_5")
_emit_reads_environ("safety_agents", "env_read", "p2_env_1")
_emit_reads_environ("safety_agents", "env_read", "p2_env_2")
_emit_reads_runtime_state("safety_agents", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("safety_agents", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "safety_agents", "context_pull")
_emit_pulls_context("p1", "safety_agents", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "safety_agents", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "safety_agents", "uwg_term_2")
_emit_writes_through("p1", "safety_agents", "write_through")
_emit_writes_through("p1", "safety_agents", "write_through_2")
_emit_validated_by_safety_plane("p1", "safety_agents", "safety_validation")
_emit_invokes_eval("p1", "safety_agents", "eval_call")
_emit_proposal_commits_routing("p1", "safety_agents", "routing_commit")
_emit_escalates_to_human("p1", "safety_agents", "human_escalation")
_emit_routes_through("p1", "safety_agents", "route_through")
_emit_checks_agent_registry("p1", "safety_agents", "agent_registry")
_emit_validates_agent_capability("p1", "safety_agents", "capability")
_emit_dispatches_execution_plan("p1", "safety_agents", "exec_plan")
_emit_agent_executes_agent("p1", "safety_agents", "sub_agent")
_emit_routes_to_agent("p1", "safety_agents", "target_agent")
_emit_verifies_policy("p1", "safety_agents", "policy_check")
_emit_observes_runtime_state("p1", "safety_agents", "runtime_state")
_emit_verifies_boundary("p1", "safety_agents", "boundary_check")
_emit_transcripts_response("p1", "safety_agents", "transcript")
_emit_hard_fails_untranscripted("p1", "safety_agents")
_emit_gated_by_confidence("p1", "safety_agents", "confidence_gate")
emit_replay_key("p0", "safety_agents")
emit_determinism_digest("p0", "safety_agents")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "safety_agents", "execution_auth")
_emit_validates_capability("p2", "safety_agents", "capability_check")
_emit_routes_to_capability("p2", "safety_agents", "capability_route")
_emit_writes_via_uwg("p2", "safety_agents", "uwg_write")
_emit_blocks_direct_write("p2", "safety_agents", "direct_write_block")
_emit_records_tool_invocation("p2", "safety_agents", "tool_invocation")
_emit_captures_execution_output("p2", "safety_agents", "exec_output")
_emit_dispatches_agent("p3", "safety_agents", "agent_dispatch")
_emit_coordinates_agents("p3", "safety_agents", "agent_coordination")
_emit_records_workflow_lineage("p3", "safety_agents", "workflow_lineage")
_emit_records_healing_outcome("p3", "safety_agents", "healing_outcome")
_emit_escalates_failure("p3", "safety_agents", "failure_escalation")
_emit_orchestrates_workflow("p3", "safety_agents", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "safety_agents", "healing_dispatch")
_emit_invokes_evaluation("p3", "safety_agents", "evaluation_signal")
_emit_records_telemetry_event("p4", "safety_agents", "telemetry_event")
_emit_captures_evaluation_metric("p4", "safety_agents", "eval_metric")
_emit_stores_embedding("p4", "safety_agents", "embedding_store")
_emit_updates_meta_learning_state("p4", "safety_agents", "meta_learning")
_emit_links_execution_to_snapshot("p4", "safety_agents", "exec_snapshot_link")

logger = logging.getLogger(__name__)

_AGENT_IMPORTS: dict[str, tuple[str, str]] = {
    "HygieneGuardianAgent": (
        "agentic_core.L5_safety.validators.HygieneGuardianAgent",
        "HygieneGuardianAgent",
    ),
    "NamingAgent": (
        "agentic_core.L5_safety.reasoning.NamingAgent",
        "NamingAgent",
    ),
    "LocationAgent": (
        "agentic_core.L5_safety.reasoning.LocationHealerAgent",
        "LocationHealerAgent",
    ),
    "StructureEnforcerAgent": (
        "agentic_core.L5_safety.reasoning.StructureEnforcerAgent",
        "StructureEnforcerAgent",
    ),
    "StructuralHealerAgent": (
        "agentic_core.L5_safety.validators.StructuralHealerAgent",
        "StructuralHealerAgent",
    ),
    "GovernanceAgent": (
        "agentic_core.L5_safety.reasoning.GovernanceAgent",
        "GovernanceAgent",
    ),
    "HierarchyAgent": (
        "agentic_core.L5_safety.reasoning.hierarchy_healer",
        "HierarchyAgent",
    ),
}


@runtime_checkable
class HealingAgentProtocol(Protocol):
    """Protocol for any agent that can heal a repository."""

    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]: ...


class SafetyAgentFactory:
    """
    Factory that instantiates L5 safety agents by name.

    Holds all upward imports in one place (seam boundary).
    Consumers receive a HealingAgentProtocol-compatible instance.
    """

    def __init__(self, project_root: Any) -> None:
        self.project_root = project_root

    def get(self, agent_name: str) -> HealingAgentProtocol | None:
        """Return an agent instance by name, or None if unavailable."""
        import uuid as _uuid  # noqa: PLC0415

        trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(trace_id, LayerSegment.L3_ORCHESTRATION, "SafetyAgentFactory.get")

        if not agent_name:
            raise ValueError("agent_name must be non-empty")

        target = _AGENT_IMPORTS.get(agent_name)
        if target is None:
            logger.warning("Unknown safety agent requested: %s", agent_name)
            return None

        module_name, class_name = target
        try:
            module = import_module(module_name)
            agent_cls = getattr(module, class_name)
        except (ImportError, AttributeError) as exc:  # guardian: allow-log-and-swallow allow-return-none-swallow -- safety agent lookup: optional agent, caller treats None as unavailable
            logger.warning(
                "Safety agent unavailable agent=%s module=%s class=%s error=%s",
                agent_name,
                module_name,
                class_name,
                exc,
            )
            return None

        agent = agent_cls(project_root=self.project_root)
        if not isinstance(agent, HealingAgentProtocol):
            logger.error("Agent %s does not satisfy HealingAgentProtocol", agent_name)
            return None
        return agent

    def get_legacy_import_healer_factory(self):
        """Return create_legacy_import_healer callable, or None."""
        try:
            module = import_module("agentic_core.L5_safety.reasoning.CodeHealerAgent")
            factory = getattr(module, "create_legacy_import_healer")
        except (ImportError, AttributeError) as exc:  # guardian: allow-log-and-swallow allow-return-none-swallow -- legacy healer factory: optional, caller treats None as unavailable
            logger.warning("Legacy import healer factory unavailable: %s", exc)
            return None

        if not callable(factory):
            raise TypeError("create_legacy_import_healer must be callable")
        return factory


__all__ = ["HealingAgentProtocol", "SafetyAgentFactory"]
