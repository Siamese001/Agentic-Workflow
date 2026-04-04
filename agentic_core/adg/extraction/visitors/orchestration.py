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
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.schema_util import (
            HEALING_DECISION_SYMBOLS,
            HEALING_ORCHESTRATOR_SYMBOLS,
            HEALING_TRIGGER_SYMBOLS,
            HEALING_VALIDATION_SYMBOLS,
            canonical_name,
        )

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
                )
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
                )
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
                )
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
                )
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
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.schema_util import (
            P1_ORCHESTRATION_SYMBOLS,
            canonical_name,
        )

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
                )
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
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.schema_util import (
            P2_EXECUTION_SYMBOLS,
            canonical_name,
        )

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
                )
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
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.schema_util import (
            P3_HEALING_SYMBOLS,
            P3_ORCHESTRATION_SYMBOLS,
            canonical_name,
        )

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
                )
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
                )
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges
