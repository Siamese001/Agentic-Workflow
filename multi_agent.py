# FILE: multi_agent.py
"""
Multi-Agent Coordination Patterns (v10_9) — ENTERPRISE MODULE

This module defines generic multi-agent coordination patterns for the
v10_9 agentic architecture. It lives in the META layer (above L1–L5)
and extends the minimal QA council support provided in agents.py.

Responsibilities:
    • Provide reusable AgentGraph patterns (pipeline, council, committee).
    • Provide deterministic delegation & voting logic for agent groups.
    • Provide a generic MultiAgentCoordinator that can:
        - route messages between agents,
        - compute votes,
        - produce metadata suitable for L4 patching.

Non-responsibilities:
    • NO L1 cognition (no planning).
    • NO L2 execution (no tool calls, no LLM calls).
    • NO L3 DAG orchestration (no direct control-flow).
    • NO L4 state mutation (returns dicts; callers apply patches).
    • NO L5 safety/policy decisions.

This module is designed to be used by:
    • L3 Orchestrators (to add multi-agent meta-passes).
    • Meta-learning or evaluation stacks (to simulate councils).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Tuple, Optional

from agents import AgentRole, AgentNode, AgentGraph, summarize_graph


# =============================================================================
# 1. MULTI-AGENT PATTERNS
# =============================================================================


class MultiAgentPattern(str, Enum):
    """
    High-level patterns for multi-agent graphs.

    These are *meta* structures; they do not execute tools or LLMs.
    """

    LINEAR_PIPELINE = "linear_pipeline"
    STAR_HUB = "star_hub"
    COUNCIL = "council"
    COMMITTEE = "committee"


def build_linear_pipeline(roles: List[AgentRole]) -> AgentGraph:
    """
    Build a linear pipeline graph: r0 → r1 → r2 → ...

    Example:
        [PLANNER, RETRIEVER, DRAFTER, QA, SAFETY]
    """
    nodes = [AgentNode(r, {}) for r in roles]
    edges: List[Tuple[AgentRole, AgentRole]] = []
    for i in range(len(roles) - 1):
        edges.append((roles[i], roles[i + 1]))
    return AgentGraph(nodes=nodes, edges=edges)


def build_star_hub(hub: AgentRole, spokes: List[AgentRole]) -> AgentGraph:
    """
    Build a star-hub graph: hub ↔ each spoke (bidirectional edges).

    This is conceptual; edges are for visualization and routing hints.
    """
    nodes = [AgentNode(hub, {})] + [AgentNode(s, {}) for s in spokes]
    edges: List[Tuple[AgentRole, AgentRole]] = []
    for s in spokes:
        edges.append((hub, s))
        edges.append((s, hub))
    return AgentGraph(nodes=nodes, edges=edges)


def build_council(role: AgentRole, size: int) -> AgentGraph:
    """
    Build a council graph: N agents with the same role, no edges
    (parallel evaluation).

    Example:
        COUNCIL(AgentRole.QA, size=3)
    """
    size = max(1, int(size))
    nodes = [AgentNode(role, {"id": i + 1, "weight": 1.0}) for i in range(size)]
    edges: List[Tuple[AgentRole, AgentRole]] = []
    return AgentGraph(nodes=nodes, edges=edges)


def build_committee(roles: List[AgentRole]) -> AgentGraph:
    """
    Build a committee graph: each role appears exactly once; no edges.
    This represents a group of independent specialists.

    Example:
        [PLANNER, DRAFTER, QA, SAFETY]
    """
    nodes = [AgentNode(r, {}) for r in roles]
    edges: List[Tuple[AgentRole, AgentRole]] = []
    return AgentGraph(nodes=nodes, edges=edges)


# =============================================================================
# 2. DETERMINISTIC ROUTING & VOTING HELPERS
# =============================================================================


@dataclass
class AgentMessage:
    """
    Generic message exchanged between agents at the meta layer.
    """

    sender: AgentRole
    recipient: AgentRole
    content: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


def can_delegate(from_role: AgentRole, to_role: AgentRole) -> bool:
    """
    Deterministic fixed delegation policy for demonstration:

        • PLANNER  → RETRIEVER, DRAFTER, QA
        • RETRIEVER→ DRAFTER
        • DRAFTER  → QA
        • QA       → SAFETY

    Other combinations are not permitted.
    """
    if from_role == AgentRole.PLANNER:
        return to_role in {AgentRole.RETRIEVER, AgentRole.DRAFTER, AgentRole.QA}
    if from_role == AgentRole.RETRIEVER:
        return to_role == AgentRole.DRAFTER
    if from_role == AgentRole.DRAFTER:
        return to_role == AgentRole.QA
    if from_role == AgentRole.QA:
        return to_role == AgentRole.SAFETY
    return False


def delegation_metadata(sender: AgentRole, recipient: AgentRole) -> Dict[str, Any]:
    """
    Build a deterministic delegation record showing whether a delegation
    is permitted between two roles.
    """
    return {
        "from": sender.value,
        "to": recipient.value,
        "allowed": can_delegate(sender, recipient),
    }


def deterministic_vote(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deterministic selection:
        • Highest score wins.
        • Ties broken by smallest id.

    This helper is used in council-style patterns.
    """
    if not candidates:
        return {"id": None, "score": 0.0, "rationale": "no_candidates"}

    sorted_candidates = sorted(
        candidates,
        key=lambda c: (-float(c.get("score", 0.0)), int(c.get("id", 999999))),
    )
    return sorted_candidates[0]


