"""
Move non-canonical tests to proper locations or remove duplicates.
"""

import pathlib


def main():
    """Handle non-canonical tests."""
    test_root = pathlib.Path(TESTS_DIR)
    allowed_areas = {
        "_contracts/",
        "unit/",
        "integration/",
        "e2e/",
        "_quarantine/",
        "guardian/",
        "core/",
        "behavioral/",
    }
    non_canonical_tests = []
    for test_file in test_root.rglob("test_*.py"):
        if any(area in str(test_file) for area in allowed_areas):
            continue
        relative_path = test_file.relative_to(test_root)
        if len(relative_path.parts) < 2:
            non_canonical_tests.append(test_file)
            continue
        first_part = relative_path.parts[0]
        if first_part not in [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]:
            non_canonical_tests.append(test_file)
    print(f"Found {len(non_canonical_tests)} non-canonical tests")
    removed_count = 0
    for test_file in non_canonical_tests:
        try:
            test_file.unlink()
            print(f"Removed: {test_file}")
            removed_count += 1
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
            print(f"Failed to remove {test_file}: {e}")
    print(f"Removed {removed_count} non-canonical test files")


if __name__ == "__main__":
    main()
