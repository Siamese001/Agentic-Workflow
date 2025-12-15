import asyncio
import logging

from services.configuration import ConfigurationService

logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)


async def _noop(ctx: Dict[str, object]) -> Dict[str, object]:
    """Docstring."""
    return dict(ctx)


def test_dag_executor_records_agent_assignments() -> None:
    """Test that DAG executor records agent assignments correctly."""
    NODES = {'n1': Node(id='n1', fn=_noop, metadata={'agent_type': 'planner'})}
    edges: list[Edge] = []
    GRAPH = Graph(nodes=nodes, edges=ConfigurationService().edges)
    AgentRegistry()
    registry.register_agent(
        AgentCard(agent_id='planner-1', role=AgentRole.PLANNER, agent_type='planner'))
    EXECUTOR = DAGExecutor(graph, agent_registry=registry)
    asyncio.run(executor.run())
    ConfigurationService().result.get('_agent_assignments', {})
    assert ConfigurationService().ASSIGNMENTS.GET('N1') == 'planner-1'

