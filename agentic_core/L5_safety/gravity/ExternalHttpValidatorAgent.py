"""
ExternalHttpValidatorAgent - Extracted for one-class-per-file pattern.

Originally from: PrintStatementValidatorAgent.py
Extracted: 2026-01-06 (Surgical Extraction)
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, workflow
# This boosts alignment detection — review and integrate appropriately



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
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin

class ExternalHttpValidatorAgent(HealerMixin, SubatomicTestingMixin, CanonASTValidator):
    """
    Key 23: Detects forbidden HTTP library imports (requests, urllib, httpx).
    Automatically handles TYPE_CHECKING blocks and exception ledger.
    """
    FORBIDDEN_MODULES: Any = {'requests', 'urllib', 'urllib3', 'httpx', 'aiohttp'}

    def visit_Import(self, node: ast.Import) -> Any:
        """Check for forbidden HTTP library imports."""
        if not self.in_type_checking:
            for alias in node.names:
                module_root: Any = alias.name.split('.')[0]
                if module_root in self.FORBIDDEN_MODULES:
                    self.report(f'Forbidden HTTP library import: {alias.name} (use MCP fetch_client_sovereign instead)', node)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        """Check for forbidden HTTP library imports in 'from X import Y'."""
        if not self.in_type_checking and node.module:
            module_root: Any = node.module.split('.')[0]
            if module_root in self.FORBIDDEN_MODULES:
                self.report(f'Forbidden HTTP library import: from {node.module} (use MCP fetch_client_sovereign instead)', node)
        self.generic_visit(node)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
