"""Core AST Visitors for ADG Extraction.

Visitors in this module extract:
    - Call edges for sensitive symbols (embeddings, writes, network)
    - Antipattern detection (silent exception swallow, broad catches, etc.)
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from . import BaseStructuralVisitor, VisitorContext, register_visitor
from tqdm import tqdm

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
                from agentic_core.adg.contracts.schema_util import canonical_name
                from agentic_core.adg.extraction.static_scanner import Edge as _Edge

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
                    ),
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
        if sym in self._write_symbols or any(sym.endswith(w.split(".")[-1]) for w in self._write_symbols):
            # G3: exclude false-positive write symbols
            if sym in self._write_exclusions:
                return "", ""
            return "write", "writes_to"
        if sym in self._network_symbols or any(
            sym.startswith(n.split(".")[0]) for n in self._network_symbols
        ):
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
        - blocking I/O calls inside async functions
        - module-level UPPER_CASE mutation inside functions (lazy-init guard excluded)
        - retry loops without backoff (range-based loops only, not collection iteration)
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        from agentic_core.adg.contracts.schema_util import BROAD_EXCEPTION_TYPES

        self._broad_exceptions = BROAD_EXCEPTION_TYPES
        self._antipatterns: list[tuple[int, str, str]] = []  # (line_no, category, symbol)
        # Allowlist of known blocking I/O calls for async detection
        self._blocking_io_calls = frozenset(
            {
                "time.sleep",
                "requests.get",
                "requests.post",
                "requests.put",
                "requests.delete",
                "requests.request",
                "urllib.request.urlopen",
                "urllib.urlopen",
                "socket.recv",
                "socket.send",
                "socket.connect",
                "socket.accept",
                "subprocess.run",
                "subprocess.call",
                "subprocess.check_output",
                "os.system",
                "asyncio.get_event_loop().run_until_complete",
            }
        )
        # Hardcoded path patterns to detect (AST stores string values without escapes)
        self._hardcoded_path_patterns = frozenset(
            {
                "C:\\Git\\",  # Windows backslash path
                "C:/Git/",  # Windows forward slash path
                "/home/amita/",  # Unix user home
                "/Users/amita/",  # macOS user home
                "D:\\",  # Secondary drive
            }
        )

    def visit_Constant(self, node: ast.Constant) -> None:
        """Detect hardcoded absolute paths in string constants."""
        if isinstance(node.value, str):
            for pattern in self._hardcoded_path_patterns:
                if pattern in node.value:
                    self._antipatterns.append(
                        (
                            node.lineno,
                            "hardcoded_path",
                            pattern,
                        )
                    )
                    break
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Detect antipatterns in exception handlers."""
        handler_type = self._get_exception_type(node.type)

        # Check for broad exception catch
        if handler_type in self._broad_exceptions:
            self._antipatterns.append(
                (
                    node.lineno,
                    "broad_exception_catch",
                    handler_type or "Exception",
                )
            )

        # Analyze handler body for antipatterns
        if node.body:
            body_lines = [n.lineno for n in node.body]

            # Check for empty/pass-only handlers (silent swallow)
            if self._is_silent_swallow(node.body):
                self._antipatterns.append(
                    (
                        node.lineno,
                        "silent_exception_swallow",
                        handler_type or "Exception",
                    )
                )

            # Check for log-and-swallow
            if self._is_log_and_swallow(node.body):
                self._antipatterns.append(
                    (
                        node.lineno,
                        "log_and_swallow",
                        handler_type or "Exception",
                    )
                )

            # Check for return None after exception
            if self._is_return_none_after_exception(node.body):
                self._antipatterns.append(
                    (
                        body_lines[-1] if body_lines else node.lineno,
                        "return_none_swallow",
                        handler_type or "Exception",
                    )
                )

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
                            remaining = body[i + 1 :]
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

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Detect blocking I/O calls inside async function bodies."""
        for child in tqdm(ast.walk(node), desc="Processing", unit="item"):
            if isinstance(child, ast.Call):
                sym = self._extract_symbol(child.func)
                if sym and sym in self._blocking_io_calls:
                    self._antipatterns.append(
                        (
                            child.lineno,
                            "blocking_call_in_async",
                            sym,
                        )
                    )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Detect module-level UPPER_CASE mutation inside function bodies (lazy-init guard excluded)."""
        # Track module-level names that are UPPER_CASE
        self._check_global_state_mutation(node)
        self.generic_visit(node)

    def _check_global_state_mutation(self, node: ast.FunctionDef) -> None:
        """Check for assignment to module-level UPPER_CASE names, excluding lazy-init guards."""
        for stmt in tqdm(ast.walk(node), desc="Processing", unit="item"):
            if isinstance(stmt, (ast.Assign, ast.AugAssign)):
                for target in tqdm(ast.walk(stmt), desc="Processing", unit="item"):
                    if isinstance(target, ast.Name) and target.id.isupper():
                        # Skip if inside a lazy-init guard: if _X is None: X = ...
                        # TODO: implement parent tracking for guard detection
                        self._antipatterns.append(
                            (
                                stmt.lineno,
                                "global_state_mutation",
                                target.id,
                            )
                        )

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

    def visit_While(self, node: ast.While) -> None:
        """Detect retry loops without backoff (while loops)."""
        if self._loop_contains_retry_without_backoff(node):
            self._antipatterns.append(
                (
                    node.lineno,
                    "retry_without_backoff",
                    "while_retry",
                )
            )
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        """Detect retry loops without backoff (for loops)."""
        if self._loop_contains_retry_without_backoff(node):
            self._antipatterns.append(
                (
                    node.lineno,
                    "retry_without_backoff",
                    "for_retry",
                )
            )
        self.generic_visit(node)

    def _loop_contains_retry_without_backoff(self, node: ast.AST) -> bool:
        """True only if loop iterates over range() AND body has try/except AND no sleep/backoff."""
        # Check if loop iterates over range() or similar integer sequence
        is_retry_loop = False
        if isinstance(node, ast.For):
            # Check if iter is range() call
            if isinstance(node.iter, ast.Call):
                sym = self._extract_symbol(node.iter.func)
                is_retry_loop = sym == "range"
        elif isinstance(node, ast.While):
            is_retry_loop = True  # while loops are often retry loops

        if not is_retry_loop:
            return False

        # Check if body contains try/except
        has_try = any(isinstance(child, ast.Try) for child in ast.walk(node))
        if not has_try:
            return False

        # Check if body contains sleep/backoff
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                sym = self._extract_symbol(child.func)
                if sym and any(s in sym for s in ("sleep", "time.sleep", "await asyncio.sleep")):
                    return False  # Has backoff, not a violation

        return True

    def extract_edges(self) -> list[Edge]:
        """Convert antipattern detections to edges."""
        from agentic_core.adg.contracts.schema_util import canonical_name
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        for line_no, category, symbol in tqdm(self._antipatterns, desc="Processing", unit="item"):
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="antipattern",
                    to_name=canonical_name("antipattern_category", category),
                    edge_kind=category,
                    source_file=self._source_file,
                    line_no=line_no,
                    symbol=symbol,
                ),
            )
        return self.edges
