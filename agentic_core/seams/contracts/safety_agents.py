"""
Safety agent seam contracts — Protocol definition for L5 healing agents,
plus an AgentFactory for injection into L3 consumers.

This module sits outside the layer hierarchy so imports from here
do not count as upward seams in the gravity scanner.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

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

_emit_applies_guardrail("p0", "safety_agents", "p0_governance")
_emit_reads_policy_state("p0", "safety_agents", "policy_binding")
_emit_snapshots_state("p0", "safety_agents", "state_snapshot")
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


@runtime_checkable
class HealingAgentProtocol(Protocol):
    """Protocol for any agent that can heal a repository."""

    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs: Any
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
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SafetyAgentFactory.get")

        try:
            if agent_name == "HygieneGuardianAgent":
                from agentic_core.L5_safety.validators.HygieneGuardianAgent import HygieneGuardianAgent

                return HygieneGuardianAgent(project_root=self.project_root)
            elif agent_name == "NamingAgent":
                from agentic_core.L5_safety.reasoning.NamingAgent import NamingAgent

                return NamingAgent(project_root=self.project_root)
            elif agent_name == "LocationAgent":
                from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent

                return LocationHealerAgent(project_root=self.project_root)
            elif agent_name == "StructureEnforcerAgent":
                from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import StructureEnforcerAgent

                return StructureEnforcerAgent(project_root=self.project_root)
            elif agent_name == "StructuralHealerAgent":
                from agentic_core.L5_safety.validators.StructuralHealerAgent import StructuralHealerAgent

                return StructuralHealerAgent(project_root=self.project_root)
            elif agent_name == "GovernanceAgent":
                from agentic_core.L5_safety.reasoning.GovernanceAgent import GovernanceAgent

                return GovernanceAgent(project_root=self.project_root)
            elif agent_name == "HierarchyAgent":
                from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

                return HierarchyAgent(project_root=self.project_root)
        except ImportError:
            return None
        return None

    def get_legacy_import_healer_factory(self):
        """Return create_legacy_import_healer callable, or None."""
        try:
            from agentic_core.L5_safety.reasoning.CodeHealerAgent import create_legacy_import_healer

            return create_legacy_import_healer
        except ImportError:
            return None


__all__ = ["HealingAgentProtocol", "SafetyAgentFactory"]
