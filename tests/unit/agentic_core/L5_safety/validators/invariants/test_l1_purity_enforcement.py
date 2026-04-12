"""
L1 Purity Enforcement Test - No Forbidden Imports

Ensures L1 cognition modules remain pure with no mutation-capable imports.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import L1_COGNITION_DIR

pytestmark = pytest.mark.unit_min_deps

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
    l1_path = Path(__file__).resolve().parent.parent.parent / L1_COGNITION_DIR
    return list(l1_path.rglob("*.py"))


def parse_file_for_forbidden_imports(file_path: Path) -> list[str]:
    """Parse AST and identify forbidden imports."""
    violations = []

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
    except SyntaxError:
        return ["SYNTAX_ERROR"]  # guardian: Syntax errors should be caught at parser level, not runtime

    for node in ast.walk(tree):  # guardian: Syntax errors should be caught at parser level, not runtime
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
    print("  L1 root: agentic_core/L1_cognition")

    # Show first 20 and last 20 files for provability
    sorted_files = sorted([f.relative_to(Path.cwd()) for f in l1_files])

    print(f"  Audited files (first 20 of {total_files}):")
    for i, file_path in enumerate(sorted_files[:20]):
        violations = parse_file_for_forbidden_imports(file_path)
        status = "VIOLATION" if violations else "OK"
        print(f"    {i + 1:2d}. {file_path} [{status}]")

    if total_files > 40:
        print(f"    ... ({total_files - 40} files omitted) ...")
        print(f"  Audited files (last 20 of {total_files}):")
        for i, file_path in enumerate(sorted_files[-20:], total_files - 19):
            violations = parse_file_for_forbidden_imports(file_path)
            status = "VIOLATION" if violations else "OK"
            print(f"    {i:2d}. {file_path} [{status}]")
    elif total_files > 20:
        print(f"  Audited files (remaining {total_files - 20}):")
        for i, file_path in enumerate(sorted_files[20:], 21):
            violations = parse_file_for_forbidden_imports(file_path)
            status = "VIOLATION" if violations else "OK"
            print(f"    {i:2d}. {file_path} [{status}]")

    violation_count = 0
    violation_files = []
    for file_path in l1_files:
        violations = parse_file_for_forbidden_imports(file_path)
        if violations:
            violation_count += 1
            violation_files.append(str(file_path.relative_to(Path.cwd())))
            print(f"  VIOLATION: {file_path.relative_to(Path.cwd())}: {violations}")

    print(f"  Files with violations: {violation_count}")
    print(f"  Files compliant: {total_files - violation_count}")

    if violation_files:
        print(f"  Violation files: {violation_files}")

    assert violation_count == 0, f"{violation_count} L1 files have forbidden imports"
