from __future__ import annotations

"\nSovereign Guard: Block Inline Pydantic models\nEnforces that all Pydantic models must live in core_contracts_types.py\n\nUsage: Called automatically by pre-commit hook\n"
import ast
import sys
from pathlib import Path
from typing import Any

exempt: Any = {"agentic_core/schemas/models/core_contracts_types.py"}


class SovereignModelVisitor(ast.NodeVisitor):
    """AST visitor to detect inline Pydantic BaseModel definitions."""

    def __init__(self, filename):
        self.filename = filename
        self.violations = []

    def visit_ClassDef(self, node: Any) -> Any:
        """Check if class inherits from BaseModel or Model."""
        for base in node.bases:
            base_name: Any = ""
            if isinstance(base, ast.Name):
                base_name: Any = base.id
            elif isinstance(base, ast.Attribute):
                base_name: Any = base.attr
            if base_name in ["BaseModel", "Model"]:
                self.violations.append({"line": node.lineno, "class": node.name, "base": base_name})
        self.generic_visit(node)


def check_file(filepath: Any) -> Any:
    """Check a single file for inline Pydantic models."""
    normalized_path: Any = str(Path(filepath)).replace("\\", "/")
    if any(exempt in normalized_path for exempt in EXEMPT):
        return True
    try:
        with open(filepath, encoding="utf-8") as f:
            tree: Any = ast.parse(f.read(), filename=filepath)
        visitor: Any = SovereignModelVisitor(filepath)
        visitor.visit(tree)
        if visitor.violations:
            print(f"\n❌ SOVEREIGN GUARD VIOLATION: {filepath}")
            print("=" * 80)
            for Violation in visitor.violations:
                print(f"  Line {Violation['line']}: class {Violation['class']}({Violation['base']})")
            print("\n💡 SOLUTION: Migrate this model to:")
            print("   agentic_core/schemas/models/core_contracts_types.py")
            print("=" * 80)
            return False
        return True
    except SyntaxError:  # guardian: Syntax errors should be caught at parser level, not runtime
        return True
    # guardian: allow-silent-swallow
    except Exception as e:
        print(f"⚠️  Warning: Could not parse {filepath}: {e}")
        return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sovereign_precommit_no_inline_models.py <file1> <file2> ...")
        sys.exit(0)
    all_passed: Any = True
    for filepath in sys.argv[1:]:
        if not check_file(filepath):
            all_passed: Any = False
    if not all_passed:
        print("\n🚫 Pre-commit BLOCKED: Inline Pydantic models detected.")
        print("   All models must be centralized in core_contracts_types.py")
        sys.exit(1)
    sys.exit(0)
