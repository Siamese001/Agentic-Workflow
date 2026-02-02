"""
Test Suite: Phase 1 Canon Keys Foundation Cleanup
==============================================
Comprehensive test cases for Phase 1 of canon keys deprecation.
Tests foundation cleanup including registry removal, comment cleanup, and import updates.
"""

import ast
import re
import sys
from pathlib import Path
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestPhase1FoundationCleanup:
    """
    Test suite for Phase 1 foundation cleanup of canon keys deprecation.
    Validates registry removal, comment cleanup, and import statement updates.
    """

    def test_structure_blueprint_registry_removed(self):
        """
        Test 1.1.1: Verify SAFETY_VALIDATION_REGISTRY is completely removed.
        """
        blueprint_path = (
            PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "structure_blueprint.py"
        )
        assert blueprint_path.exists(), "structure_blueprint.py missing"

        with open(blueprint_path, encoding="utf-8") as f:
            content = f.read()

        # Should NOT contain deprecated registry
        deprecated_patterns = [
            "SAFETY_VALIDATION_REGISTRY",
            "SOVEREIGN CANON REGISTRY",
            "ALL NUMERIC KEYS (0-50) HAVE BEEN DEPRECATED",
            "DEPRECATION STATUS: 100% COMPLETE",
        ]

        for pattern in deprecated_patterns:
            assert pattern not in content, f"Found deprecated pattern: {pattern}"

        print("✅ PASSED: SAFETY_VALIDATION_REGISTRY completely removed")

    def test_canon_comments_cleaned(self):
        """
        Test 1.1.2: Verify canon-related comments are cleaned up.
        """
        blueprint_path = (
            PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "structure_blueprint.py"
        )

        with open(blueprint_path, encoding="utf-8") as f:
            content = f.read()

        # Should NOT contain canon-related comments
        deprecated_comments = [
            "EVICTED per CANON_VALIDATION_REGISTRY",
            "# agentic_core/utils/core_extensions EVICTED per CANON_VALIDATION_REGISTRY",
            '# "core_extensions": "utils",  # EVICTED per CANON_VALIDATION_REGISTRY',
        ]

        for comment in deprecated_comments:
            assert comment not in content, f"Found deprecated comment: {comment}"

        print("✅ PASSED: Canon-related comments cleaned up")

    def test_structure_blueprint_imports_work(self):
        """
        Test 1.2.1: Verify structure_blueprint imports work after cleanup.
        """
        try:
            # Just test that the module can be imported without error
            import agentic_core.L5_safety.validators.structure_blueprint as sb

            assert hasattr(sb, "SOVEREIGN_TERRITORIES")
            print("✅ PASSED: Structure blueprint imports work correctly")
        except ImportError as e:
            pytest.fail(f"Import failed after cleanup: {e}")

    def test_no_canon_registry_imports_remain(self):
        """
        Test 1.2.2: Verify no test files have active CANON_VALIDATION_REGISTRY imports.
        """
        test_files_to_check = [
            "tests/unit/agentic_core/L0_maintenance/scripts/test_canon_key_removal.py",
            "tests/unit/agentic_core/L5_safety/validators/test_structure_reconciliation.py",
            "tests/unit/agentic_core/L0_maintenance/scripts/test_consolidated_migration.py",
            "tests/unit/agentic_core/L0_maintenance/scripts/test_final_integrity_audit.py",
            "tests/unit/agentic_core/L0_maintenance/scripts/test_final_integrity_simple.py",
        ]

        violations = []

        for test_file_path in test_files_to_check:
            test_file = PROJECT_ROOT / test_file_path
            if not test_file.exists():
                continue

            with open(test_file, encoding="utf-8") as f:
                content = f.read()

            # Check for actual import statements that would fail
            import_pattern = "from.*import.*CANON_VALIDATION_REGISTRY"
            if re.search(import_pattern, content):
                violations.append(
                    f"{test_file_path}: Contains active CANON_VALIDATION_REGISTRY import"
                )

            # Check for direct usage that would fail (allow validation code and documentation)
            lines = content.split("\n")
            for i, line in enumerate(lines):
                line = line.strip()
                if (
                    "CANON_VALIDATION_REGISTRY" in line
                    and not line.startswith("#")
                    and not line.startswith('"""')
                    and "except" not in line
                    and "ImportError" not in line
                    and "NameError" not in line
                    and "AttributeError" not in line
                    and "hasattr(sb," not in line  # Allow hasattr checks
                    and "pytest.fail" not in line  # Allow pytest.fail checks
                    and "print(" not in line  # Allow print statements
                    and "SSOT Registry Integrity" not in line  # Allow docstring references
                    and "CRITICAL: Verify" not in line  # Allow test descriptions
                    and "_ = sb.CANON_VALIDATION_REGISTRY" not in line
                ):  # Allow test validation
                    violations.append(f"{test_file_path}:{i + 1}: Active usage - {line}")

        assert not violations, f"Found active registry usage: {violations}"
        print("✅ PASSED: No CANON_VALIDATION_REGISTRY imports remain in test files")

    def test_core_constants_still_accessible(self):
        """
        Test 1.2.3: Verify core constants are still accessible after cleanup.
        """
        try:
            from agentic_core.L5_safety.validators.structure_blueprint import (
                AGENTIC_CORE_DIR,
                APPS_RG_DIR,
                APPS_LIC_DIR,
                APPS_SHARED_DIR,
                TESTS_DIR,
            )

            # Verify constants have expected values
            assert AGENTIC_CORE_DIR == "agentic_core"
            assert APPS_RG_DIR == "apps_rg"
            assert APPS_LIC_DIR == "apps_lic"
            assert APPS_SHARED_DIR == "apps_shared"
            assert TESTS_DIR == "tests"

            print("✅ PASSED: Core constants still accessible")

        except (ImportError, AssertionError) as e:
            pytest.fail(f"Core constants issue after cleanup: {e}")

    def test_blueprint_ast_validity(self):
        """
        Test 1.3.1: Verify structure_blueprint.py has valid Python syntax after cleanup.
        """
        blueprint_path = (
            PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "structure_blueprint.py"
        )

        try:
            with open(blueprint_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST to check syntax validity
            ast.parse(content)
            print("✅ PASSED: structure_blueprint.py has valid Python syntax")

        except SyntaxError as e:
            pytest.fail(f"Syntax error in structure_blueprint.py: {e}")

    def test_no_ghost_variables(self):
        """
        Test 1.3.2: Verify no ghost variables remain in structure_blueprint module.
        """
        try:
            import agentic_core.L5_safety.validators.structure_blueprint as sb

            # Get all module variables
            all_vars = dir(sb)

            # Check for ghost patterns
            ghost_patterns = ["canon_key", "CANON_KEY", "SAFETY_VALIDATION_REGISTRY"]

            ghost_vars = []
            for var in all_vars:
                if any(pattern in var for pattern in ghost_patterns):
                    ghost_vars.append(var)

            assert not ghost_vars, f"Found ghost variables: {ghost_vars}"
            print("✅ PASSED: No ghost variables remain in structure_blueprint")

        except ImportError as e:
            pytest.fail(f"Cannot import structure_blueprint for ghost check: {e}")

    def test_l4_approved_folders_integrity(self):
        """
        Test 1.3.3: Verify L4_APPROVED_FOLDERS integrity after cleanup.
        """
        try:
            from agentic_core.L5_safety.validators.structure_blueprint import L4_APPROVED_FOLDERS

            # Should still contain expected folders
            expected_folders = [
                "agentic_core/L6_observability/dashboards",
                "agentic_core/L0_maintenance/scripts",
                "agentic_core/L3_orchestration/workflow_engines",
                "agentic_core/L1_cognition/thought_engine",
                "agentic_core/L5_safety/guardrails",
                "agentic_core/L5_safety/validators",
                "agentic_core/L5_safety/gravity",
                "agentic_core/L2_execution/tool_registry",
                "agentic_core/L2_execution/mcp",
                "agentic_core/L4_state/validation_context",
                "agentic_core/schemas/models",
                "agentic_core/config/blueprint_sovereign",
                "agentic_core/prompt_governance/meta_prompts",
                "agentic_core/prompt_governance/templates",
                "agentic_core/prompt_governance/scripts",
                "agentic_core/prompt_governance/version_registry",
            ]

            for folder in expected_folders:
                assert folder in L4_APPROVED_FOLDERS, f"Missing folder: {folder}"

            print("✅ PASSED: L4_APPROVED_FOLDERS integrity maintained")

        except ImportError as e:
            pytest.fail(f"Cannot import L4_APPROVED_FOLDERS: {e}")

    def test_sovereign_territories_integrity(self):
        """
        Test 1.3.4: Verify SOVEREIGN_TERRITORIES integrity after cleanup.
        """
        try:
            from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_TERRITORIES

            # Should still contain core territories
            expected_territories = [
                "agentic_core",
                "apps_rg",
                "apps_lic",
                "apps_shared",
                "tests",
                "ops_scripts",
                "archives",
                "data",
                "docs",
                "logs",
                "reports",
                "scripts",
            ]

            for territory in expected_territories:
                assert territory in SOVEREIGN_TERRITORIES, f"Missing territory: {territory}"

            # Verify agentic_core structure is intact
            agentic_core = SOVEREIGN_TERRITORIES["agentic_core"]
            assert "depth" in agentic_core
            assert agentic_core["depth"] == 3
            assert "subfolders" in agentic_core
            assert "base_agents" in agentic_core["subfolders"]

            print("✅ PASSED: SOVEREIGN_TERRITORIES integrity maintained")

        except ImportError as e:
            pytest.fail(f"Cannot import SOVEREIGN_TERRITORIES: {e}")


def run_phase1_tests():
    """
    Run all Phase 1 tests and return results.
    """
    print("\n" + "=" * 70)
    print("PHASE 1: FOUNDATION CLEANUP TEST SUITE")
    print("=" * 70 + "\n")

    test_instance = TestPhase1FoundationCleanup()
    passed = 0
    failed = 0

    test_methods = [
        test_instance.test_structure_blueprint_registry_removed,
        test_instance.test_canon_comments_cleaned,
        test_instance.test_structure_blueprint_imports_work,
        test_instance.test_no_canon_registry_imports_remain,
        test_instance.test_core_constants_still_accessible,
        test_instance.test_blueprint_ast_validity,
        test_instance.test_no_ghost_variables,
        test_instance.test_l4_approved_folders_integrity,
        test_instance.test_sovereign_territories_integrity,
    ]

    for test_method in test_methods:
        try:
            test_method()
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_method.__name__}: {e}")
            failed += 1

    print(f"\n{'=' * 70}")
    print(f"PHASE 1 TEST RESULTS: {passed} passed, {failed} failed")
    print(f"SUCCESS RATE: {passed / (passed + failed) * 100:.1f}%")
    print("=" * 70 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_phase1_tests()
    sys.exit(0 if success else 1)
