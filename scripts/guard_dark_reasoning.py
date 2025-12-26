"""
Sovereign Guard: Prevent Dark Reasoning (Phase 10 – Dec 26, 2025)
Ensures every reasoning/action in L1-L5 emits observability to L6.

This guardian enforces the L0-L6 Governance Cycle by detecting reasoning
operations that don't leave an L6 observability footprint.
"""
import ast
import sys
from pathlib import Path
from typing import List, Dict

# Refined signals: only trigger on high-level cognitive intentions
REASONING_SIGNALS = {"think", "plan", "reason", "decide", "analyze", "generate", "synthesize"}
OBSERVABILITY_SIGNALS = {"logger.", "logging.", "self.logger.", "trace(", "metric("}

class DarkReasoningVisitor(ast.NodeVisitor):
    """AST visitor to detect reasoning functions without observability."""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.issues = []
        self.in_reasoning_function = False
        self.has_observability = False
        self.current_function = "<anonymous>"

    def visit_FunctionDef(self, node):
        """Visit function definitions and check for dark reasoning."""
        func_name = node.name.lower()
        was_reasoning = self.in_reasoning_function
        
        # Check if function name contains reasoning signals
        if any(sig in func_name for sig in REASONING_SIGNALS):
            self.in_reasoning_function = True
            self.current_function = node.name
            self.has_observability = False
        
        # Visit children to detect observability calls
        self.generic_visit(node)
        
        # Check for darkness upon exiting the function scope
        if self.in_reasoning_function and not was_reasoning:
            if not self.has_observability:
                self.issues.append({
                    "line": node.lineno,
                    "function": self.current_function,
                    "reason": "Reasoning function lacks L6 observability footprint",
                    "suggestion": f"Add logger.info('[REASONING START] {self.current_function}')"
                })
            self.in_reasoning_function = False
            self.has_observability = False

    def visit_AsyncFunctionDef(self, node):
        """Visit async function definitions (same logic as sync)."""
        self.visit_FunctionDef(node)
    
    def _check_observability(self, node_str: str):
        """Centralized observability signal detection"""
        if any(obs in node_str for obs in OBSERVABILITY_SIGNALS):
            self.has_observability = True
    
    def visit_Call(self, node):
        """Visit function calls to detect observability signals."""
        call_str = ""
        try:
            # Use unparse for high-fidelity string representation
            call_str = ast.unparse(node)
        except Exception:
            # Fallback to dump for safety
            call_str = ast.dump(node)
        self._check_observability(call_str.lower())
        self.generic_visit(node)
    
    def visit_Expr(self, node):
        """Visit expression statements to catch standalone logging calls."""
        if self.in_reasoning_function:
            expr_str = ""
            try:
                expr_str = ast.unparse(node)
            except Exception:
                expr_str = ast.dump(node)
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
        # Skip L6 observability layer and tests
        if "L6_observability" in str(filepath) or "tests/" in str(filepath):
            return []
        
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
        visitor = DarkReasoningVisitor(filepath)
        visitor.visit(tree)
        return visitor.issues
    except Exception:
        # Silently skip files that can't be parsed
        return []


def main():
    """Main entry point for pre-commit hook."""
    all_issues = []
    
    for arg in sys.argv[1:]:
        try:
            path = Path(arg)
            issues = check_dark_reasoning(path)
            
            for issue in issues:
                all_issues.append(f"{path}:{issue['line']} | {issue['reason']} in {issue['function']}")
        except Exception:
            pass
    
    # Print all issues
    for issue in all_issues:
        print(f"[✗] Dark Reasoning: {issue}")
    
    # Exit with error code if issues found
    sys.exit(1 if all_issues else 0)


if __name__ == "__main__":
    main()
