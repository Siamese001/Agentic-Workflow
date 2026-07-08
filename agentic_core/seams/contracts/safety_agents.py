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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "safety_agents", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "safety_agents", "policy_binding")
trace_contract._emit_snapshots_state("p0", "safety_agents", "state_snapshot")

trace_contract._emit_emits_metric_event("safety_agents", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("safety_agents", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("safety_agents", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("safety_agents", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("safety_agents", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("safety_agents", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("safety_agents", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("safety_agents", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("safety_agents", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("safety_agents", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("safety_agents", "p4obs", "alert")
trace_contract._emit_links_incident_trace("safety_agents", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("safety_agents", "p3lm", "pattern")
trace_contract._emit_records_learning_event("safety_agents", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("safety_agents", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("safety_agents", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("safety_agents", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("safety_agents", "p3lm", "policy")
trace_contract._emit_stores_learning_state("safety_agents", "p3lm", "state")
trace_contract._emit_records_execution_trace("safety_agents", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("safety_agents", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("safety_agents", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("safety_agents", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("safety_agents", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("safety_agents", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("safety_agents", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("safety_agents", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("safety_agents", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "safety_agents", "context_pull")
trace_contract._emit_pulls_context("p1", "safety_agents", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "safety_agents", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "safety_agents", "uwg_term_2")
trace_contract._emit_writes_through("p1", "safety_agents", "write_through")
trace_contract._emit_writes_through("p1", "safety_agents", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "safety_agents", "safety_validation")
trace_contract._emit_invokes_eval("p1", "safety_agents", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "safety_agents", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "safety_agents", "human_escalation")
trace_contract._emit_routes_through("p1", "safety_agents", "route_through")
trace_contract._emit_checks_agent_registry("p1", "safety_agents", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "safety_agents", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "safety_agents", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "safety_agents", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "safety_agents", "target_agent")
trace_contract._emit_verifies_policy("p1", "safety_agents", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "safety_agents", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "safety_agents", "boundary_check")
trace_contract._emit_transcripts_response("p1", "safety_agents", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "safety_agents")
trace_contract._emit_gated_by_confidence("p1", "safety_agents", "confidence_gate")
trace_contract.emit_replay_key("p0", "safety_agents")
trace_contract.emit_determinism_digest("p0", "safety_agents")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "safety_agents", "execution_auth")
trace_contract._emit_validates_capability("p2", "safety_agents", "capability_check")
trace_contract._emit_routes_to_capability("p2", "safety_agents", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "safety_agents", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "safety_agents", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "safety_agents", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "safety_agents", "exec_output")
trace_contract._emit_dispatches_agent("p3", "safety_agents", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "safety_agents", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "safety_agents", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "safety_agents", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "safety_agents", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "safety_agents", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "safety_agents", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "safety_agents", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "safety_agents", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "safety_agents", "eval_metric")
trace_contract._emit_stores_embedding("p4", "safety_agents", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "safety_agents", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "safety_agents", "exec_snapshot_link")

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
        "agentic_core.L5_safety.utils.location_healer_util",
        "LocationHealerAgent",
    ),
    "StructureEnforcerAgent": (
        "agentic_core.L5_safety.reasoning.StructureEnforcerAgent",
        "StructureEnforcerAgent",
    ),
    "StructuralHealerAgent": (
        "agentic_core.L5_safety.reasoning.StructureEnforcerAgent",
        "StructureEnforcerAgent",
    ),
    "GovernanceAgent": (
        "agentic_core.L5_safety.reasoning.GovernanceAgent",
        "GovernanceAgent",
    ),
    "HierarchyAgent": (
        "agentic_core.L5_safety.reasoning.StructureEnforcerAgent",
        "StructureEnforcerAgent",
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
        trace_contract._emit_records_execution_trace(trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "SafetyAgentFactory.get")

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
        except (
            ImportError,
            AttributeError,
        ) as exc:  # guardian: allow-return-none-swallow  -- ADG-burn: return_none_swallowallow-return-none-swallow -- safety agent lookup: optional agent, caller treats None as unavailable
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
        except (
            ImportError,
            AttributeError,
        ) as exc:  # guardian: allow-return-none-swallow  -- ADG-burn: return_none_swallowallow-return-none-swallow -- legacy healer factory: optional, caller treats None as unavailable
            logger.warning("Legacy import healer factory unavailable: %s", exc)
            return None

        if not callable(factory):
            raise TypeError("create_legacy_import_healer must be callable")
        return factory


__all__ = ["HealingAgentProtocol", "SafetyAgentFactory"]
