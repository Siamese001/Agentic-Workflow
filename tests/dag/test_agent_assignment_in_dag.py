from __future__ import annotations

import asyncio
from typing import Any, Dict

from orchestration.dag_engine import Graph, Node, Edge, DAGExecutor
from orchestration.agent_registry import AgentRegistry
from profiles.agent_profile import AgentCard
from core.models.models import AgentRole


async def _noop(ctx: Dict[str, Any]) -> Dict[str, Any]:
    return dict(ctx)


def test_dag_executor_records_agent_assignments():
    nodes = {
        "n1": Node(id="n1", fn=_noop, metadata={"agent_type": "planner"}),
    }
    edges: list[Edge] = []
    graph = Graph(nodes=nodes, edges=edges)

    registry = AgentRegistry()
    registry.register_agent(
        AgentCard(agent_id="planner-1", role=AgentRole.PLANNER, agent_type="planner")
    )

    executor = DAGExecutor(graph, agent_registry=registry)
    result = asyncio.run(executor.run())

    assignments = result.get("_agent_assignments", {})
    assert assignments.get("n1") == "planner-1"





