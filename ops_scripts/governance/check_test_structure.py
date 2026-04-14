"""
Strictly enforce the project test-folder structure without import-time side effects.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tqdm import tqdm


ALLOWED_ROOTS = {
    "unit",
    "integration",
    "e2e",
    "functional",
    "fixtures",
    "migration",
    "governance",
    "L0_routing",
}
ALLOWED_ROOT_FILES = {"conftest.py", "pytest.ini", "README.md", "__init__.py"}
CATEGORY_ALLOWED_FILES = {"__init__.py", "conftest.py"}
CATEGORY_ALLOWED_DIRS = {"__pycache__", ".pytest_cache"}


def check_mirror_depth(project_root: Path, category_path: Path, violations: list[str]) -> None:
    for child in category_path.iterdir():
        if child.is_file():
            if child.name not in CATEGORY_ALLOWED_FILES and not child.name.endswith(".pyc"):
                violations.append(
                    f"[DEPTH VIOLATION] Test file found too shallow: {child.relative_to(project_root)}"
                )
        elif child.is_dir() and child.name in CATEGORY_ALLOWED_DIRS:
            continue


def check_structure(tests_root: Path) -> list[str]:
    violations: list[str] = []

    if not tests_root.exists():
        return [f"CRITICAL: tests directory missing: {tests_root}"]

    project_root = tests_root.parent
    for item in tqdm(list(tests_root.iterdir()), desc="Checking test structure", unit="item"):
        if item.is_file():
            if item.name not in ALLOWED_ROOT_FILES:
                violations.append(f"[ROOT VIOLATION] File found in tests root: {item.name}")
            continue

        if not item.is_dir():
            continue

        if item.name not in ALLOWED_ROOTS and item.name not in CATEGORY_ALLOWED_DIRS:
            violations.append(f"[FOLDER VIOLATION] Unknown test category: tests/{item.name}")
            continue

        if item.name in {"unit", "integration"}:
            check_mirror_depth(project_root, item, violations)

    return violations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tests-root",
        type=Path,
        default=Path.cwd() / "tests",
        help="Project tests directory to validate.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tests_root = args.tests_root.resolve()

    print(f"[GOVERNANCE] Scanning {tests_root} for structural violations...")
    violations = check_structure(tests_root)
    if violations:
        print(f"[FAILED] Found {len(violations)} structural violations:")
        for violation in violations:
            print(f"  - {violation}")
        return 1

    print("[PASSED] Test structure is strictly compliant.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
