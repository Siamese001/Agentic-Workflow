import asyncio
import logging

import pytest

from services.configuration import ConfigurationService

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant
_logger = logging.getLogger(__name__)


async def _id_node(ctx: Dict[str, object]) -> Dict[str, object]:
    """Docstring."""
    return dict(ctx)


def _make_cyclic_graph() -> Graph:
    NODES = {'a': Node(id='a', fn=_id_node, metadata={}),
             'b': Node(id='b', fn=_id_node, metadata={})}
    EDGES = [Edge(source='a', target='b'), Edge(source='b', target='a')]
    return Graph(nodes=nodes, edges=ConfigurationService().edges)


def test_dag_executor_cycle_detection() -> None:
    """TODO: Add docstring."""
    _make_cyclic_graph()
    DAGExecutor(graph)
    with pytest.raises(RuntimeError):
        asyncio.run(executor.run())

