"""Architecture tests for ADG inheritance graph (Graph 3, H3).

Plan ref: tests/architecture/test_adg_inheritance_graph.py
"""

from __future__ import annotations

import ast

from agentic_core.adg.extraction.static_scanner import (
    Edge,
    _InheritanceVisitor,
    run_scanner_self_test,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_adg_inheritance_graph")
_emit_applies_guardrail("p0", "test_adg_inheritance_graph", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_inheritance_graph", "policy_binding")
_emit_snapshots_state("p0", "test_adg_inheritance_graph", "state_snapshot")
emit_replay_key("p0", "test_adg_inheritance_graph")
emit_determinism_digest("p0", "test_adg_inheritance_graph")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def _parse_and_visit(
    source: str,
    module_adg: str = "ADG::Module::test",
    source_file: str = "test.py",
) -> list[Edge]:
    tree = ast.parse(source)
    visitor = _InheritanceVisitor(module_adg, source_file)
    visitor.visit(tree)
    return visitor.edges


class TestInheritanceGraph:
    """Graph 3 — class inheritance (implements) edges."""

    def test_single_base_class(self):
        src = """
class ConcreteAgent(SovereignBaseAgent):
    pass
"""
        edges = _parse_and_visit(src)
        assert len(edges) == 1
        e = edges[0]
        assert e.relation_type == "implements"
        assert e.symbol == "SovereignBaseAgent"
        assert e.edge_kind == "unresolved"

    def test_multiple_inheritance(self):
        src = """
class MultiAgent(BaseA, BaseB):
    pass
"""
        edges = _parse_and_visit(src)
        assert len(edges) == 2
        syms = {e.symbol for e in edges}
        assert syms == {"BaseA", "BaseB"}

    def test_object_base_excluded(self):
        src = """
class PlainClass(object):
    pass
"""
        edges = _parse_and_visit(src)
        assert edges == []

    def test_internal_base_resolved(self):
        src = """
class MyAgent(agentic_core.base.SovereignBaseAgent):
    pass
"""
        edges = _parse_and_visit(src)
        assert len(edges) == 1
        assert edges[0].edge_kind == "resolved_internal"

    def test_external_qualified_base(self):
        src = """
class MyModel(pydantic.BaseModel):
    pass
"""
        edges = _parse_and_visit(src)
        assert len(edges) == 1
        assert edges[0].edge_kind == "external"

    def test_no_bases(self):
        src = """
class Standalone:
    pass
"""
        edges = _parse_and_visit(src)
        assert edges == []

    def test_nested_class_captured(self):
        src = """
class Outer:
    class Inner(SomeBase):
        pass
"""
        edges = _parse_and_visit(src)
        assert len(edges) == 1
        assert edges[0].symbol == "SomeBase"

    def test_line_number_recorded(self):
        src = "\nclass Agent(Base):\n    pass\n"
        edges = _parse_and_visit(src)
        assert edges[0].line_no == 2


class TestScannerSelfTestS1:
    """S1: Scanner self-test validates all graph types."""

    def test_self_test_passes(self):
        assert run_scanner_self_test() is True
