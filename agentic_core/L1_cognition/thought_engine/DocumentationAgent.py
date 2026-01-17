"""DocumentationAgent - Documentation quality enforcement.

Part of the quality enforcement agent family.
Validates docstring presence in classes and functions.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import List, Tuple

from agentic_core.L1_cognition.thought_engine.SubAtomicAgent import SubAtomicAgent
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.mixins import SubatomicTestingMixin

@dataclass
class DocumentationAgent(MCPHardenedMixin, SubatomicTestingMixin, SubAtomicAgent):
    """
    Documentation enforcement agent for docstring validation.
    
    Validates Canon Keys:
        - Key 21: No missing docstrings in classes and functions.
    
    Role:
        Pure focus on docstring presence and quality.
    
    Note:
        Legacy L1 class - true agent is DocEnforcerAgent in L2.
    
    Attributes:
        agent: Injected CanonBaseAgentInterface implementation.
    """

    def execute(self) -> None:
        """
        Execute documentation validation checks.
        
        Runs Key 21 (missing docstrings) check and reports results
        to the validation context.
        """
        print(f'\n[>>>] {self.agent.name} ACTIVATED: Documentation Check...')
        passed, details = self.check_key_21_no_missing_docstrings()
        self.agent.ctx.report(self.agent.name, 21, passed, details)

    def _has_missing_docstring(self, node: ast.AST) -> bool:
        """
        Check if an AST node is missing a docstring.
        
        Args:
            node: AST node (FunctionDef or ClassDef) to check.
            
        Returns:
            True if docstring is missing, False otherwise.
        """
        return not ast.get_docstring(node)

    def _find_missing_docstring_violations_in_tree(self, tree: ast.AST, fp: str) -> List[str]:
        """
        Find all missing docstring violations in an AST tree.
        
        Args:
            tree: Parsed AST tree to analyze.
            fp: File path for violation reporting.
            
        Returns:
            List of violation strings in 'filepath:line name' format.
        """
        file_violations: List[str] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and self._has_missing_docstring(node):
                file_violations.append(f'{fp}:{node.lineno} {node.name}')
        return file_violations

    def check_key_21_no_missing_docstrings(self) -> Tuple[bool, List[str]]:
        """
        Check for missing docstrings in classes and functions.
        
        Uses AST parsing to identify FunctionDef and ClassDef nodes
        without docstrings.
        
        Returns:
            Tuple of (passed: bool, violations: List[str]).
            - passed: True if no violations found.
            - violations: List of 'filepath:line name' strings.
        """
        violations: List[str] = []
        for fp in self.agent.ctx.python_files:
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                violations.extend(self._find_missing_docstring_violations_in_tree(tree, fp))
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def heal_repository(self) -> dict:
        """
        Execute healing chain via parent class.
        
        Returns:
            Dict with healing results from parent implementation.
        """
        return super().heal_repository()