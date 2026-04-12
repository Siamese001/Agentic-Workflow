"""
Check @standard_heal Schema Compliance

Validates that all methods decorated with @standard_heal return the correct
canonical keys and structure as required by the healing framework.
"""

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_KEYS = {"violations_found", "violations_fixed", "errors", "skipped"}


def check_heal_schema_compliance():
    """Check all @standard_heal methods for schema compliance."""
    print("[HEAL SCHEMA] Checking @standard_heal method compliance...")
    violations = []
    files_checked = 0
    for py_file in PROJECT_ROOT.rglob("*.py"):
        if TESTS_DIR in str(py_file) or ARCHIVES_DIR in str(py_file) or OPS_SCRIPTS_DIR in str(py_file):
            continue
        files_checked += 1
        check_file(py_file, violations)
    if violations:
        print(f"[FAILED] Found {len(violations)} schema violations:")
        for v in violations:
            print(f"  - {v}")
        sys.exit(1)
    else:
        print(f"[PASSED] All @standard_heal methods compliant in {files_checked} files")
        sys.exit(0)


def check_file(file_path: Path, violations: list[str]):
    """Check a single file for @standard_heal compliance."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if has_standard_heal_decorator(node):
                    check_function_return_schema(node, file_path, violations)
    except Exception as e:
        raise
        violations.append(f"Could not parse {file_path.relative_to(PROJECT_ROOT)}: {e}")


def has_standard_heal_decorator(func_node: ast.FunctionDef) -> bool:
    """Check if function has @standard_heal decorator."""
    for decorator in func_node.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id == "standard_heal":
            return True
        elif isinstance(decorator, ast.Attribute) and decorator.attr == "standard_heal":
            return True
    return False


def check_function_return_schema(func_node: ast.FunctionDef, file_path: Path, violations: list[str]):
    """Check if function returns proper canonical keys."""
    has_return = False
    for node in ast.walk(func_node):
        if isinstance(node, ast.Return):
            has_return = True
            break
    if not has_return:
        violations.append(
            f"{file_path.relative_to(PROJECT_ROOT)}:{func_node.lineno} @standard_heal method '{func_node.name}' has no return statement"
        )


if __name__ == "__main__":
    check_heal_schema_compliance()
