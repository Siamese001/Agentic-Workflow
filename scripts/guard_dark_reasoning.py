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

REASONING_SIGNALS = {"think", "plan", "reason", "decide", "analyze", "execute", "generate"}
OBSERVABILITY_SIGNALS = {"logger.", "logging.", "self.logger.", "trace(", "metric(", "print("}

class DarkReasoningVisitor(ast.NodeVisitor):
    """AST visitor to detect reasoning functions without observability."""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.issues = []
        self.in_reasoning_function = False

    def visit_FunctionDef(self, node):
        """Visit function definitions and check for dark reasoning."""
        func_name = node.name.lower()
        old_state = self.in_reasoning_function
        
        # Check if function name contains reasoning signals
        if any(sig in func_name for sig in REASONING_SIGNALS):
            self.in_reasoning_function = True
        
        # Check if function body contains at least one observability signal
        if self.in_reasoning_function:
            body_str = ast.dump(node).lower()
            has_observability = any(sig in body_str for sig in OBSERVABILITY_SIGNALS)
            
            if not has_observability:
                self.issues.append({
                    "line": node.lineno,
                    "function": node.name,
                    "reason": "Reasoning function lacks L6 observability footprint"
                })
            
        self.generic_visit(node)
        self.in_reasoning_function = old_state

    def visit_AsyncFunctionDef(self, node):
        """Visit async function definitions (same logic as sync)."""
        self.visit_FunctionDef(node)


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
