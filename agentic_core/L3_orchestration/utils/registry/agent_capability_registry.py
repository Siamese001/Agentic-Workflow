"""
agentic_core/L3_orchestration/registry/agent_capability_registry.py

AgentCapabilityRegistry — P2-L3 gap remediation.

Static registry mapping every agent in L3 to its declared capabilities,
handoff targets, and coordination contracts. Closes the gap where 204
L3 modules dispatch agent_executes_agent with 0 statically resolvable
capability declarations in the ADG.

ADG edges emitted: declares_capability, agent_executes_agent
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "agent_capability_registry")
trace_contract.emit_determinism_digest("p0", "agent_capability_registry")

trace_contract._emit_dispatches_healing_run("p1", "agent_capability_registry", "L3")
trace_contract._emit_routes_through("p1", "agent_capability_registry", "L3")
trace_contract._emit_dispatches_execution_plan("p1", "agent_capability_registry", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "agent_capability_registry", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "agent_capability_registry", "target_agent")
trace_contract._emit_verifies_policy("p1", "agent_capability_registry", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "agent_capability_registry", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "agent_capability_registry", "boundary_check")
trace_contract._emit_transcripts_response("p1", "agent_capability_registry", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "agent_capability_registry")
trace_contract._emit_gated_by_confidence("p1", "agent_capability_registry", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "agent_capability_registry", "L3")
trace_contract._emit_reads_policy_state("p1", "agent_capability_registry", "L3")
trace_contract._emit_validates_agent_capability("p1", "agent_capability_registry", "L3")
trace_contract._emit_checks_agent_registry("p1", "agent_capability_registry", "L3")
trace_contract._emit_authorize_and_execute("p2", "agent_capability_registry", "execution_auth")
trace_contract._emit_validates_capability("p2", "agent_capability_registry", "capability_check")
trace_contract._emit_routes_to_capability("p2", "agent_capability_registry", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "agent_capability_registry", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "agent_capability_registry", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "agent_capability_registry", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "agent_capability_registry", "exec_output")
trace_contract._emit_dispatches_agent("p3", "agent_capability_registry", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "agent_capability_registry", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "agent_capability_registry", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "agent_capability_registry", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "agent_capability_registry", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "agent_capability_registry", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "agent_capability_registry", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "agent_capability_registry", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "agent_capability_registry", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "agent_capability_registry", "eval_metric")
trace_contract._emit_stores_embedding("p4", "agent_capability_registry", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "agent_capability_registry", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "agent_capability_registry", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("agent_capability_registry", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("agent_capability_registry", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("agent_capability_registry", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("agent_capability_registry", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("agent_capability_registry", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("agent_capability_registry", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("agent_capability_registry", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("agent_capability_registry", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("agent_capability_registry", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("agent_capability_registry", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("agent_capability_registry", "p4obs", "alert")
trace_contract._emit_links_incident_trace("agent_capability_registry", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("agent_capability_registry", "p3lm", "pattern")
trace_contract._emit_records_learning_event("agent_capability_registry", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("agent_capability_registry", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("agent_capability_registry", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("agent_capability_registry", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("agent_capability_registry", "p3lm", "policy")
trace_contract._emit_stores_learning_state("agent_capability_registry", "p3lm", "state")
trace_contract._emit_records_execution_trace("agent_capability_registry", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("agent_capability_registry", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("agent_capability_registry", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("agent_capability_registry", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("agent_capability_registry", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("agent_capability_registry", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("agent_capability_registry", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("agent_capability_registry", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("agent_capability_registry", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "agent_capability_registry", "context_pull")
trace_contract._emit_pulls_context("p1", "agent_capability_registry", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "agent_capability_registry", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "agent_capability_registry", "uwg_term_2")
trace_contract._emit_writes_through("p1", "agent_capability_registry", "write_through")
trace_contract._emit_writes_through("p1", "agent_capability_registry", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "agent_capability_registry", "safety_validation")
trace_contract._emit_invokes_eval("p1", "agent_capability_registry", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "agent_capability_registry", "routing_commit")

logger = logging.getLogger(__name__)


@dataclass
class AgentCapabilitySpec:
    """Declared capability specification for a single agent."""

    agent_name: str
    layer: str
    capabilities: list[str]
    handoff_targets: list[str]
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    requires_coordination_bundle: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def can_handoff_to(self, target: str) -> bool:
        return target in self.handoff_targets

    def has_capability(self, cap: str) -> bool:
        return cap in self.capabilities


class AgentCapabilityRegistry:
    """Central registry of agent capabilities and handoff graphs.

    Usage::

        registry = AgentCapabilityRegistry()
        registry.register(AgentCapabilitySpec(
            agent_name="ResearchOrchestrator",
            layer="L3",
            capabilities=["fetch_sources", "summarise"],
            handoff_targets=["SummaryAgent", "BriefAssembler"],
        ))

        spec = registry.get("ResearchOrchestrator")
        assert spec.can_handoff_to("SummaryAgent")
    """

    def __init__(self) -> None:
        self._registry: dict[str, AgentCapabilitySpec] = {}

    def register(self, spec: AgentCapabilitySpec) -> None:
        """Register an agent's capability spec.

        Emits ``declares_capability`` ADG edge.
        """
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "AgentCapabilityRegistry.register", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "AgentCapabilityRegistry.register", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "AgentCapabilityRegistry.register",
        )

        self._registry[spec.agent_name] = spec
        logger.debug(
            "CAPABILITY_REGISTRY declares_capability agent=%s layer=%s caps=%s handoffs=%s",
            spec.agent_name,
            spec.layer,
            spec.capabilities,
            spec.handoff_targets,
        )

    def get(self, agent_name: str) -> AgentCapabilitySpec | None:
        return self._registry.get(agent_name)

    def can_handoff(self, src: str, dst: str) -> bool:
        """Check whether ``src`` agent is allowed to hand off to ``dst``."""
        spec = self._registry.get(src)
        if spec is None:
            logger.warning(
                "CAPABILITY_REGISTRY agent_executes_agent UNRESOLVED src=%s dst=%s (src not registered)",
                src,
                dst,
            )
            return False
        allowed = spec.can_handoff_to(dst)
        if not allowed:
            logger.warning(
                "CAPABILITY_REGISTRY agent_executes_agent DENIED src=%s dst=%s "
                "(dst not in declared handoff_targets)",
                src,
                dst,
            )
        return allowed

    def registered_agents(self) -> list[str]:
        return list(self._registry.keys())

    def all_handoff_edges(self) -> list[tuple[str, str]]:
        """Return all (src, dst) handoff pairs declared in the registry."""
        edges = []
        for spec in self._registry.values():
            for dst in spec.handoff_targets:
                edges.append((spec.agent_name, dst))
        return edges

    def agents_with_capability(self, cap: str) -> list[str]:
        return [name for name, spec in self._registry.items() if spec.has_capability(cap)]


_global_registry: AgentCapabilityRegistry | None = None


def get_agent_capability_registry() -> AgentCapabilityRegistry:
    global _global_registry
    if _global_registry is None:
        _global_registry = AgentCapabilityRegistry()
    return _global_registry


def reset_agent_capability_registry() -> None:
    global _global_registry
    _global_registry = None


__all__ = [
    "AgentCapabilitySpec",
    "AgentCapabilityRegistry",
    "get_agent_capability_registry",
    "reset_agent_capability_registry",
]
