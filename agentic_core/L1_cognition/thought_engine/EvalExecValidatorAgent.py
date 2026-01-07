"""
EvalExecValidatorAgent - Extracted for one-class-per-file pattern.

Originally from: PrintStatementValidatorAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations
import importlib  # AUTO-INJECTED BY GRAVITY HEALER
import ast
from pathlib import Path
from typing import List, Dict, Any
from agentic_core.runtime.shared_runtime.ast_validator import CanonASTValidator, parse_and_validate
# GRAVITY FIXED (Upward Leak): from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
_mod = importlib.import_module('agentic_core.L5_safety.guardrails.mcp_hardened_mixin')
MCPHardenedMixin = getattr(_mod, 'MCPHardenedMixin')
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin

class EvalExecValidatorAgent(HealerMixin, SubatomicTestingMixin, CanonASTValidator):
    """
    Key 6: Detects eval() and exec() calls using AST.
    """

    def visit_Call(self, node: ast.Call) -> Any:
        """Check for eval() or exec() function calls."""
        if isinstance(node.func, ast.Name) and node.func.id in ('eval', 'exec'):
            if not self.in_type_checking:
                self.report(f'Forbidden {node.func.id}() call detected', node)
        self.generic_visit(node)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()