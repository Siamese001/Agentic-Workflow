"""
DocumentationAgent - Extracted from canon_agents_quality.py
Part of the quality enforcement agent family.
"""
from __future__ import annotations
import importlib  # AUTO-INJECTED BY GRAVITY HEALER
import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin
# GRAVITY FIXED (Upward Leak): from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
_mod = importlib.import_module('agentic_core.L5_safety.guardrails.mcp_hardened_mixin')
MCPHardenedMixin = getattr(_mod, 'MCPHardenedMixin')
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L1_cognition.thought_engine.SubAtomicAgent import SubAtomicAgent
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin

# NOT_AN_AGENT — legacy L1 class, true agent is DocEnforcerAgent in L2 — excluded from discovery
class DocumentationAgent(MCPHardenedMixin, SubatomicTestingMixin, SubAtomicAgent):
    """
    KEYS: 21 (Missing Docstrings)
    ROLE: Pure focus on Docstrings.
    """

    def execute(self) -> None:
        """
        Executes the documentation check, specifically for Missing docstrings.
        """
        print(f'\n[>>>] {self.agent.name} ACTIVATED: Documentation Check...')
        passed, details = self.check_key_21_no_missing_docstrings()
        self.agent.ctx.report(self.agent.name, 21, passed, details)

    def _has_missing_docstring(self, node: ast.AST) -> bool:
        """Helper to determine if a node (FunctionDef or ClassDef) has a Missing docstring."""
        return not ast.get_docstring(node)

    def _find_missing_docstring_violations_in_tree(self, tree: ast.AST, fp: str) -> List[str]:
        """Helper to find Missing docstrings in an AST tree."""
        file_violations = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and self._has_missing_docstring(node):
                file_violations.append(f'{fp}:{node.lineno} {node.name}')
        return file_violations

    def check_key_21_no_missing_docstrings(self) -> Tuple[bool, List[str]]:
        """
        Checks for Missing docstrings in classes and functions using AST parsing.
        """
        violations: Any = []
        for fp in self.agent.ctx.python_files:
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    tree: Any = ast.parse(f.read())
                violations.extend(self._find_missing_docstring_violations_in_tree(tree, fp))
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()