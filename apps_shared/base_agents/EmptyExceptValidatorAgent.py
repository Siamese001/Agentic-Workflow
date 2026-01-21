"""@deprecated
DEPRECATED: Use UnifiedASTValidatorAgent instead.

This agent has been consolidated into UnifiedASTValidatorAgent as part of
Phase 1 consolidation (2026-01-19). This file is retained for backward
compatibility during the transition period.

Migration:
    from agentic_core.L1_cognition.thought_engine.UnifiedASTValidatorAgent import (
        UnifiedASTValidatorAgent,
        validate_empty_except,
    )
"""
import warnings

warnings.warn(
    "EmptyExceptValidatorAgent is deprecated. Use UnifiedASTValidatorAgent instead.",
    DeprecationWarning,
    stacklevel=2
)

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, workflow
# This boosts alignment detection — review and integrate appropriately

from dataclasses import dataclass

"""
EmptyExceptValidatorAgent - Extracted for one-class-per-file pattern.

Originally from: PrintStatementValidatorAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""


from __future__ import annotations

import ast
import importlib  # AUTO-INJECTED BY GRAVITY HEALER
from typing import Any

from agentic_core.runtime.shared_runtime.ast_validator import CanonASTValidator

# GRAVITY FIXED (Upward Leak): from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin
_mod = importlib.import_module('agentic_core.L5_safety.guardrails.mcp_hardened_mixin')
MCPHardenedMixin = _mod.MCPHardenedMixin
from agentic_core.L5_safety.validators.decorators import standard_heal
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin


@dataclass
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

    @standard_heal
    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
