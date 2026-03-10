"""Tests for ADG inheritance graph (Graph 3, H3) — _InheritanceVisitor."""

from __future__ import annotations

import ast

from agentic_core.adg.extraction.static_scanner import (
    Edge,
    _InheritanceVisitor,
    run_scanner_self_test,
)


def _parse_and_visit(
    source: str, module_adg: str = "ADG::Module::test", source_file: str = "test.py"
) -> list[Edge]:
    tree = ast.parse(source)
    visitor = _InheritanceVisitor(module_adg, source_file)
    visitor.visit(tree)
    return visitor.edges


class TestInheritanceVisitor:
    def test_single_base_class(self):
        src = """
class Concrete(BaseAgent):
    pass
"""
        edges = _parse_and_visit(src)
        assert len(edges) == 1
        e = edges[0]
        assert e.relation_type == "implements"
        assert e.symbol == "BaseAgent"
        assert e.edge_kind == "unresolved"

    def test_qualified_base_class(self):
        src = """
class Foo(agentic_core.base.SovereignBase):
    pass
"""
        edges = _parse_and_visit(src)
        assert len(edges) == 1
        e = edges[0]
        assert e.symbol == "agentic_core.base.SovereignBase"
        assert e.edge_kind == "resolved_internal"

    def test_external_base_class(self):
        src = """
class Foo(some.external.lib.Base):
    pass
"""
        edges = _parse_and_visit(src)
        assert len(edges) == 1
        assert edges[0].edge_kind == "external"

    def test_object_base_excluded(self):
        src = """
class Foo(object):
    pass
"""
        edges = _parse_and_visit(src)
        assert edges == []

    def test_multiple_inheritance(self):
        src = """
class Multi(Base1, Mixin2, Base3):
    pass
"""
        edges = _parse_and_visit(src)
        assert len(edges) == 3
        symbols = {e.symbol for e in edges}
        assert symbols == {"Base1", "Mixin2", "Base3"}

    def test_nested_class(self):
        src = """
class Outer(OBase):
    class Inner(IBase):
        pass
"""
        edges = _parse_and_visit(src)
        assert len(edges) == 2
        relations = {e.relation_type for e in edges}
        assert relations == {"implements"}

    def test_no_bases(self):
        src = """
class NoBases:
    pass
"""
        edges = _parse_and_visit(src)
        assert edges == []

    def test_class_adg_name_contains_class_name(self):
        src = """
class MyAgent(SovereignBase):
    pass
"""
        edges = _parse_and_visit(src, source_file="agentic_core/L2_execution/reasoning/my_agent.py")
        assert len(edges) == 1
        assert "MyAgent" in edges[0].from_name

    def test_line_number_captured(self):
        src = """

class AgentX(Base):
    pass
"""
        edges = _parse_and_visit(src)
        assert edges[0].line_no >= 1


class TestScannerSelfTest:
    def test_self_test_passes(self):
        """S1: Scanner self-test must return True."""
        result = run_scanner_self_test()
        assert result is True
