"""Context & Control Visitors for ADG Extraction.

Visitors in this module extract context synchronization and control flow edges:
    - _JITContextVisitor: JIT context sync/freeze edges
    - _BoundaryVerifierVisitor: Execution boundary verification
    - _DeterminismControlVisitor: Determinism control (seed, patch, digest)
    - _IOInterceptionVisitor: Network/I/O interception edges
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from . import BaseRuntimeVisitor, VisitorContext, register_visitor

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import Edge


@register_visitor("jit_context")
class _JITContextVisitor(BaseRuntimeVisitor):
    """G9 (gap): JIT context sync / freeze edge extraction.

    Emits:
      module --pulls_context--> ADG::Symbol::<JITContext>
      module --freezes_context--> ADG::Symbol::<freeze_method>
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
        """Extract JIT context edges from call expressions."""
        from agentic_core.adg.contracts.schema_util import (
            FREEZE_METHOD_NAMES,
            JIT_CONTEXT_CLASSES,
            canonical_name,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        # Suppress instrumentation helpers from generating context edges
        if tail.startswith("_emit_") or tail.startswith("emit_"):
            self.generic_visit(node)
            return
        if tail in JIT_CONTEXT_CLASSES or base in JIT_CONTEXT_CLASSES:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="pulls_context",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="context_pull",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        elif tail in FREEZE_METHOD_NAMES:
            if "unfreeze" in tail:
                relation, edge_kind = "unfreezes_context", "context_pull"
            elif "pull" in tail or "sync" in tail:
                relation, edge_kind = "pulls_context", "context_pull"
            else:
                relation, edge_kind = "freezes_context", "context_freeze"
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type=relation,
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind=edge_kind,
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("boundary_verifier")
class _BoundaryVerifierVisitor(BaseRuntimeVisitor):
    """G10 (gap): Execution boundary verification edge extraction.

    Emits:
      module --verifies_boundary--> ADG::Symbol::<L2BoundaryVerifier>
      module --certifies_envelope--> ADG::Symbol::<CapabilityChokepoint>
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
        """Extract boundary verification edges from call expressions."""
        from agentic_core.adg.contracts.schema_util import (
            BOUNDARY_VERIFIER_CLASSES,
            CAPABILITY_CHOKEPOINT_CLASSES,
            canonical_name,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in BOUNDARY_VERIFIER_CLASSES or base in BOUNDARY_VERIFIER_CLASSES:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="verifies_boundary",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="boundary_accept",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        elif tail in CAPABILITY_CHOKEPOINT_CLASSES or base in CAPABILITY_CHOKEPOINT_CLASSES:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="certifies_envelope",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="boundary_accept",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("determinism_control")
class _DeterminismControlVisitor(BaseRuntimeVisitor):
    """G11 (gap): Determinism control runtime edge extraction.

    Emits:
      module --seeds_rng--> ADG::Symbol::<SemanticClock|rng_seed_method>
      module --patches_time--> ADG::Symbol::<patch_time method>
      module --guards_replay--> ADG::Symbol::<ReplayGuard>
      module --emits_determinism_digest--> ADG::Symbol::<emit_method>
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
        """Extract determinism control edges from call expressions."""
        from agentic_core.adg.contracts.schema_util import (
            DETERMINISM_PATCH_METHODS,
            REPLAY_GUARD_CLASSES,
            SEMANTIC_CLOCK_CLASSES,
            canonical_name,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in SEMANTIC_CLOCK_CLASSES or base in SEMANTIC_CLOCK_CLASSES:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="patches_time",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="replay_patch",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        elif tail in REPLAY_GUARD_CLASSES or base in REPLAY_GUARD_CLASSES:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="guards_replay",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="replay_patch",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        elif tail in DETERMINISM_PATCH_METHODS:
            if "digest" in tail or tail in ("stamp_decision", "emit_routing_digest"):
                relation, edge_kind = "emits_determinism_digest", "determinism_digest_emit"
            elif "seed" in tail or "rng" in tail or "random" in tail or "uuid" in tail:
                relation, edge_kind = "seeds_rng", "determinism_seed"
            else:
                relation, edge_kind = "patches_time", "replay_patch"
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type=relation,
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind=edge_kind,
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("io_interception")
class _IOInterceptionVisitor(BaseRuntimeVisitor):
    """G12 (gap): Network / I/O interception edge extraction.

    Emits:
      module --intercepts_io--> ADG::Symbol::<IOInterceptor>
      module --transcripts_response--> ADG::Symbol::<transcript_method>
      module --hard_fails_untranscripted--> ADG::Symbol::<hard_fail_method>
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
        """Extract I/O interception edges from call expressions."""
        from agentic_core.adg.contracts.schema_util import (
            IO_INTERCEPT_CLASSES,
            NETWORK_TRANSCRIPT_SYMBOLS,
            canonical_name,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in IO_INTERCEPT_CLASSES or base in IO_INTERCEPT_CLASSES:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="intercepts_io",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="io_transcript",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                ),
            )
        elif tail in NETWORK_TRANSCRIPT_SYMBOLS:
            if "hard_fail" in tail:
                relation, ek = "hard_fails_untranscripted", "io_hard_fail"
            else:
                relation, ek = "transcripts_response", "io_transcript"
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
