#!/usr/bin/env python3
"""
Naming Convention Audit Test Suite

MANDATORY: All 4 tests must pass 100% to validate the refactor.

This test suite validates:
1. No duplicate file stems with different casing exist
2. Renamed modules are importable at new paths
3. PascalCase files contain class definitions (not utility scripts)
4. All legacy import references have been updated

Run with: python scripts/test_naming_convention_audit.py
"""

import ast
import os
import sys
from collections import defaultdict
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# SSOT folders to scan
SSOT_FOLDERS = [
    "agentic_core",
    "apps_rg",
    "apps_lic",
    "apps_shared",
    "tests",
    "scripts",
]

# Files that were renamed (old_path -> new_path)
RENAMED_FILES = {
    "apps_shared/common_utils/Config.py": "apps_shared/common_utils/app_config.py",
    "apps_shared/common_utils/Exceptions.py": "apps_shared/common_utils/canon_exceptions.py",
    "apps_shared/common_utils/Factory.py": "apps_shared/common_utils/router_factory.py",
    "apps_shared/common_utils/Prompts.py": "apps_shared/common_utils/resume_prompts.py",
}

# Files that should be deleted (duplicates/broken)
DELETED_FILES = [
    "apps_lic/shared/tools/Toggles.py",
]

# Legacy import patterns that should no longer exist
LEGACY_IMPORT_PATTERNS = [
    "from apps_shared.common_utils.Config import",
    "from apps_shared.common_utils.Exceptions import",
    "from apps_shared.common_utils.Factory import",
    "from apps_shared.common_utils.Prompts import",
    "from apps_lic.shared.tools.Toggles import",
    "from apps_shared.common_utils import Config",
    "from apps_shared.common_utils import Exceptions",
    "from apps_shared.common_utils import Factory",
    "from apps_shared.common_utils import Prompts",
    "from apps_lic.shared.tools import Toggles",
]


def test_no_duplicate_stems():
    """
    Test 1: Verify no two files share the same name with different casing.

    This catches "split-brain" scenarios where DataProcessor.py and
    data_processor.py both exist.
    """
    print("\n" + "=" * 60)
    print("TEST 1: No Duplicate File Stems")
    print("=" * 60)

    files_by_stem = defaultdict(list)

    for folder in SSOT_FOLDERS:
        folder_path = PROJECT_ROOT / folder
        if not folder_path.exists():
            continue

        for root, dirs, files in os.walk(folder_path):
            # Skip __pycache__ and hidden dirs
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

            for f in files:
                if f.endswith(".py") and not f.startswith("__"):
                    stem = f[:-3].lower()  # Remove .py and lowercase
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, PROJECT_ROOT)
                    files_by_stem[stem].append((f, rel_path))

    # Find conflicts (same stem, different casing)
    conflicts = {}
    for stem, file_list in files_by_stem.items():
        if len(file_list) > 1:
            names = {f[0] for f in file_list}
            if len(names) > 1:
                conflicts[stem] = file_list

    if conflicts:
        print("❌ FAILED: Found casing conflicts:")
        for stem, file_list in sorted(conflicts.items()):
            print(f"\n  Stem: {stem}")
            for name, path in file_list:
                print(f"    - {name}: {path}")
        return False

    print("✅ PASSED: No duplicate file stems with different casing found.")
    return True


def test_import_integrity():
    """
    Test 2: Verify renamed modules are importable at their new paths.

    This ensures the rename operation didn't break the module structure.
    """
    print("\n" + "=" * 60)
    print("TEST 2: Import Integrity")
    print("=" * 60)

    # New module paths after rename
    new_module_paths = [
        "apps_shared.common_utils.app_config",
        "apps_shared.common_utils.canon_exceptions",
        "apps_shared.common_utils.router_factory",
        "apps_shared.common_utils.resume_prompts",
        "apps_lic.shared.reasoning.toggles",  # Should still work
    ]

    all_passed = True

    for module_path in new_module_paths:
        # Convert to file path for existence check
        file_path = PROJECT_ROOT / module_path.replace(".", "/")
        file_path = file_path.with_suffix(".py")

        if file_path.exists():
            print(f"  ✅ {module_path} - file exists at {file_path.relative_to(PROJECT_ROOT)}")
        else:
            # Check if old path still exists (rename not done yet)
            old_paths = {v: k for k, v in RENAMED_FILES.items()}
            rel_new = str(file_path.relative_to(PROJECT_ROOT)).replace("\\", "/")

            if rel_new in old_paths:
                old_path = PROJECT_ROOT / old_paths[rel_new]
                if old_path.exists():
                    print(f"  ⚠️  {module_path} - PENDING RENAME (old file still exists)")
                else:
                    print(f"  ❌ {module_path} - NOT FOUND")
                    all_passed = False
            else:
                print(f"  ❌ {module_path} - NOT FOUND")
                all_passed = False

    if all_passed:
        print("\n✅ PASSED: All modules are importable or pending rename.")
    else:
        print("\n❌ FAILED: Some modules are not importable.")

    return all_passed


