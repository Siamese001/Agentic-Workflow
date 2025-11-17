from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any


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
