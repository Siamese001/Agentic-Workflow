"""Runtime Semantic AST Visitors for ADG Extraction.

Visitors in this module extract execution-grade semantic edges:
    - Data lineage (flows_to edges)
    - Control flow (controls_flow edges)
    - Side effects (emits_side_effect edges)
    - Evaluation spine (scores_groundedness, builds_dpo_batch, etc.)
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from . import BaseRuntimeVisitor, VisitorContext, register_visitor

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import Edge


# Side effect prefixes for IO/mutation detection
_SIDE_EFFECT_PREFIXES: frozenset[str] = frozenset(
    {
        "open",
        "write",
        "read",
        "os.",
        "sys.",
        "subprocess.",
        "requests.",
        "urllib.",
        "socket.",
        "sqlite3.",
        "shutil.",
        "redis.",
        "print",
        "logging.",
        "json.dump",
        "json.load",
        "pathlib.",
        "tempfile.",
        "io.",
    }
)

_MUTATION_METHODS: frozenset[str] = frozenset(
    {
        "append",
        "extend",
        "insert",
        "pop",
        "remove",
        "clear",
        "update",
        "setdefault",
        "add",
        "discard",
        "__setitem__",
        "__delitem__",
    }
)

_TRIVIAL_DISPATCH_METHODS: frozenset[str] = frozenset(
    {
        "append",
        "extend",
        "insert",
        "pop",
        "remove",
        "clear",
        "update",
        "setdefault",
        "add",
        "discard",
        "copy",
        "keys",
        "values",
        "items",
        "get",
        "join",
        "split",
        "strip",
        "lower",
        "upper",
        "replace",
        "startswith",
        "endswith",
        "encode",
        "decode",
        "format",
        "hexdigest",
        "digest",
        "info",
        "debug",
        "warning",
        "error",
        "critical",
        "exception",
    }
)


@register_visitor("execution_semantic")
class _ExecutionSemanticVisitor(BaseRuntimeVisitor):
    """Execution-grade semantic enrichment — closes depth gaps without phantom nodes.

    Gaps closed:
      - Data Lineage: intra-function variable def→use chains (flows_to edges)
      - Control Flow: branch/loop/exception structure (controls_flow edges)
      - Side Effect Modeling: IO/mutation calls flagged (emits_side_effect edges)
      - Temporal Ordering: per-function statement sequence via edge metadata
      - Callsite Resolution: attribute dispatch vs direct call classification
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg = ctx.module_adg_name
        self._rel = ctx.source_file
        self._current_class: str | None = None
        self._func_seq: int = 0  # temporal ordering within a function

    def _func_adg(self) -> str:
        """Return the ADG name of the current function (structural node)."""
        if self._current_function == "":
            return self._module_adg
        sym = f"{self._rel}::{self._current_function}"
        if self._current_class:
            sym = f"{self._rel}::{self._current_class}.{self._current_function}"
        from agentic_core.adg.schema_util import canonical_name
        return canonical_name("Symbol", sym)

    @staticmethod
    def _sym_of_call(node: ast.Call) -> str:
        """Extract symbol from a call expression."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            val = node.func.value
            prefix = val.id if isinstance(val, ast.Name) else ""
            return f"{prefix}.{node.func.attr}" if prefix else node.func.attr
        return ""

    @staticmethod
    def _is_side_effect(sym: str) -> bool:
        """Check if a symbol represents a side-effect operation."""
        return any(sym.startswith(p) or sym == p for p in _SIDE_EFFECT_PREFIXES)

    @staticmethod
    def _is_mutation_method(sym: str) -> bool:
        """Check if a symbol represents a mutation method."""
        tail = sym.rsplit(".", 1)[-1] if "." in sym else sym
        return tail in _MUTATION_METHODS

    def _span(self, node: ast.AST) -> tuple[int, int, int, int]:
        """Extract source span from AST node."""
        ln = getattr(node, "lineno", 0)
        col = getattr(node, "col_offset", 0)
        eln = getattr(node, "end_lineno", ln)
        ecol = getattr(node, "end_col_offset", col)
        return ln, col, eln, ecol

    def _emit(
        self,
        relation_type: str,
        to_name: str,
        node: ast.AST,
        symbol: str,
        semantic_type: str,
        confidence: float = 1.0,
        dynamic_resolution: str = "",
    ) -> None:
        """Emit an execution semantic edge."""
        ln, col, eln, ecol = self._span(node)
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        self.edges.append(
            _Edge(
                from_name=self._func_adg(),
                relation_type=relation_type,
                to_name=to_name,
                edge_kind="execution",
                source_file=self._rel,
                line_no=ln,
                symbol=symbol,
                semantic_type=semantic_type,
                confidence=confidence,
                source_span_line=ln,
                source_span_column=col,
                target_span_line=eln,
                target_span_column=ecol,
                dynamic_resolution=dynamic_resolution,
            )
        )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track current class context."""
        old = self._current_class
        self._current_class = node.name
        self.generic_visit(node)
        self._current_class = old

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Process function for control flow, data lineage, and calls."""
        self._enter_function(node.name)
        old_seq = self._func_seq
        self._func_seq = 0

        # Emit control flow edges for branches/loops/try inside this function
        self._walk_control_flow(node.body)

        # Emit data lineage edges for variable assignments inside this function
        self._walk_data_lineage(node.body)

        # Emit side-effect and callsite-resolution edges
        self._walk_calls(node.body)

        self._exit_function()
        self._func_seq = old_seq

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Process async functions same as sync."""
        self.visit_FunctionDef(node)  # type: ignore[arg-type]

    def _walk_control_flow(self, body: list[ast.stmt]) -> None:
        """Emit one edge per control structure (if/for/while/try) in a function."""
        if self._current_function == "":
            return
        for stmt in ast.walk(ast.Module(body=body, type_ignores=[])):
            if isinstance(stmt, ast.If):
                self._func_seq += 1
                self._emit(
                    "controls_flow",
                    self._func_adg(),
                    stmt,
                    f"if@L{getattr(stmt, 'lineno', 0)}",
                    "branch",
                    confidence=0.95,
                    dynamic_resolution=f"seq={self._func_seq}",
                )
            elif isinstance(stmt, (ast.For, ast.While)):
                self._func_seq += 1
                kind = "for" if isinstance(stmt, ast.For) else "while"
                self._emit(
                    "controls_flow",
                    self._func_adg(),
                    stmt,
                    f"{kind}@L{getattr(stmt, 'lineno', 0)}",
                    "loop",
                    confidence=0.95,
                    dynamic_resolution=f"seq={self._func_seq}",
                )
            elif isinstance(stmt, ast.Try):
                self._func_seq += 1
                self._emit(
                    "controls_flow",
                    self._func_adg(),
                    stmt,
                    f"try@L{getattr(stmt, 'lineno', 0)}",
                    "exception_handler",
                    confidence=0.95,
                    dynamic_resolution=f"seq={self._func_seq}",
                )

    def _walk_data_lineage(self, body: list[ast.stmt]) -> None:
        """Emit flows_to edges for variable assignments within functions."""
        if self._current_function == "":
            return
        for stmt in ast.walk(ast.Module(body=body, type_ignores=[])):
            if not isinstance(stmt, ast.Assign):
                continue
            # Collect source variables read in the RHS
            sources: set[str] = set()
            for sub in ast.walk(stmt.value):
                if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load):
                    sources.add(sub.id)
            if not sources:
                continue
            # For each target, emit a flows_to edge
            for tgt in stmt.targets:
                if isinstance(tgt, ast.Name):
                    self._func_seq += 1
                    self._emit(
                        "flows_to",
                        self._func_adg(),
                        stmt,
                        f"{','.join(sorted(sources))}->{tgt.id}",
                        "data_lineage",
                        confidence=0.9,
                        dynamic_resolution=f"seq={self._func_seq}",
                    )

    def _walk_calls(self, body: list[ast.stmt]) -> None:
        """Emit side-effect and callsite-resolution edges for calls."""
        if self._current_function == "":
            return
        for stmt in ast.walk(ast.Module(body=body, type_ignores=[])):
            if not isinstance(stmt, ast.Call):
                continue
            sym = self._sym_of_call(stmt)
            if not sym:
                continue

            is_se = self._is_side_effect(sym)
            is_mut = self._is_mutation_method(sym)
            is_dyn = isinstance(stmt.func, ast.Attribute)

            if is_se or is_mut:
                self._func_seq += 1
                se_type = "io" if is_se else "mutation"
                self._emit(
                    "emits_side_effect",
                    self._module_adg,
                    stmt,
                    sym,
                    se_type,
                    confidence=0.85,
                    dynamic_resolution=f"seq={self._func_seq}",
                )

            if is_dyn and not is_se and not is_mut:
                tail = sym.rsplit(".", 1)[-1] if "." in sym else sym
                if tail not in _TRIVIAL_DISPATCH_METHODS:
                    self._func_seq += 1
                    self._emit(
                        "resolves_callsite",
                        self._module_adg,
                        stmt,
                        sym,
                        "attribute_dispatch",
                        confidence=0.7,
                        dynamic_resolution=f"seq={self._func_seq}",
                    )

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("eval_spine")
class _EvalSpineVisitor(BaseRuntimeVisitor):
    """G16 (gap): Evaluation / optimization spine runtime edge extraction.

    Emits:
      module --scores_groundedness--> ADG::Symbol::<EvalMetric>
      module --emits_drift_alert--> ADG::Symbol::<drift_alert method>
      module --builds_dpo_batch--> ADG::Symbol::<DPOBatchBuilder>
      module --commits_optimization--> ADG::Symbol::<commit_optimization>
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file

    def visit_Call(self, node: ast.Call) -> None:
        """Extract evaluation spine edges from call expressions."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.schema_util import (
            DPO_BATCH_CLASSES,
            DRIFT_ALERT_METHODS,
            EVAL_METRIC_CLASSES,
            canonical_name,
        )

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""

        if tail in EVAL_METRIC_CLASSES or base in EVAL_METRIC_CLASSES:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="scores_groundedness",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="eval_score",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        elif tail in DPO_BATCH_CLASSES or base in DPO_BATCH_CLASSES:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="builds_dpo_batch",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="dpo_build",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        elif tail in DRIFT_ALERT_METHODS:
            if "drift" in tail:
                relation, ek = "emits_drift_alert", "drift_alert"
            elif "dpo" in tail or "batch" in tail:
                relation, ek = "builds_dpo_batch", "dpo_build"
            elif "commit" in tail:
                relation, ek = "commits_optimization", "optimization_commit"
            else:
                relation, ek = "scores_groundedness", "eval_score"
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type=relation,
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind=ek,
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)

    def _get_call_symbol(self, node: ast.expr) -> str:
        """Extract symbol from a call expression."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            val = node.value
            prefix = val.id if isinstance(val, ast.Name) else ""
            return f"{prefix}.{node.attr}" if prefix else node.attr
        return ""

    def extract_edges(self) -> list[Edge]:
        return self.edges
