"""Advanced Lifecycle Visitors for ADG Extraction.

Visitors in this module extract advanced lifecycle and behavioral edges:
    - _PromptSlotVisitor: Prompt-slot generation and consumption (E20)
    - _ExecutionTraceVisitor: Execution trace → prompt linkage (E23)
    - _HealerValidatorVisitor: Healer/validator loop edges (G1)
    - _EmbeddingPipelineVisitor: Embedding/knowledge graph pipeline (G3)
    - _HITLVisitor: HITL/confidence-threshold gating (G4)
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from . import BaseRuntimeVisitor, BaseStructuralVisitor, VisitorContext, register_visitor

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import Edge


@register_visitor("prompt_slot")
class _PromptSlotVisitor(BaseStructuralVisitor):
    """E20: Prompt lifecycle graph — extract prompt-slot generation and consumption edges.

    Emits:
      module --generates_prompt--> ADG::PromptSlot::<SLOT>::<source_file>
      module --consumes_prompt--> ADG::PromptTemplate::<KEY>
    """

    _ASSEMBLER_NAMES: frozenset[str] = frozenset(
        {"AirlockAssembler", "GovernedPayload", "assemble", "build_payload"},
    )
    _CONSUME_NAMES: frozenset[str] = frozenset(
        {"get_prompt", "get_constitution", "load_prompt", "fetch_prompt"},
    )

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file

    def _sym(self, node: ast.expr) -> str:
        """Extract symbol from expression."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""

    def visit_Call(self, node: ast.Call) -> None:
        """Extract prompt slot edges from call expressions."""
        from agentic_core.adg.contracts.schema_util import canonical_name
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        func_sym = self._sym(node.func)
        func_tail = func_sym.split(".")[-1] if func_sym else ""

        if func_sym in self._ASSEMBLER_NAMES or func_tail in self._ASSEMBLER_NAMES:
            self._handle_assembler(node, _Edge, canonical_name)
        elif func_sym in self._CONSUME_NAMES or func_tail in self._CONSUME_NAMES:
            self._handle_consume(node, _Edge, canonical_name)

        self.generic_visit(node)

    def _handle_assembler(self, node: ast.Call, _Edge, canonical_name) -> None:
        """Emit generates_prompt for each recognised slot kwarg."""
        from agentic_core.adg.contracts.schema_util import PROMPT_FIELD_TO_SLOT

        for kw in node.keywords:
            slot = PROMPT_FIELD_TO_SLOT.get(kw.arg or "")
            if slot:
                to_name = canonical_name("PromptSlot", slot, self._source_file)
                self.edges.append(
                    _Edge(
                        from_name=self._module_adg_name,
                        relation_type="generates_prompt",
                        to_name=to_name,
                        edge_kind="prompt_generation",
                        source_file=self._source_file,
                        line_no=node.lineno,
                        symbol=f"{slot}:{kw.arg}",
                    ),
                )

    def _handle_consume(self, node: ast.Call, _Edge, canonical_name) -> None:
        """Emit consumes_prompt for get_prompt(<KEY>) and get_constitution() calls."""
        key = ""
        if node.args:
            arg0 = node.args[0]
            if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                key = arg0.value
        if not key:
            key = "CONSTITUTION"
        to_name = canonical_name("PromptTemplate", key)
        self.edges.append(
            _Edge(
                from_name=self._module_adg_name,
                relation_type="consumes_prompt",
                to_name=to_name,
                edge_kind="prompt_consumption",
                source_file=self._source_file,
                line_no=node.lineno,
                symbol=key,
            ),
        )

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("execution_trace")
class _ExecutionTraceVisitor(BaseRuntimeVisitor):
    """E23: Execution trace → prompt linkage graph.

    Emits:
      module --triggered_telemetry--> ADG::ExecutionTrace::<trace_id or source_file>
    """

    _TRACE_CALL_NAMES: frozenset[str] = frozenset(
        {
            "record_trace",
            "emit_telemetry",
            "log_run",
            "record_run",
            "emit_trace",
            "log_trace",
        },
    )
    _TRACE_ID_KWARGS: frozenset[str] = frozenset({"trace_id", "run_id", "request_id", "execution_id"})

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file

    def _sym(self, node: ast.expr) -> str:
        """Extract symbol from expression."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""

    def _extract_id(self, node: ast.Call) -> str:
        """Return the trace/run id kwarg value if present, else empty string."""
        for kw in node.keywords:
            if kw.arg in self._TRACE_ID_KWARGS:
                if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                    return kw.value.value
        return ""

    def visit_Call(self, node: ast.Call) -> None:
        """Extract execution trace edges from call expressions."""
        from agentic_core.adg.contracts.schema_util import canonical_name
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        func_sym = self._sym(node.func)
        func_tail = func_sym.split(".")[-1] if func_sym else ""

        if func_sym in self._TRACE_CALL_NAMES or func_tail in self._TRACE_CALL_NAMES:
            trace_id = self._extract_id(node)
            to_name = canonical_name("ExecutionTrace", trace_id or self._source_file)
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="triggered_telemetry",
                    to_name=to_name,
                    edge_kind="trace_prompt_link",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=trace_id or "",
                ),
            )

        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("healer_validator")
class _HealerValidatorVisitor(BaseRuntimeVisitor):
    """G1 (gap): Runtime behavior plane — healer/validator loop edge extraction.

    Emits:
      module --heals--> ADG::Symbol::<HealerBase>
      module --validates--> ADG::Symbol::<ValidatorBase>
      module --orchestrates_healing--> ADG::Symbol::<method>
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file

    def _sym(self, node: ast.expr) -> str:
        """Extract symbol from expression."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Extract healer/validator inheritance edges."""
        from agentic_core.adg.contracts.schema_util import (
            HEALER_BASE_CLASSES,
            VALIDATOR_BASE_CLASSES,
            canonical_name,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        for base in node.bases:
            base_name = self._sym(base)
            base_tail = base_name.split(".")[-1] if base_name else ""
            if base_tail in HEALER_BASE_CLASSES:
                to_name = canonical_name("Symbol", base_name or base_tail)
                self.edges.append(
                    _Edge(
                        from_name=self._module_adg_name,
                        relation_type="heals",
                        to_name=to_name,
                        edge_kind="healer_action",
                        source_file=self._source_file,
                        line_no=node.lineno,
                        symbol=base_name or base_tail,
                    ),
                )
            elif base_tail in VALIDATOR_BASE_CLASSES:
                to_name = canonical_name("Symbol", base_name or base_tail)
                self.edges.append(
                    _Edge(
                        from_name=self._module_adg_name,
                        relation_type="validates",
                        to_name=to_name,
                        edge_kind="validator_check",
                        source_file=self._source_file,
                        line_no=node.lineno,
                        symbol=base_name or base_tail,
                    ),
                )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Extract healing orchestration edges from call expressions."""
        from agentic_core.adg.contracts.schema_util import HEALER_METHOD_NAMES, canonical_name
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._sym(node.func)
        tail = sym.split(".")[-1] if sym else ""
        if tail in HEALER_METHOD_NAMES:
            to_name = canonical_name("Symbol", sym or tail)
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="orchestrates_healing",
                    to_name=to_name,
                    edge_kind="healing_dispatch",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("embedding_pipeline")
class _EmbeddingPipelineVisitor(BaseRuntimeVisitor):
    """G3 (gap): Embedding/knowledge graph — pipeline edge extraction.

    Emits:
      module --chunks_into--> ADG::Symbol::<chunker>
      module --embeds_into--> ADG::Symbol::<embedder>
      module --stores_embedding--> ADG::Symbol::<store>
      module --retrieves_via--> ADG::Symbol::<retriever>
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file

    def _sym(self, node: ast.expr) -> str:
        """Extract symbol from expression."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int, _Edge, canonical_name) -> None:
        """Emit an embedding pipeline edge."""
        to_name = canonical_name("Symbol", sym)
        self.edges.append(
            _Edge(
                from_name=self._module_adg_name,
                relation_type=relation,
                to_name=to_name,
                edge_kind=edge_kind,
                source_file=self._source_file,
                line_no=line_no,
                symbol=sym,
            ),
        )

    def visit_Call(self, node: ast.Call) -> None:
        """Extract embedding pipeline edges from call expressions."""
        from agentic_core.adg.contracts.schema_util import (
            EMBEDDING_PIPELINE_SYMBOLS,
            EMBEDDING_SYMBOLS,
            RETRIEVAL_SYMBOLS,
            VECTOR_STORE_SYMBOLS,
            canonical_name,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._sym(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""

        if tail in EMBEDDING_PIPELINE_SYMBOLS or base in EMBEDDING_PIPELINE_SYMBOLS:
            self._emit("chunks_into", "chunking_pipeline", sym or tail, node.lineno, _Edge, canonical_name)
        elif tail in EMBEDDING_SYMBOLS or base in EMBEDDING_SYMBOLS:
            self._emit("embeds_into", "embedding_pipeline", sym or tail, node.lineno, _Edge, canonical_name)
        elif tail in VECTOR_STORE_SYMBOLS or base in VECTOR_STORE_SYMBOLS:
            self._emit("stores_embedding", "embedding_pipeline", sym or tail, node.lineno, _Edge, canonical_name)
        elif tail in RETRIEVAL_SYMBOLS or sym in RETRIEVAL_SYMBOLS:
            self._emit("retrieves_via", "retrieval_pipeline", sym or tail, node.lineno, _Edge, canonical_name)

        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("hitl")
class _HITLVisitor(BaseRuntimeVisitor):
    """G4 (gap): HITL / confidence-threshold gating edge extraction.

    Emits:
      module --gated_by_confidence--> ADG::Symbol::<ConfidenceScorer>
      module --escalates_to_human--> ADG::Symbol::<escalation_method>
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file

    def _sym(self, node: ast.expr) -> str:
        """Extract symbol from expression."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""

    def visit_Call(self, node: ast.Call) -> None:
        """Extract HITL confidence and escalation edges from call expressions."""
        from agentic_core.adg.contracts.schema_util import (
            CONFIDENCE_SCORING_CLASSES,
            HITL_ESCALATION_METHODS,
            canonical_name,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._sym(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""

        if tail in CONFIDENCE_SCORING_CLASSES or base in CONFIDENCE_SCORING_CLASSES:
            to_name = canonical_name("Symbol", sym or tail)
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="gated_by_confidence",
                    to_name=to_name,
                    edge_kind="confidence_gate",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        elif tail in HITL_ESCALATION_METHODS:
            to_name = canonical_name("Symbol", sym or tail)
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="escalates_to_human",
                    to_name=to_name,
                    edge_kind="hitl_escalation",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )

        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges
