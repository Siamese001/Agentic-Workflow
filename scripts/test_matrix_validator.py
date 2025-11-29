#!/usr/bin/env python3
"""
test_matrix_validator.py
Ensures strict module <-> test mappings from test_matrix.yaml.

Covers:
- Every module in matrix exists
- Every test in matrix exists
- All tests in tests/ are mapped (no orphans)
- Every module has >=1 test mapping
"""

import os
import sys
import yaml

REPO_ROOT = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11"
TEST_MATRIX_PATH = os.path.join(REPO_ROOT, "test_matrix.yaml")


def walk_py_files(root):
    files = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.endswith(".py"):
                rel = os.path.relpath(os.path.join(dirpath, f), root).replace("\\", "/")
                files.append(rel)
    return files


def main():
    if not os.path.exists(TEST_MATRIX_PATH):
        print(f"[TEST-MATRIX] Missing {TEST_MATRIX_PATH}")
        sys.exit(1)

    with open(TEST_MATRIX_PATH, "r", encoding="utf-8") as f:
        matrix = yaml.safe_load(f)

    errors = []

    all_modules = set(matrix.keys())
    all_mapped_tests = {t for tests in matrix.values() for t in tests}

    repo_files = walk_py_files(REPO_ROOT)
    repo_tests = [f for f in repo_files if f.startswith("tests/") and f.startswith("tests/")]

    # Modules exist
    for mod in all_modules:
        if mod not in repo_files:
            errors.append(f"[TEST-MATRIX] Module listed but missing in repo: {mod}")

    # Tests exist
    for t in all_mapped_tests:
        if t not in repo_files:
            errors.append(f"[TEST-MATRIX] Test listed but missing in repo: {t}")

    # Orphan tests
    orphan_tests = set(repo_tests) - all_mapped_tests
    for o in sorted(orphan_tests):
        errors.append(f"[TEST-MATRIX] Orphan test not mapped in matrix: {o}")

    # Untested modules
    for mod in all_modules:
        if len(matrix.get(mod, [])) == 0:
            errors.append(f"[TEST-MATRIX] Module has no tests mapped: {mod}")

    if errors:
        print("\n=== TEST MATRIX VALIDATION FAILED ===")
        for e in errors:
            print(e)
        sys.exit(2)

    print("Test matrix validation PASSED.")
    sys.exit(0)


if __name__ == "__main__":
    main()
