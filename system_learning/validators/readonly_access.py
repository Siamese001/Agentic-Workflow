"""
system_learning/validators/readonly_access.py

Validates that system_learning only performs read-only access to
agentic_core data structures.

Write operations (mutations to agentic_core state) are forbidden.
This validator checks for AST-level patterns that indicate writes.
"""
import ast
from pathlib import Path
from typing import List

_SL_ROOT = Path(__file__).parent.parent

_WRITE_INDICATORS = frozenset(
    {
        "write",
        "save",
        "persist",
        "commit",
        "update",
        "mutate",
        "set_",
        "put",
        "insert",
        "delete",
        "remove",
    }
)


class _ReadOnlyVisitor(ast.NodeVisitor):
    """Detects assignment to agentic_core attributes (write patterns)."""

    def __init__(self) -> None:
        self.violations: List[str] = []

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Attribute):
                val = ast.unparse(target.value) if hasattr(ast, "unparse") else ""
                if "agentic_core" in val:
                    self.violations.append(
                        f"Line {node.lineno}: Write to agentic_core attribute '{ast.unparse(target)}'"
                        if hasattr(ast, "unparse")
                        else f"Line {node.lineno}: Write to agentic_core attribute"
                    )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute):
            val = ast.unparse(node.func.value) if hasattr(ast, "unparse") else ""
            method = node.func.attr.lower()
            if "agentic_core" in val and any(
                method.startswith(w) for w in _WRITE_INDICATORS
            ):
                self.violations.append(
                    f"Line {node.lineno}: Potential write call '{node.func.attr}' on agentic_core object"
                )
        self.generic_visit(node)


def check_file_readonly(file_path: Path) -> List[str]:
    """Return list of write-pattern violations for a single file."""
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        return [f"SyntaxError: {exc}"]
    visitor = _ReadOnlyVisitor()
    visitor.visit(tree)
    return visitor.violations


def check_system_learning_readonly() -> bool:
    """Check all system_learning files for read-only access compliance."""
    all_violations: List[str] = []
    for py_file in _SL_ROOT.rglob("*.py"):
        file_violations = check_file_readonly(py_file)
        if file_violations:
            for v in file_violations:
                all_violations.append(f"{py_file.relative_to(_SL_ROOT)}: {v}")

    if all_violations:
        print("system_learning read-only access violations found:")
        for v in all_violations:
            print(f"  {v}")
        return False

    print("OK: system_learning maintains read-only access to agentic_core")
    return True


if __name__ == "__main__":
    import sys

    sys.exit(0 if check_system_learning_readonly() else 1)
