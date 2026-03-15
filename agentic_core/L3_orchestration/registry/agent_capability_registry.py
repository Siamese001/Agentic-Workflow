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
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

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
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AgentCapabilityRegistry.register")

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
