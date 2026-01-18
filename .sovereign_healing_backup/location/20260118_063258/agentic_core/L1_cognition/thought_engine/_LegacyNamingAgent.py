"""
_LegacyNamingAgent - Extracted from canon_agents_quality.py
Part of the quality enforcement agent family.
"""
from __future__ import annotations
import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L3_orchestration.fission_logic.SubAtomicAgent import SubAtomicAgent

# NOT_AN_AGENT — legacy L1 class removed 2026-01-06, use utils canonical
# from agentic_core.utils.core_extensions.NamingAgent import NamingAgent
class _LegacyNamingAgent(SubAtomicAgent):
    """
    KEYS: 47 (Naming Conventions)
    ROLE: Enforces Snake_Case/PascalCase.
    """

    def execute(self) -> None:
        """
        Executes the naming convention check.
        """
        print(f'\n[>>>] {self.agent.name} ACTIVATED: Naming Convention Check...')
        passed, details = self.check_key_47_naming_conventions()
        self.agent.ctx.report(self.agent.name, 47, passed, details)

    def _is_invalid_function_name(self, name: str) -> bool:
        """Helper to check if a function name violates PEP 8 snake_case."""
        return not re.match('^[a-z_][a-z0-9_]*$', name)

    def _is_invalid_class_name(self, name: str) -> bool:
        """Helper to check if a class name violates PEP 8 PascalCase."""
        return not re.match('^[A-Z][a-zA-Z0-9]*$', name)

    def _find_naming_convention_violations_in_tree(self, tree: ast.AST, fp: str) -> List[str]:
        """Helper to find naming convention violations in an AST tree."""
        file_violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and self._is_invalid_function_name(node.name):
                file_violations.append(f'{fp}:{node.lineno} function {node.name}')
            elif isinstance(node, ast.ClassDef) and self._is_invalid_class_name(node.name):
                file_violations.append(f'{fp}:{node.lineno} class {node.name}')
        return file_violations

    def check_key_47_naming_conventions(self) -> Tuple[bool, List[str]]:
        """
        Checks for PEP 8 naming conventions for functions (snake_case)
        and classes (PascalCase) using AST parsing.
        """
        violations: Any = []
        for fp in self.agent.ctx.python_files:
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    tree: Any = ast.parse(f.read())
                violations.extend(self._find_naming_convention_violations_in_tree(tree, fp))
            except Exception:
                continue
        return (len(violations) == 0, violations)
    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
