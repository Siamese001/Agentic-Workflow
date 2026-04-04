"""P4 observability & telemetry wave visitors for G31, G33-G35 gaps."""

import ast

from agentic_core.adg.extraction.edge_builder import Edge
from agentic_core.adg.extraction.visitors import BaseStructuralVisitor, VisitorContext, register_visitor


@register_visitor("p4_state_telemetry")
class _P4StateTelemetryVisitor(BaseStructuralVisitor):
    """G31 (gap): P4 state, telemetry & learning proof edges."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        """Extract P4 state, telemetry & learning edges."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.schema_util import (
            P4_LEARNING_SYMBOLS,
            P4_STATE_SYMBOLS,
            P4_TELEMETRY_SYMBOLS,
            canonical_name,
        )

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""

        if tail in P4_STATE_SYMBOLS or base in P4_STATE_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="manages_p4_state",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="p4_state",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in P4_TELEMETRY_SYMBOLS or base in P4_TELEMETRY_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="collects_p4_telemetry",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="p4_telemetry",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in P4_LEARNING_SYMBOLS or base in P4_LEARNING_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="learns_p4",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="p4_learning",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("p4_observability_governance")
class _P4ObservabilityGovernanceVisitor(BaseStructuralVisitor):
    """G33 (gap): P4 observability & governance proof edges."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        """Extract P4 observability & governance edges."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.schema_util import (
            CAPTURES_RUNTIME_ANOMALY_SYMBOLS,
            EMITS_METRIC_EVENT_SYMBOLS,
            LINKS_INCIDENT_TRACE_SYMBOLS,
            RECORDS_INCIDENT_EVENT_SYMBOLS,
            TRIGGERS_ALERT_SYMBOLS,
            UPDATES_MONITORING_STATE_SYMBOLS,
            WRITES_OBSERVABILITY_LOG_SYMBOLS,
            canonical_name,
        )

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""

        if tail in EMITS_METRIC_EVENT_SYMBOLS or base in EMITS_METRIC_EVENT_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="emits_metric_event",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="metric_event",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in RECORDS_INCIDENT_EVENT_SYMBOLS or base in RECORDS_INCIDENT_EVENT_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="records_incident_event",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="incident_event",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in CAPTURES_RUNTIME_ANOMALY_SYMBOLS or base in CAPTURES_RUNTIME_ANOMALY_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="captures_runtime_anomaly",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="runtime_anomaly",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in WRITES_OBSERVABILITY_LOG_SYMBOLS or base in WRITES_OBSERVABILITY_LOG_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="writes_observability_log",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="observability_log",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in UPDATES_MONITORING_STATE_SYMBOLS or base in UPDATES_MONITORING_STATE_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="updates_monitoring_state",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="monitoring_state",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in TRIGGERS_ALERT_SYMBOLS or base in TRIGGERS_ALERT_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="triggers_alert",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="alert_trigger",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in LINKS_INCIDENT_TRACE_SYMBOLS or base in LINKS_INCIDENT_TRACE_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="links_incident_trace",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="incident_trace",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("retrieval_wiring")
class _RetrievalWiringVisitor(BaseStructuralVisitor):
    """G35 (gap): Retrieval wiring graph - L1-L5 retrieval bridge edge extraction."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self.edges: list[Edge] = []

    def visit_Call(self, node: ast.Call) -> None:
        """Extract retrieval wiring edges."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.schema_util import (
            L1_RETRIEVAL_SYMBOLS,
            L2_RETRIEVAL_SYMBOLS,
            L3_RETRIEVAL_SYMBOLS,
            L4_RETRIEVAL_SYMBOLS,
            L5_RETRIEVAL_SYMBOLS,
            RETRIEVAL_WIRING_SYMBOLS,
            canonical_name,
        )

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""

        if tail in RETRIEVAL_WIRING_SYMBOLS or base in RETRIEVAL_WIRING_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="wires_retrieval",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="retrieval_wiring",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in L1_RETRIEVAL_SYMBOLS or base in L1_RETRIEVAL_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="retrieves_l1",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="l1_retrieval",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in L2_RETRIEVAL_SYMBOLS or base in L2_RETRIEVAL_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="retrieves_l2",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="l2_retrieval",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in L3_RETRIEVAL_SYMBOLS or base in L3_RETRIEVAL_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="retrieves_l3",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="l3_retrieval",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in L4_RETRIEVAL_SYMBOLS or base in L4_RETRIEVAL_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="retrieves_l4",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="l4_retrieval",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        if tail in L5_RETRIEVAL_SYMBOLS or base in L5_RETRIEVAL_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self.ctx.module_adg_name,
                    relation_type="retrieves_l5",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="l5_retrieval",
                    source_file=self.ctx.source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges
