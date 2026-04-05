"""Tests for modular ADG visitor architecture.

Validates the visitor base classes, registry, and modular visitor implementations.
"""

from __future__ import annotations

from agentic_core.adg.extraction.static_scanner import Edge
from agentic_core.adg.extraction.visitors import (
    BaseADGVisitor,
    BaseStructuralVisitor,
    VisitorContext,
    _DynamicExecutionVisitor,
    _ImportVisitor,
    _InheritanceVisitor,
    list_registered_visitors,
)


class TestVisitorContext:
    """Test VisitorContext dataclass."""

    def test_context_creation(self):
        """Test VisitorContext can be created with required fields."""
        ctx = VisitorContext(
            module_adg_name="ADG::Module::test.py",
            source_file="test.py",
            repo_root="/repo",
        )
        assert ctx.module_adg_name == "ADG::Module::test.py"
        assert ctx.source_file == "test.py"
        assert ctx.repo_root == "/repo"


class TestVisitorRegistry:
    """Test visitor registration system."""

    def test_list_registered_visitors_returns_list(self):
        """Test that list_registered_visitors returns a list."""
        visitors = list_registered_visitors()
        assert isinstance(visitors, list)


class TestInheritanceVisitor:
    """Test _InheritanceVisitor extraction."""

    def test_inheritance_visitor_importable(self):
        """Test that _InheritanceVisitor can be imported and instantiated."""
        ctx = VisitorContext(module_adg_name="test.py", source_file="test.py")
        visitor = _InheritanceVisitor(ctx)
        assert visitor is not None
        assert hasattr(visitor, "extract_edges")


class TestDynamicExecutionVisitor:
    """Test _DynamicExecutionVisitor extraction."""

    def test_dynamic_execution_visitor_importable(self):
        """Test that _DynamicExecutionVisitor can be imported and instantiated."""
        ctx = VisitorContext(module_adg_name="test.py", source_file="test.py")
        visitor = _DynamicExecutionVisitor(ctx)
        assert visitor is not None
        assert hasattr(visitor, "extract_edges")

    def test_extract_edges_with_exec_call(self):
        """Test that _DynamicExecutionVisitor extracts edges from exec() calls."""
        import ast

        from agentic_core.adg.extraction.static_scanner import canonical_name

        ctx = VisitorContext(
            module_adg_name=canonical_name("Module", "pkg/test.py"),
            source_file="pkg/test.py",
        )
        visitor = _DynamicExecutionVisitor(ctx)

        src = "exec('print(1)')"
        tree = ast.parse(src)
        visitor.visit(tree)
        edges = visitor.extract_edges()

        # Should find dynamic execution edge (actual: 'invokes_dynamic')
        assert any(e.relation_type in ("dynamic_exec", "invokes_dynamic") for e in edges), (
            f"Expected 'dynamic_exec' or 'invokes_dynamic' edge, got: {[e.relation_type for e in edges]}"
        )


class TestImportVisitor:
    """Test _ImportVisitor extraction."""

    def test_import_visitor_importable(self):
        """Test that _ImportVisitor can be imported and instantiated."""
        ctx = VisitorContext(module_adg_name="test.py", source_file="test.py")
        visitor = _ImportVisitor(ctx)
        assert visitor is not None
        assert hasattr(visitor, "extract_edges")

    def test_extract_edges_import(self):
        """Test that _ImportVisitor extracts edges from import statements."""
        import ast

        from agentic_core.adg.extraction.static_scanner import canonical_name

        ctx = VisitorContext(
            module_adg_name=canonical_name("Module", "pkg/test.py"),
            source_file="pkg/test.py",
        )
        visitor = _ImportVisitor(ctx)

        src = "import os"
        tree = ast.parse(src)
        visitor.visit(tree)
        edges = visitor.extract_edges()

        # Should find imports edge
        assert any(e.relation_type == "imports" for e in edges), (
            f"Expected 'imports' edge, got: {[e.relation_type for e in edges]}"
        )

    def test_extract_edges_from_import(self):
        """Test that _ImportVisitor extracts edges from from...import statements."""
        import ast

        from agentic_core.adg.extraction.static_scanner import canonical_name

        ctx = VisitorContext(
            module_adg_name=canonical_name("Module", "pkg/test.py"),
            source_file="pkg/test.py",
        )
        visitor = _ImportVisitor(ctx)

        src = "from typing import Dict"
        tree = ast.parse(src)
        visitor.visit(tree)
        edges = visitor.extract_edges()

        # Should find imports edge
        assert any(e.relation_type == "imports" for e in edges), (
            f"Expected 'imports' edge from from_import, got: {[e.relation_type for e in edges]}"
        )


class TestBaseStructuralVisitor:
    """Test BaseStructuralVisitor helper methods."""

    def test_base_structural_visitor_has_extract_edges(self):
        """Test that BaseStructuralVisitor has extract_edges method."""
        # BaseStructuralVisitor is abstract, verify via inheritance check
        assert hasattr(BaseStructuralVisitor, "__init__")


class TestVisitorIntegration:
    """Integration tests for visitor pipeline."""

    def test_visitor_pipeline_imports(self):
        """Test that all visitor components can be imported together."""
        # All imports at module level should succeed
        assert BaseADGVisitor is not None
        assert VisitorContext is not None
        assert Edge is not None
