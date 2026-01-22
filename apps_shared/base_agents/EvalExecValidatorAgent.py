"""@deprecated
DEPRECATED: Use UnifiedASTValidatorAgent instead.

This agent has been consolidated into UnifiedASTValidatorAgent as part of
Phase 1 consolidation (2026-01-19). This file is retained for backward
compatibility during the transition period.

Migration:
    from agentic_core.L1_cognition.thought_engine.UnifiedASTValidatorAgent import (
        UnifiedASTValidatorAgent,
        validate_eval_exec,
    )
"""

import warnings

warnings.warn(
    "EvalExecValidatorAgent is deprecated. Use UnifiedASTValidatorAgent instead.",
    DeprecationWarning,
    stacklevel=2,
)

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, workflow
# This boosts alignment detection — review and integrate appropriately


"""
EvalExecValidatorAgent - Extracted for one-class-per-file pattern.

Originally from: PrintStatementValidatorAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


import ast
import importlib  # AUTO-INJECTED BY GRAVITY HEALER


# GRAVITY FIXED (Upward Leak): from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin
_mod = importlib.import_module("agentic_core.L5_safety.guardrails.mcp_hardened_mixin")
MCPHardenedMixin = _mod.MCPHardenedMixin


@dataclass
class EvalExecValidatorAgent(HealerMixin, SubatomicTestingMixin, CanonASTValidator):
    """
    Key 6: Detects eval() and exec() calls using AST.
    """

    def visit_Call(self, node: ast.Call) -> Any:
        """Check for eval() or exec() function calls."""
        if isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec"):
            if not self.in_type_checking:
                self.report(f"Forbidden {node.func.id}() call detected", node)
        self.generic_visit(node)

    @standard_heal
    def heal_repository(self) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository()
