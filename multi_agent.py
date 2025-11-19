# FILE: multi_agent.py
"""
Multi-Agent Coordination Patterns (v10_9_REFACTORED) — META LAYER ONLY

This module provides reusable multi-agent coordination primitives
(governance graphs, pipeline shapes, councils, committees) strictly
within the META layer.

STRICT LAYER BOUNDARIES:
    • NO L1 planning
    • NO L2 execution
    • NO L3 orchestration
    • NO L4 state mutation
    • NO L5 safety/policy decisions
    • PURE advisory logic only
    • SAFE to call anywhere

This refactor:
    • Fixes broken node construction (original used AgentNode(role,...)
      instead of AgentNode(role=<role_name>, config=...))
    • Normalizes to use modern AgentNode + AgentGraph from agents.py
    • Integrates fully with meta_profile (for future weighted patterns)
    • Returns patch-ready structures for L4, but does not mutate
    • Deterministic voting + routing consistent with agents.py
    • Aligns committee, council, pipeline, star graphs to new schema
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Tuple, Optional

from agents import (
    AgentRole,
    AgentNode,
    AgentGraph,
    summarize_graph,
    deterministic_vote,     # from agents.py — correct tie-breaking
)
from models import (
    MultiAgentVote,
    MultiAgentCouncilResult,
)
from meta_profile import (
    get_planning_bias,
    get_routing_bias,
    get_safety_bias,
    get_qa_bias,
)


# ============================================================================
# SECTION 1 — MULTI-AGENT GRAPH PATTERNS (CORRECTED)
# ============================================================================

class MultiAgentPattern(str, Enum):
    """Conceptual patterns for multi-agent coordination graphs."""
    LINEAR_PIPELINE = "linear_pipeline"
    STAR_HUB = "star_hub"
    COUNCIL = "council"
    COMMITTEE = "committee"


# ----------------------------------------------------------------------------
# LINEAR PIPELINE
# ----------------------------------------------------------------------------

def build_linear_pipeline(roles: List[str]) -> AgentGraph:
    """
    Build a linear pipeline:
        r0 → r1 → r2 → ...

    Example:
        build_linear_pipeline([
            AgentRole.PLANNER,
            AgentRole.RETRIEVER,
            AgentRole.DRAFTER,
            AgentRole.QA,
            AgentRole.SAFETY,
        ])
    """
    nodes = {str(r): AgentNode(role=str(r), config={}) for r in roles}
    edges = {}
    for i in range(len(roles) - 1):
        src = str(roles[i])
        dst = str(roles[i + 1])
        edges.setdefault(src, []).append(dst)

    return AgentGraph(nodes=nodes, edges=edges, metadata={"pattern": "linear_pipeline"})


# ----------------------------------------------------------------------------
# STAR HUB (hub ↔ spokes)
# ----------------------------------------------------------------------------

def build_star_hub(hub: str, spokes: List[str]) -> AgentGraph:
    """
    Build a star-hub graph:
        hub ↔ each spoke
    """
    nodes = {hub: AgentNode(role=hub, config={})}
    for s in spokes:
        nodes[s] = AgentNode(role=s, config={})

    edges = {}
    for s in spokes:
        edges.setdefault(hub, []).append(s)
        edges.setdefault(s, []).append(hub)

    return AgentGraph(nodes=nodes, edges=edges, metadata={"pattern": "star_hub"})


# ----------------------------------------------------------------------------
# COUNCIL (multiple agents with the same role)
# ----------------------------------------------------------------------------

def build_council(role: str, size: int) -> AgentGraph:
    """
    Build a role-homogeneous council of size N.

    Example:
        build_council(AgentRole.QA, 3)
    """
    size = max(1, int(size))

    nodes = {}
    for i in range(size):
        name = f"{role}_{i+1}"
        nodes[name] = AgentNode(
            role=str(role),
            config={"id": i + 1, "weight": 1.0}
        )

    return AgentGraph(nodes=nodes, edges={}, metadata={"pattern": "council"})


# ----------------------------------------------------------------------------
# COMMITTEE (one per role, no edges)
# ----------------------------------------------------------------------------

def build_committee(roles: List[str]) -> AgentGraph:
    """
    Build a committee: each role appears once, no directed edges.
    """
    nodes = {str(r): AgentNode(role=str(r), config={}) for r in roles}
    return AgentGraph(nodes=nodes, edges={}, metadata={"pattern": "committee"})


# ============================================================================
# SECTION 2 — DETERMINISTIC DELEGATION + ROUTING
# ============================================================================

@dataclass
class AgentMessage:
    """Meta-layer conceptual message exchanged between agent roles."""
    sender: str
    recipient: str
    content: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


def can_delegate(from_role: str, to_role: str) -> bool:
    """
    Canonical deterministic delegation rules.
    Mirrors (and extends) the logic from agents.py.
    """
    if from_role == AgentRole.PLANNER:
        return to_role in {AgentRole.RETRIEVER, AgentRole.DRAFTER, AgentRole.QA}
    if from_role == AgentRole.RETRIEVER:
        return to_role == AgentRole.DRAFTER
    if from_role == AgentRole.DRAFTER:
        return to_role == AgentRole.QA
    if from_role == AgentRole.QA:
        return to_role == AgentRole.SAFETY
    if from_role == AgentRole.SAFETY:
        return to_role in {AgentRole.HIL, AgentRole.META}
    return False


def delegation_metadata(sender: str, recipient: str) -> Dict[str, Any]:
    """Return structured metadata describing permitted/blocked delegation."""
    return {
        "from": sender,
        "to": recipient,
        "allowed": can_delegate(sender, recipient),
    }


# ============================================================================
# SECTION 3 — COUNCIL VOTING (META-ONLY, FIXED)
# ============================================================================

def council_vote(graph: AgentGraph, role: str, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deterministic council voting given candidate scores.

    Returns:
        {
          "selected": {...},
          "candidates": [...],
          "graph_summary": {...}
        }
    """
    if not candidates:
        return {
            "selected": {"id": None, "score": 0.0, "rationale": "no_candidates"},
            "candidates": [],
            "graph_summary": summarize_graph(graph),
        }

    # This uses agents.deterministic_vote (correct tiebreaker).
    winner = deterministic_vote(candidates)

    return {
        "selected": winner,
        "candidates": candidates,
        "graph_summary": summarize_graph(graph),
    }


