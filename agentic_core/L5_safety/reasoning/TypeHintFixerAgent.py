from __future__ import annotations

import ast
from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"\nTypeHintFixerAgent - Extracted for one-class-per-file pattern.\n\nOriginally from: TypeHintEnforcementAgent.py\nExtracted: 2026-01-06 (Surgical Extraction)\n"
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)
from agentic_core.utils.decorators_compat_util import standard_heal


@dataclass
class TypeHintFixerAgent(SovereignBaseAgent, ast.NodeTransformer):
    """
    AST transformer that adds Missing type hints to public symbols.
    """

    def __init__(self, fallback_param: str, fallback_return: str, fallback_var: str) -> None:
        """Initialize the instance."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "TypeHintFixerAgent.__init__", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "TypeHintFixerAgent.__init__", "p0_governance")
        self.added_count = 0
        self.fallback_param = fallback_param
        self.fallback_return = fallback_return
        self.fallback_var = fallback_var

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Execute visit_FunctionDef operation."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "TypeHintFixerAgent.visit_FunctionDef"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:TypeHintFixerAgent.visit_FunctionDef".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if node.name.startswith("_"):
            return node
        for arg in node.args.args:
            if arg.annotation is None and arg.arg != "self" and (arg.arg != "cls"):
                arg.annotation = ast.Name(id=self.fallback_param, ctx=ast.Load())
                self.added_count += 1
        if node.returns is None:
            node.returns = ast.Name(id=self.fallback_return, ctx=ast.Load())
            self.added_count += 1
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        """Execute visit_AsyncFunctionDef operation."""
        return self.visit_FunctionDef(node)

    def visit_Assign(self, node: ast.Assign) -> ast.Assign | ast.AnnAssign:
        """Execute visit_Assign operation."""
        if len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and (not target.id.startswith("_")):
                new_node = ast.AnnAssign(
                    target=target,
                    annotation=ast.Name(id=self.fallback_var, ctx=ast.Load()),
                    value=node.value,
                    simple=1,
                )
                self.added_count += 1
                return new_node
        return node

    @standard_heal
    # guardian: allow-type-erasure
    def heal_repository(self, **kwargs) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository(**kwargs)

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)
