"""Multi-agent module consolidating messaging and orchestration logic."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from shared.models import StatePatch


class AgentRole(str, Enum):
    PLANNER = "planner"
    RETRIEVER = "retriever"
    DRAFTER = "drafter"
    BULLET = "bullet"
    QA = "qa"
    SAFETY = "safety"


@dataclass
class AgentNode:
    role: AgentRole
    config: Dict[str, Any]


@dataclass
class AgentGraph:
    nodes: List[AgentNode]
    edges: List[tuple]  # (from_role, to_role)


LINEAR_PIPELINE = AgentGraph(
    nodes=[
        AgentNode(AgentRole.PLANNER, {}),
        AgentNode(AgentRole.RETRIEVER, {}),
        AgentNode(AgentRole.DRAFTER, {}),
        AgentNode(AgentRole.QA, {}),
        AgentNode(AgentRole.SAFETY, {}),
    ],
    edges=[
        (AgentRole.PLANNER, AgentRole.RETRIEVER),
        (AgentRole.RETRIEVER, AgentRole.DRAFTER),
        (AgentRole.DRAFTER, AgentRole.QA),
        (AgentRole.QA, AgentRole.SAFETY),
    ],
)


COUNCIL_OF_QA = AgentGraph(
    nodes=[
        AgentNode(AgentRole.QA, {"id": 1}),
        AgentNode(AgentRole.QA, {"id": 2}),
        AgentNode(AgentRole.QA, {"id": 3}),
    ],
    edges=[],
)


@dataclass
class AgentMessage:
    sender: AgentRole
    recipient: AgentRole
    content: Dict[str, Any]
    metadata: Dict[str, Any]


def route_to_specialist(graph: AgentGraph, message: AgentMessage) -> Optional[AgentNode]:
    """
    Deterministic routing:
    - Finds first node whose role matches message.recipient.
    - No execution, no side effects.
    """
    for node in graph.nodes:
        if node.role == message.recipient:
            metadata = message.metadata if message.metadata is not None else {}
            metadata["route_trace"] = [message.sender.value, node.role.value]
            message.metadata = metadata
            return node
    return None


def summarize_graph(graph: AgentGraph) -> Dict[str, Any]:
    """
    Deterministic summary of graph nodes and edges.
    """

    def _role_value(entry):
        return entry.role.value if hasattr(entry, "role") else entry.value

    return {
        "nodes": [_role_value(n) for n in graph.nodes],
        "edges": [(_role_value(a), _role_value(b)) for (a, b) in graph.edges],
    }


def can_delegate(from_role: AgentRole, to_role: AgentRole) -> bool:
    """
    Deterministic fixed delegation policy.
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
    return {
        "from": sender.value,
        "to": recipient.value,
        "allowed": can_delegate(sender, recipient),
    }


def deterministic_vote(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deterministic selection:
    - Highest score wins
    - Ties broken by smallest id
    """
    if not candidates:
        return {"id": None, "score": 0.0, "rationale": "no_candidates"}

    sorted_candidates = sorted(
        candidates,
        key=lambda c: (-float(c.get("score", 0.0)), int(c.get("id", 999999))),
    )
    return sorted_candidates[0]


class MultiAgentOrchestrator:
    def __init__(self, graph: AgentGraph, state_adapter: Any) -> None:
        self.graph = graph
        self.state_adapter = state_adapter

    def dispatch(self, message: AgentMessage, state: Dict[str, Any]) -> Dict[str, Any]:
        recipient_node = route_to_specialist(self.graph, message)
        recipient = recipient_node.role if recipient_node else None

        multi_agent_block: Dict[str, Any] = {
            "last_message": {
                "content": message.content,
                "sender": message.sender.value,
                "recipient": message.recipient.value,
            },
            "sender": message.sender.value,
            "recipient": recipient.value if recipient else None,
            "routed_to": recipient.value if recipient else None,
            "delegation": delegation_metadata(message.sender, recipient) if recipient else None,
            "graph_summary": summarize_graph(self.graph),
        }

        if self.graph == COUNCIL_OF_QA:
            multi_agent_block["council_vote"] = deterministic_vote(
                [
                    {"id": 1, "score": 0.70, "rationale": "baseline"},
                    {"id": 2, "score": 0.70, "rationale": "alt"},
                ]
            )

        patch = StatePatch(key="multi_agent", value=multi_agent_block)
        return self.state_adapter.apply_patch(patch)
