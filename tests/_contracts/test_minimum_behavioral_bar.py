#!/usr/bin/env python3
"""
Minimum Behavioral Bar Contract for Generated Tests
artifact_class: BEHAVIORAL_CONTRACT
"""

import ast
import pathlib

import pytest


def test_minimum_behavioral_bar():
    """Test that newly created tests meet minimum behavioral requirements."""
    test_root = pathlib.Path("tests")

    violations = []
    generated_tests_found = []

    # ONLY check tests with the marker comment
    for test_file in test_root.rglob("test_*.py"):
        # Skip contract tests themselves
        if test_file.name == "test_minimum_behavioral_bar.py":
            continue

        # Skip other contract tests
        if "_contracts/" in str(test_file):
            continue

        # Skip guardian tests
        if "guardian/" in str(test_file):
            continue

        try:
            content = test_file.read_text(encoding="utf-8")

            # Skip if no marker comment
            if "# GENERATED_MIRROR_TEST" not in content:
                continue

            generated_tests_found.append(test_file)

            # Parse AST to check structure
            try:
                tree = ast.parse(content)
            except SyntaxError:
                violations.append(f"{test_file}: Syntax error in test file")
                continue

            # Check for minimum requirements
            has_module_import = False
            assertion_count = 0
            test_functions = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Check if importing from the module under test
                        if any(part in alias.name for part in ["agentic_core", "apps_"]):
                            has_module_import = True
                elif isinstance(node, ast.ImportFrom):
                    if node.module and any(part in node.module for part in ["agentic_core", "apps_"]):
                        has_module_import = True
                elif isinstance(node, ast.Call):
                    # Check for importlib.import_module usage
                    if (
                        isinstance(node.func, ast.Attribute)
                        and isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "importlib"
                        and node.func.attr == "import_module"
                    ):
                        # Check if the argument is a module path
                        if node.args and isinstance(node.args[0], ast.Constant):
                            module_name = node.args[0].value
                            # Verify it matches the expected module from file path
                            if any(part in module_name for part in ["agentic_core", "apps_"]):
                                has_module_import = True
                elif isinstance(node, ast.Assert):
                    assertion_count += 1
                elif isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    test_functions += 1

            # Check requirements
            if not has_module_import:
                violations.append(f"{test_file}: No module import from target")

            if assertion_count < 2:
                violations.append(f"{test_file}: Insufficient assertions ({assertion_count} < 2)")

            if test_functions < 1:
                violations.append(f"{test_file}: No test functions found")

        except Exception as e:
            violations.append(f"{test_file}: Error analyzing file - {e}")

    # Assert we found enough generated tests
    assert len(generated_tests_found) >= 500, (
        f"Expected at least 500 generated tests, found {len(generated_tests_found)}"
    )

    if violations:
        # Show only first 10 violations for readability
        shown_violations = violations[:10]
        violation_summary = "\n".join(shown_violations)
        if len(violations) > 10:
            violation_summary += f"\n... and {len(violations) - 10} more violations"

        pytest.fail(f"Minimum behavioral bar violations found:\n{violation_summary}")

    # If we get here, all checked tests pass the bar
    assert True, f"All {len(generated_tests_found)} generated mirror tests meet minimum behavioral bar"


if __name__ == "__main__":
    test_minimum_behavioral_bar()
    print(" Minimum behavioral bar satisfied!")
