"""Governance & Safety Visitors for ADG Extraction.

Visitors in this module extract governance and safety enforcement edges:
    - _GovernancePlaneVisitor: writes_through, routes_through, reads_through
    - _SafetyEnforcementVisitor: applies_guardrail, verifies_policy
    - _SandboxAirlockVisitor: sandbox/work-contract edges
    - _CapabilityBudgetVisitor: resource governance edges
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from . import BaseStructuralVisitor, VisitorContext, register_visitor

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import Edge


@register_visitor("governance_plane")
class _GovernancePlaneVisitor(BaseStructuralVisitor):
    """GG: Emit writes_through / routes_through / reads_through edges for governance chokepoints."""

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Extract governance edges from class inheritance."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.contracts.schema_util import GOVERNANCE_WRITE_SYMBOLS, canonical_name

        for base in node.bases:
            sym = self._extract_symbol(base)
            if sym:
                tail = sym.split(".")[-1]
                base_name = sym.split(".")[0]
                if base_name in GOVERNANCE_WRITE_SYMBOLS or tail in GOVERNANCE_WRITE_SYMBOLS:
                    self.edges.append(
                        _Edge(
                            from_name=self._module_adg_name,
                            relation_type="writes_through",
                            to_name=canonical_name("Symbol", sym),
                            edge_kind="write",
                            source_file=self._source_file,
                            line_no=node.lineno,
                            symbol=sym,
                        )
                    )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Extract governance edges from function calls."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.contracts.schema_util import (
            GOVERNANCE_READ_SYMBOLS,
            GOVERNANCE_ROUTE_SYMBOLS,
            GOVERNANCE_WRITE_SYMBOLS,
            canonical_name,
        )

        sym = self._extract_symbol(node.func)
        if sym:
            base = sym.split(".")[0]
            tail = sym.split(".")[-1]
            # Suppress instrumentation helpers from generating governance edges
            if tail.startswith("_emit_") or tail.startswith("emit_"):
                self.generic_visit(node)
                return
            if base in GOVERNANCE_WRITE_SYMBOLS or tail in GOVERNANCE_WRITE_SYMBOLS:
                to_name = canonical_name("Symbol", sym)
                self.edges.append(
                    _Edge(
                        from_name=self._module_adg_name,
                        relation_type="writes_through",
                        to_name=to_name,
                        edge_kind="write",
                        source_file=self._source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
            elif base in GOVERNANCE_ROUTE_SYMBOLS or tail in GOVERNANCE_ROUTE_SYMBOLS:
                to_name = canonical_name("Symbol", sym)
                self.edges.append(
                    _Edge(
                        from_name=self._module_adg_name,
                        relation_type="routes_through",
                        to_name=to_name,
                        edge_kind="call",
                        source_file=self._source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
            elif base in GOVERNANCE_READ_SYMBOLS or tail in GOVERNANCE_READ_SYMBOLS:
                to_name = canonical_name("Symbol", sym)
                self.edges.append(
                    _Edge(
                        from_name=self._module_adg_name,
                        relation_type="reads_through",
                        to_name=to_name,
                        edge_kind="read",
                        source_file=self._source_file,
                        line_no=node.lineno,
                        symbol=sym,
                    )
                )
        self.generic_visit(node)

    @staticmethod
    def _extract_symbol(func_node: ast.expr) -> str:
        """Extract symbol from function expression."""
        if isinstance(func_node, ast.Name):
            return func_node.id
        if isinstance(func_node, ast.Attribute):
            parts: list[str] = []
            current: ast.expr = func_node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return ""

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("safety_enforcement")
class _SafetyEnforcementVisitor(BaseStructuralVisitor):
    """G5 (gap): Safety enforcement runtime plane — guardrail + policy hash edge extraction.

    Emits:
      module --applies_guardrail--> ADG::Symbol::<GuardrailClass>
      module --verifies_policy--> ADG::Symbol::<policy_hash_method>
    """

    def __init__(self, ctx: VisitorContext) -> None:
        super().__init__(ctx)
        self._module_adg_name = ctx.module_adg_name
        self._source_file = ctx.source_file

    def visit_Call(self, node: ast.Call) -> None:
        """Extract safety enforcement edges from call expressions."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.contracts.schema_util import GUARDRAIL_CLASS_NAMES, POLICY_HASH_METHODS, canonical_name

        sym = self._sym(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""

        if tail in GUARDRAIL_CLASS_NAMES or base in GUARDRAIL_CLASS_NAMES:
            to_name = canonical_name("Symbol", sym or tail)
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="applies_guardrail",
                    to_name=to_name,
                    edge_kind="guardrail_execution",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        elif tail in POLICY_HASH_METHODS:
            to_name = canonical_name("Symbol", sym or tail)
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="verifies_policy",
                    to_name=to_name,
                    edge_kind="policy_verification",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )

        self.generic_visit(node)

    @staticmethod
    def _sym(node: ast.expr) -> str:
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

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("sandbox_airlock")
class _SandboxAirlockVisitor(BaseStructuralVisitor):
    """G7 (gap): Sandbox airlock / work-contract edge extraction.

    Emits:
      module --stamps_work_contract--> ADG::Symbol::<WorkContract>
      module --issues_capability_token--> ADG::Symbol::<CapabilityToken>
      module --enters_sandbox--> ADG::Symbol::<SandboxEnvelope>
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
        """Extract sandbox airlock edges from call expressions."""
        from agentic_core.adg.contracts.schema_util import (
            CAPABILITY_TOKEN_CLASSES,
            SANDBOX_ENVELOPE_CLASSES,
            WORK_CONTRACT_METHODS,
        )

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in SANDBOX_ENVELOPE_CLASSES or base in SANDBOX_ENVELOPE_CLASSES:
            self._emit("enters_sandbox", "sandbox_entry", sym or tail, node.lineno)
        elif tail in CAPABILITY_TOKEN_CLASSES or base in CAPABILITY_TOKEN_CLASSES:
            self._emit("issues_capability_token", "capability_token_issue", sym or tail, node.lineno)
        elif tail in WORK_CONTRACT_METHODS:
            self._emit("stamps_work_contract", "work_contract_stamp", sym or tail, node.lineno)
        self.generic_visit(node)

    def _emit(self, relation: str, edge_kind: str, sym: str, line_no: int) -> None:
        """Emit a sandbox airlock edge."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.contracts.schema_util import canonical_name
        self.edges.append(
            _Edge(
                from_name=self._module_adg_name,
                relation_type=relation,
                to_name=canonical_name("Symbol", sym),
                edge_kind=edge_kind,
                source_file=self._source_file,
                line_no=line_no,
                symbol=sym,
            )
        )

    def extract_edges(self) -> list[Edge]:
        return self.edges


