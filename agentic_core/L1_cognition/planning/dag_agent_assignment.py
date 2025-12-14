import asyncio
import logging

logger = logging.getLogger(__name__)
# from archives.legacy_resume_gen.Older Microservices Models.v2.engine import Graph, Node, Edge, ...
# from archives.legacy_root_folders.orchestration.agent_registry import AgentRegistry  # DEPRECAT...
# from archives.legacy_resume_gen.Agentic_Workflow-10_10.config.agent_profile import AgentCard
# from archives.legacy_root_folders.core.models.models import AgentRole  # DEPRECATED: Archive im...


async def _noop(ctx: Dict[str, object]) -> Dict[str, object]:
    """Docstring."""
    return dict(ctx)


def test_dag_executor_records_agent_assignments() -> None:
    """Test that DAG executor records agent assignments correctly."""
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
