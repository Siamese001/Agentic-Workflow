from pathlib import Path

#!/usr/bin/env python3
"""
SSOT Compliance Verification for Archive Paths

Verifies that:
1. ArchivalGatekeeper imports ARCHIVES_DIR from structure_blueprint
2. Archive paths resolve to [project_root]/archives/... (not .archive)
3. archives/ is in SOVEREIGN_EXCLUDED_FOLDERS
4. No hardcoded archive paths remain

USAGE:
    python scripts/maintenance/verify_ssot_compliance.py
"""

import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_ssot_import():
    """Test 1: Verify ArchivalGatekeeper can import ARCHIVES_DIR."""
    print("\n[TEST 1] SSOT Import Test")
    try:
        # Verify ARCHIVES_DIR value
        assert ARCHIVES_DIR == "archives", f"Expected 'archives', got '{ARCHIVES_DIR}'"

        # Verify ArchivalGatekeeper uses correct name
        assert ArchivalGatekeeper.ARCHIVE_ROOT_NAME == "archives", (
            f"Expected 'archives', got '{ArchivalGatekeeper.ARCHIVE_ROOT_NAME}'"
        )

        print("  ✅ PASS: ARCHIVES_DIR imported successfully")
        print(f"     ARCHIVES_DIR = '{ARCHIVES_DIR}'")
        print(
            f"     ArchivalGatekeeper.ARCHIVE_ROOT_NAME = '{ArchivalGatekeeper.ARCHIVE_ROOT_NAME}'"
        )
        return True
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return False


def test_path_resolution():
    """Test 2: Verify archive_root resolves to archives/ not .archive."""
    print("\n[TEST 2] Path Resolution Test")
    try:
        project_root = Path.cwd()
        ArchivalGatekeeper.reset_instance()
        gatekeeper = ArchivalGatekeeper.get_instance(project_root)

        # Verify path contains 'archives' not '.archive'
        archive_path = str(gatekeeper.archive_root)

        assert "archives" in archive_path, f"'archives' not in path: {archive_path}"
        assert ".archive" not in archive_path, f"'.archive' found in path: {archive_path}"
        assert "gatekeeper" in archive_path, f"'gatekeeper' not in path: {archive_path}"

        expected = project_root / "archives" / "gatekeeper"
        assert gatekeeper.archive_root == expected, (
            f"Expected {expected}, got {gatekeeper.archive_root}"
        )

        print("  ✅ PASS: Archive root resolves correctly")
        print(f"     archive_root = {gatekeeper.archive_root}")

        ArchivalGatekeeper.reset_instance()
        return True
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return False


def test_exclusion_logic():
    """Test 3: Verify archives/ is in SOVEREIGN_EXCLUDED_FOLDERS."""
    print("\n[TEST 3] Exclusion Logic Test")
    try:
        assert "archives" in SOVEREIGN_EXCLUDED_FOLDERS, (
            "'archives' not in SOVEREIGN_EXCLUDED_FOLDERS"
        )

        print("  ✅ PASS: 'archives' is in SOVEREIGN_EXCLUDED_FOLDERS")
        print(f"     SOVEREIGN_EXCLUDED_FOLDERS = {sorted(SOVEREIGN_EXCLUDED_FOLDERS)}")
        return True
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return False


def test_no_hardcoded_paths():
    """Test 4: Verify no hardcoded .archive paths remain."""
    print("\n[TEST 4] Hardcoded Path Check")
    try:
        import inspect

        # Get source code
        source = inspect.getsource(ArchivalGatekeeper)

        # Check for hardcoded .archive
        if '".archive"' in source or "'.archive'" in source:
            print("  ❌ FAIL: Found hardcoded '.archive' in ArchivalGatekeeper")
            return False

        print("  ✅ PASS: No hardcoded '.archive' paths found")
        return True
    except Exception as e:
        print(f"  ❌ FAIL: {e}")
        return False


def main():
    print("=" * 70)
    print("SSOT Compliance Verification")
    print("=" * 70)

    results = []
    results.append(("SSOT Import", test_ssot_import()))
    results.append(("Path Resolution", test_path_resolution()))
    results.append(("Exclusion Logic", test_exclusion_logic()))
    results.append(("No Hardcoded Paths", test_no_hardcoded_paths()))

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ ALL TESTS PASSED - SSOT COMPLIANT")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED - NOT SSOT COMPLIANT")
        return 1


if __name__ == "__main__":
    sys.exit(main())
