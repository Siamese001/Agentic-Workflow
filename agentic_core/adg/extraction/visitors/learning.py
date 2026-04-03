"""Learning maturity visitors for G26-G27, G32 gaps."""

import ast

from agentic_core.adg.extraction.edge_builder import Edge
from agentic_core.adg.extraction.visitors import BaseStructuralVisitor, VisitorContext, register_visitor


@register_visitor("l5_validation_proof")
class _L5ValidationProofVisitor(BaseStructuralVisitor):
    """G26 (gap): L5 validation proof edges."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        """Extract L5 validation proof edges."""
        from agentic_core.adg.schema_util import (
            canonical_name,
            L5_VALIDATION_SYMBOLS,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""

        if tail in L5_VALIDATION_SYMBOLS or base in L5_VALIDATION_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="validates_l5",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="l5_validation",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("learning_provenance")
class _LearningProvenanceVisitor(BaseStructuralVisitor):
    """G27 (gap): Learning pipeline and prompt provenance proof edges."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        """Extract learning provenance edges."""
        from agentic_core.adg.schema_util import (
            canonical_name,
            LEARNING_PIPELINE_SYMBOLS,
            PROMPT_PROVENANCE_SYMBOLS,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""

        if tail in LEARNING_PIPELINE_SYMBOLS or base in LEARNING_PIPELINE_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="records_learning_pipeline",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="learning_pipeline",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in PROMPT_PROVENANCE_SYMBOLS or base in PROMPT_PROVENANCE_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="proves_prompt_origin",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="prompt_provenance",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("p3_learning_maturity")
class _P3LearningMaturityVisitor(BaseStructuralVisitor):
    """G32 (gap): P3 learning maturity proof edges."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        """Extract P3 learning maturity edges."""
        from agentic_core.adg.schema_util import (
            canonical_name,
            CAPTURES_PATTERN_SYMBOLS,
            RECORDS_LEARNING_EVENT_SYMBOLS,
            WRITES_LEARNING_SNAPSHOT_SYMBOLS,
            FEEDS_META_LEARNING_SYMBOLS,
            UPDATES_ROUTING_STRATEGY_SYMBOLS,
            IMPROVES_AGENT_POLICY_SYMBOLS,
            STORES_LEARNING_STATE_SYMBOLS,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""

        if tail in CAPTURES_PATTERN_SYMBOLS or base in CAPTURES_PATTERN_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="captures_pattern",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="pattern_capture",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in RECORDS_LEARNING_EVENT_SYMBOLS or base in RECORDS_LEARNING_EVENT_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="records_learning_event",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="learning_event",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in WRITES_LEARNING_SNAPSHOT_SYMBOLS or base in WRITES_LEARNING_SNAPSHOT_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="writes_learning_snapshot",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="learning_snapshot",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in FEEDS_META_LEARNING_SYMBOLS or base in FEEDS_META_LEARNING_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="feeds_meta_learning",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="meta_learning",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in UPDATES_ROUTING_STRATEGY_SYMBOLS or base in UPDATES_ROUTING_STRATEGY_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="updates_routing_strategy",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="routing_update",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in IMPROVES_AGENT_POLICY_SYMBOLS or base in IMPROVES_AGENT_POLICY_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="improves_agent_policy",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="policy_improvement",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in STORES_LEARNING_STATE_SYMBOLS or base in STORES_LEARNING_STATE_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="stores_learning_state",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="learning_state",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges
