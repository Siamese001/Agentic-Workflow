"""
BareExceptValidatorAgent - Extracted for one-class-per-file pattern.

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

class BareExceptValidatorAgent(HealerMixin, SubatomicTestingMixin, CanonASTValidator):
    """
    Key 5: Detects bare except: statements (catching all exceptions).
    """

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> Any:
        """Check for bare except statements."""
        if node.type is None and (not self.in_type_checking):
            self.report('Bare except: statement detected (should specify exception type)', node)
        self.generic_visit(node)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
