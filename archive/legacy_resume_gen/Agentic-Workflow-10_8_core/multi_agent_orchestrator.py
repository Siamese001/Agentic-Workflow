from typing import Dict, Any

from multi_agent import AgentGraph, summarize_graph, COUNCIL_OF_QA
from multi_agent import AgentMessage, route_to_specialist
from multi_agent import deterministic_vote
from multi_agent import delegation_metadata
from utils_types import StatePatch


class MultiAgentOrchestrator:
    def __init__(self, graph: AgentGraph, state_adapter):
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

        patch = StatePatch({"multi_agent": multi_agent_block})
        return self.state_adapter.apply_patch(patch)
