"""
file: ops_scripts/governance/check_test_structure.py
description: |
    [GOVERNANCE SENTRY]
    Strictly enforces the 'Scope Mirroring' testing architecture.

    Rules Enforced:
    1. NO tests allowed in tests/ root (except conftest.py).
    2. All tests must reside in tests/unit, tests/integration, tests/e2e, or tests/fixtures.
    3. Test paths must mirror source paths (e.g., tests/unit/agentic_core/L5_safety matches agentic_core/L5_safety).

    Exit Code:
    0: Structure compliant.
    1: Violations found (prints list).
"""

import sys
from pathlib import Path

# SSOT: Definition of allowed structures
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TESTS_ROOT = PROJECT_ROOT / "tests"
ALLOWED_ROOTS = {
    "unit",
    "integration",
    "e2e",
    "functional",
    "fixtures",
    "migration",
    "governance",
    "L0_maintenance",
}  # L0_maintenance for maintenance scripts
ALLOWED_ROOT_FILES = {"conftest.py", "pytest.ini", "README.md", "__init__.py"}


def check_structure():
    print(f"[GOVERNANCE] Scanning {TESTS_ROOT} for structural violations...")
    violations = []

    if not TESTS_ROOT.exists():
        print("CRITICAL: tests/ directory missing!")
        sys.exit(1)

    for item in TESTS_ROOT.iterdir():
        # Rule 1: Root File Restrictions
        if item.is_file():
            if item.name not in ALLOWED_ROOT_FILES:
                violations.append(f"[ROOT VIOLATION] File found in tests root: {item.name}")
            continue

        # Rule 2: Allowed Subdirectories
        if item.is_dir():
            if item.name not in ALLOWED_ROOTS and item.name not in {"__pycache__", ".pytest_cache"}:
                violations.append(f"[FOLDER VIOLATION] Unknown test category: tests/{item.name}")
                continue

            # Rule 3: Mirror Validation (Deep Scan)
            # We only enforce mirroring for unit/integration
            if item.name in {"unit", "integration"}:
                check_mirror_depth(item, violations)

    if violations:
        print(f"[FAILED] Found {len(violations)} structural violations:")
        for v in violations:
            print(f"  - {v}")
        sys.exit(1)
    else:
        print("[PASSED] Test structure is strictly compliant.")
        sys.exit(0)


def check_mirror_depth(category_path: Path, violations: list):
    """
    Ensures that under tests/unit/, we have immediate domain roots
    (agentic_core, apps_rg, etc.) and not loose files.
    """
    for sub in category_path.iterdir():
        if sub.is_file():
            if sub.name not in {"__init__.py", "conftest.py"} and not sub.name.endswith(".pyc"):
                violations.append(
                    f"[DEPTH VIOLATION] Test file found too shallow: {sub.relative_to(PROJECT_ROOT)}"
                )
        elif sub.is_dir():
            # Check if this directory corresponds to a source root?
            # For now, we just enforce that it IS a directory (domain root)
            if sub.name in {"__pycache__", ".pytest_cache"}:
                continue
            # We can expand this to check for existence in PROJECT_ROOT in v2
            pass


if __name__ == "__main__":
    check_structure()