# =============================================================================
# 3. MULTI-AGENT COORDINATOR
# =============================================================================


@dataclass
class MultiAgentCoordinator:
    """
    Generic multi-agent coordinator.

    It holds:
        • an AgentGraph
        • minimal deterministic delegation/voting policies

    It does NOT:
        • execute tools/LLMs
        • own safety or state mutation

    Callers use this to:
        • compute routing suggestions
        • compute council votes
        • attach "multi_agent" metadata into state via StatePatch at L4.
    """

    graph: AgentGraph

    def _find_node_for_role(self, role: AgentRole) -> Optional[AgentNode]:
        for node in self.graph.nodes:
            if node.role == role:
                return node
        return None

    def summarize(self) -> Dict[str, Any]:
        """
        Return a deterministic summary of the underlying graph.
        """
        return summarize_graph(self.graph)

    def route_message(self, message: AgentMessage) -> Dict[str, Any]:
        """
        Compute routing metadata for a single AgentMessage.

        Returns:
            {
              "sender": <role>,
              "recipient": <role or None>,
              "allowed": bool,
              "graph_summary": {...}
            }
        """
        sender = message.sender
        recipient = message.recipient

        if not self._find_node_for_role(recipient):
            # Recipient not in graph; drop message.
            allowed = False
        else:
            allowed = can_delegate(sender, recipient)

        return {
            "last_message": {
                "content": message.content,
                "sender": sender.value,
                "recipient": recipient.value,
            },
            "sender": sender.value,
            "recipient": recipient.value if allowed else None,
            "delegation": delegation_metadata(sender, recipient),
            "graph_summary": self.summarize(),
        }

    def council_vote(
        self,
        role: AgentRole,
        candidates: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Run a council-like vote for all nodes with the given role.

        Example:
            role = AgentRole.QA
            candidates = [
              {"id": 1, "score": 0.71, "rationale": "..."},
              {"id": 2, "score": 0.68, "rationale": "..."},
            ]
        """
        council_nodes = [n for n in self.graph.nodes if n.role == role]
        if not council_nodes:
            return {
                "selected": {"id": None, "score": 0.0, "rationale": "no_council_members"},
                "candidates": candidates,
                "graph_summary": self.summarize(),
            }

        winner = deterministic_vote(candidates)
        return {
            "selected": winner,
            "candidates": candidates,
            "graph_summary": self.summarize(),
        }

    def build_state_patch(self, block_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convenience helper for L3/L4: return a dict that can be used
        as a value in a StatePatch(key=block_name, value=payload).

        Example:
            patch = coordinator.build_state_patch("multi_agent", {...})
            state_adapter.apply_patch(StatePatch(key="multi_agent", value=patch["multi_agent"]))
        """
        return {str(block_name): payload}
