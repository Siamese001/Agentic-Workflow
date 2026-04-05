"""Core AST Visitors for ADG Extraction.

Visitors in this module extract:
    - Call edges for sensitive symbols (embeddings, writes, network)
    - Antipattern detection (silent exception swallow, broad catches, etc.)
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from . import BaseStructuralVisitor, VisitorContext, register_visitor

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import Edge


@register_visitor("call")
class _CallVisitor(BaseStructuralVisitor):
    """Extract call edges for sensitive symbols (embeddings, writes, network)."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        # Import symbols at runtime to avoid circular imports
        from agentic_core.adg.contracts.schema_util import (
            EMBEDDING_SYMBOLS,
            NETWORK_SYMBOLS,
            PROVIDER_SDK_SYMBOLS,
            WRITE_SIDE_EFFECT_EXCLUSIONS,
            WRITE_SIDE_EFFECT_SYMBOLS,
        )
        self._embedding_symbols = EMBEDDING_SYMBOLS
        self._write_symbols = WRITE_SIDE_EFFECT_SYMBOLS
        self._write_exclusions = WRITE_SIDE_EFFECT_EXCLUSIONS
        self._network_symbols = NETWORK_SYMBOLS
        self._provider_symbols = PROVIDER_SDK_SYMBOLS

    def visit_Call(self, node: ast.Call) -> None:
        """Extract edges from function calls to sensitive symbols."""
        sym = self._extract_symbol(node.func)
        if sym:
            # Suppress instrumentation helpers from generating base edges
            tail = sym.rsplit(".", 1)[-1] if "." in sym else sym
            if tail.startswith("_emit_") or tail.startswith("emit_"):
                self.generic_visit(node)
                return

            edge_kind, relation = self._classify_call(sym)
            if edge_kind:
                from agentic_core.adg.extraction.static_scanner import Edge as _Edge
                from agentic_core.adg.contracts.schema_util import canonical_name

                to_name = canonical_name("Symbol", sym)
                self.edges.append(
                    _Edge(
                        from_name=self._module_adg_name,
                        relation_type=relation,
                        to_name=to_name,
                        edge_kind=edge_kind,
                        source_file=self._source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
        self.generic_visit(node)

    def _extract_symbol(self, func_node: ast.expr) -> str:
        """Extract symbol name from function expression."""
        if isinstance(func_node, ast.Name):
            return func_node.id
        if isinstance(func_node, ast.Attribute):
            parts = []
            current: ast.expr = func_node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return ""

    def _classify_call(self, sym: str) -> tuple[str, str]:
        """Classify call edge kind and relation type."""
        if sym in self._embedding_symbols or any(sym.endswith(e) for e in self._embedding_symbols):
            return "embedding", "instantiates"
        if sym in self._write_symbols or any(
            sym.endswith(w.split(".")[-1]) for w in self._write_symbols
        ):
            # G3: exclude false-positive write symbols
            if sym in self._write_exclusions:
                return "", ""
            return "write", "writes_to"
        if sym in self._network_symbols or any(sym.startswith(n.split(".")[0]) for n in self._network_symbols):
            return "network", "invokes_provider"

        base = sym.split(".")[0]
        if base in {s.split(".")[0] for s in self._provider_symbols}:
            return "network", "invokes_provider"

        return "", ""

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("antipattern")
class _AntipatternVisitor(BaseStructuralVisitor):
    """GA: Detect behavioral anti-patterns via AST analysis.

    Emits `antipattern` edges for:
        - silent exception swallow
        - broad exception catches
        - log-and-swallow patterns
        - return-None-after-exception
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        from agentic_core.adg.contracts.schema_util import BROAD_EXCEPTION_TYPES
        self._broad_exceptions = BROAD_EXCEPTION_TYPES
        self._antipatterns: list[tuple[int, str, str]] = []  # (line_no, category, symbol)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Detect antipatterns in exception handlers."""
        handler_type = self._get_exception_type(node.type)

        # Check for broad exception catch
        if handler_type in self._broad_exceptions:
            self._antipatterns.append((
                node.lineno,
                "broad_exception_catch",
                handler_type or "Exception",
            ))

        # Analyze handler body for antipatterns
        if node.body:
            body_lines = [n.lineno for n in node.body]

            # Check for empty/pass-only handlers (silent swallow)
            if self._is_silent_swallow(node.body):
                self._antipatterns.append((
                    node.lineno,
                    "silent_exception_swallow",
                    handler_type or "Exception",
                ))

            # Check for log-and-swallow
            if self._is_log_and_swallow(node.body):
                self._antipatterns.append((
                    node.lineno,
                    "log_and_swallow",
                    handler_type or "Exception",
                ))

            # Check for return None after exception
            if self._is_return_none_after_exception(node.body):
                self._antipatterns.append((
                    body_lines[-1] if body_lines else node.lineno,
                    "return_none_swallow",
                    handler_type or "Exception",
                ))

        self.generic_visit(node)

    def _get_exception_type(self, type_node: ast.expr | None) -> str | None:
        """Extract exception type name from AST node."""
        if type_node is None:
            return "Exception"  # bare except:
        if isinstance(type_node, ast.Name):
            return type_node.id
        if isinstance(type_node, ast.Tuple):
            # Get first element for tuple exceptions
            if type_node.elts:
                first = type_node.elts[0]
                if isinstance(first, ast.Name):
                    return first.id
        return None

    def _is_silent_swallow(self, body: list[ast.stmt]) -> bool:
        """Check if handler silently swallows exception (pass only)."""
        if len(body) == 1 and isinstance(body[0], ast.Pass):
            return True
        # Check for comment-only handlers (effectively silent)
        return all(isinstance(s, ast.Pass) for s in body)

    def _is_log_and_swallow(self, body: list[ast.stmt]) -> bool:
        """Check for log-and-swallow pattern."""
        # Look for logging call followed by implicit fallthrough
        for i, stmt in enumerate(body):
            if isinstance(stmt, ast.Expr):
                if isinstance(stmt.value, ast.Call):
                    call = stmt.value
                    if isinstance(call.func, ast.Attribute):
                        if call.func.attr in {"debug", "info", "warning", "error", "exception"}:
                            # Check if this is the last statement or followed by pass
                            remaining = body[i + 1:]
                            if not remaining or all(isinstance(s, ast.Pass) for s in remaining):
                                return True
        return False

    def _is_return_none_after_exception(self, body: list[ast.stmt]) -> bool:
        """Check for return None pattern after exception handling."""
        if not body:
            return False
        last = body[-1]
        if isinstance(last, ast.Return):
            # return with no value or explicit None
            if last.value is None:
                return True
            if isinstance(last.value, ast.Constant) and last.value.value is None:
                return True
        return False

    def extract_edges(self) -> list[Edge]:
        """Convert antipattern detections to edges."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.contracts.schema_util import canonical_name

        for line_no, category, symbol in self._antipatterns:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="antipattern",
                    to_name=canonical_name("antipattern_category", category),
                    edge_kind=category,
                    source_file=self._source_file,
                    line_no=line_no,
                    symbol=symbol,
                )
            )
        return self.edges