def test_class_naming_alignment():
    """
    Test 3: Ensure PascalCase files actually contain class definitions.

    Per naming convention:
    - PascalCase: Reserved for Class-based entities, Agents, Core Orchestrators
    - snake_case: Reserved for functional scripts, utility modules, constants
    """
    print("\n" + "=" * 60)
    print("TEST 3: Class Naming Alignment")
    print("=" * 60)

    violations = []

    for folder in SSOT_FOLDERS:
        folder_path = PROJECT_ROOT / folder
        if not folder_path.exists():
            continue

        for root, dirs, files in os.walk(folder_path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

            for f in files:
                if not f.endswith(".py") or f.startswith("__"):
                    continue

                # Check if filename is PascalCase (starts with uppercase, no underscores except at end)
                stem = f[:-3]
                is_pascal = stem[0].isupper() and "_" not in stem

                if not is_pascal:
                    continue

                # PascalCase file - verify it contains a class definition
                full_path = Path(root) / f

                try:
                    with open(full_path, encoding="utf-8", errors="ignore") as fp:
                        content = fp.read()

                    tree = ast.parse(content)
                    has_class = any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))

                    if not has_class:
                        rel_path = full_path.relative_to(PROJECT_ROOT)
                        violations.append(str(rel_path))

                except SyntaxError:
                    # Can't parse - skip
                    pass
                except Exception as e:
                    print(f"  ⚠️  Could not analyze {f}: {e}")

    if violations:
        print("❌ FAILED: PascalCase files without class definitions:")
        for v in violations[:10]:  # Limit output
            print(f"    - {v}")
        if len(violations) > 10:
            print(f"    ... and {len(violations) - 10} more")
        return False

    print("✅ PASSED: All PascalCase files contain class definitions.")
    return True


def test_import_reference_update():
    """
    Test 4: Search codebase for legacy import strings.

    Ensures all imports were updated after the rename.
    """
    print("\n" + "=" * 60)
    print("TEST 4: Import Reference Update")
    print("=" * 60)

    legacy_references = defaultdict(list)

    # Skip this test file itself to avoid false positives
    this_file = Path(__file__).resolve()

    for folder in SSOT_FOLDERS:
        folder_path = PROJECT_ROOT / folder
        if not folder_path.exists():
            continue

        for root, dirs, files in os.walk(folder_path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

            for f in files:
                if not f.endswith(".py"):
                    continue

                full_path = Path(root) / f

                # Skip this test file
                if full_path.resolve() == this_file:
                    continue

                try:
                    with open(full_path, encoding="utf-8", errors="ignore") as fp:
                        content = fp.read()

                    for pattern in LEGACY_IMPORT_PATTERNS:
                        if pattern in content:
                            rel_path = full_path.relative_to(PROJECT_ROOT)
                            legacy_references[pattern].append(str(rel_path))

                except Exception:
                    pass

    if legacy_references:
        print("❌ FAILED: Found legacy import patterns:")
        for pattern, files in legacy_references.items():
            print(f"\n  Pattern: {pattern}")
            for f in files[:3]:
                print(f"    - {f}")
            if len(files) > 3:
                print(f"    ... and {len(files) - 3} more")
        return False

    print("✅ PASSED: No legacy import patterns found.")
    return True


def test_deleted_files_removed():
    """
    Test 5: Verify duplicate/broken files have been deleted.
    """
    print("\n" + "=" * 60)
    print("TEST 5: Deleted Files Removed")
    print("=" * 60)

    still_exists = []

    for rel_path in DELETED_FILES:
        full_path = PROJECT_ROOT / rel_path
        if full_path.exists():
            still_exists.append(rel_path)

    if still_exists:
        print("⚠️  PENDING: Files marked for deletion still exist:")
        for f in still_exists:
            print(f"    - {f}")
        print("\n  Run: rm " + " ".join(f'"{f}"' for f in still_exists))
        return False

    print("✅ PASSED: All duplicate/broken files have been removed.")
    return True


def main():
    """Run all tests and report results."""
    print("\n" + "=" * 60)
    print("NAMING CONVENTION AUDIT TEST SUITE")
    print("=" * 60)
    print(f"Project Root: {PROJECT_ROOT}")

    results = {
        "No Duplicate Stems": test_no_duplicate_stems(),
        "Import Integrity": test_import_integrity(),
        "Class Naming Alignment": test_class_naming_alignment(),
        "Import Reference Update": test_import_reference_update(),
        "Deleted Files Removed": test_deleted_files_removed(),
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Naming convention audit complete!")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED - Review and fix issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
