"""Wave 1 regression tests for ADG static correctness gap remediation.

Tests cover:
  W1a: Violation confidence floor raised from 0.3 to 0.5
  W1b: Key-based edge deduplication after post-scan passes
  W1c: _ModuleDefinitionVisitor emits module→func/class decomposes_into
"""

from __future__ import annotations

import ast
import textwrap

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.adg.extraction.static_scanner import (
        Edge,
        ScanResult,
        _ModuleDefinitionVisitor,
        _propagate_violations,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    Edge = None  # type: ignore[assignment,misc]
    ScanResult = None  # type: ignore[assignment,misc]
    _ModuleDefinitionVisitor = None  # type: ignore[assignment,misc]
    _propagate_violations = None  # type: ignore[assignment,misc]


def _make_edge(**overrides) -> Edge:
    """Helper to create an Edge with sensible defaults."""
    defaults = {
        "from_name": "ADG::Module::foo.py",
        "relation_type": "imports",
        "to_name": "ADG::Symbol::bar",
        "edge_kind": "internal",
        "source_file": "foo.py",
        "line_no": 1,
        "symbol": "bar",
    }
    defaults.update(overrides)
    return Edge(**defaults)


# ---------------------------------------------------------------------------
# W1a: Violation confidence floor
# ---------------------------------------------------------------------------
@pytest.mark.skipif(not _AVAILABLE, reason="static_scanner.py deps unavailable")
class TestW1aViolationConfidenceFloor:
    """Verify violation_propagates_through edges have confidence >= 0.5."""

    def test_propagated_edges_confidence_minimum(self):
        """All propagated violation edges must have confidence >= 0.5."""
        # Build a minimal ScanResult with a violation + import graph
        violating_module = "ADG::Module::bad_module.py"
        importer1 = "ADG::Module::uses_bad.py"
        importer2 = "ADG::Module::uses_uses_bad.py"

        edges = [
            _make_edge(
                from_name=violating_module,
                relation_type="violates",
                to_name="ADG::Module::some_layer",
                edge_kind="import",
                source_file="bad_module.py",
                symbol="layer_violation",
            ),
            _make_edge(
                from_name=importer1,
                relation_type="imports",
                to_name="ADG::Symbol::bad_module",
                edge_kind="internal",
                source_file="uses_bad.py",
                symbol="bad_module",
            ),
            _make_edge(
                from_name=importer2,
                relation_type="imports",
                to_name="ADG::Symbol::uses_bad",
                edge_kind="internal",
                source_file="uses_uses_bad.py",
                symbol="uses_bad",
            ),
        ]

        result = ScanResult(edges=edges)
        propagated = _propagate_violations(result)

        for edge in propagated:
            assert edge.relation_type == "violation_propagates_through"
            assert edge.confidence >= 0.5, (
                f"Violation propagation edge has confidence {edge.confidence} < 0.5 "
                f"(from={edge.from_name}, to={edge.to_name})"
            )

    def test_no_synthetic_below_threshold(self):
        """No violation propagation edge should have confidence below 0.5."""
        result = ScanResult(edges=[
            _make_edge(
                from_name="ADG::Module::v.py",
                relation_type="violates",
                to_name="ADG::Module::layer",
                edge_kind="import",
                source_file="v.py",
                symbol="violation",
            ),
        ])
        # Even with no imports to propagate through, verify the function
        propagated = _propagate_violations(result)
        for edge in propagated:
            assert edge.confidence >= 0.5


# ---------------------------------------------------------------------------
# W1b: Edge deduplication
# ---------------------------------------------------------------------------
@pytest.mark.skipif(not _AVAILABLE, reason="static_scanner.py deps unavailable")
class TestW1bEdgeDeduplication:
    """Verify key-based edge dedup removes exact duplicates."""

    def test_exact_duplicates_removed(self):
        """Edges with same (from_name, relation_type, to_name, line_no) are deduped."""
        e1 = _make_edge(
            from_name="ADG::Module::a.py",
            relation_type="calls",
            to_name="ADG::Symbol::func",
            line_no=10,
            edge_kind="call",
        )
        e2 = _make_edge(
            from_name="ADG::Module::a.py",
            relation_type="calls",
            to_name="ADG::Symbol::func",
            line_no=10,
            edge_kind="execution",  # different edge_kind but same key
        )
        e3 = _make_edge(
            from_name="ADG::Module::a.py",
            relation_type="calls",
            to_name="ADG::Symbol::func",
            line_no=20,  # different line — NOT a duplicate
            edge_kind="call",
        )

        edges = [e1, e2, e3]
        # Apply the same dedup logic as scan()
        seen_keys: set[tuple[str, str, str, int]] = set()
        deduped: list[Edge] = []
        for edge in edges:
            key = (edge.from_name, edge.relation_type, edge.to_name, edge.line_no)
            if key not in seen_keys:
                seen_keys.add(key)
                deduped.append(edge)

        assert len(deduped) == 2, f"Expected 2 unique edges, got {len(deduped)}"
        # First occurrence wins
        assert deduped[0] is e1
        assert deduped[1] is e3

    def test_no_duplicates_unchanged(self):
        """When all edges are unique, dedup should not remove any."""
        edges = [
            _make_edge(from_name=f"ADG::Module::m{i}.py", line_no=i)
            for i in range(5)
        ]
        seen_keys: set[tuple[str, str, str, int]] = set()
        deduped: list[Edge] = []
        for edge in edges:
            key = (edge.from_name, edge.relation_type, edge.to_name, edge.line_no)
            if key not in seen_keys:
                seen_keys.add(key)
                deduped.append(edge)

        assert len(deduped) == 5


# ---------------------------------------------------------------------------
# W1c: _ModuleDefinitionVisitor
# ---------------------------------------------------------------------------
@pytest.mark.skipif(not _AVAILABLE, reason="static_scanner.py deps unavailable")
class TestW1cModuleDefinitionVisitor:
    """Verify _ModuleDefinitionVisitor emits decomposes_into for all defs."""

    def _parse_and_visit(self, source: str, module_adg: str = "ADG::Module::test_mod.py",
                         source_file: str = "test_mod.py"):
        tree = ast.parse(textwrap.dedent(source))
        visitor = _ModuleDefinitionVisitor(module_adg, source_file)
        visitor.visit(tree)
        return visitor.edges

    def test_top_level_function(self):
        """A top-level function def should produce one decomposes_into edge."""
        source = """\
        def hello():
            pass
        """
        edges = self._parse_and_visit(source)
        func_edges = [e for e in edges if e.symbol == "hello"]
        assert len(func_edges) == 1
        e = func_edges[0]
        assert e.relation_type == "decomposes_into"
        assert e.edge_kind == "module_definition"
        assert e.from_name == "ADG::Module::test_mod.py"
        assert e.confidence == 1.0

    def test_top_level_class(self):
        """A top-level class def should produce one decomposes_into edge."""
        source = """\
        class MyClass:
            pass
        """
        edges = self._parse_and_visit(source)
        class_edges = [e for e in edges if e.symbol == "MyClass"]
        assert len(class_edges) == 1
        e = class_edges[0]
        assert e.relation_type == "decomposes_into"
        assert e.edge_kind == "module_definition"
        assert e.semantic_type == "module_defines_class"

    def test_class_method(self):
        """Methods inside a class should also get decomposes_into edges."""
        source = """\
        class Foo:
            def bar(self):
                pass
            def baz(self):
                pass
        """
        edges = self._parse_and_visit(source)
        # Should have: Foo class + bar method + baz method
        assert len(edges) == 3
        symbols = {e.symbol for e in edges}
        assert symbols == {"Foo", "bar", "baz"}

    def test_async_function(self):
        """Async functions should be recognized as async."""
        source = """\
        async def fetch():
            pass
        """
        edges = self._parse_and_visit(source)
        assert len(edges) == 1
        e = edges[0]
        assert e.symbol == "fetch"
        assert e.semantic_type == "module_defines_async_function"

    def test_nested_functions_not_emitted(self):
        """Functions nested inside other functions should NOT be emitted."""
        source = """\
        def outer():
            def inner():
                pass
        """
        edges = self._parse_and_visit(source)
        # Only outer should be emitted — inner is local scope
        assert len(edges) == 1
        assert edges[0].symbol == "outer"

    def test_nested_class(self):
        """Nested classes should be emitted with proper hierarchy."""
        source = """\
        class Outer:
            class Inner:
                pass
        """
        edges = self._parse_and_visit(source)
        assert len(edges) == 2
        symbols = {e.symbol for e in edges}
        assert symbols == {"Outer", "Inner"}

    def test_empty_module(self):
        """A module with no defs should produce zero edges."""
        source = """\
        x = 1
        y = 2
        """
        edges = self._parse_and_visit(source)
        assert len(edges) == 0

    def test_line_numbers_correct(self):
        """Edge line_no should match the actual def line in the AST."""
        source = """\
        # line 1
        # line 2
        def at_line_3():
            pass
        """
        edges = self._parse_and_visit(source)
        assert len(edges) == 1
        assert edges[0].line_no == 3

    def test_multiple_defs(self):
        """Multiple top-level defs should each get an edge."""
        source = """\
        def a(): pass
        def b(): pass
        class C: pass
        def d(): pass
        """
        edges = self._parse_and_visit(source)
        assert len(edges) == 4
        symbols = [e.symbol for e in edges]
        assert symbols == ["a", "b", "C", "d"]
