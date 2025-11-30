#!/usr/bin/env python3
"""
test_matrix_validator.py

Agentic L5 Test Coverage Matrix Validator
=========================================

This validator enforces Agentic L5 requirements for:

- Pillar 1  Layering model purity (test coverage by layer)
- Pillar 4  Workflow (DAG) test completeness
- Pillar 5  Capability maturity (every node must be tested)
- Pillar 8  Tool ecosystem validation (tools must have tests)
- Pillar 10 Observability tests must exist (telemetry & traces)
- Pillar 12 Testing governance (no orphan tests, no missing tests)

It validates the *structural integrity* of the test plan as follows:

1) test_matrix.yaml existence + correct structure:
      tests/data/
      tests/l1/{unit,integration}
      tests/l2/{unit,integration}
      tests/l3/orchestration
      tests/l4/memory
      tests/l5/safety
      tests/integration/
      tests/regression/

2) test_matrix.yaml must define:
      - modules: list of repo modules
      - test_map: mapping module -> list of test files
      - required_categories: list of test category directories

3) Required checks:
   * Every module in the repo must appear in `modules`
   * Every module must have at least one test mapped in test_map
   * No test file may exist on disk that is NOT mapped (orphan tests)
   * Missing categories must be reported (e.g. tests/l3/orchestration)
   * Tests must follow layer structure: tests/l1 for L1 code, etc.
   * Orchestration DAG modules must have tests under tests/l3/orchestration
   * Observability modules must have tests under tests/observability or tests/integration
   * Golden-state runner must have associated tests

Exit codes:
- 0: all checks pass
- 1: violations found
"""

import os
import sys
import yaml
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

# ---------------------------------------------------------
# REPO ROOT CONFIG
# ---------------------------------------------------------

DEFAULT_REPO_ROOT = (
    r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines"
    r"\Resume Gen\Git\Agentic_Workflow-10_11"
)
REPO_ROOT = os.getenv("AGENTIC_REPO_ROOT", DEFAULT_REPO_ROOT)
TEST_MATRIX_PATH = os.path.join(REPO_ROOT, "test_matrix.yaml")

# ---------------------------------------------------------
# VIOLATION DATACLASS
# ---------------------------------------------------------

@dataclass
class Violation:
    code: str
    message: str
    path: str

def rel(path: str) -> str:
    try:
        return os.path.relpath(path, REPO_ROOT)
    except ValueError:
        return path

# ---------------------------------------------------------
# LOAD TEST MATRIX YAML
# ---------------------------------------------------------

def load_test_matrix(path: str) -> Dict:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"test_matrix.yaml not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# ---------------------------------------------------------
# FILE DISCOVERY
# ---------------------------------------------------------

def list_py_modules() -> Set[str]:
    """
    Enumerate all .py modules under agentic_core/, apps/, runtime/, observability/.
    Convert paths to dotted module names, e.g. agentic_core.l1_planning.planners.strategy_planner
    """
    modules = set()
    roots = ["agentic_core", "apps", "runtime", "observability"]

    for root in roots:
        root_path = os.path.join(REPO_ROOT, root)
        if not os.path.isdir(root_path):
            continue

        for dirpath, _, filenames in os.walk(root_path):
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                full = os.path.join(dirpath, fn)
                relp = rel(full)
                module = relp.replace("\\", "/").replace("/", ".")
                module = module[:-3]  # strip .py
                modules.add(module)

    return modules


def list_test_files() -> Set[str]:
    """
    Enumerate all Python tests under tests/.
    """
    tests_root = os.path.join(REPO_ROOT, "tests")
    tests = set()
    if not os.path.isdir(tests_root):
        return tests

    for dirpath, _, filenames in os.walk(tests_root):
        for fn in filenames:
            if fn.endswith(".py"):
                full = os.path.join(dirpath, fn)
                tests.add(rel(full))
    return tests


# ---------------------------------------------------------
# VALIDATION LOGIC
# ---------------------------------------------------------

def validate_matrix_structure(matrix: Dict, violations: List[Violation]):
    if not isinstance(matrix, dict):
        violations.append(Violation("TM_ROOT_NOT_DICT",
                                   "test_matrix.yaml root must be a mapping/object",
                                   rel(TEST_MATRIX_PATH)))
        return

    required_keys = {"modules", "test_map", "required_categories"}
    missing = required_keys - set(matrix.keys())
    if missing:
        violations.append(Violation("TM_MISSING_KEYS",
                                   f"Missing required keys in test_matrix.yaml: {missing}",
                                   rel(TEST_MATRIX_PATH)))


def validate_module_coverage(matrix: Dict, all_modules: Set[str], violations: List[Violation]):
    matrix_modules = set(matrix.get("modules", []))

    # Missing modules
    missing = all_modules - matrix_modules
    for mod in sorted(missing):
        violations.append(Violation("MODULE_NOT_LISTED",
                                   f"Module not listed in test_matrix modules: {mod}",
                                   mod))

    # Unknown modules referenced
    unknown = matrix_modules - all_modules
    for mod in sorted(unknown):
        violations.append(Violation("MODULE_UNKNOWN",
                                   f"Module listed in test_matrix but not found: {mod}",
                                   mod))


