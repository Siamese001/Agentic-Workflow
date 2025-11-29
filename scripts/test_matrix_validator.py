# test_matrix_validator.py
# Ensures module <-> test relationships from test_matrix.yaml are strict & symmetrical.

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
        print(f"Missing {TEST_MATRIX_PATH}")
        sys.exit(1)

    with open(TEST_MATRIX_PATH, "r", encoding="utf-8") as f:
        matrix = yaml.safe_load(f)

    errors = []

    all_modules = set(matrix.keys())
    all_tests = set()
    for mod, tests in matrix.items():
        for t in tests:
            all_tests.add(t)

    repo_files = walk_py_files(REPO_ROOT)

    # Check modules exist
    for mod in all_modules:
        if mod not in repo_files:
            errors.append(f"Module in matrix missing from repo: {mod}")

    # Check tests exist
    for t in all_tests:
        if t not in repo_files:
            errors.append(f"Test in matrix missing from repo: {t}")

    # Check for orphan tests
    repo_test_files = [f for f in repo_files if f.startswith("tests/")]
    orphan_tests = set(repo_test_files) - all_tests
    for ot in orphan_tests:
        errors.append(f"Orphan test not mapped: {ot}")

    # Check untested modules
    untested = [m for m in all_modules if len(matrix.get(m, [])) == 0]
    for ut in untested:
        errors.append(f"Module lacks tests: {ut}")

    if errors:
        print("\n=== TEST MATRIX VALIDATION FAILED ===")
        for e in errors:
            print(e)
        sys.exit(2)

    print("Test matrix validation PASSED.")
    sys.exit(0)

if __name__ == "__main__":
    main()
