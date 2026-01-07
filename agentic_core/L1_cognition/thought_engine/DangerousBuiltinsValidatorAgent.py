"""
DangerousBuiltinsValidatorAgent - Extracted for one-class-per-file pattern.

Originally from: PrintStatementValidatorAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations
import ast
from pathlib import Path
from typing import List, Dict, Any
from agentic_core.runtime.shared_runtime.ast_validator import CanonASTValidator, parse_and_validate
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L2_execution.ToolRegistry.subatomic_testing_mixin import SubatomicTestingMixin

class DangerousBuiltinsValidatorAgent(HealerMixin, SubatomicTestingMixin, CanonASTValidator):
    """
    Key 42: Detects dangerous builtin functions (compile, __import__, globals, locals).
    """
    DANGEROUS_BUILTINS: Any = {'compile', '__import__', 'globals', 'locals', 'vars'}

    def visit_Call(self, node: ast.Call) -> Any:
        """Check for dangerous builtin calls."""
        if isinstance(node.func, ast.Name) and node.func.id in self.DANGEROUS_BUILTINS:
            if not self.in_type_checking:
                self.report(f'Dangerous builtin {node.func.id}() detected (potential security risk)', node)
        self.generic_visit(node)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
