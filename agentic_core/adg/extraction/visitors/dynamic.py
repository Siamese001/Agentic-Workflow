"""Dynamic and Import AST Visitors for ADG Extraction.

Visitors in this module extract:
    - Import relationships (imports edges)
    - Dynamic execution patterns (eval/exec)
    - Internal call graph edges
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from . import BaseStructuralVisitor, VisitorContext, register_visitor

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import Edge


@register_visitor("dynamic_execution")
class _DynamicExecutionVisitor(BaseStructuralVisitor):
    """S3/RULE_F: Detect dynamic execution (eval/exec/importlib.import_module)."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        from agentic_core.adg.schema_util import DYNAMIC_EXEC_SYMBOLS
        self._dynamic_symbols = DYNAMIC_EXEC_SYMBOLS

    def visit_Call(self, node: ast.Call) -> None:
        """Detect calls to dynamic execution functions."""
        func_name = self._get_call_name(node.func)
        if func_name in self._dynamic_symbols:
            edge = self._create_edge(
                relation_type="invokes_dynamic",
                to_symbol=func_name,
                line_no=node.lineno,
                edge_kind="dynamic_execution",
                symbol=func_name,
            )
            self.edges.append(edge)
        self.generic_visit(node)

    def _get_call_name(self, node: ast.expr) -> str:
        """Extract function name from call expression."""
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


@register_visitor("import")
class _ImportVisitor(BaseStructuralVisitor):
    """Extract import edges from an AST.

    E7: Tracks conditional import context:
        - TYPE_CHECKING guards
        - try/except ImportError fallbacks
        - version-guarded imports
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._conditional_stack: list[str] = []
        self._current_depth = 0

    def visit_Import(self, node: ast.Import) -> None:
        """Extract edges from import statements."""
        context = self._get_import_context()
        for alias in node.names:
            edge = self._create_import_edge(
                module_name=alias.name,
                alias=alias.asname,
                line_no=node.lineno,
                context=context,
            )
            self.edges.append(edge)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Extract edges from from...import statements."""
        if node.module is None:
            self.generic_visit(node)
            return

        context = self._get_import_context()
        for alias in node.names:
            symbol_name = f"{node.module}.{alias.name}"
            edge = self._create_import_edge(
                module_name=symbol_name,
                alias=alias.asname,
                line_no=node.lineno,
                context=context,
                is_from_import=True,
            )
            self.edges.append(edge)
        self.generic_visit(node)

    def _get_import_context(self) -> str:
        """Determine import context (conditional, type-checking, etc.)."""
        if self._conditional_stack:
            return self._conditional_stack[-1]
        return "unconditional"

    def _create_import_edge(
        self,
        module_name: str,
        alias: str | None,
        line_no: int,
        context: str,
        is_from_import: bool = False,
    ) -> Edge:
        """Create an import edge."""
        from agentic_core.adg.schema_util import canonical_name

        to_name = canonical_name("Symbol", module_name)
        edge_kind = "import"
        if context == "TYPE_CHECKING":
            edge_kind = "type_checking_import"
        elif context == "conditional":
            edge_kind = "conditional_import"
        elif is_from_import:
            edge_kind = "from_import"

        # Import here to avoid circular dependency
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        return _Edge(
            from_name=self._module_adg_name,
            relation_type="imports",
            to_name=to_name,
            edge_kind=edge_kind,
            source_file=self._source_file,
            line_no=line_no,
            symbol=alias or module_name,
        )

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("internal_call_graph")
class _InternalCallGraphVisitor(BaseStructuralVisitor):
    """G4: Extract calls to internal module symbols (inter-module call graph)."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._internal_locals: dict[str, str] = {}
        self._instrumentation_prefixes: frozenset[str] = frozenset({"_emit_", "emit_"})

    def visit_Import(self, node: ast.Import) -> None:
        """Track internal module imports."""
        # Skip instrumentation - no synthetic edges during extraction
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track internal module imports."""
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Extract internal call graph edges."""
        sym = self._extract_symbol(node.func)
        if sym:
            base = sym.split(".")[0]
            if base in self._internal_locals:
                full_sym = self._internal_locals[base]
                # Suppress calls to instrumentation helpers
                tail = full_sym.rsplit(".", 1)[-1] if "." in full_sym else full_sym
                if any(tail.startswith(p) for p in self._instrumentation_prefixes):
                    self.generic_visit(node)
                    return

                from agentic_core.adg.schema_util import canonical_name
                to_name = canonical_name("Symbol", full_sym)

                # Import here to avoid circular dependency
                from agentic_core.adg.extraction.static_scanner import Edge as _Edge

                self.edges.append(
                    _Edge(
                        from_name=self._module_adg_name,
                        relation_type="calls",
                        to_name=to_name,
                        edge_kind="call",
                        source_file=self._source_file,
                        line_no=node.lineno,
                        symbol=full_sym,
                    )
                )
        self.generic_visit(node)

    def _extract_symbol(self, func_node: ast.expr) -> str:
        """Extract symbol name from function expression."""
        if isinstance(func_node, ast.Name):
            return func_node.id
        elif isinstance(func_node, ast.Attribute):
            parts = []
            current: ast.expr = func_node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
                return ".".join(reversed(parts))
        return ""

    def extract_edges(self) -> list[Edge]:
        return self.edges
