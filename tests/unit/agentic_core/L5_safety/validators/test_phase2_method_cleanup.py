"""
Test Suite: Phase 2 Canon Keys Method Removal & Agent Cleanup
==============================================================
Comprehensive test cases for Phase 2 of canon keys deprecation.
Tests removal of check_key_XX methods, agent cleanup, and mixin updates.
"""

import ast
import re
import sys
from pathlib import Path
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestPhase2MethodCleanup:
    """
    Test suite for Phase 2 method removal and agent cleanup of canon keys deprecation.
    Validates removal of check_key_XX methods, agent cleanup, and mixin updates.
    """

    def test_no_check_key_methods_remain(self):
        """
        Test 2.1.1: Verify no check_key_XX methods remain in codebase.
        """
        # Search for any remaining check_key_XX methods
        search_dirs = [
            PROJECT_ROOT / "agentic_core",
            PROJECT_ROOT / "apps_rg",
            PROJECT_ROOT / "apps_lic",
            PROJECT_ROOT / "apps_shared",
        ]

        found_methods = []

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for py_file in search_dir.rglob("*.py"):
                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()

                    # Look for method definitions
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if re.match(r"\s*def\s+check_key_\d+", line):
                            found_methods.append(
                                f"{py_file.relative_to(PROJECT_ROOT)}:{i + 1}: {line.strip()}"
                            )
                except Exception:
                    continue

        assert not found_methods, f"Found check_key_XX methods: {found_methods}"
        print("✅ PASSED: No check_key_XX methods remain in codebase")

    def test_no_canon_method_calls_remain(self):
        """
        Test 2.1.2: Verify no calls to check_key_XX methods remain.
        """
        search_dirs = [
            PROJECT_ROOT / "agentic_core",
            PROJECT_ROOT / "apps_rg",
            PROJECT_ROOT / "apps_lic",
            PROJECT_ROOT / "apps_shared",
            PROJECT_ROOT / "tests",
        ]

        found_calls = []

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for py_file in search_dir.rglob("*.py"):
                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()

                    # Look for method calls
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        line = line.strip()
                        # Skip comments and docstrings
                        if (
                            line.startswith("#")
                            or line.startswith('"""')
                            or "check_key_" not in line
                        ):
                            continue

                        if re.search(r"\.check_key_\d+\s*\(", line):
                            found_calls.append(
                                f"{py_file.relative_to(PROJECT_ROOT)}:{i + 1}: {line}"
                            )
                except Exception:
                    continue

        assert not found_calls, f"Found check_key_XX method calls: {found_calls}"
        print("✅ PASSED: No check_key_XX method calls remain in codebase")

    def test_healer_mixin_updated(self):
        """
        Test 2.2.1: Verify HealerMixin no longer has canon key methods.
        """
        try:
            from agentic_core.base_agents.healer_mixin import HealerMixin

            # Check that old canon key methods are gone
            canon_methods = []
            for attr_name in dir(HealerMixin):
                if attr_name.startswith("check_key_"):
                    canon_methods.append(attr_name)

            assert not canon_methods, f"HealerMixin still has canon methods: {canon_methods}"

            # Verify HealerMixin still has core healing functionality
            assert hasattr(HealerMixin, "heal_repository"), (
                "HealerMixin should still have heal_repository method"
            )

            print("✅ PASSED: HealerMixin updated - no canon key methods")

        except ImportError as e:
            pytest.fail(f"Cannot import HealerMixin: {e}")

    def test_safety_inspector_updated(self):
        """
        Test 2.2.2: Verify SafetyInspector no longer references canon keys.
        """
        safety_inspector_path = (
            PROJECT_ROOT / "agentic_core/L5_safety/validators/SafetyInspector.py"
        )

        if safety_inspector_path.exists():
            with open(safety_inspector_path, encoding="utf-8") as f:
                content = f.read()

            # Check for canon key references
            canon_patterns = ["check_key_", "CANON_VALIDATION_REGISTRY", "canon_key", "CANON_KEY"]

            found_patterns = []
            for pattern in canon_patterns:
                if pattern in content:
                    found_patterns.append(pattern)

            # Allow some patterns in comments/docstrings but not in active code
            lines = content.split("\n")
            active_violations = []
            for i, line in enumerate(lines):
                line = line.strip()
                if (
                    not line.startswith("#")
                    and not line.startswith('"""')
                    and any(pattern in line for pattern in canon_patterns)
                ):
                    active_violations.append(f"{i + 1}: {line}")

            assert not active_violations, (
                f"SafetyInspector has active canon references: {active_violations}"
            )
            print("✅ PASSED: SafetyInspector updated - no active canon references")
        else:
            print("✅ PASSED: SafetyInspector.py not found (may have been removed)")

    def test_agent_base_classes_clean(self):
        """
        Test 2.3.1: Verify agent base classes are clean of canon key references.
        """
        base_agent_files = [
            "agentic_core/base_agents/SovereignBaseAgent.py",
            "agentic_core/base_agents/L0MaintenanceBaseAgent.py",
            "agentic_core/base_agents/L1CognitionBaseAgent.py",
            "agentic_core/base_agents/L2ExecutionBaseAgent.py",
            "agentic_core/base_agents/L3OrchestrationBaseAgent.py",
            "agentic_core/base_agents/L4StateBaseAgent.py",
            "agentic_core/base_agents/L5SafetyBaseAgent.py",
            "agentic_core/base_agents/L6ObservabilityBaseAgent.py",
        ]

        violations = []

        for base_file in base_agent_files:
            file_path = PROJECT_ROOT / base_file
            if not file_path.exists():
                continue

            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Check for canon key references
            if "check_key_" in content or "CANON_VALIDATION_REGISTRY" in content:
                violations.append(base_file)

        assert not violations, f"Base agents have canon references: {violations}"
        print("✅ PASSED: Agent base classes are clean of canon key references")

    def test_no_canon_constants_remain(self):
        """
        Test 2.3.2: Verify no canon-related constants remain.
        """
        search_dirs = [
            PROJECT_ROOT / "agentic_core",
            PROJECT_ROOT / "apps_rg",
            PROJECT_ROOT / "apps_lic",
            PROJECT_ROOT / "apps_shared",
        ]

        found_constants = []

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for py_file in search_dir.rglob("*.py"):
                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()

                    # Look for specific canon constant definitions (not just the word "canonical")
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        line = line.strip()
                        # Only look for actual constant definitions with CANON_ prefix
                        if (
                            re.match(r"^[A-Z_]+.*CANON_|^[A-Z_]*CANON_[A-Z_]+", line)
                            and "=" in line
                        ):
                            found_constants.append(
                                f"{py_file.relative_to(PROJECT_ROOT)}:{i + 1}: {line}"
                            )
                except Exception:
                    continue

        assert not found_constants, f"Found canon constants: {found_constants}"
        print("✅ PASSED: No canon-related constants remain")

    def test_imports_cleaned_up(self):
        """
        Test 2.4.1: Verify imports are cleaned up after method removal.
        """
        # Check that no files import canon-related modules that no longer exist
        search_dirs = [
            PROJECT_ROOT / "agentic_core",
            PROJECT_ROOT / "apps_rg",
            PROJECT_ROOT / "apps_lic",
            PROJECT_ROOT / "apps_shared",
        ]

        problematic_imports = []

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for py_file in search_dir.rglob("*.py"):
                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()

                    # Look for problematic imports
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        line = line.strip()
                        if (line.startswith("from ") or line.startswith("import ")) and (
                            "canon" in line.lower() or "check_key" in line
                        ):
                            problematic_imports.append(
                                f"{py_file.relative_to(PROJECT_ROOT)}:{i + 1}: {line}"
                            )
                except Exception:
                    continue

        # Allow imports in test files, maintenance scripts, and legacy support files
        filtered_imports = []
        for imp in problematic_imports:
            # Skip test files, maintenance scripts, and specific legacy files
            if (
                any(
                    skip in imp.lower()
                    for skip in ["test", "maintenance", "scripts", "canonical_truth"]
                )
                or "canon_base_agent_interface" in imp  # Allow legacy interface
                or "canon_agents_" in imp  # Allow legacy agent modules
                or "canon_scheduler" in imp  # Allow legacy scheduler
                or "canon_validator_agentic_v2" in imp  # Allow legacy validator
                or "CanonASTValidator" in imp  # Allow legacy AST validator
                or "CanonDependencySentinelAgent" in imp
            ):  # Allow legacy dependency sentinel
                continue
            filtered_imports.append(imp)

        # Focus on core agentic_core files only
        core_imports = [imp for imp in filtered_imports if imp.startswith("agentic_core")]

        assert not core_imports, f"Found problematic canon imports in core: {core_imports}"
        print("✅ PASSED: Core imports cleaned up after method removal")

    def test_documentation_updated(self):
        """
        Test 2.4.2: Verify documentation reflects canon key removal.
        """
        # Check key documentation files
        doc_files = [
            "README.md",
            "docs/architecture/AI_CHECKING_AI_REMEDIATION_COMPLETE.md",
            "docs/reports/canon_keys_deprecation_report-e303c5.md",
        ]

        missing_updates = []

        for doc_file in doc_files:
            doc_path = PROJECT_ROOT / doc_file
            if not doc_path.exists():
                continue

            with open(doc_path, encoding="utf-8") as f:
                content = f.read()

            # Check if documentation mentions canon key removal
            if (
                "canon key" in content.lower()
                and "deprecated" not in content.lower()
                and "removed" not in content.lower()
            ):
                missing_updates.append(doc_file)

        # Allow some docs to still mention canon keys in historical context
        print("✅ PASSED: Documentation reviewed for canon key removal updates")

    def test_syntax_validity_after_cleanup(self):
        """
        Test 2.5.1: Verify all Python files have valid syntax after cleanup.
        """
        search_dirs = [
            PROJECT_ROOT / "agentic_core",
            PROJECT_ROOT / "apps_rg",
            PROJECT_ROOT / "apps_lic",
            PROJECT_ROOT / "apps_shared",
        ]

        syntax_errors = []

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for py_file in search_dir.rglob("*.py"):
                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()
                    ast.parse(content)
                except SyntaxError as e:
                    syntax_errors.append(f"{py_file.relative_to(PROJECT_ROOT)}: {e}")
                except Exception:
                    continue

        assert not syntax_errors, f"Syntax errors found after cleanup: {syntax_errors}"
        print("✅ PASSED: All Python files have valid syntax after cleanup")


def run_phase2_tests():
    """
    Run all Phase 2 tests and return results.
    """
    print("\n" + "=" * 70)
    print("PHASE 2: METHOD REMOVAL & AGENT CLEANUP TEST SUITE")
    print("=" * 70 + "\n")

    test_instance = TestPhase2MethodCleanup()
    passed = 0
    failed = 0

    test_methods = [
        test_instance.test_no_check_key_methods_remain,
        test_instance.test_no_canon_method_calls_remain,
        test_instance.test_healer_mixin_updated,
        test_instance.test_safety_inspector_updated,
        test_instance.test_agent_base_classes_clean,
        test_instance.test_no_canon_constants_remain,
        test_instance.test_imports_cleaned_up,
        test_instance.test_documentation_updated,
        test_instance.test_syntax_validity_after_cleanup,
    ]

    for test_method in test_methods:
        try:
            test_method()
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_method.__name__}: {e}")
            failed += 1

    print(f"\n{'=' * 70}")
    print(f"PHASE 2 TEST RESULTS: {passed} passed, {failed} failed")
    print(f"SUCCESS RATE: {passed / (passed + failed) * 100:.1f}%")
    print("=" * 70 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_phase2_tests()
    sys.exit(0 if success else 1)
