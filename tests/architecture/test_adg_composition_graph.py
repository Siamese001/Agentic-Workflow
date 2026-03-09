"""Architecture tests for ADG composition graph (Graph 6, H5) and config reads (Graph 5, H4).

Plan ref: tests/architecture/test_adg_composition_graph.py
"""

from __future__ import annotations

import ast

from agentic_core.adg.extraction.static_scanner import (
    Edge,
    _AttributeVisitor,
    _CompositionVisitor,
    _DynamicExecutionVisitor,
)


def _visit_comp(source: str, source_file: str = "test.py") -> list[Edge]:
    tree = ast.parse(source)
    visitor = _CompositionVisitor("ADG::Module::test", source_file)
    visitor.visit(tree)
    return visitor.edges


def _visit_attr(source: str, source_file: str = "test.py") -> list[Edge]:
    tree = ast.parse(source)
    visitor = _AttributeVisitor("ADG::Module::test", source_file)
    visitor.visit(tree)
    return visitor.edges


def _visit_dyn(source: str, source_file: str = "test.py") -> list[Edge]:
    tree = ast.parse(source)
    visitor = _DynamicExecutionVisitor("ADG::Module::test", source_file)
    visitor.visit(tree)
    return visitor.edges


class TestCompositionGraph:
    """Graph 6 — object composition in __init__ (instantiates edges)."""

    def test_self_assignment_in_init(self):
        src = """
class MyAgent:
    def __init__(self):
        self.provider = SomeProvider()
"""
        edges = _visit_comp(src)
        assert len(edges) == 1
        assert edges[0].relation_type == "instantiates"
        assert edges[0].edge_kind == "composition"
        assert edges[0].symbol == "SomeProvider"

    def test_noise_constructors_excluded(self):
        src = """
class MyAgent:
    def __init__(self):
        self.data = dict()
        self.items = list()
        self.path = Path("/tmp")
"""
        edges = _visit_comp(src)
        assert edges == []

    def test_outside_init_excluded(self):
        src = """
class MyAgent:
    def run(self):
        self.x = SomeProvider()
"""
        edges = _visit_comp(src)
        assert edges == []

    def test_non_self_target_excluded(self):
        src = """
class MyAgent:
    def __init__(self):
        local = SomeProvider()
"""
        edges = _visit_comp(src)
        assert edges == []

    def test_qualified_constructor(self):
        src = """
class MyAgent:
    def __init__(self):
        self.client = some.module.Client()
"""
        edges = _visit_comp(src)
        assert len(edges) == 1
        assert edges[0].symbol == "Client"

    def test_multiple_compositions(self):
        src = """
class MyAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.cache = RedisCache()
"""
        edges = _visit_comp(src)
        assert len(edges) == 2
        syms = {e.symbol for e in edges}
        assert syms == {"LLMClient", "RedisCache"}


class TestConfigReadGraph:
    """Graph 5 — env/config reads (reads_from edges)."""

    def test_os_getenv_detected(self):
        src = "x = os.getenv('KEY')\n"
        edges = _visit_attr(src)
        assert any(e.relation_type == "reads_from" and e.edge_kind == "reads_env" for e in edges)

    def test_os_environ_detected(self):
        src = "x = os.environ.get('KEY')\n"
        edges = _visit_attr(src)
        assert any(e.edge_kind == "reads_env" for e in edges)


class TestDynamicExecutionGraph:
    """GF — dynamic execution (dynamic_exec edges, RULE_F)."""

    def test_eval_detected(self):
        src = "result = eval('1+1')\n"
        edges = _visit_dyn(src)
        assert any(e.edge_kind == "dynamic_exec" and e.symbol == "eval" for e in edges)

    def test_exec_detected(self):
        src = "exec('x = 1')\n"
        edges = _visit_dyn(src)
        assert any(e.edge_kind == "dynamic_exec" for e in edges)

    def test_importlib_detected(self):
        src = "importlib.import_module('some.mod')\n"
        edges = _visit_dyn(src)
        assert any(e.edge_kind == "dynamic_exec" for e in edges)

    def test_plain_call_not_flagged(self):
        src = "result = some_function()\n"
        edges = _visit_dyn(src)
        assert edges == []
