from __future__ import annotations

import asyncio
import contextlib
import sys
import types
from typing import Any, List

import pytest


def install_langgraph_stub() -> None:
    if "langgraph" in sys.modules:
        return

    langgraph = types.ModuleType("langgraph")
    graph_module = types.ModuleType("langgraph.graph")

    class StateGraph:  # type: ignore[override]
        def __init__(self, _state_type):
            self.nodes = {}

        def add_node(self, name, func):
            self.nodes[name] = func

        def set_entry_point(self, _name):
            return None

        def add_edge(self, *_args, **_kwargs):
            return None

    graph_module.StateGraph = StateGraph
    graph_module.END = "END"

    errors_module = types.ModuleType("langgraph.errors")

    class GraphRecursionError(Exception):
        ...

    errors_module.GraphRecursionError = GraphRecursionError

    langgraph.graph = graph_module
    langgraph.errors = errors_module
    sys.modules["langgraph"] = langgraph
    sys.modules["langgraph.graph"] = graph_module
    sys.modules["langgraph.errors"] = errors_module


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "asyncio: enable asyncio event loop")
    config.addinivalue_line("markers", "slow_graph: mark tests that execute the compiled graph")


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-slow-graph",
        action="store_true",
        default=False,
        help="run tests marked as slow_graph",
    )


@contextlib.contextmanager
def _run_loop():
    loop = asyncio.new_event_loop()
    try:
        yield loop
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


def pytest_pyfunc_call(pyfuncitem):
    marker = pyfuncitem.get_closest_marker("asyncio")
    if marker and asyncio.iscoroutinefunction(pyfuncitem.obj):
        argnames = getattr(pyfuncitem._fixtureinfo, "argnames", ()) or ()
        kwargs = {name: pyfuncitem.funcargs[name] for name in argnames}
        with _run_loop() as loop:
            loop.run_until_complete(pyfuncitem.obj(**kwargs))
        return True
    return False


def pytest_collection_modifyitems(config: pytest.Config, items: List[pytest.Item]) -> None:
    if config.getoption("--run-slow-graph"):
        return
    skip_marker = pytest.mark.skip(reason="pass --run-slow-graph to execute this test")
    for item in items:
        if "slow_graph" in item.keywords:
            item.add_marker(skip_marker)


__all__ = [
    "install_langgraph_stub",
    "pytest_collection_modifyitems",
    "pytest_configure",
    "pytest_pyfunc_call",
]
