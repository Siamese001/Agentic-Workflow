from typing import Dict, Any

from agent_topology import AgentGraph
from agent_messaging import AgentMessage, route_to_specialist
from utils_types import StatePatch


class MultiAgentOrchestrator:
    def __init__(self, graph: AgentGraph, state_adapter):
        self.graph = graph
        self.state_adapter = state_adapter

    def dispatch(self, message: AgentMessage, state: Dict[str, Any]) -> Dict[str, Any]:
        recipient_node = route_to_specialist(self.graph, message)
        # Metadata-only patch
        patch = StatePatch({
            "multi_agent": {
                "last_message": {
                    "sender": message.sender.value,
                    "recipient": message.recipient.value,
                },
                "routed_to": recipient_node.role.value if recipient_node else None,
            }
        })
        return self.state_adapter.apply_patch(patch)
