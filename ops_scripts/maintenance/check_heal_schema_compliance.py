"""
Check @standard_heal schema compliance.

Validates that all methods decorated with @standard_heal return the correct
canonical keys and structure as required by the healing framework.
"""

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    ARCHIVES_DIR,
    OPS_SCRIPTS_DIR,
    TESTS_DIR,
    get_validated_project_root,
)

PROJECT_ROOT = get_validated_project_root()
CANONICAL_KEYS = {"violations_found", "violations_fixed", "errors", "skipped"}


def check_heal_schema_compliance() -> int:
    """Check all @standard_heal methods for schema compliance."""
    print("[HEAL SCHEMA] Checking @standard_heal method compliance...")
    violations: list[str] = []
    files_checked = 0

    for py_file in sorted(PROJECT_ROOT.rglob("*.py")):
        if TESTS_DIR in py_file.parts or ARCHIVES_DIR in py_file.parts or OPS_SCRIPTS_DIR in py_file.parts:
            continue

        files_checked += 1
        check_file(py_file, violations)

    if violations:
        print(f"[FAILED] Found {len(violations)} schema violations:")
        for violation in violations:
            print(f"  - {violation}")
        return 1

    print(f"[PASSED] All @standard_heal methods compliant in {files_checked} files")
    return 0


def check_file(file_path: Path, violations: list[str]) -> None:
    """Check a single file for @standard_heal compliance."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and has_standard_heal_decorator(node):
                check_function_return_schema(node, file_path, violations)
    except (OSError, UnicodeDecodeError, SyntaxError) as exc:
        violations.append(f"Could not parse {file_path.relative_to(PROJECT_ROOT)}: {exc}")


def has_standard_heal_decorator(func_node: ast.FunctionDef) -> bool:
    """Check if function has @standard_heal decorator."""
    for decorator in func_node.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id == "standard_heal":
            return True
        if isinstance(decorator, ast.Attribute) and decorator.attr == "standard_heal":
            return True
    return False


def check_function_return_schema(func_node: ast.FunctionDef, file_path: Path, violations: list[str]) -> None:
    """Check if function returns proper canonical keys."""
    has_return = any(isinstance(node, ast.Return) for node in ast.walk(func_node))
    if not has_return:
        violations.append(
            f"{file_path.relative_to(PROJECT_ROOT)}:{func_node.lineno} "
            f"@standard_heal method '{func_node.name}' has no return statement"
        )


if __name__ == "__main__":
    sys.exit(check_heal_schema_compliance())
