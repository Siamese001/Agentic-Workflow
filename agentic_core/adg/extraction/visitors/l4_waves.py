"""L4/UWG Wave Visitors for ADG Extraction.

Visitors in this module extract L4 state management and UWG governance edges:
    - Wave 1: Ingress Gate validation
    - Wave 2: Mutation Record Assembly
    - Wave 3: Authoritative Commit + L4 Read Surface
    - Wave 4: Outbound Read Bridge
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from . import BaseStructuralVisitor, VisitorContext, register_visitor

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import Edge


@register_visitor("uwg_ingress_gate")
class _UWGIngressGateVisitor(BaseStructuralVisitor):
    """G34: L4/UWG Wave 1 Ingress Gate edge extraction.

    Emits:
      - validates_uwg_intent
      - checks_policy_hash_at_uwg
      - checks_capability_set
      - validates_blast_radius_at_uwg
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file

    def _sym(self, node: ast.AST) -> str:
        """Extract symbol from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f"{self._sym(node.value)}.{node.attr}"
        return ""

    def visit_Call(self, node: ast.Call) -> None:
        """Extract UWG ingress gate edges from call expressions."""
        from agentic_core.adg.contracts.schema_util import (
            UWG_BLAST_RADIUS_SYMBOLS,
            UWG_CHECKS_CAPABILITY_SET_SYMBOLS,
            UWG_CHECKS_POLICY_HASH_SYMBOLS,
            UWG_VALIDATES_INTENT_SYMBOLS,
            canonical_name,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._sym(node.func)
        if not sym:
            self.generic_visit(node)
            return

        tail = sym.split(".")[-1]
        base = sym.split(".")[0]

        # Check UWG ingress gate symbols
        if base in UWG_VALIDATES_INTENT_SYMBOLS or tail in UWG_VALIDATES_INTENT_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="validates_uwg_intent",
                    edge_kind="uwg_validation",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )
        elif base in UWG_CHECKS_POLICY_HASH_SYMBOLS or tail in UWG_CHECKS_POLICY_HASH_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="checks_policy_hash_at_uwg",
                    edge_kind="uwg_validation",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )
        elif base in UWG_CHECKS_CAPABILITY_SET_SYMBOLS or tail in UWG_CHECKS_CAPABILITY_SET_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="checks_capability_set",
                    edge_kind="uwg_validation",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )
        elif base in UWG_BLAST_RADIUS_SYMBOLS or tail in UWG_BLAST_RADIUS_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="validates_blast_radius_at_uwg",
                    edge_kind="uwg_validation",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )

        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("mutation_record_assembly")
class _MutationRecordAssemblyVisitor(BaseStructuralVisitor):
    """G35: L4/UWG Wave 2 Mutation Record Assembly edge extraction.

    Emits:
      - generates_mutation_diff
      - computes_mutation_replay_key
      - applies_hmac_seal
      - packages_execution_trace
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file

    def _sym(self, node: ast.AST) -> str:
        """Extract symbol from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f"{self._sym(node.value)}.{node.attr}"
        return ""

    def visit_Call(self, node: ast.Call) -> None:
        """Extract mutation record assembly edges from call expressions."""
        from agentic_core.adg.contracts.schema_util import (
            EXECUTION_TRACE_PACKAGE_SYMBOLS,
            HMAC_SEAL_SYMBOLS,
            MUTATION_DIFF_SYMBOLS,
            MUTATION_REPLAY_KEY_SYMBOLS,
            canonical_name,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._sym(node.func)
        if not sym:
            self.generic_visit(node)
            return

        tail = sym.split(".")[-1]
        base = sym.split(".")[0]

        # Check mutation record assembly symbols
        if base in MUTATION_DIFF_SYMBOLS or tail in MUTATION_DIFF_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="generates_mutation_diff",
                    edge_kind="mutation_assembly",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )
        elif base in MUTATION_REPLAY_KEY_SYMBOLS or tail in MUTATION_REPLAY_KEY_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="computes_mutation_replay_key",
                    edge_kind="mutation_assembly",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )
        elif base in HMAC_SEAL_SYMBOLS or tail in HMAC_SEAL_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="applies_hmac_seal",
                    edge_kind="mutation_assembly",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )
        elif base in EXECUTION_TRACE_PACKAGE_SYMBOLS or tail in EXECUTION_TRACE_PACKAGE_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="packages_execution_trace",
                    edge_kind="mutation_assembly",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )

        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("authoritative_commit")
class _AuthoritativeCommitVisitor(BaseStructuralVisitor):
    """G36: L4/UWG Wave 3 Authoritative Commit + L4 Read Surface edge extraction.

    Emits:
      - claims_write_lock
      - commits_mutation_durable
      - appends_hash_chain
      - heals_on_rollback_failure
      - materializes_read_view
      - refreshes_retrieval_surface
      - swaps_version_alias
      - syncs_l4_telemetry
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file

    def _sym(self, node: ast.AST) -> str:
        """Extract symbol from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f"{self._sym(node.value)}.{node.attr}"
        return ""

    def visit_Call(self, node: ast.Call) -> None:
        """Extract authoritative commit edges from call expressions."""
        from agentic_core.adg.contracts.schema_util import (
            CLAIMS_WRITE_LOCK_SYMBOLS,
            DURABLE_COMMIT_SYMBOLS,
            HASH_CHAIN_APPEND_SYMBOLS,
            L4_TELEMETRY_SYNC_SYMBOLS,
            MATERIALIZES_READ_VIEW_SYMBOLS,
            RETRIEVAL_SURFACE_REFRESH_SYMBOLS,
            ROLLBACK_HEAL_SYMBOLS,
            SWAPS_VERSION_ALIAS_SYMBOLS,
            canonical_name,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._sym(node.func)
        if not sym:
            self.generic_visit(node)
            return

        tail = sym.split(".")[-1]
        base = sym.split(".")[0]

        # Check authoritative commit symbols
        if base in CLAIMS_WRITE_LOCK_SYMBOLS or tail in CLAIMS_WRITE_LOCK_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="claims_write_lock",
                    edge_kind="authoritative_commit",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )
        elif base in DURABLE_COMMIT_SYMBOLS or tail in DURABLE_COMMIT_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="commits_mutation_durable",
                    edge_kind="authoritative_commit",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )
        elif base in HASH_CHAIN_APPEND_SYMBOLS or tail in HASH_CHAIN_APPEND_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="appends_hash_chain",
                    edge_kind="authoritative_commit",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )
        elif base in ROLLBACK_HEAL_SYMBOLS or tail in ROLLBACK_HEAL_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="heals_on_rollback_failure",
                    edge_kind="authoritative_commit",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )
        # Check L4 read surface symbols
        elif base in MATERIALIZES_READ_VIEW_SYMBOLS or tail in MATERIALIZES_READ_VIEW_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="materializes_read_view",
                    edge_kind="l4_read_surface",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )
        elif base in RETRIEVAL_SURFACE_REFRESH_SYMBOLS or tail in RETRIEVAL_SURFACE_REFRESH_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="refreshes_retrieval_surface",
                    edge_kind="l4_read_surface",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )
        elif base in SWAPS_VERSION_ALIAS_SYMBOLS or tail in SWAPS_VERSION_ALIAS_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="swaps_version_alias",
                    edge_kind="l4_read_surface",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )
        elif base in L4_TELEMETRY_SYNC_SYMBOLS or tail in L4_TELEMETRY_SYNC_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="syncs_l4_telemetry",
                    edge_kind="l4_read_surface",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )

        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("outbound_read_bridge")
class _OutboundReadBridgeVisitor(BaseStructuralVisitor):
    """G37: L4/UWG Wave 4 Outbound Read Bridge edge extraction.

    Emits:
      - reads_l4_surface (C0/L1 context builds)
      - receives_policy_hash (L0 routing)
      - l5_reads_l4_surface (L5 constitution)
      - l3_reads_l4_surface (L3 DAG workflow)
      - l6_ingests_l4_trace (L6 observability)
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file

    def _sym(self, node: ast.AST) -> str:
        """Extract symbol from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f"{self._sym(node.value)}.{node.attr}"
        return ""

    def visit_Call(self, node: ast.Call) -> None:
        """Extract outbound read bridge edges from call expressions."""
        from agentic_core.adg.contracts.schema_util import (
            L0_RECEIVES_POLICY_HASH_SYMBOLS,
            L3_READS_L4_SURFACE_SYMBOLS,
            L5_READS_L4_SURFACE_SYMBOLS,
            L6_INGESTS_L4_TRACE_SYMBOLS,
            READS_L4_SURFACE_SYMBOLS,
            canonical_name,
        )
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge

        sym = self._sym(node.func)
        if not sym:
            self.generic_visit(node)
            return

        tail = sym.split(".")[-1]
        base = sym.split(".")[0]

        # Check outbound read bridge symbols
        if base in READS_L4_SURFACE_SYMBOLS or tail in READS_L4_SURFACE_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="reads_l4_surface",
                    edge_kind="outbound_read_bridge",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )
        elif base in L0_RECEIVES_POLICY_HASH_SYMBOLS or tail in L0_RECEIVES_POLICY_HASH_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="receives_policy_hash",
                    edge_kind="outbound_read_bridge",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )
        elif base in L5_READS_L4_SURFACE_SYMBOLS or tail in L5_READS_L4_SURFACE_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="l5_reads_l4_surface",
                    edge_kind="outbound_read_bridge",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )
        elif base in L3_READS_L4_SURFACE_SYMBOLS or tail in L3_READS_L4_SURFACE_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="l3_reads_l4_surface",
                    edge_kind="outbound_read_bridge",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )
        elif base in L6_INGESTS_L4_TRACE_SYMBOLS or tail in L6_INGESTS_L4_TRACE_SYMBOLS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    to_name=canonical_name("Symbol", sym),
                    relation_type="l6_ingests_l4_trace",
                    edge_kind="outbound_read_bridge",
                    source_file=self._source_file,
                    line_no=getattr(node, "lineno", 1),
                    symbol=sym,
                ),
            )

        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges
