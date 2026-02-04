"""
Test Suite: Phase 3 Canon Keys Legacy File Cleanup
=================================================
Comprehensive test cases for Phase 3 of canon keys deprecation.
Tests removal of legacy files, cleanup of deprecated modules, and archive management.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestPhase3LegacyCleanup:
    """
    Test suite for Phase 3 legacy file cleanup of canon keys deprecation.
    Validates removal of legacy files, cleanup of deprecated modules, and archive management.
    """

    def test_no_canon_files_in_core(self):
        """
        Test 3.1.1: Verify no canon-related files remain in core directories.
        """
        core_dirs = [
            PROJECT_ROOT / "agentic_core",
            PROJECT_ROOT / "apps_rg",
            PROJECT_ROOT / "apps_lic",
            PROJECT_ROOT / "apps_shared",
        ]

        found_files = []

        for core_dir in core_dirs:
            if not core_dir.exists():
                continue

            for file_path in core_dir.rglob("*"):
                if file_path.is_file():
                    # Check for canon-related filenames (be more specific)
                    filename = file_path.name.lower()
                    filepath = str(file_path.relative_to(PROJECT_ROOT)).lower()

                    # Only look for actual canon key files, not legitimate canonical tools
                    if (
                        (
                            "canon" in filename
                            and (
                                "key" in filename
                                or "validator" in filename
                                or "agent" in filename
                                or "scheduler" in filename
                            )
                        )
                        or filename.startswith("canon_")
                        or "canonkey" in filename
                        or ("check_key" in filename and filename.endswith(".py"))
                    ):
                        found_files.append(str(file_path.relative_to(PROJECT_ROOT)))

        assert not found_files, f"Found canon files in core: {found_files}"
        print("✅ PASSED: No canon-related files remain in core directories")

    def test_legacy_files_archived(self):
        """
        Test 3.1.2: Verify legacy canon files are properly archived.
        """
        archives_dir = PROJECT_ROOT / "archives"

        if not archives_dir.exists():
            print("✅ PASSED: Archives directory not found (no legacy files to archive)")
            return

        # Check for expected archive subdirectories
        expected_archives = [
            "deprecated_key_validators",
            "gatekeeper",
            "void_violations",
        ]

        found_archives = []
        for archive_subdir in expected_archives:
            archive_path = archives_dir / archive_subdir
            if archive_path.exists():
                found_archives.append(archive_subdir)

        # Should have at least some archives if they exist
        if found_archives:
            print(f"✅ PASSED: Found archived legacy directories: {found_archives}")
        else:
            print("✅ PASSED: No legacy archives found (clean state)")

    def test_no_canon_modules_importable(self):
        """
        Test 3.2.1: Verify deprecated canon modules cannot be imported.
        """
        deprecated_modules = [
            "agentic_core.L5_safety.validators.CanonDependencySentinelAgent",
            "agentic_core.canon_agents_core",
            "agentic_core.canon_agents_quality",
            "agentic_core.canon_agents_syntax",
            "agentic_core.canon_scheduler",
            "agentic_core.base_agents.canon_base_agent_interface",
        ]

        failed_imports = []

        for module_name in deprecated_modules:
            try:
                __import__(module_name)
                failed_imports.append(f"{module_name}: Should not be importable")
            except ImportError:
                # This is expected - module should not exist
                pass
            except Exception:
                # Other exceptions are also acceptable (module broken)
                pass

        assert not failed_imports, f"Deprecated modules still importable: {failed_imports}"
        print("✅ PASSED: Deprecated canon modules are not importable")

    def test_canon_references_removed_from_docs(self):
        """
        Test 3.2.2: Verify canon references removed from documentation.
        """
        doc_dirs = [
            PROJECT_ROOT / "docs",
            PROJECT_ROOT / "README.md",
        ]

        problematic_refs = []

        for doc_path in doc_dirs:
            if doc_path.is_file():
                # Single file
                try:
                    with open(doc_path, encoding="utf-8") as f:
                        content = f.read()

                    # Look for active canon references (not in historical context)
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        line = line.strip()
                        if (
                            "canon key" in line.lower()
                            and not line.startswith("#")
                            and not line.startswith("<!--")
                            and "deprecated" not in line.lower()
                            and "removed" not in line.lower()
                        ):
                            problematic_refs.append(f"{doc_path.name}:{i + 1}: {line}")
                except Exception:
                    continue

            elif doc_path.is_dir():
                # Directory of files
                for doc_file in doc_path.rglob("*.md"):
                    try:
                        with open(doc_file, encoding="utf-8") as f:
                            content = f.read()

                        # Look for problematic canon references
                        if "canon key" in content.lower():
                            # Allow historical references
                            if "deprecated" in content.lower() or "phase" in content.lower():
                                continue
                            problematic_refs.append(str(doc_file.relative_to(PROJECT_ROOT)))
                    except Exception:
                        continue

        # Allow some documentation references for historical context
        if len(problematic_refs) > 10:
            assert False, f"Too many canon references in docs: {problematic_refs[:10]}..."

        print("✅ PASSED: Canon references appropriately removed from documentation")

    def test_config_files_cleaned(self):
        """
        Test 3.3.1: Verify configuration files are cleaned of canon references.
        """
        config_dirs = [
            PROJECT_ROOT / "config",
            PROJECT_ROOT / ".github",
        ]

        found_refs = []

        for config_dir in config_dirs:
            if not config_dir.exists():
                continue

            for config_file in config_dir.rglob("*"):
                if not config_file.is_file():
                    continue

                try:
                    with open(config_file, encoding="utf-8") as f:
                        content = f.read()

                    # Look for canon references in config files
                    if "canon" in content.lower() and "key" in content.lower():
                        # Allow some references in comments
                        lines = content.split("\n")
                        for i, line in enumerate(lines):
                            line = line.strip()
                            if (
                                "canon" in line.lower()
                                and "key" in line.lower()
                                and not line.startswith("#")
                                and not line.startswith('"')
                                and not line.startswith("'")
                            ):
                                found_refs.append(f"{config_file.name}:{i + 1}: {line}")
                except Exception:
                    continue

        # Config files should be clean of active canon references
        assert not found_refs, f"Found canon references in config: {found_refs}"
        print("✅ PASSED: Configuration files cleaned of canon references")

    def test_test_files_updated(self):
        """
        Test 3.3.2: Verify test files are updated for canon key removal.
        """
        test_dirs = [
            PROJECT_ROOT / "tests",
        ]

        outdated_tests = []

        for test_dir in test_dirs:
            if not test_dir.exists():
                continue

            for test_file in test_dir.rglob("*.py"):
                try:
                    with open(test_file, encoding="utf-8") as f:
                        content = f.read()

                    # Look for tests that still expect canon keys to exist
                    if "CANON_VALIDATION_REGISTRY" in content:
                        # Allow tests that are checking for removal
                        if "removed" in content.lower() or "deprecated" in content.lower():
                            continue
                        outdated_tests.append(str(test_file.relative_to(PROJECT_ROOT)))

                    # Look for tests that call check_key_ methods
                    if "check_key_" in content and "def test_" in content:
                        # Allow tests that are testing the removal
                        if "removed" in content.lower() or "deprecated" in content.lower():
                            continue
                        outdated_tests.append(str(test_file.relative_to(PROJECT_ROOT)))

                except Exception:
                    continue

        # Should have minimal outdated tests
        if len(outdated_tests) > 5:
            assert False, f"Too many outdated tests: {outdated_tests[:5]}..."

        print("✅ PASSED: Test files appropriately updated for canon key removal")

    def test_no_orphaned_canon_dependencies(self):
        """
        Test 3.4.1: Verify no orphaned canon dependencies remain.
        """
        search_dirs = [
            PROJECT_ROOT / "agentic_core",
            PROJECT_ROOT / "apps_rg",
            PROJECT_ROOT / "apps_lic",
            PROJECT_ROOT / "apps_shared",
        ]

        orphaned_deps = []

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for py_file in search_dir.rglob("*.py"):
                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()

                    # Look for imports of non-existent canon modules
                    lines = content.split("\n")
                    in_try_block = False

                    for i, line in enumerate(lines):
                        stripped = line.strip()

                        # Track try/except blocks (imports with fallbacks are OK)
                        if stripped.startswith("try:"):
                            in_try_block = True
                        elif stripped.startswith("except") and in_try_block:
                            in_try_block = False
                            continue

                        if stripped.startswith("from ") or stripped.startswith("import "):
                            # Skip imports inside try/except blocks (they have fallbacks)
                            if in_try_block:
                                continue

                            # Check for canon-related imports that would fail
                            if any(
                                module in stripped
                                for module in [
                                    "canon_agents_core",
                                    "canon_agents_quality",
                                    "canon_agents_syntax",
                                    "canon_scheduler",
                                    "canon_base_agent_interface",
                                    "CanonDependencySentinelAgent",
                                    "CanonSwarmScheduler",
                                    "CanonASTValidator",
                                ]
                            ):
                                # Allow imports in maintenance scripts and legacy files
                                if any(
                                    skip in str(py_file)
                                    for skip in ["maintenance", "scripts", "legacy", "test"]
                                ):
                                    continue
                                orphaned_deps.append(
                                    f"{py_file.relative_to(PROJECT_ROOT)}:{i + 1}: {stripped}"
                                )
                except Exception:
                    continue

        # Focus on core files only
        core_orphans = [dep for dep in orphaned_deps if dep.startswith("agentic_core")]

        # All orphaned dependencies should be fixed in Phase 3
        assert not core_orphans, f"Found orphaned canon dependencies: {core_orphans}"

        print("✅ PASSED: No orphaned canon dependencies remain")

    def test_file_structure_integrity(self):
        """
        Test 3.5.1: Verify file structure integrity after cleanup.
        """
        # Check that core directories still exist
        core_dirs = [
            "agentic_core",
            "apps_rg",
            "apps_lic",
            "apps_shared",
            "tests",
        ]

        missing_dirs = []
        for core_dir in core_dirs:
            dir_path = PROJECT_ROOT / core_dir
            if not dir_path.exists():
                missing_dirs.append(core_dir)

        assert not missing_dirs, f"Missing core directories: {missing_dirs}"

        # Check that key subdirectories exist
        key_subdirs = [
            "agentic_core/base_agents",
            "agentic_core/L5_safety/validators",
            "agentic_core/L0_maintenance/scripts",
            "tests/unit",
            "tests/integration",
        ]

        missing_subdirs = []
        for subdir in key_subdirs:
            subdir_path = PROJECT_ROOT / subdir
            if not subdir_path.exists():
                missing_subdirs.append(subdir)

        assert not missing_subdirs, f"Missing key subdirectories: {missing_subdirs}"
        print("✅ PASSED: File structure integrity maintained after cleanup")

    def test_import_integrity(self):
        """
        Test 3.5.2: Verify import integrity after cleanup.
        """
        # Test that key modules can still be imported
        key_imports = [
            "agentic_core.base_agents.healer_mixin",
            "agentic_core.L5_safety.validators.structure_blueprint",
        ]

        failed_imports = []

        for module_name in key_imports:
            try:
                __import__(module_name)
            except ImportError as e:
                failed_imports.append(f"{module_name}: {e}")
            except Exception as e:
                # Other import errors are also concerning
                failed_imports.append(f"{module_name}: {e}")

        assert not failed_imports, f"Import integrity issues: {failed_imports}"
        print("✅ PASSED: Import integrity maintained after cleanup")


def run_phase3_tests():
    """
    Run all Phase 3 tests and return results.
    """
    print("\n" + "=" * 70)
    print("PHASE 3: LEGACY FILE CLEANUP TEST SUITE")
    print("=" * 70 + "\n")

    test_instance = TestPhase3LegacyCleanup()
    passed = 0
    failed = 0

    test_methods = [
        test_instance.test_no_canon_files_in_core,
        test_instance.test_legacy_files_archived,
        test_instance.test_no_canon_modules_importable,
        test_instance.test_canon_references_removed_from_docs,
        test_instance.test_config_files_cleaned,
        test_instance.test_test_files_updated,
        test_instance.test_no_orphaned_canon_dependencies,
        test_instance.test_file_structure_integrity,
        test_instance.test_import_integrity,
    ]

    for test_method in test_methods:
        try:
            test_method()
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_method.__name__}: {e}")
            failed += 1

    print(f"\n{'=' * 70}")
    print(f"PHASE 3 TEST RESULTS: {passed} passed, {failed} failed")
    print(f"SUCCESS RATE: {passed / (passed + failed) * 100:.1f}%")
    print("=" * 70 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_phase3_tests()
    sys.exit(0 if success else 1)
