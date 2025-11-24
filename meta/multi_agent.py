"""Multi-Agent Coordination - Meta Layer

This module provides multi-agent coordination primitives.


Layer: Meta
Responsibilities:
- Graph patterns (pipeline, star-hub, council, committee)
- Deterministic delegation rules
- Council voting
- Agent message routing
- Pure advisory logic

Non-responsibilities:
- L1 planning
- L2 execution
- L3 orchestration
- L4 state mutation
- L5 safety/policy
"""

# FILE: multi_agent.py

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

from core.models.models import (  # type: ignore[attr-defined]
    AgentMessage,
    MultiAgentVote,
    MultiAgentCouncilResult,
)


# NOTE: v10_10 does not carry the full AgentGraph/AgentNode definitions
# from v10_9's agents.py. To preserve layering and keep this META-only,
# we define a minimal, local graph representation sufficient for:
#   • summarization
#   • council voting
#   • debugging/simulation
# This can be safely evolved independently.


@dataclass
class AgentNode:
    """Minimal agent node representation used by the META layer.

    This is a structural analog of the v10_9 AgentNode but stripped
    down to only the fields needed for meta-layer coordination.
    """

    role: str
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentGraph:
    """Minimal agent graph representation.

    nodes: mapping of node_id -> AgentNode
    edges: mapping of node_id -> list[node_id]
    metadata: arbitrary graph-level metadata
    """

    nodes: Dict[str, AgentNode] = field(default_factory=dict)
    edges: Dict[str, List[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


def summarize_graph(graph: AgentGraph) -> Dict[str, Any]:
    """Return a lightweight, deterministic summary of an AgentGraph."""

    return {
        "nodes": {node_id: {"role": n.role, "config": dict(n.config)} for node_id, n in graph.nodes.items()},
        "edges": {k: list(v) for k, v in graph.edges.items()},
        "metadata": dict(graph.metadata),
    }


class MultiAgentPattern(str, Enum):
    """Conceptual patterns for multi-agent coordination graphs."""

    LINEAR_PIPELINE = "linear_pipeline"
    STAR_HUB = "star_hub"
    COUNCIL = "council"
    COMMITTEE = "committee"


# ---------------------------------------------------------------------------
# LINEAR PIPELINE
# ---------------------------------------------------------------------------


def build_linear_pipeline(roles: List[str]) -> AgentGraph:
    """Build a linear pipeline: r0 → r1 → r2 → ..."""

    nodes = {str(r): AgentNode(role=str(r), config={}) for r in roles}
    edges: Dict[str, List[str]] = {}
    for i in range(len(roles) - 1):
        src = str(roles[i])
        dst = str(roles[i + 1])
        edges.setdefault(src, []).append(dst)

    return AgentGraph(nodes=nodes, edges=edges, metadata={"pattern": MultiAgentPattern.LINEAR_PIPELINE.value})


# ---------------------------------------------------------------------------
# STAR HUB (hub ↔ spokes)
# ---------------------------------------------------------------------------


def build_star_hub(hub: str, spokes: List[str]) -> AgentGraph:
    """Build a star-hub graph: hub ↔ each spoke."""

    nodes: Dict[str, AgentNode] = {hub: AgentNode(role=hub, config={})}
    for s in spokes:
        nodes[s] = AgentNode(role=s, config={})

    edges: Dict[str, List[str]] = {}
    for s in spokes:
        edges.setdefault(hub, []).append(s)
        edges.setdefault(s, []).append(hub)

    return AgentGraph(nodes=nodes, edges=edges, metadata={"pattern": MultiAgentPattern.STAR_HUB.value})


# ---------------------------------------------------------------------------
# COUNCIL (multiple agents with the same role)
# ---------------------------------------------------------------------------


def build_council(role: str, size: int) -> AgentGraph:
    """Build a role-homogeneous council of size N."""

    size = max(1, int(size))
    nodes: Dict[str, AgentNode] = {}
    for i in range(size):
        name = f"{role}_{i+1}"
        nodes[name] = AgentNode(role=str(role), config={"id": i + 1, "weight": 1.0})

    return AgentGraph(nodes=nodes, edges={}, metadata={"pattern": MultiAgentPattern.COUNCIL.value})


# ---------------------------------------------------------------------------
# COMMITTEE (one per role, no edges)
# ---------------------------------------------------------------------------


def build_committee(roles: List[str]) -> AgentGraph:
    """Build a committee: each role appears once, no directed edges."""

    nodes = {str(r): AgentNode(role=str(r), config={}) for r in roles}
    return AgentGraph(nodes=nodes, edges={}, metadata={"pattern": MultiAgentPattern.COMMITTEE.value})


# ---------------------------------------------------------------------------
# DETERMINISTIC DELEGATION RULES
# ---------------------------------------------------------------------------


class AgentRole(str, Enum):
    """Canonical multi-agent roles.

    These mirror the conceptual roles from v10_9 but are defined
    locally to keep this module self-contained.
    """

    PLANNER = "strategy_worker"
    RETRIEVER = "retrieval_worker"
    DRAFTER = "draft_worker"
    QA = "qa_worker"
    SAFETY = "safety_worker"
    HIL = "hil_worker"
    META = "meta_worker"


def can_delegate(from_role: str, to_role: str) -> bool:
    """Deterministic delegation rules (v10_9-compatible)."""

    if from_role == AgentRole.PLANNER.value:
        return to_role in {AgentRole.RETRIEVER.value, AgentRole.DRAFTER.value, AgentRole.QA.value}
    if from_role == AgentRole.RETRIEVER.value:
        return to_role == AgentRole.DRAFTER.value
    if from_role == AgentRole.DRAFTER.value:
        return to_role == AgentRole.QA.value
    if from_role == AgentRole.QA.value:
        return to_role == AgentRole.SAFETY.value
    if from_role == AgentRole.SAFETY.value:
        return to_role in {AgentRole.HIL.value, AgentRole.META.value}
    return False


def delegation_metadata(sender: str, recipient: str) -> Dict[str, Any]:
    """Return structured metadata describing permitted/blocked delegation."""

    return {
        "from": sender,
        "to": recipient,
        "allowed": can_delegate(sender, recipient),
    }


# ---------------------------------------------------------------------------
# COUNCIL VOTING (META-ONLY, TYPED)
# ---------------------------------------------------------------------------


def deterministic_vote(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Simple deterministic vote: highest score, tie-broken by id."""

    if not candidates:
        return {"id": None, "score": 0.0, "rationale": "no_candidates"}

    # Normalize
    norm: List[Dict[str, Any]] = []
    for c in candidates:
        norm.append(
            {
                "id": c.get("id"),
                "score": float(c.get("score", 0.0)),
                "rationale": str(c.get("rationale", "")),
            }
        )

    norm.sort(key=lambda x: (-x["score"], str(x["id"])))
    return norm[0]


def council_vote(graph: AgentGraph, role: str, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Deterministic council voting given candidate scores."""

    if not candidates:
        return {
            "selected": {"id": None, "score": 0.0, "rationale": "no_candidates"},
            "candidates": [],
            "graph_summary": summarize_graph(graph),
        }

    winner = deterministic_vote(candidates)

    return {
        "selected": winner,
        "candidates": candidates,
        "graph_summary": summarize_graph(graph),
    }


def build_council_result(
    candidates: List[Dict[str, Any]],
    winner: Dict[str, Any],
) -> MultiAgentCouncilResult:
    """Build a typed MultiAgentCouncilResult for downstream layers."""

    votes: List[MultiAgentVote] = []
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


# ---------------------------------------------------------------------------
# MULTI-AGENT COORDINATOR (META-ONLY)
# ---------------------------------------------------------------------------


@dataclass
class MultiAgentCoordinator:
    """High-level meta-layer coordinator for multi-agent behaviors.

    Responsibilities:
        • route_message() — determine routing metadata
        • run_council()  — run role-specific councils
        • build_patch()  — create L4-ready patch blocks (NOT applied)
        • summarize()    — full graph summary

    MUST NOT mutate state. MUST NOT call L1–L5.
    """

    graph: AgentGraph

    def summarize(self) -> Dict[str, Any]:
        return summarize_graph(self.graph)

    def route_message(self, message: AgentMessage) -> Dict[str, Any]:
        """Compute routing metadata for conceptual messages."""

        sender = str(message.sender)
        recipient = str(message.recipient)

        allowed = can_delegate(sender, recipient)

        return {
            "last_message": {
                "sender": sender,
                "recipient": recipient if allowed else None,
                "content": dict(message.content),
                "metadata": dict(message.metadata),
            },
            "delegation": delegation_metadata(sender, recipient),
            "graph_summary": self.summarize(),
        }

    def run_council(self, role: str, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Wrapper for council voting returning both raw + typed results."""

        result = council_vote(self.graph, role, candidates)
        winner = result.get("selected", {})
        typed = build_council_result(candidates, winner)
        result["typed"] = typed.dict()
        return result

    def build_patch(self, block_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Return a dict representing an L4-ready patch: {block_name: payload}."""

        return {str(block_name): payload}


# ---------------------------------------------------------------------------
# META-LAYER SIMULATION (DEBUG ONLY)
# ---------------------------------------------------------------------------


@dataclass
class MultiAgentSimulation:
    """Pure simulation for debugging multi-agent routing and councils."""

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
        return result


def extract_council_arbitration(result: Dict[str, Any]) -> Dict[str, Any]:
    """Return a normalized arbitration summary from a run_council result.

    This helper is META-layer only and intended for evaluation/simulation.
    It does not mutate input or depend on runtime layers.
    """

    selected = result.get("selected") or {}
    typed = result.get("typed") or {}

    # typed is a dict produced by MultiAgentCouncilResult.dict()
    aggregated_decision = typed.get("aggregated_decision")
    aggregated_confidence = typed.get("aggregated_confidence")
    metadata = typed.get("metadata") or {}

    return {
        "selected_id": selected.get("id", metadata.get("selected_id")),
        "selected_score": selected.get("score"),
        "selected_rationale": selected.get("rationale"),
        "aggregated_decision": aggregated_decision,
        "aggregated_confidence": aggregated_confidence,
        "vote_count": len(typed.get("votes", [])),
        "metadata": dict(metadata),
    }
