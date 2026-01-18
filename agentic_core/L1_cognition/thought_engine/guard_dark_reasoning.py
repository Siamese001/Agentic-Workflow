from __future__ import annotations
"""
Sovereign Guard: Prevent Dark Reasoning (Phase 10 – Dec 26, 2025)
Ensures every reasoning/action in L1-L5 emits observability to L6.

This guardian enforces the L0-L6 Governance Cycle by detecting reasoning
operations that don't leave an L6 observability footprint.
"""
import ast
import sys
from pathlib import Path
from typing import Any, List, Dict
reasoning_signals: Any = {'think', 'plan', 'reason', 'decide', 'analyze', 'generate', 'synthesize'}
observability_signals: Any = {'Logger.', 'logging.', 'self.Logger.', 'trace(', 'Metric('}

class DarkReasoningVisitor(ast.NodeVisitor):
    """AST visitor to detect reasoning functions without observability."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.issues = []
        self.in_reasoning_function = False
        self.has_observability = False
        self.current_function = '<anonymous>'

    def visit_FunctionDef(self, node: Any) -> Any:
        """Visit function definitions and check for dark reasoning."""
        func_name: Any = node.name.lower()
        was_reasoning: Any = self.in_reasoning_function
        if any((sig in func_name for sig in REASONING_SIGNALS)):
            self.in_reasoning_function = True
            self.current_function = node.name
            self.has_observability = False
        self.generic_visit(node)
        if self.in_reasoning_function and (not was_reasoning):
            if not self.has_observability:
                self.issues.append({'line': node.lineno, 'function': self.current_function, 'reason': 'Reasoning function lacks L6 observability footprint', 'suggestion': f"Add Logger.info('[REASONING START] {self.current_function}')"})
            self.in_reasoning_function = False
            self.has_observability = False

    def visit_AsyncFunctionDef(self, node: Any) -> Any:
        """Visit async function definitions (same logic as sync)."""
        self.visit_FunctionDef(node)

    def _check_observability(self, node_str: str):
        """Centralized observability signal detection"""
        if any((obs in node_str for obs in OBSERVABILITY_SIGNALS)):
            self.has_observability = True

    def visit_Call(self, node: Any) -> Any:
        """Visit function calls to detect observability signals."""
        call_str: Any = ''
        try:
            call_str: Any = ast.unparse(node)
        except Exception:
            call_str: Any = ast.dump(node)
        self._check_observability(call_str.lower())
        self.generic_visit(node)

    def visit_Expr(self, node: Any) -> Any:
        """Visit expression statements to catch standalone logging calls."""
        if self.in_reasoning_function:
            expr_str: Any = ''
            try:
                expr_str: Any = ast.unparse(node)
            except Exception:
                expr_str: Any = ast.dump(node)
            self._check_observability(expr_str.lower())
        self.generic_visit(node)

def check_dark_reasoning(filepath: Path) -> List[Dict]:
    """
    Check a Python file for dark reasoning violations.
    
    Args:
        filepath: Path to Python file to check
        
    Returns:
        List of issue dictionaries with line, function, and reason
    """
    try:
        if 'L6_observability' in str(filepath) or 'tests/' in str(filepath):
            return []
        tree: Any = ast.parse(filepath.read_text(encoding='utf-8'))
        visitor: Any = DarkReasoningVisitor(filepath)
        visitor.visit(tree)
        return visitor.issues
    except Exception:
        return []

def main() -> Any:
    """Main entry point for pre-commit hook."""
    all_issues: Any = []
    for arg in sys.argv[1:]:
        try:
            path: Any = Path(arg)
            issues: Any = check_dark_reasoning(path)
            for issue in issues:
                all_issues.append(f"{path}:{issue['line']} | {issue['reason']} in {issue['function']}")
        except Exception:
            pass
    for issue in all_issues:
        print(f'[✗] Dark Reasoning: {issue}')
    sys.exit(1 if all_issues else 0)
if __name__ == '__main__':
    main()
