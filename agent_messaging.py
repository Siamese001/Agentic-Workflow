from dataclasses import dataclass
from typing import Dict, Any
from agent_topology import AgentRole


@dataclass
class AgentMessage:
    sender: AgentRole
    recipient: AgentRole
    content: Dict[str, Any]
    metadata: Dict[str, Any]


def route_to_specialist(graph, message: AgentMessage):
    """
    Deterministic routing:
    - Finds first node whose role matches message.recipient.
    - No execution, no side effects.
    """
    for node in graph.nodes:
        if node.role == message.recipient:
            return node
    return None
