"""Transport & Proof Visitors for ADG Extraction.

Visitors in this module extract mutation transport and execution proof edges:
    - _MutationTransportVisitor: diff packaging, blast radius validation, commit
    - _ExecutionProofVisitor: execution trace recording, replay keys, proof comparison
    - _PathControlVisitor: path routing, stalling, safety reentry, vigilance reroute
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from . import BaseRuntimeVisitor, VisitorContext, register_visitor

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import Edge


@register_visitor("mutation_transport")
class _MutationTransportVisitor(BaseRuntimeVisitor):
    """G13 (gap): Mutation transport / commit protocol edge extraction.

    Emits:
      module --packages_diff--> ADG::Symbol::<RFC6902 diff method>
      module --validates_blast_radius--> ADG::Symbol::<BlastRadiusChecker>
      module --signs_execution_trace--> ADG::Symbol::<MutationTransport>
      module --commits_mutation--> ADG::Symbol::<TwoPhaseCommit>
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file

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
        """Extract mutation transport edges from call expressions."""
        from agentic_core.adg.contracts.schema_util import (
            MUTATION_TRANSPORT_CLASSES,
            RFC6902_DIFF_SYMBOLS,
            canonical_name,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in RFC6902_DIFF_SYMBOLS:
            if "blast" in tail:
                relation, ek = "validates_blast_radius", "blast_radius_check"
            else:
                relation, ek = "packages_diff", "diff_package"
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type=relation,
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind=ek,
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        elif tail in MUTATION_TRANSPORT_CLASSES or base in MUTATION_TRANSPORT_CLASSES:
            if "commit" in tail.lower() or "TwoPhase" in tail:
                relation, ek = "commits_mutation", "two_phase_commit"
            elif "Distrib" in tail:
                relation, ek = "distributes_mutation", "mutation_distribution"
            else:
                relation, ek = "signs_execution_trace", "diff_package"
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type=relation,
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind=ek,
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("execution_proof")
class _ExecutionProofVisitor(BaseRuntimeVisitor):
    """G14 (gap): Execution trace / proof runtime edge extraction.

    Emits:
      module --records_execution_trace--> ADG::Symbol::<ExecutionTrace>
      module --emits_replay_key--> ADG::Symbol::<emit_replay_key method>
      module --compares_proof--> ADG::Symbol::<compare_proof method>
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file

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
        """Extract execution proof edges from call expressions."""
        from agentic_core.adg.contracts.schema_util import (
            EXECUTION_TRACE_CLASSES,
            REPLAY_KEY_METHODS,
            canonical_name,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in EXECUTION_TRACE_CLASSES or base in EXECUTION_TRACE_CLASSES:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="records_execution_trace",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="execution_trace_record",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        elif tail in REPLAY_KEY_METHODS:
            if "compare" in tail:
                relation, ek = "compares_proof", "proof_comparison"
            elif "replay" in tail and "key" in tail or "replay_key" in tail:
                relation, ek = "emits_replay_key", "replay_key_emit"
            elif tail in (
                "stamp_decision",
                "guards_replay",
                "verify_routing_replay",
                "emit_determinism_digest",
                "emit_routing_digest",
            ):
                relation, ek = "emits_replay_key", "replay_key_emit"
            else:
                relation, ek = "records_execution_trace", "execution_trace_record"
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type=relation,
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind=ek,
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("path_control")
class _PathControlVisitor(BaseRuntimeVisitor):
    """G15 (gap): Execution path control runtime edge extraction.

    Emits:
      module --routes_path--> ADG::Symbol::<PathRouter>
      module --forces_stall--> ADG::Symbol::<StallForcer>
      module --reenters_safety--> ADG::Symbol::<SafetyReentryGate>
      module --vigilance_reroute--> ADG::Symbol::<VigilanceRerouter>
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file

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
        """Extract path control edges from call expressions."""
        from agentic_core.adg.contracts.schema_util import (
            PATH_CONTROL_CLASSES,
            PATH_REROUTE_METHODS,
            canonical_name,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in PATH_CONTROL_CLASSES or base in PATH_CONTROL_CLASSES:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="routes_path",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="path_route",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        elif tail in PATH_REROUTE_METHODS:
            if "stall" in tail or "force" in tail:
                relation, ek = "forces_stall", "path_stall"
            elif "reenter" in tail or "safety" in tail:
                relation, ek = "reenters_safety", "path_safety_reentry"
            elif "vigilance" in tail or "reroute" in tail:
                relation, ek = "vigilance_reroute", "path_vigilance_reroute"
            else:
                relation, ek = "routes_path", "path_route"
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type=relation,
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind=ek,
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges
