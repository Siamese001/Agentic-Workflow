"""
L1 Purity Enforcement Test - No Forbidden Imports

Ensures L1 cognition modules remain pure with no mutation-capable imports.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

FORBIDDEN_IMPORTS = {
    "subprocess",
    "redis",
    "pinecone",
    "requests",
    "http",
    "socket",
    "sqlite",
    "psycopg",
    "boto",
}

FORBIDDEN_OPEN_MODES = {"w", "a", "x"}


def get_l1_files() -> list[Path]:
    """Get all Python files in L1 cognition directory."""
    l1_path = Path(__file__).resolve().parent.parent.parent.parent / "agentic_core" / "L1_cognition"
    return list(l1_path.rglob("*.py"))


def parse_file_for_forbidden_imports(file_path: Path) -> list[str]:
    """Parse AST and identify forbidden imports."""
    violations = []

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
    except SyntaxError:
        return ["SYNTAX_ERROR"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in FORBIDDEN_IMPORTS:
                    violations.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module and any(forbidden in node.module for forbidden in FORBIDDEN_IMPORTS):
                violations.append(f"from {node.module} import ...")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "open":
                if len(node.args) >= 2:
                    mode_arg = node.args[1]
                    if isinstance(mode_arg, ast.Constant) and mode_arg.value in FORBIDDEN_OPEN_MODES:
                        violations.append(f"open(..., '{mode_arg.value}')")

    return violations


@pytest.mark.parametrize("file_path", get_l1_files())
def test_l1_no_mutation_imports(file_path: Path) -> None:
    """Test that L1 files contain no forbidden imports."""
    violations = parse_file_for_forbidden_imports(file_path)

    assert not violations, f"L1 purity violation in {file_path}: {violations}"


def test_l1_import_audit_summary() -> None:
    """Summary test to report all L1 files audited."""
    l1_files = get_l1_files()
    total_files = len(l1_files)

    print("\nL1 Import Audit Summary:")
    print(f"  Total L1 files: {total_files}")

    violation_count = 0
    for file_path in l1_files:
        violations = parse_file_for_forbidden_imports(file_path)
        if violations:
            violation_count += 1
            print(f"  VIOLATION: {file_path.relative_to(Path.cwd())}: {violations}")

    print(f"  Files with violations: {violation_count}")
    print(f"  Files compliant: {total_files - violation_count}")

    assert violation_count == 0, f"{violation_count} L1 files have forbidden imports"
