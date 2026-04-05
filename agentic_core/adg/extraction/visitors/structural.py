"""Structural AST Visitors for ADG Extraction.

Visitors in this module extract static structural relationships:
    - Class inheritance (implements edges)
    - Config/env reads (reads_from edges)
    - Object composition (instantiates edges)
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from . import BaseStructuralVisitor, VisitorContext, register_visitor

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import Edge


@register_visitor("inheritance")
class _InheritanceVisitor(BaseStructuralVisitor):
    """H3: Extract class inheritance (implements) edges for Graph 3."""

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Extract inheritance edges from class definitions."""
        for base in node.bases:
            base_name = self._get_base_name(base)
            if base_name:
                edge = self._create_edge(
                    relation_type="implements",
                    to_symbol=base_name,
                    line_no=node.lineno,
                    edge_kind="inheritance",
                    symbol=base_name,
                )
                self.edges.append(edge)
        self.generic_visit(node)

    def _get_base_name(self, node: ast.expr) -> str:
        """Extract name from a base class expression."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            parts = []
            current: ast.expr = node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
                return ".".join(reversed(parts))
        return ""

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("attribute")
class _AttributeVisitor(BaseStructuralVisitor):
    """H4: Extract config/env reads for Graph 5 (reads_from edges)."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        # Import from schema_util at runtime to avoid circular imports
        from agentic_core.adg.contracts.schema_util import CONFIG_READ_SYMBOLS
        self._config_symbols = CONFIG_READ_SYMBOLS

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Detect config read patterns like os.environ.get."""
        symbol = self._get_attribute_chain(node)
        if symbol in self._config_symbols:
            edge = self._create_edge(
                relation_type="reads_from",
                to_symbol=symbol,
                line_no=node.lineno,
                edge_kind="config_read",
                symbol=symbol,
            )
            self.edges.append(edge)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Detect function calls that read config/env."""
        func_name = self._get_call_name(node.func)
        if func_name in self._config_symbols:
            edge = self._create_edge(
                relation_type="reads_from",
                to_symbol=func_name,
                line_no=node.lineno,
                edge_kind="config_read",
                symbol=func_name,
            )
            self.edges.append(edge)
        self.generic_visit(node)

    def _get_attribute_chain(self, node: ast.expr) -> str:
        """Build dotted name from attribute chain."""
        parts = []
        current: ast.expr = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
            return ".".join(reversed(parts))
        return ""

    def _get_call_name(self, node: ast.expr) -> str:
        """Extract function name from call expression."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_attribute_chain(node)
        return ""

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("composition")
class _CompositionVisitor(BaseStructuralVisitor):
    """H5: Extract object composition (instantiates edges in __init__) for Graph 6."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        # Import from static_scanner at runtime to avoid circular imports
        from agentic_core.adg.extraction.static_scanner import _COMPOSITION_NOISE
        self._noise_symbols = _COMPOSITION_NOISE
        self._in_init = False
        self._current_class = ""

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track current class for self.x assignments."""
        old_class = self._current_class
        self._current_class = node.name
        self.generic_visit(node)
        self._current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track when we're in __init__ method."""
        if node.name == "__init__" and self._current_class:
            self._in_init = True
            self.generic_visit(node)
            self._in_init = False
        else:
            self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Handle async __init__ (rare but possible)."""
        if node.name == "__init__" and self._current_class:
            self._in_init = True
            self.generic_visit(node)
            self._in_init = False
        else:
            self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Extract composition from self.x = SomeClass() assignments."""
        if not self._in_init:
            self.generic_visit(node)
            return

        for target in node.targets:
            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                if target.value.id == "self":
                    # Check if RHS is a constructor call
                    if isinstance(node.value, ast.Call):
                        ctor_name = self._get_constructor_name(node.value.func)
                        if ctor_name and ctor_name not in self._noise_symbols:
                            edge = self._create_edge(
                                relation_type="instantiates",
                                to_symbol=ctor_name,
                                line_no=node.lineno,
                                edge_kind="composition",
                                symbol=f"{self._current_class}.{target.attr}",
                            )
                            self.edges.append(edge)
        self.generic_visit(node)

    def _get_constructor_name(self, node: ast.expr) -> str:
        """Extract class name from constructor call."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            parts = []
            current: ast.expr = node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
                return ".".join(reversed(parts))
        return ""

    def extract_edges(self) -> list[Edge]:
        return self.edges
