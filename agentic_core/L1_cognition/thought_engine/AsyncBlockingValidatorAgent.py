"""
AsyncBlockingValidatorAgent - Extracted for one-class-per-file pattern.

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
from agentic_core.utils.mixins import SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

class AsyncBlockingValidatorAgent(HealerMixin, SubatomicTestingMixin, CanonASTValidator, MCPHardenedMixin):
    """
    Key 31: Detects blocking calls in async functions (time.sleep, requests, etc).
    """

    def __init__(self, file_path: Path, content: str, key_id: int) -> None:
        super().__init__(file_path, content, key_id)
        self.in_async_function = False

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        """Track when we're inside an async function."""
        old_async: Any = self.in_async_function
        self.in_async_function = True
        self.generic_visit(node)
        self.in_async_function = old_async

    def visit_Call(self, node: ast.Call) -> Any:
        """Check for blocking calls inside async functions."""
        if self.in_async_function and (not self.in_type_checking):
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == 'time' and (node.func.attr == 'sleep'):
                    self.report('Blocking time.sleep() in async function (use asyncio.sleep())', node)
                elif isinstance(node.func.value, ast.Name) and node.func.value.id == 'requests':
                    self.report(f'Blocking requests.{node.func.attr}() in async function (use httpx.AsyncClient or asyncio.to_thread())', node)
        self.generic_visit(node)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()