# ============================================================================
# SECTION 4 — MULTI-AGENT COORDINATOR (PURE META LAYER)
# ============================================================================

@dataclass
class MultiAgentCoordinator:
    """
    High-level meta-layer coordinator for multi-agent behaviors.

    Responsibilities:
        • route_message() — determine routing metadata
        • council_vote()  — run role-specific councils
        • build_patch()   — create L4-ready patch blocks (NOT applied)
        • summarize()     — full graph summary

    MUST NOT mutate state. MUST NOT call L1–L5.
    """

    graph: AgentGraph

    def summarize(self) -> Dict[str, Any]:
        return summarize_graph(self.graph)

    def route_message(self, message: AgentMessage) -> Dict[str, Any]:
        """
        Compute routing metadata for conceptual messages.
        Validates delegation rules and embeds graph summary.
        """
        sender = str(message.sender)
        recipient = str(message.recipient)

        allowed = can_delegate(sender, recipient)

        return {
            "last_message": {
                "sender": sender,
                "recipient": recipient if allowed else None,
                "content": message.content,
                "metadata": message.metadata,
            },
            "delegation": delegation_metadata(sender, recipient),
            "graph_summary": self.summarize(),
        }

    def run_council(self, role: str, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Wrapper for council voting."""
        return council_vote(self.graph, role, candidates)

    # --- patch helper ------------------------------------------------------

    def build_patch(self, block_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return a dict representing an L4-ready patch:

            {block_name: payload}

        L4.StateAdapter is responsible for actually applying it.
        """
        return {str(block_name): payload}


# ============================================================================
# SECTION 5 — COUNCIL RESULT BUILDER (Typed Output)
# ============================================================================

def build_council_result(
    candidates: List[Dict[str, Any]],
    winner: Dict[str, Any],
) -> MultiAgentCouncilResult:
    """
    Build a typed MultiAgentCouncilResult for downstream layers.
    This normalizes candidate votes into fully structured objects.
    """

    votes = []
    for cand in candidates:
        votes.append(
            MultiAgentVote(
                agent_id=str(cand.get("id")),
                decision="revise" if cand.get("score", 0) >= 0.8 else "allow",
                confidence=float(cand.get("score", 0.0)),
                rationale=str(cand.get("rationale", "")),
                payload={"candidate": cand},
            )
        )

    return MultiAgentCouncilResult(
        votes=votes,
        aggregated_decision="revise" if winner.get("score", 0) >= 0.8 else "allow",
        aggregated_confidence=float(winner.get("score", 0.0)),
        rationale=str(winner.get("rationale", "")),
        metadata={"selected_id": winner.get("id")},
    )


# ============================================================================
# SECTION 6 — META-LAYER SIMULATION (NO-OP, DEBUG ONLY)
# ============================================================================

@dataclass
class MultiAgentSimulation:
    """
    Pure simulation for debugging multi-agent routing and councils.
    NEVER used at runtime.
    """

    coordinator: MultiAgentCoordinator

    def simulate_routing(self, sender: str, recipient: str, content: Dict[str, Any]) -> Dict[str, Any]:
        msg = AgentMessage(sender=sender, recipient=recipient, content=content)
        return self.coordinator.route_message(msg)

    def simulate_council(self, role: str) -> Dict[str, Any]:
        dummy_candidates = [
            {"id": 1, "score": 0.72, "rationale": "synthetic"},
            {"id": 2, "score": 0.65, "rationale": "synthetic"},
            {"id": 3, "score": 0.81, "rationale": "synthetic"},
        ]
        result = self.coordinator.run_council(role, dummy_candidates)
        result["typed"] = build_council_result(dummy_candidates, result["selected"]).to_dict()
        return result
