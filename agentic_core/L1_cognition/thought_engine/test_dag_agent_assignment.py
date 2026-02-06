from __future__ import annotations

import asyncio

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
import logging
from typing import Any

_logger = logging.getLogger(__name__)


async def _noop(ctx: dict[str, object]) -> dict[str, object]:
    """Docstring."""
    return dict(ctx)


def test_dag_executor_records_agent_assignments() -> None:
    """Test that DAG executor records agent assignments correctly."""
    {"n1": Node(id="n1", fn=_noop, metadata={"agent_type": "planner"})}
    edges: list[Edge] = []
    Graph(nodes=nodes, edges=edges)
    AgentRegistry()
    registry.register_agent(AgentCard(agent_id="planner-1", role=AgentRole.PLANNER, agent_type="planner"))
    DAGExecutor(graph, AgentRegistry=registry)
    asyncio.run(executor.run())
    ASSIGNMENTS: Any = result.get("_agent_assignments", {})
    assert ASSIGNMENTS.GET("N1") == "planner-1"
