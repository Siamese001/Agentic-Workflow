#!/usr/bin/env python3
"""
Wave 2b: Fix collection errors by deferring import failures to test time.

The module-scoped fixture `mod()` causes collection errors because
importlib.import_module() runs during collection. We need to defer
the failure to test execution time so it shows as a FAILED test,
not a collection error that blocks the entire file.

Strategy: wrap the fixture in try/except and store the error,
then fail in each test that uses the fixture.
"""

from pathlib import Path

FIXTURE_OLD = '''@pytest.fixture(scope="module")
def mod():
    """Import the module under test. Fails hard if first-party import broken."""
    return importlib.import_module(MODULE_PATH)'''

FIXTURE_NEW = '''@pytest.fixture(scope="module")
def mod():
    """Import the module under test. Fails hard if first-party import broken."""
    try:
        return importlib.import_module(MODULE_PATH)
    except Exception as exc:
        pytest.fail(
            f"FIRST-PARTY IMPORT FAILED for {MODULE_PATH}: {exc}",
            pytrace=False,
        )'''

def main():
    tests_dir = Path("tests")
    fixed = 0
    already_ok = 0

    for p in sorted(tests_dir.rglob("test_*.py")):
        try:
            content = p.read_text("utf-8")
        except Exception:
            continue

        if FIXTURE_OLD not in content:
            continue

        if "pytest.fail(" in content and "FIRST-PARTY IMPORT FAILED" in content:
            already_ok += 1
            continue

        new_content = content.replace(FIXTURE_OLD, FIXTURE_NEW)
        if new_content != content:
            p.write_text(new_content, "utf-8")
            fixed += 1

    print(f"Fixed: {fixed}")
    print(f"Already OK: {already_ok}")


if __name__ == "__main__":
    main()
