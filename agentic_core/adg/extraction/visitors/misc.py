"""Miscellaneous Visitors for ADG Extraction.

Visitors in this module extract various remaining edge types:
    - _TestTraceabilityVisitor: Test coverage edges
    - _TypeAnnotationVisitor: Type annotation edges
    - _DecoratorVisitor: Decorator application edges
    - _SymbolInventoryVisitor: Module exports
    - _UnusedImportVisitor: Dead import detection
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from . import BaseStructuralVisitor, VisitorContext, register_visitor

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import Edge


@register_visitor("test_traceability")
class _TestTraceabilityVisitor(BaseStructuralVisitor):
    """GT: Emit `covers` edges from test modules to the internal modules they import."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file
        self._test_file_indicators = ("tests/", "test_", "_test.py")

    def visit_Import(self, node: ast.Import) -> None:
        """Extract test coverage edges from imports in test files."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.contracts.schema_util import canonical_name

        # Only process if this is a test file
        if not any(indicator in self._source_file for indicator in self._test_file_indicators):
            self.generic_visit(node)
            return

        for alias in node.names:
            module = alias.name.split(".")[0]
            to_name = canonical_name("Symbol", f"{module}.*")
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="covers",
                    to_name=to_name,
                    edge_kind="test_coverage",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=module,
                )
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Extract test coverage edges from from-imports in test files."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.contracts.schema_util import canonical_name

        # Only process if this is a test file
        if not any(indicator in self._source_file for indicator in self._test_file_indicators):
            self.generic_visit(node)
            return

        module = node.module or ""
        to_name = canonical_name("Symbol", f"{module}.*")
        for alias in node.names:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="covers",
                    to_name=to_name,
                    edge_kind="test_coverage",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=alias.name,
                )
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("type_annotation")
class _TypeAnnotationVisitor(BaseStructuralVisitor):
    """E4: G8 — Emit `reads_from` edges for type annotations."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file

    def _extract_annotation_names(self, node: ast.expr) -> list[str]:
        """Extract all names referenced in a type annotation."""
        names: list[str] = []
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                names.append(child.id)
            elif isinstance(child, ast.Attribute):
                # Handle qualified names like typing.List
                name = self._get_attr_name(child)
                if name:
                    names.append(name.split(".")[0])
        return names

    def _get_attr_name(self, node: ast.Attribute) -> str:
        """Get the full name of an attribute access."""
        parts: list[str] = []
        current: ast.expr = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Extract type annotation edges from function definitions."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.contracts.schema_util import canonical_name

        # Return type annotation
        if node.returns:
            for name in self._extract_annotation_names(node.returns):
                self.edges.append(
                    _Edge(
                        from_name=self._module_adg_name,
                        relation_type="reads_from",
                        to_name=canonical_name("Symbol", name),
                        edge_kind="type_annotation",
                        source_file=self._source_file,
                        line_no=node.lineno,
                        symbol=name,
                    )
                )

        # Argument annotations
        for arg in node.args.args + node.args.kwonlyargs:
            if arg.annotation:
                for name in self._extract_annotation_names(arg.annotation):
                    self.edges.append(
                        _Edge(
                            from_name=self._module_adg_name,
                            relation_type="reads_from",
                            to_name=canonical_name("Symbol", name),
                            edge_kind="type_annotation",
                            source_file=self._source_file,
                            line_no=node.lineno,
                            symbol=name,
                        )
                    )

        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Extract type annotation edges from annotated assignments."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.contracts.schema_util import canonical_name

        if node.annotation:
            for name in self._extract_annotation_names(node.annotation):
                self.edges.append(
                    _Edge(
                        from_name=self._module_adg_name,
                        relation_type="reads_from",
                        to_name=canonical_name("Symbol", name),
                        edge_kind="type_annotation",
                        source_file=self._source_file,
                        line_no=node.lineno,
                        symbol=name,
                    )
                )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("decorator")
class _DecoratorVisitor(BaseStructuralVisitor):
    """E3: G7 — Emit `applies` edges for decorator usage."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file

    def _get_decorator_name(self, node: ast.expr) -> str:
        """Extract decorator name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = []
            current: ast.expr = node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        if isinstance(node, ast.Call):
            return self._get_decorator_name(node.func)
        return ""

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Extract decorator edges from function definitions."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.contracts.schema_util import canonical_name

        for decorator in node.decorator_list:
            name = self._get_decorator_name(decorator)
            if name:
                self.edges.append(
                    _Edge(
                        from_name=self._module_adg_name,
                        relation_type="applies",
                        to_name=canonical_name("Symbol", name),
                        edge_kind="decorator",
                        source_file=self._source_file,
                        line_no=node.lineno,
                        symbol=name,
                    )
                )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Extract decorator edges from class definitions."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.contracts.schema_util import canonical_name

        for decorator in node.decorator_list:
            name = self._get_decorator_name(decorator)
            if name:
                self.edges.append(
                    _Edge(
                        from_name=self._module_adg_name,
                        relation_type="applies",
                        to_name=canonical_name("Symbol", name),
                        edge_kind="decorator",
                        source_file=self._source_file,
                        line_no=node.lineno,
                        symbol=name,
                    )
                )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("symbol_inventory")
class _SymbolInventoryVisitor(BaseStructuralVisitor):
    """E1: Emit `exports` edges for every public top-level symbol."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Extract exports for public functions."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.contracts.schema_util import canonical_name

        if not node.name.startswith("_"):
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="exports",
                    to_name=canonical_name("Symbol", node.name),
                    edge_kind="public_function",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=node.name,
                )
            )
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Extract exports for public async functions."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.contracts.schema_util import canonical_name

        if not node.name.startswith("_"):
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="exports",
                    to_name=canonical_name("Symbol", node.name),
                    edge_kind="public_async_function",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=node.name,
                )
            )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Extract exports for public classes."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.contracts.schema_util import canonical_name

        if not node.name.startswith("_"):
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="exports",
                    to_name=canonical_name("Symbol", node.name),
                    edge_kind="public_class",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=node.name,
                )
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("unused_import")
class _UnusedImportVisitor(BaseStructuralVisitor):
    """E6: Detect imported names that are never used in the file body."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file
        self._imported_names: dict[str, int] = {}  # name -> line_no
        self._used_names: set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        """Track imported names."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name.split(".")[0]
            self._imported_names[name] = node.lineno
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track from-imported names."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self._imported_names[name] = node.lineno
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        """Track name usages."""
        if isinstance(node.ctx, ast.Load):
            self._used_names.add(node.id)
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        """Emit edges for unused imports."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.contracts.schema_util import canonical_name

        unused = set(self._imported_names.keys()) - self._used_names
        for name in unused:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="unused_import",
                    to_name=canonical_name("Symbol", name),
                    edge_kind="dead_import",
                    source_file=self._source_file,
                    line_no=self._imported_names[name],
                    symbol=name,
                )
            )
        return self.edges