@register_visitor("capability_budget")
class _CapabilityBudgetVisitor(BaseStructuralVisitor):
    """G8 (gap): Capability-token / tool-budget resource governance edge extraction.

    Emits:
      module --grants_resource--> ADG::Symbol::<ToolBudget>
      module --exceeds_budget--> ADG::Symbol::<BudgetExceededException>
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
        """Extract capability budget edges from call expressions."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.contracts.schema_util import TOOL_BUDGET_CLASSES, canonical_name

        sym = self._get_call_symbol(node.func)
        tail = sym.split(".")[-1] if sym else ""
        base = sym.split(".")[0] if sym else ""
        if tail in TOOL_BUDGET_CLASSES or base in TOOL_BUDGET_CLASSES:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="grants_resource",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="budget_grant",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> None:
        """Extract exceeds_budget edges from raise statements."""
        from agentic_core.adg.extraction.static_scanner import Edge as _Edge
        from agentic_core.adg.contracts.schema_util import BUDGET_EXCEEDED_EXCEPTIONS, canonical_name

        if node.exc is None:
            self.generic_visit(node)
            return
        sym = self._get_call_symbol(node.exc)
        tail = sym.split(".")[-1] if sym else ""
        if tail in BUDGET_EXCEEDED_EXCEPTIONS or sym in BUDGET_EXCEEDED_EXCEPTIONS:
            self.edges.append(
                _Edge(
                    from_name=self._module_adg_name,
                    relation_type="exceeds_budget",
                    to_name=canonical_name("Symbol", sym or tail),
                    edge_kind="budget_exceeded",
                    source_file=self._source_file,
                    line_no=node.lineno,
                    symbol=sym or tail,
                )
            )
        self.generic_visit(node)

    def extract_edges(self) -> list[Edge]:
        return self.edges
