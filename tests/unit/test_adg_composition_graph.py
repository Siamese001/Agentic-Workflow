"""Tests for ADG composition graph (Graph 6, H5) — _CompositionVisitor."""

from __future__ import annotations

import ast

from agentic_core.adg.extraction.static_scanner import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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


class TestCompositionVisitor:
    def test_self_assignment_in_init(self):
        src = """
class MyAgent:
    def __init__(self):
        self.provider = SomeProvider()
"""
        edges = _visit_comp(src)
        assert len(edges) == 1
        e = edges[0]
        assert e.relation_type == "instantiates"
        assert e.edge_kind == "composition"
        assert e.symbol == "SomeProvider"

    def test_noise_constructors_excluded(self):
        src = """
class MyAgent:
    def __init__(self):
        self.data = dict()
        self.items = list()
        self.val = str()
        self.p = Path("/tmp")
"""
        edges = _visit_comp(src)
        assert edges == []

    def test_non_init_method_excluded(self):
        src = """
class MyAgent:
    def run(self):
        self.local = SomeProvider()
"""
        edges = _visit_comp(src)
        assert edges == []

    def test_non_self_assignment_excluded(self):
        src = """
class MyAgent:
    def __init__(self):
        local_var = SomeProvider()
"""
        edges = _visit_comp(src)
        assert edges == []

    def test_multiple_compositions(self):
        src = """
class BigAgent:
    def __init__(self):
        self.llm = LLMGateway()
        self.store = VectorStore()
        self.router = SemanticRouter()
"""
        edges = _visit_comp(src)
        assert len(edges) == 3
        symbols = {e.symbol for e in edges}
        assert symbols == {"LLMGateway", "VectorStore", "SemanticRouter"}

    def test_class_name_in_from(self):
        src = """
class SpecificAgent:
    def __init__(self):
        self.dep = DepClass()
"""
        edges = _visit_comp(src)
        assert len(edges) == 1
        assert "SpecificAgent" in edges[0].from_name

    def test_attribute_constructor(self):
        src = """
class Agent:
    def __init__(self):
        self.client = llm_provider.OpenAIClient()
"""
        edges = _visit_comp(src)
        assert len(edges) == 1
        assert edges[0].symbol == "OpenAIClient"


class TestAttributeVisitor:
    def test_os_getenv(self):
        src = """
import os
val = os.getenv("KEY")
"""
        edges = _visit_attr(src)
        assert any(e.relation_type == "reads_from" and "getenv" in e.symbol for e in edges)

    def test_os_environ(self):
        src = """
import os
val = os.environ.get("KEY")
"""
        edges = _visit_attr(src)
        assert any(e.relation_type == "reads_from" for e in edges)

    def test_no_false_positives_on_regular_calls(self):
        src = """
result = some_func()
x = other.method()
"""
        edges = _visit_attr(src)
        assert edges == []


class TestDynamicExecutionVisitor:
    def test_eval_detected(self):
        src = """
result = eval("1+1")
"""
        edges = _visit_dyn(src)
        assert len(edges) == 1
        assert edges[0].symbol == "eval"
        assert edges[0].edge_kind == "dynamic_exec"

    def test_exec_detected(self):
        src = """
exec("print('hello')")
"""
        edges = _visit_dyn(src)
        assert any(e.symbol == "exec" for e in edges)

    def test_importlib_detected(self):
        src = """
import importlib
mod = importlib.import_module("some.mod")
"""
        edges = _visit_dyn(src)
        assert any("import_module" in e.symbol for e in edges)

    def test_regular_calls_not_flagged(self):
        src = """
result = my_function()
x = obj.method()
"""
        edges = _visit_dyn(src)
        assert edges == []
