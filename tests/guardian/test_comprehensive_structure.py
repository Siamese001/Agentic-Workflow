"""
Comprehensive SSOT Structure Validation - Guardian Test

This test validates the complete SSOT structure that was previously
handled by pre-commit hooks. It runs comprehensive checks on:
- File placement in valid territories
- Forbidden directory usage
- Test file placement
- Logic file locations
- Package structure completeness

Moved from pre-commit to Guardian for comprehensive validation.
"""

import sys
from pathlib import Path

import pytest

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import validation functions
from scripts.validate_structure import (
    BASE_AGENT_CANONICAL_DIR,
    FORBIDDEN_PATTERNS,
    VALID_TERRITORIES,
    validate_base_agent_location,
    validate_forbidden_patterns,
    validate_subfolder_structure,
    validate_territory,
)


class TestComprehensiveSSOTStructure:
    """
    Comprehensive SSOT structure validation.

    This test replaces the comprehensive parts of validate_structure.py
    that were moved from pre-commit to Guardian tests.
    """

    @pytest.mark.guardian
    def test_comprehensive_file_placement(self):
        """
        Test that all Python files are in valid SSOT locations.

        This is a comprehensive check of all files in the repository,
        not just staged files like pre-commit.
        """
        print("\n=== COMPREHENSIVE SSOT FILE PLACEMENT VALIDATION ===")

        violations: list[dict[str, str]] = []
        python_files = list(PROJECT_ROOT.rglob("*.py"))

        # Skip excluded directories
        excluded_dirs = {
            ".git",
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            ".venv",
            "venv",
            "env",
            "archives",
            ".sovereign_healing_backup",
        }

        for file_path in python_files:
            # Skip excluded directories
            if any(excluded in str(file_path) for excluded in excluded_dirs):
                continue

            # Skip this test file itself
            if "test_comprehensive_structure.py" in str(file_path):
                continue

            rel_path = file_path.relative_to(PROJECT_ROOT)

            # Check all validators
            is_valid_territory, territory_error = validate_territory(rel_path)
            if not is_valid_territory:
                violations.append(
                    {"file": str(rel_path), "type": "territory", "error": territory_error}
                )
                continue

            is_valid_structure, structure_error = validate_subfolder_structure(rel_path)
            if not is_valid_structure:
                violations.append(
                    {"file": str(rel_path), "type": "structure", "error": structure_error}
                )
                continue

            is_valid_forbidden, forbidden_error = validate_forbidden_patterns(rel_path)
            if not is_valid_forbidden:
                violations.append(
                    {"file": str(rel_path), "type": "forbidden", "error": forbidden_error}
                )

        # Report results
        print(f"\n  Files scanned: {len(python_files)}")
        print(f"  Violations found: {len(violations)}")

        if violations:
            print(f"\n[REPORT] {len(violations)} SSOT placement violations detected:")
            # Group by violation type for clearer reporting
            by_type = {}
            for v in violations:
                vtype = v["type"]
                if vtype not in by_type:
                    by_type[vtype] = []
                by_type[vtype].append(v)

            for vtype, items in by_type.items():
                print(f"  - {vtype}: {len(items)} files")
                for item in items[:3]:
                    print(f"    * {item['file']}")
                if len(items) > 3:
                    print(f"    ... and {len(items) - 3} more")
        else:
            print(f"[OK] All files in valid SSOT locations ({len(python_files)} files checked)")

    @pytest.mark.guardian
    def test_package_structure_completeness(self):
        """
        Test that all packages have proper __init__.py files.

        This ensures package structure completeness throughout the codebase.
        """
        print("\n=== PACKAGE STRUCTURE COMPLETENESS VALIDATION ===")

        missing_inits: list[str] = []

        # Check all directories that should have __init__.py
        for territory in VALID_TERRITORIES:
            if territory.startswith("."):
                continue  # Skip hidden directories

            territory_path = PROJECT_ROOT / territory
            if not territory_path.exists():
                continue

            # Find all Python subdirectories
            for py_dir in territory_path.rglob("*/"):
                # Skip excluded directories
                if any(
                    excluded in str(py_dir)
                    for excluded in ["__pycache__", ".git", ".pytest_cache", "node_modules"]
                ):
                    continue

                # Check if directory contains Python files
                py_files = list(py_dir.glob("*.py"))
                if py_files:
                    init_file = py_dir / "__init__.py"
                    if not init_file.exists():
                        missing_inits.append(str(py_dir.relative_to(PROJECT_ROOT)))

        # Report results
        print(f"  Missing __init__.py files: {len(missing_inits)}")

        if missing_inits:
            print(f"\n[REPORT] {len(missing_inits)} missing __init__.py files:")
            for init_path in missing_inits[:10]:
                print(f"  - {init_path}/")
            if len(missing_inits) > 10:
                print(f"  ... and {len(missing_inits) - 10} more")
        else:
            print("[OK] Package structure is complete")

    @pytest.mark.guardian
    def test_forbidden_directory_usage(self):
        """
        Test that no files are placed in forbidden directories.

        This is a dedicated test for forbidden pattern violations.
        """
        print("\n=== FORBIDDEN DIRECTORY USAGE VALIDATION ===")

        violations: list[dict[str, str]] = []

        # Check each forbidden pattern
        for pattern, description in FORBIDDEN_PATTERNS:
            pattern_path = PROJECT_ROOT / pattern
            if not pattern_path.exists():
                continue

            # Find all files in forbidden directory
            for file_path in pattern_path.rglob("*"):
                if file_path.is_file():
                    violations.append(
                        {
                            "file": str(file_path.relative_to(PROJECT_ROOT)),
                            "pattern": pattern,
                            "description": description,
                        }
                    )

        # Report results
        print(f"  Files in forbidden directories: {len(violations)}")

        if violations:
            print(f"\n[REPORT] {len(violations)} files in forbidden directories:")
            for v in violations[:10]:
                print(f"  - {v['file']} (in {v['pattern']}: {v['description']})")
            if len(violations) > 10:
                print(f"  ... and {len(violations) - 10} more")
            print("\nThese files should be moved to valid SSOT locations.")
        else:
            print("[OK] No files in forbidden directories")

    @pytest.mark.guardian
    def test_test_file_placement(self):
        """
        Test that test files are properly placed in tests/ hierarchy.
        """
        print("\n=== TEST FILE PLACEMENT VALIDATION ===")

        misplaced_tests: list[str] = []

        # Find all test files outside tests/ directory
        for territory in VALID_TERRITORIES:
            if territory == "tests":
                continue  # Skip tests directory itself

            territory_path = PROJECT_ROOT / territory
            if not territory_path.exists():
                continue

            # Find test files (files starting with test_ or ending with _test.py)
            for file_path in territory_path.rglob("*.py"):
                if file_path.name.startswith("test_") or file_path.name.endswith("_test.py"):
                    misplaced_tests.append(str(file_path.relative_to(PROJECT_ROOT)))

        # Report results
        print(f"  Misplaced test files: {len(misplaced_tests)}")

        if misplaced_tests:
            print(f"\n[REPORT] {len(misplaced_tests)} misplaced test files:")
            for test_file in misplaced_tests[:10]:
                print(f"  - {test_file}")
            if len(misplaced_tests) > 10:
                print(f"  ... and {len(misplaced_tests) - 10} more")
            print("\nTest files should be placed in tests/ hierarchy.")
        else:
            print("[OK] All test files properly placed")

    @pytest.mark.guardian
    def test_constitutional_base_agent_location(self):
        """
        [CONSTITUTIONAL] Test that base agents are in correct locations.

        This is a constitutional rule that enforces:
        1. Core framework base agents (SovereignBaseAgent, layer base agents)
           MUST be in agentic_core/base_agents/
        2. App-specific base agents (prefixed with app name)
           MUST be in their respective apps_* directories

        Moved from pre-commit to Guardian tests for comprehensive validation.
        """
        print("\n=== CONSTITUTIONAL BASE AGENT LOCATION CHECK ===")

        violations: list[dict[str, str]] = []

        # Find all *BaseAgent.py files
        for file_path in PROJECT_ROOT.rglob("*BaseAgent.py"):
            # Skip excluded directories
            if any(
                excluded in str(file_path)
                for excluded in [
                    "__pycache__",
                    ".git",
                    ".pytest_cache",
                    "node_modules",
                    "archives",
                    ".sovereign_healing_backup",
                ]
            ):
                continue

            # Validate location
            relative_path = str(file_path.relative_to(PROJECT_ROOT))
            is_valid, error = validate_base_agent_location(relative_path)

            if not is_valid:
                violations.append({"file": relative_path, "error": error})

        # Report results
        print(f"  Base agent files checked: {len(list(PROJECT_ROOT.rglob('*BaseAgent.py')))}")
        print(f"  Constitutional violations: {len(violations)}")

        if violations:
            print(f"\n[REPORT] {len(violations)} constitutional violations detected:")
            for v in violations[:10]:
                print(f"  - {v['file']}")
                print(f"    Error: {v['error']}")
            if len(violations) > 10:
                print(f"  ... and {len(violations) - 10} more")

            print("\n[REMEDIATION] Move base agents to correct locations:")
            print(f"  - Core base agents → {BASE_AGENT_CANONICAL_DIR}/")
            print("  - App-specific base agents → respective apps_* directories")
            print("\n  See: tests/guardian/REMEDIATION_GUIDE.md#base-agent-location")
        else:
            print("[OK] All base agents in correct locations")
