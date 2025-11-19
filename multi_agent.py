# FILE: multi_agent.py
"""
Multi-Agent Coordination Patterns (v10_9) — META LAYER ONLY

This module provides reusable multi-agent coordination primitives for
v10_9, extending the minimal QA council logic in agents.py.

Layer Guardrails (strict):
    • NO L1 planning logic.
    • NO L2 tool/LLM execution.
    • NO L3 orchestration or phase control.
    • NO L4 state mutation (only returns patch payloads).
    • NO L5 safety / policy decisions.

Only meta-layer responsibilities:
    • Create multi-agent graph patterns (pipeline, star-hub, council, committee).
    • Provide deterministic delegation policies.
    • Provide deterministic voting for councils (e.g., QA triple council).
    • Provide message routing metadata between conceptual agents.
    • Provide patch blocks that L3 may store via StateAdapter.

It is intentionally “dumb” — it does not call tools, LLMs, or the safety
system. All logic must be pure and deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Tuple, Optional

from agents import AgentRole, AgentNode, AgentGraph, summarize_graph
from models import MultiAgentVote, MultiAgentCouncilResult


# ============================================================================
# 1. MULTI-AGENT PATTERNS
# ============================================================================


class MultiAgentPattern(str, Enum):
    """Conceptual graph patterns for multi-agent coordination."""

    LINEAR_PIPELINE = "linear_pipeline"
    STAR_HUB = "star_hub"
    COUNCIL = "council"
    COMMITTEE = "committee"


def build_linear_pipeline(roles: List[AgentRole]) -> AgentGraph:
    """
    Build a linear pipeline graph:
        r0 → r1 → r2 → ...

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
    Build a star-hub graph:
        hub ↔ each spoke
    (Bidirectional conceptual edges)
    """
    nodes = [AgentNode(hub, {})] + [AgentNode(s, {}) for s in spokes]
    edges: List[Tuple[AgentRole, AgentRole]] = []
    for s in spokes:
        edges.append((hub, s))
        edges.append((s, hub))
    return AgentGraph(nodes=nodes, edges=edges)


def build_council(role: AgentRole, size: int) -> AgentGraph:
    """
    Build a council graph: N agents with the same role.

    Used for parallel evaluation:
        COUNCIL(AgentRole.QA, size=3)
    """
    size = max(1, int(size))
    nodes = [AgentNode(role, {"id": i + 1, "weight": 1.0}) for i in range(size)]
    edges: List[Tuple[AgentRole, AgentRole]] = []
    return AgentGraph(nodes=nodes, edges=edges)


def build_committee(roles: List[AgentRole]) -> AgentGraph:
    """
    Build a committee graph: each role appears once, no edges.
    """
    nodes = [AgentNode(r, {}) for r in roles]
    return AgentGraph(nodes=nodes, edges=[])


# ============================================================================
# 2. DETERMINISTIC DELEGATION & VOTING
# ============================================================================

@dataclass
class AgentMessage:
    """Generic message exchanged between conceptual agents."""

    sender: AgentRole
    recipient: AgentRole
    content: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


def can_delegate(from_role: AgentRole, to_role: AgentRole) -> bool:
    """
    Deterministic delegation policy. This is purely heuristic and intended
    only as a routing hint for multi-agent meta-flows.

    Policy:
        • PLANNER  → RETRIEVER, DRAFTER, QA
        • RETRIEVER→ DRAFTER
        • DRAFTER  → QA
        • QA       → SAFETY
        • SAFETY   → HIL or META
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


def delegation_metadata(sender: AgentRole, recipient: AgentRole) -> Dict[str, Any]:
    """Return structured metadata describing permitted/blocked delegation."""
    return {
        "from": sender.value,
        "to": recipient.value,
        "allowed": can_delegate(sender, recipient),
    }


