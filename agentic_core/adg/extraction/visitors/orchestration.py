"""Orchestration visitors for P1-P3 orchestration and healing gaps (G22, G28-G30)."""

import ast

from agentic_core.adg.extraction.edge_builder import Edge
from agentic_core.adg.extraction.visitors import BaseStructuralVisitor, VisitorContext, register_visitor


@register_visitor("healing_orchestrator")
class _HealingOrchestratorVisitor(BaseStructuralVisitor):
    """G22 (gap): Healing orchestrator edge extraction.

    Emits:
        - triggers_healing
        - records_healing_decision
        - validates_healing_outcome
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        """Extract healing orchestrator edges from call expressions."""
        from agentic_core.adg.contracts.schema_util import (
            HEALING_DECISION_SYMBOLS,
            HEALING_ORCHESTRATOR_SYMBOLS,
            HEALING_TRIGGER_SYMBOLS,
            HEALING_VALIDATION_SYMBOLS,
            canonical_name,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""

        if tail in HEALING_ORCHESTRATOR_SYMBOLS or base in HEALING_ORCHESTRATOR_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="triggers_healing",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="healing_trigger",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        if tail in HEALING_TRIGGER_SYMBOLS or base in HEALING_TRIGGER_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="triggers_healing",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="healing_trigger",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        if tail in HEALING_DECISION_SYMBOLS or base in HEALING_DECISION_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="records_healing_decision",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="healing_decision",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        if tail in HEALING_VALIDATION_SYMBOLS or base in HEALING_VALIDATION_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="validates_healing_outcome",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="healing_validation",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("p1_orchestration")
class _P1OrchestrationVisitor(BaseStructuralVisitor):
    """G28 (gap): P1 orchestration proof edges."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        """Extract P1 orchestration edges."""
        from agentic_core.adg.contracts.schema_util import (
            P1_ORCHESTRATION_SYMBOLS,
            canonical_name,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""

        if tail in P1_ORCHESTRATION_SYMBOLS or base in P1_ORCHESTRATION_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="orchestrates_p1",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="p1_orchestration",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("p2_execution_capability")
class _P2ExecutionCapabilityVisitor(BaseStructuralVisitor):
    """G29 (gap): P2 execution capability proof edges."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        """Extract P2 execution capability edges."""
        from agentic_core.adg.contracts.schema_util import (
            P2_EXECUTION_SYMBOLS,
            canonical_name,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""

        if tail in P2_EXECUTION_SYMBOLS or base in P2_EXECUTION_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="executes_p2",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="p2_execution",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("p3_orchestration_healing")
class _P3OrchestrationHealingVisitor(BaseStructuralVisitor):
    """G30 (gap): P3 orchestration & healing proof edges."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        """Extract P3 orchestration & healing edges."""
        from agentic_core.adg.contracts.schema_util import (
            P3_HEALING_SYMBOLS,
            P3_ORCHESTRATION_SYMBOLS,
            canonical_name,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""

        if tail in P3_ORCHESTRATION_SYMBOLS or base in P3_ORCHESTRATION_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="orchestrates_p3",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="p3_orchestration",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        if tail in P3_HEALING_SYMBOLS or base in P3_HEALING_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="heals_p3",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="p3_healing",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("architecture_handoff")
class _ArchitectureHandoffVisitor(BaseStructuralVisitor):
    """Extract architecture handoff edges (validates_request, produces_plan, proposes_route, etc.).

    Emits edges for the 13 forward-pass handoff relation types by matching call symbols
    against the HANDOFF_* symbol sets defined in schema_util.py.
    """

    _SYMBOL_SET_MAP = (
        ("HANDOFF_VALIDATE_SYMBOLS", "validates_request", "handoff_validate"),
        ("HANDOFF_PLAN_SYMBOLS", "produces_plan", "handoff_plan"),
        ("HANDOFF_ROUTE_SYMBOLS", "proposes_route", "handoff_route"),
        ("HANDOFF_PREFILTER_SYMBOLS", "prefilters_scope", "handoff_prefilter"),
        ("HANDOFF_EVIDENCE_SYMBOLS", "produces_evidence_contract", "handoff_evidence"),
        ("HANDOFF_PROMPT_PKG_SYMBOLS", "packages_prompt_envelope", "handoff_prompt_pkg"),
        ("HANDOFF_EXEC_STAMP_SYMBOLS", "stamps_execution_packet", "handoff_exec_stamp"),
        ("HANDOFF_POLICY_HASH_SYMBOLS", "propagates_policy_hash", "handoff_policy_hash"),
        ("HANDOFF_REPLAY_KEY_SYMBOLS", "propagates_replay_key", "handoff_replay_key"),
        ("HANDOFF_BLAST_RADIUS_SYMBOLS", "verifies_blast_radius", "handoff_blast_radius"),
        ("HANDOFF_COMMIT_RECEIPT_SYMBOLS", "appends_commit_receipt", "handoff_commit_receipt"),
        ("HANDOFF_RETRIEVAL_SURFACE_SYMBOLS", "publishes_retrieval_surface", "handoff_retrieval_surface"),
        ("HANDOFF_PROMOTE_SYMBOLS", "promotes_future_run_change", "handoff_promote"),
    )

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self.edges: list[Edge] = []

    def _get_call_symbol(self, node: ast.expr) -> str:
        """Extract symbol from call expression."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            val = node.value
            prefix = val.id if isinstance(val, ast.Name) else ""
            return f"{prefix}.{node.attr}" if prefix else node.attr
        return ""

    def visit_Call(self, node: ast.Call) -> None:
        """Extract architecture handoff edges from call expressions."""
        import agentic_core.adg.contracts.schema_util as _su
        from agentic_core.adg.contracts.schema_util import canonical_name
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._get_call_symbol(node.func)
        if not sym:
            self.generic_visit(node)
            return
        tail = sym.split(".")[-1]
        base = sym.split(".")[0]

        for attr, relation_type, edge_kind in self._SYMBOL_SET_MAP:
            symbol_set: frozenset[str] = getattr(_su, attr, frozenset())
            if tail in symbol_set or base in symbol_set:
                self.edges.append(
                    _Edge(
                        from_name=self.ctx.module_adg_name,
                        relation_type=relation_type,
                        to_name=canonical_name("Symbol", sym),
                        edge_kind=edge_kind,
                        source_file=self.ctx.source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    ),
                )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges
