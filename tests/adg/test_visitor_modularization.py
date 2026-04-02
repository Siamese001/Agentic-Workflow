"""Tests for modular ADG visitor architecture.

Validates the visitor base classes, registry, and modular visitor implementations.
"""

from __future__ import annotations

import ast
import pytest

from agentic_core.adg.extraction.visitors import (
    BaseADGVisitor,
    BaseStructuralVisitor,
    BaseRuntimeVisitor,
    VisitorContext,
    register_visitor,
    get_registered_visitor,
    list_registered_visitors,
    _InheritanceVisitor,
    _AttributeVisitor,
    _CompositionVisitor,
    _DynamicExecutionVisitor,
    _ImportVisitor,
    _InternalCallGraphVisitor,
)
from agentic_core.adg.extraction.static_scanner import Edge


class TestVisitorContext:
    """Test VisitorContext dataclass."""

    def test_context_creation(self) -> None:
        """Verify VisitorContext stores parameters correctly."""
        ctx = VisitorContext(
            module_adg_name="ADG::Module::test.py",
            source_file="/repo/test.py",
            repo_root="/repo",
        )
        assert ctx.module_adg_name == "ADG::Module::test.py"
        assert ctx.source_file == "/repo/test.py"
        assert ctx.repo_root == "/repo"

    def test_context_defaults(self) -> None:
        """Verify VisitorContext default values."""
        ctx = VisitorContext(
            module_adg_name="ADG::Module::test.py",
            source_file="/repo/test.py",
        )
        assert ctx.repo_root == ""


class TestVisitorRegistry:
    """Test visitor registration system."""

    def test_list_registered_visitors(self) -> None:
        """Verify registered visitors are discoverable."""
        visitors = list_registered_visitors()
        assert "inheritance" in visitors
        assert "attribute" in visitors
        assert "composition" in visitors
        assert "dynamic_execution" in visitors
        assert "import" in visitors
        assert "internal_call_graph" in visitors

    def test_get_registered_visitor(self) -> None:
        """Verify visitor retrieval by name."""
        visitor_class = get_registered_visitor("inheritance")
        assert visitor_class is not None
        assert visitor_class.__name__ == "_InheritanceVisitor"

    def test_get_nonexistent_visitor(self) -> None:
        """Verify None returned for unregistered visitor."""
        visitor_class = get_registered_visitor("nonexistent")
        assert visitor_class is None


class TestInheritanceVisitor:
    """Test _InheritanceVisitor extraction."""

    def test_simple_inheritance(self) -> None:
        """Extract edge from class inheriting from base."""
        code = "class Child(Parent): pass"
        tree = ast.parse(code)
        ctx = VisitorContext(
            module_adg_name="ADG::Module::test.py",
            source_file="test.py",
        )
        visitor = _InheritanceVisitor(ctx)
        visitor.visit(tree)
        edges = visitor.extract_edges()

        assert len(edges) == 1
        assert edges[0].relation_type == "implements"
        assert "Parent" in edges[0].to_name

    def test_multiple_inheritance(self) -> None:
        """Extract edges from multiple inheritance."""
        code = "class Child(Base1, Base2): pass"
        tree = ast.parse(code)
        ctx = VisitorContext(
            module_adg_name="ADG::Module::test.py",
            source_file="test.py",
        )
        visitor = _InheritanceVisitor(ctx)
        visitor.visit(tree)
        edges = visitor.extract_edges()

        assert len(edges) == 2
        base_names = [e.to_name for e in edges]
        assert any("Base1" in n for n in base_names)
        assert any("Base2" in n for n in base_names)

    def test_no_inheritance(self) -> None:
        """No edges when class inherits only from object."""
        code = "class Child: pass"
        tree = ast.parse(code)
        ctx = VisitorContext(
            module_adg_name="ADG::Module::test.py",
            source_file="test.py",
        )
        visitor = _InheritanceVisitor(ctx)
        visitor.visit(tree)
        edges = visitor.extract_edges()

        # Object inheritance is filtered out
        assert len(edges) == 0


class TestDynamicExecutionVisitor:
    """Test _DynamicExecutionVisitor extraction."""

    def test_eval_detection(self) -> None:
        """Detect eval() calls."""
        code = "eval('1 + 1')"
        tree = ast.parse(code)
        ctx = VisitorContext(
            module_adg_name="ADG::Module::test.py",
            source_file="test.py",
        )
        visitor = _DynamicExecutionVisitor(ctx)
        visitor.visit(tree)
        edges = visitor.extract_edges()

        assert len(edges) == 1
        assert edges[0].relation_type == "invokes_dynamic"
        assert edges[0].symbol == "eval"

    def test_exec_detection(self) -> None:
        """Detect exec() calls."""
        code = "exec('print(1)')"
        tree = ast.parse(code)
        ctx = VisitorContext(
            module_adg_name="ADG::Module::test.py",
            source_file="test.py",
        )
        visitor = _DynamicExecutionVisitor(ctx)
        visitor.visit(tree)
        edges = visitor.extract_edges()

        assert len(edges) == 1
        assert edges[0].relation_type == "invokes_dynamic"
        assert edges[0].symbol == "exec"

    def test_no_dynamic_calls(self) -> None:
        """No edges for regular function calls."""
        code = "print('hello')"
        tree = ast.parse(code)
        ctx = VisitorContext(
            module_adg_name="ADG::Module::test.py",
            source_file="test.py",
        )
        visitor = _DynamicExecutionVisitor(ctx)
        visitor.visit(tree)
        edges = visitor.extract_edges()

        assert len(edges) == 0


class TestImportVisitor:
    """Test _ImportVisitor extraction."""

    def test_simple_import(self) -> None:
        """Extract edge from import statement."""
        code = "import os"
        tree = ast.parse(code)
        ctx = VisitorContext(
            module_adg_name="ADG::Module::test.py",
            source_file="test.py",
        )
        visitor = _ImportVisitor(ctx)
        visitor.visit(tree)
        edges = visitor.extract_edges()

        assert len(edges) == 1
        assert edges[0].relation_type == "imports"
        assert "os" in edges[0].to_name

    def test_from_import(self) -> None:
        """Extract edge from from...import statement."""
        code = "from os.path import join"
        tree = ast.parse(code)
        ctx = VisitorContext(
            module_adg_name="ADG::Module::test.py",
            source_file="test.py",
        )
        visitor = _ImportVisitor(ctx)
        visitor.visit(tree)
        edges = visitor.extract_edges()

        assert len(edges) == 1
        assert edges[0].relation_type == "imports"
        assert "os.path.join" in edges[0].to_name
        assert edges[0].edge_kind == "from_import"

    def test_multiple_imports(self) -> None:
        """Extract multiple edges from single import statement."""
        code = "import os, sys, json"
        tree = ast.parse(code)
        ctx = VisitorContext(
            module_adg_name="ADG::Module::test.py",
            source_file="test.py",
        )
        visitor = _ImportVisitor(ctx)
        visitor.visit(tree)
        edges = visitor.extract_edges()

        assert len(edges) == 3
        imported = [e.symbol for e in edges]
        assert "os" in imported
        assert "sys" in imported
        assert "json" in imported


class TestBaseStructuralVisitor:
    """Test BaseStructuralVisitor helper methods."""

    def test_local_symbol_registration(self) -> None:
        """Verify local symbol tracking via concrete visitor."""
        ctx = VisitorContext(
            module_adg_name="ADG::Module::test.py",
            source_file="test.py",
        )
        # Use concrete visitor to test base class functionality
        visitor = _InheritanceVisitor(ctx)
        visitor._register_local("MyClass")

        assert visitor._is_local_symbol("MyClass.method")
        assert visitor._is_local_symbol("MyClass")
        assert not visitor._is_local_symbol("OtherClass")

    def test_edge_creation(self) -> None:
        """Verify _create_edge produces valid Edge via concrete visitor."""
        ctx = VisitorContext(
            module_adg_name="ADG::Module::test.py",
            source_file="test.py",
        )
        # Use concrete visitor to test base class functionality
        visitor = _InheritanceVisitor(ctx)
        edge = visitor._create_edge(
            relation_type="test_relation",
            to_symbol="test.module.Symbol",
            line_no=42,
            edge_kind="test_kind",
            symbol="Symbol",
        )

        assert edge.from_name == "ADG::Module::test.py"
        assert edge.relation_type == "test_relation"
        assert edge.line_no == 42
        assert edge.edge_kind == "test_kind"
        assert edge.symbol == "Symbol"


class TestVisitorIntegration:
    """Integration tests for visitor pipeline."""

    def test_multiple_visitors_same_ast(self) -> None:
        """Multiple visitors can process same AST independently."""
        code = """
import os

class MyClass(BaseClass):
    def __init__(self):
        self.value = eval("1 + 1")
"""
        tree = ast.parse(code)
        ctx = VisitorContext(
            module_adg_name="ADG::Module::test.py",
            source_file="test.py",
        )

        # Run multiple visitors
        import_visitor = _ImportVisitor(ctx)
        import_visitor.visit(tree)
        import_edges = import_visitor.extract_edges()

        inheritance_visitor = _InheritanceVisitor(ctx)
        inheritance_visitor.visit(tree)
        inheritance_edges = inheritance_visitor.extract_edges()

        dynamic_visitor = _DynamicExecutionVisitor(ctx)
        dynamic_visitor.visit(tree)
        dynamic_edges = dynamic_visitor.extract_edges()

        # Verify independent extraction
        assert len(import_edges) == 1  # import os
        assert len(inheritance_edges) == 1  # inherits BaseClass
        assert len(dynamic_edges) == 1  # eval() call