def deterministic_vote(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deterministic selection rule for council voting:
        • Highest score wins.
        • Ties broken by smallest id.
    """
    if not candidates:
        return {"id": None, "score": 0.0, "rationale": "no_candidates"}

    sorted_candidates = sorted(
        candidates,
        key=lambda c: (-float(c.get("score", 0.0)), int(c.get("id", 1_000_000))),
    )
    return sorted_candidates[0]


# ============================================================================
# 3. MULTI-AGENT COORDINATOR
# ============================================================================

@dataclass
class MultiAgentCoordinator:
    """
    Generic multi-agent coordinator.

    Responsibilities (META layer only):
        • route_message: compute routing metadata between two roles.
        • council_vote: select a winner among candidates.
        • build_state_patch: return a dict for L3 to integrate via L4.
        • summarize: return a deterministic graph summary.

    Constraints:
        • Does NOT mutate L4 state directly.
        • Does NOT call L1/L2/L5.
        • Does NOT call tools/LLMs.
    """

    graph: AgentGraph

    def _find_node_for_role(self, role: AgentRole) -> Optional[AgentNode]:
        for node in self.graph.nodes:
            if node.role == role:
                return node
        return None

    def summarize(self) -> Dict[str, Any]:
        """Return a deterministic summary of the underlying graph."""
        return summarize_graph(self.graph)

    # ----------------------------------------------------------------------
    # MESSAGE ROUTING
    # ----------------------------------------------------------------------

    def route_message(self, message: AgentMessage) -> Dict[str, Any]:
        """
        Compute routing metadata for a conceptual message exchange.

        Returns:
            {
              "last_message": {...},
              "sender": "planner",
              "recipient": "qa" or None,
              "delegation": {...},
              "graph_summary": {...}
            }
        """
        sender = message.sender
        recipient = message.recipient

        # Validate recipient exists in this graph
        if not self._find_node_for_role(recipient):
            allowed = False
        else:
            allowed = can_delegate(sender, recipient)

        return {
            "last_message": {
                "sender": sender.value,
                "recipient": recipient.value,
                "content": message.content,
                "metadata": message.metadata,
            },
            "sender": sender.value,
            "recipient": recipient.value if allowed else None,
            "delegation": delegation_metadata(sender, recipient),
            "graph_summary": self.summarize(),
        }

    # ----------------------------------------------------------------------
    # COUNCIL VOTING
    # ----------------------------------------------------------------------

    def council_vote(
        self, role: AgentRole, candidates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Deterministic council voting:

            • Filter nodes with the given role.
            • Apply deterministic_vote over candidate scores.
            • Return metadata with graph summary & winner.
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

    # ----------------------------------------------------------------------
    # STATE PATCH BUILDER
    # ----------------------------------------------------------------------

    def build_state_patch(
        self, block_name: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Return a dict representing a state block:

            {block_name: payload}

        L3 Orchestrator is responsible for applying this via:
            state_adapter.apply_patch(StatePatch(key=block_name, value=payload))
        """
        return {str(block_name): payload}


# ============================================================================
# 4. COUNCIL RESULT BUILDER (Typed Output)
# ============================================================================


def build_council_result(
    candidates: List[Dict[str, Any]],
    winner: Dict[str, Any],
) -> MultiAgentCouncilResult:
    """
    Construct a typed MultiAgentCouncilResult for downstream introspection.
    This mirrors agents.build_council_result but is exposed here for
    external meta-tools that want typed outputs.

    Returns MultiAgentCouncilResult.
    """
    votes: List[MultiAgentVote] = []
    for cand in candidates:
        votes.append(
            MultiAgentVote(
                candidate_id=cand.get("id"),
                score=float(cand.get("score", 0.0)),
                rationale=str(cand.get("rationale", "")),
            )
        )

    return MultiAgentCouncilResult(
        selected_id=winner.get("id"),
        selected_score=float(winner.get("score", 0.0)),
        votes=votes,
    )


# ============================================================================
# 5. DEMO / EXTENSIBILITY HOOKS (NO-OP)
# ============================================================================

@dataclass
class MultiAgentSimulation:
    """
    Small helper utility to simulate multi-agent message passing and
    council voting for debugging or demos.

    This is pure simulation — does not perform any state writes.
    """

    coordinator: MultiAgentCoordinator

    def simulate_routing(
        self, sender: AgentRole, recipient: AgentRole, content: Dict[str, Any]
    ) -> Dict[str, Any]:
        msg = AgentMessage(
            sender=sender,
            recipient=recipient,
            content=content,
        )
        return self.coordinator.route_message(msg)

    def simulate_council(self, role: AgentRole) -> Dict[str, Any]:
        """Deterministic council demo using synthetic candidates."""
        candidates = [
            {"id": 1, "score": 0.77, "rationale": "synthetic"},
            {"id": 2, "score": 0.65, "rationale": "synthetic"},
            {"id": 3, "score": 0.81, "rationale": "synthetic"},
        ]
        decision = self.coordinator.council_vote(role, candidates)
        decision["typed_result"] = build_council_result(
            candidates, decision["selected"]
        ).to_dict()
        return decision