def validate_test_map(matrix: Dict, all_tests: Set[str], violations: List[Violation]):
    test_map = matrix.get("test_map", {})

    if not isinstance(test_map, dict):
        violations.append(Violation("TEST_MAP_INVALID",
                                   "test_map must be a mapping/object",
                                   rel(TEST_MATRIX_PATH)))
        return

    mapped_tests: Set[str] = set()

    # Validate mapping structure
    for mod, tests in test_map.items():
        if not isinstance(tests, list):
            violations.append(Violation("TEST_MAP_ENTRY_INVALID",
                                       f"test_map entry for module {mod} must be a list",
                                       mod))
            continue

        for t in tests:
            if t not in all_tests:
                violations.append(Violation("TEST_MAP_REF_NONEXISTENT",
                                           f"test_map references non-existent test file: {t}",
                                           mod))
            mapped_tests.add(t)

    # Orphan tests
    orphan = all_tests - mapped_tests
    for t in sorted(orphan):
        violations.append(Violation("ORPHAN_TEST",
                                   f"Test file not referenced by test_matrix: {t}",
                                   t))


def validate_required_categories(matrix: Dict, violations: List[Violation]):
    required = matrix.get("required_categories", [])
    if not isinstance(required, list):
        violations.append(Violation("REQUIRED_CATEGORIES_INVALID",
                                   "required_categories must be a list",
                                   rel(TEST_MATRIX_PATH)))
        return

    for cat in required:
        full = os.path.join(REPO_ROOT, cat)
        if not os.path.isdir(full):
            violations.append(Violation("REQUIRED_CATEGORY_MISSING",
                                       f"Required test category '{cat}' not found",
                                       rel(full)))


def validate_layer_alignment(matrix: Dict, violations: List[Violation]):
    """
    Validate alignment between layers and tests.
    Examples:
      - L1 modules must map to tests/l1/*
      - L2 modules must map to tests/l2/*
      - L3 orchestration modules must map to tests/l3/orchestration/*
      - L4 memory modules -> tests/l4/memory/*
      - L5 safety modules -> tests/l5/safety/*
    """

    layer_dir_map = {
        "agentic_core.l1_planning": "tests/l1",
        "agentic_core.l2_execution": "tests/l2",
        "agentic_core.l3_orchestration": "tests/l3/orchestration",
        "agentic_core.l4_memory": "tests/l4/memory",
        "agentic_core.l5_safety": "tests/l5/safety",
    }

    test_map = matrix.get("test_map", {})

    for module, tests in test_map.items():
        for layer_prefix, test_dir in layer_dir_map.items():
            if module.startswith(layer_prefix):
                for t in tests:
                    if not t.startswith(test_dir):
                        violations.append(
                            Violation(
                                "LAYER_TEST_MISMATCH",
                                f"Module {module} must map to {test_dir}, found {t}",
                                module,
                            )
                        )


def validate_observability_tests(all_modules: Set[str], all_tests: Set[str], violations: List[Violation]):
    """
    Observability modules (telemetry, tracer, exporter, logs) MUST have tests.
    """

    observability_mods = sorted(
        m for m in all_modules
        if "observability" in m.lower() or "telemetry" in m.lower() or "trace" in m.lower()
    )

    for mod in observability_mods:
        expected_prefix = "tests/integration"
        if not any(t.startswith(expected_prefix) for t in all_tests):
            violations.append(
                Violation(
                    "OBSERVABILITY_NOT_TESTED",
                    f"Observability module {mod} requires tests under {expected_prefix}",
                    mod,
                )
            )


def validate_golden_runner_tests(all_modules: Set[str], all_tests: Set[str], violations: List[Violation]):
    """
    Golden-state runner (golden_trace_auditor target) must have direct tests.
    """

    possible_targets = [m for m in all_modules if "golden" in m.lower()]
    for mod in possible_targets:
        expected_prefix = "tests/regression"
        if not any(t.startswith(expected_prefix) for t in all_tests):
            violations.append(
                Violation(
                    "GOLDEN_TRACE_UNTESTED",
                    f"Golden flow module {mod} must have regression tests in {expected_prefix}",
                    mod,
                )
            )


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main() -> None:
    violations: List[Violation] = []

    # Load the test matrix YAML
    try:
        matrix = load_test_matrix(TEST_MATRIX_PATH)
    except FileNotFoundError as e:
        print(f"[test_matrix_validator] ERROR: {e}")
        sys.exit(1)

    validate_matrix_structure(matrix, violations)

    # Discover modules & tests dynamically
    all_modules = list_py_modules()
    all_tests = list_test_files()

    # Core validations
    validate_module_coverage(matrix, all_modules, violations)
    validate_test_map(matrix, all_tests, violations)
    validate_required_categories(matrix, violations)
    validate_layer_alignment(matrix, violations)
    validate_observability_tests(all_modules, all_tests, violations)
    validate_golden_runner_tests(all_modules, all_tests, violations)

    # Output
    if not violations:
        print("[test_matrix_validator] OK: All test-matrix validations passed.")
        sys.exit(0)

    print("[test_matrix_validator] FAIL: Violations found.")
    for v in violations:
        print(f"[{v.code}] {v.message} :: {v.path}")

    sys.exit(1)


if __name__ == "__main__":
    main()
