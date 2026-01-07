"""
EmptyExceptValidatorAgent - Extracted for one-class-per-file pattern.

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

class EmptyExceptValidatorAgent(HealerMixin, SubatomicTestingMixin, CanonASTValidator):
    """
    Key 4: Detects empty except blocks (except: pass).
    """

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> Any:
        """Check for empty except blocks."""
        is_empty: Any = not node.body or (len(node.body) == 1 and isinstance(node.body[0], ast.Pass))
        if is_empty and (not self.in_type_checking):
            self.report('Empty except block detected (except: pass)', node)
        self.generic_visit(node)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
