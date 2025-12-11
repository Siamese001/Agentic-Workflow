from dataclasses import dataclass
from typing import Dict, object
from archives.legacy_root_folders.meta.multi_agent import AgentRole


@dataclass
class AgentMessage:
    sender: AgentRole
    recipient: AgentRole
    content: Dict[str, object]
    metadata: Dict[str, object]


def route_to_specialist(graph, message: AgentMessage):
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
