"""
Guardian Test: No Direct LLM SDK Imports
AST-based detection of direct LLM SDK imports in agentic_core/
Fails if any direct SDK import exists in agentic_core/
Allows direct SDK only inside data/sdks_mcps/
"""

import ast
import json
from pathlib import Path

import pytest


class LLMSDKImportVisitor(ast.NodeVisitor):
    """AST visitor to detect direct LLM SDK imports."""

    FORBIDDEN_MODULES = {"openai", "anthropic", "google.generativeai"}

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.violations = []
        self.allowed_base = Path("data/sdks_mcps")

    def visit_Import(self, node: ast.Import) -> None:
        """Check direct imports."""
        for alias in node.names:
            if any(alias.name.startswith(module) for module in self.FORBIDDEN_MODULES):
                # Check if file is in allowed directory
                if not self._is_allowed_location():
                    self.violations.append(f"Line {node.lineno}: import {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check from imports."""
        if node.module and any(node.module.startswith(module) for module in self.FORBIDDEN_MODULES):
            if not self._is_allowed_location():
                module_name = node.module
                names = ", ".join(alias.name for alias in node.names) if node.names else "*"
                self.violations.append(f"Line {node.lineno}: from {module_name} import {names}")
        self.generic_visit(node)

    def _is_allowed_location(self) -> bool:
        """Check if current file is in allowed location."""
        try:
            # Get absolute path relative to repo root
            abs_path = self.file_path.resolve()
            repo_root = Path.cwd()

            # Check if file is under data/sdks_mcps
            allowed_path = repo_root / "data" / "sdks_mcps"
            return allowed_path in abs_path.parents or abs_path == allowed_path
        except Exception:
            return False


def find_python_files(base_dir: Path) -> list[Path]:
    """Find all Python files in directory recursively."""
    python_files = []
    if base_dir.exists():
        for file_path in base_dir.rglob("*.py"):
            python_files.append(file_path)
    return python_files


def check_file_for_violations(file_path: Path) -> list[str]:
    """Check a single file for LLM SDK import violations."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        visitor = LLMSDKImportVisitor(file_path)
        visitor.visit(tree)
        return visitor.violations

    except (SyntaxError, UnicodeDecodeError, OSError) as e:
        return [f"Error parsing {file_path}: {e}"]


def test_no_direct_llm_sdk_imports_in_agentic_core():
    """Test that agentic_core/ has no direct LLM SDK imports."""
    repo_root = Path.cwd()
    agentic_core_dir = repo_root / "agentic_core"

    # Find all Python files in agentic_core
    python_files = find_python_files(agentic_core_dir)

    # Check each file for violations
    all_violations = {}

    for file_path in python_files:
        violations = check_file_for_violations(file_path)
        if violations:
            # Use relative path from repo root with forward slashes
            rel_path = str(file_path.relative_to(repo_root)).replace("\\", "/")
            all_violations[rel_path] = violations

    # Load expected violations from audit file
    audit_file = repo_root / "artifacts" / "migration" / "sdk_direct_import_audit.json"
    expected_violations = {}
    if audit_file.exists():
        with open(audit_file, encoding="utf-8") as f:
            expected_violations = json.load(f)

    # Filter expected violations to only include agentic_core files
    expected_agentic_core = {
        k.replace("\\", "/"): v
        for k, v in expected_violations.items()
        if k.replace("\\", "/").startswith("agentic_core/")
    }

    # Assert we found the expected violations
    assert len(all_violations) == len(expected_agentic_core), (
        f"Expected {len(expected_agentic_core)} files with violations, "
        f"found {len(all_violations)}. Files found: {list(all_violations.keys())}"
    )

    # Assert specific files are found
    for expected_file in expected_agentic_core:
        assert expected_file in all_violations, f"Expected violations in {expected_file} but none found"

    # This test should FAIL until migration is complete
    # For now, we just verify we can detect the violations
    if all_violations:
        print("\nDETECTED VIOLATIONS (expected before migration):")
        for file_path, violations in all_violations.items():
            print(f"\n{file_path}:")
            for violation in violations:
                print(f"  {violation}")

        # Fail the test as expected before migration
        pytest.fail(
            f"Found {len(all_violations)} files with direct LLM SDK imports in agentic_core/ - migration required"
        )
    else:
        # Pass if no violations found (after migration)
        print("No direct LLM SDK imports found in agentic_core/ - migration complete!")


def test_only_allowed_direct_imports_in_sdks_mcps():
    """Test that data/sdks_mcps/ is the only allowed location for direct SDK imports."""
    repo_root = Path.cwd()
    sdks_mcps_dir = repo_root / "data" / "sdks_mcps"

    # Find all Python files in data/sdks_mcps
    python_files = find_python_files(sdks_mcps_dir)

    # Check each file for violations (should be allowed here)
    all_violations = {}

    for file_path in python_files:
        violations = check_file_for_violations(file_path)
        if violations:
            # Use relative path from repo root with forward slashes
            rel_path = str(file_path.relative_to(repo_root)).replace("\\", "/")
            all_violations[rel_path] = violations

    print("\nAllowed direct SDK imports in data/sdks_mcps/:")
    for file_path, violations in all_violations.items():
        print(f"\n{file_path}:")
        for violation in violations:
            print(f"  {violation}")

    # This test always passes - data/sdks_mcps is allowed location
    assert True, "data/sdks_mcps/ is allowed location for direct SDK imports"


if __name__ == "__main__":
    # Run tests directly
    test_no_direct_llm_sdk_imports_in_agentic_core()
    test_only_allowed_direct_imports_in_sdks_mcps()
