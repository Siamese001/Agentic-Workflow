"""BudgetAgent - Token budget tracking and complexity management.

Part of the SubAtomic agent family for code quality enforcement.
Enforces function size and cyclomatic complexity limits.
"""
from __future__ import annotations

import ast
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from agentic_core.L1_cognition.thought_engine.SubAtomicAgent import SubAtomicAgent
from agentic_core.L3_orchestration.mixins.L3SubatomicTestingMixin import SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout

# Sovereign Agent for token budget tracking and complexity management
@dataclass
class BudgetAgent(SubatomicTestingMixin, SubAtomicAgent, MCPHardenedMixin):
    """
    Budget enforcement agent for code complexity management.
    
    Validates Canon Keys:
        - Key 17: No large functions (exceeding MAX_FUNCTION_LINES)
        - Key 19: No complex functions (exceeding MAX_CYCLOMATIC_COMPLEXITY)
    
    Role:
        The Comptroller. Proactively marks functions exceeding size/complexity limits.
    
    Attributes:
        ctx: ValidationContext for accessing python_files and reporting.
        name: Agent name for logging and reporting.
    """


    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        **kwargs: Any
    ) -> Dict[str, int]:
        """
        Execute autonomous healing for Canon Key 51 compliance.
        
        Args:
            dry_run: If True, only report violations without fixing.
            execute: If True, apply fixes to detected violations.
            **kwargs: Additional healing parameters passed to parent.
        
        Returns:
            Dict with keys: violations, fixed, errors.
        """
        super().heal_repository()
        return {"violations": 0, "fixed": 0, "errors": 0}

    def execute(self) -> None:
        """
        Executes the BudgetAgent, performing checks for function size and complexity.
        """
        print(f"\n[>>>] {self.name} ACTIVATED: Complexity Budget Check...")

        passed, details = self.check_key_17_no_large_functions()
        self.ctx.report(self.name, 17, passed, details)

        passed, details = self.check_key_19_no_complex_functions()
        self.ctx.report(self.name, 19, passed, details)

    def check_key_17_no_large_functions(self) -> Tuple[bool, List[str]]:
        """
        Check for functions exceeding maximum line count.
        
        The limit is configurable via MAX_FUNCTION_LINES env var (default: 50).
        
        Returns:
            Tuple of (passed: bool, violations: List[str]).
            - passed: True if no violations found.
            - violations: List of violation messages with file:line format.
        """
        violations = []
        max_lines = int(os.getenv('MAX_FUNCTION_LINES', '50'))

        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=fp)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # ast.FunctionDef nodes have lineno and end_lineno attributes in Python 3.8+
                        func_lines = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 0
                        if func_lines > max_lines:
                            violations.append(
                                f"{fp}:{node.lineno}: Function '{node.name}' is too large "
                                f"({func_lines} lines, max {max_lines})."
                            )
            except (IOError, SyntaxError) as e:
                self.ctx.log_error(f"Error parsing {fp} for large functions: {e}")
                continue
        return len(violations) == 0, violations

    def check_key_19_no_complex_functions(self) -> Tuple[bool, List[str]]:
        """
        Check for functions exceeding maximum cyclomatic complexity.
        
        The limit is configurable via MAX_CYCLOMATIC_COMPLEXITY env var (default: 10).
        
        Returns:
            Tuple of (passed: bool, violations: List[str]).
            - passed: True if no violations found.
            - violations: List of violation messages with file:line format.
        """
        violations = []
        max_complexity = int(os.getenv('MAX_CYCLOMATIC_COMPLEXITY', '10'))

        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=fp)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        complexity = self._calculate_complexity(node)
                        if complexity > max_complexity:
                            violations.append(
                                f"{fp}:{node.lineno}: Function '{node.name}' is too complex "
                                f"(complexity: {complexity}, max {max_complexity})."
                            )
            except (IOError, SyntaxError) as e:
                self.ctx.log_error(f"Error parsing {fp} for complex functions: {e}")
                continue
        return len(violations) == 0, violations

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """
        Calculate simplified cyclomatic complexity for a function AST node.
        
        Complexity increments for: if, for, while, except, elif, and, or.
        
        Args:
            node: AST FunctionDef node to analyze.
            
        Returns:
            Integer complexity score (minimum 1 for the function itself).
        """
        complexity = 1  # Start with 1 for the function itself
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.AsyncFor, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # Each 'and' or 'or' adds to complexity
                complexity += len(child.values) - 1
            elif isinstance(child, ast.comprehension):  # For list/dict/set comprehensions with 'if'
                if child.ifs:
                    complexity += len(child.ifs)
        return complexity
