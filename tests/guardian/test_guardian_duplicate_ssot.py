"""
Guardian: Duplicate SSOT Anti-Pattern Tests.

Detects multiple files that each independently define the same structural
constant that should have exactly one canonical owner.

Covered violations:
  1. Multiple Python files defining the same path-constant string (e.g. two
     files each containing  DOCS_REPORTS_PLANS = "docs/reports/plans").
  2. Multiple class definitions for singleton gate classes (e.g. two files
     each defining a class named 'UniversalWriteGateway').
  3. Multiple module-level assignments of the same global name to the same
     literal value, inside the scan roots.

These are caught via AST scan — no regex / grep.

§1 windsurfrules compliance:
- §1.1  Every changed logic has deterministic test coverage
- §1.3  Deterministic: filesystem is read canonically (sorted paths)
- §1.4  No mocks for the filesystem seam; real tmp_path fixtures used
- §1.5  Edge cases: empty repo, single owner (no dup), two owners (dup)
- §1.7  Determinism: same repo layout → same violation list (sorted)
- §1.8  Fail-closed: test asserts zero violations; any dup is a hard fail
- §1.9  Matrix: constant-type × owner-count
- §1.11 Regression: near-miss (same name, different value; different name,
        same value)

ROBUSTNESS_MATRIX:
  Surface                          | success | edge | failure | determinism
  ---------------------------------|---------|------|---------|------------
  single-owner constant            |   ✅   |  ✅  |   N/A  |     ✅
  two-owner constant (dup SSOT)    |   N/A  |  ✅  |   ✅   |     ✅
  three-owner constant             |   N/A  |  ✅  |   ✅   |     ✅
  singleton class duplicate        |   N/A  |  ✅  |   ✅   |     ✅
  same name, different value       |   ✅   |  ✅  |   N/A  |     ✅
  different name, same value       |   ✅   |  ✅  |   N/A  |     ✅
  empty scan root                  |   ✅   |  ✅  |   N/A  |     ✅

DEFECT_MODEL:
  D1 - Two files both define DOCS_REPORTS_PLANS with identical string value
  D2 - Two files each define class UniversalWriteGateway
  D3 - Same-name different-value assignments treated as duplicates (false +)
  D4 - scan is non-deterministic (different violation order per run)
  D5 - Allowlisted re-export (__init__.py) incorrectly triggers violation
"""

from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AGENTIC_CORE_DIR,
    SYSTEM_LEARNING_DIR,
)

pytestmark = pytest.mark.guardian

# ---------------------------------------------------------------------------
# Scanner implementation (pure, no mocks required)
# ---------------------------------------------------------------------------

_SINGLETON_CLASS_NAMES = frozenset(
    [
        "UniversalWriteGateway",
        "SovereignLLMGateway",
        "OscillationDetector",
    ]
)

_EXCLUDED_FILENAMES = frozenset(["__init__.py", "conftest.py"])


def _collect_py_files(root: Path) -> list[Path]:
    """Return sorted .py files under root, excluding __init__.py."""
    return sorted(p for p in root.rglob("*.py") if p.name not in _EXCLUDED_FILENAMES)


def _extract_module_level_string_assignments(
    path: Path,
) -> dict[str, str]:
    """
    Return {name: value} for module-level assignments where the value is a
    string literal, e.g.  DOCS_REPORTS_PLANS = "docs/reports/plans"
    """
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return {}

    result: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        result[target.id] = node.value.value
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.value:
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    result[node.target.id] = node.value.value
    return result


def _extract_class_names(path: Path) -> list[str]:
    """Return names of all top-level class definitions in *path*."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []
    return [node.name for node in tree.body if isinstance(node, ast.ClassDef)]


def find_duplicate_string_constants(root: Path) -> list[str]:
    """
    Scan *root* for module-level string-constant assignments with the same
    name AND same value defined in more than one file.

    Returns a sorted list of human-readable violation strings.
    """
    # name → {value: [paths]}
    registry: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

    for py_file in _collect_py_files(root):
        assignments = _extract_module_level_string_assignments(py_file)
        rel = py_file.relative_to(root).as_posix()
        for name, value in assignments.items():
            registry[name][value].append(rel)

    violations: list[str] = []
    for name, value_map in sorted(registry.items()):
        for value, paths in sorted(value_map.items()):
            if len(paths) > 1:
                paths_str = ", ".join(sorted(paths))
                violations.append(f"Duplicate SSOT constant '{name}' = {value!r} in: {paths_str}")
    return violations


def find_duplicate_singleton_classes(root: Path) -> list[str]:
    """
    Scan *root* for singleton gate class names defined in more than one file.

    Returns a sorted list of human-readable violation strings.
    """
    class_registry: dict[str, list[str]] = defaultdict(list)

    for py_file in _collect_py_files(root):
        rel = py_file.relative_to(root).as_posix()
        for cls_name in _extract_class_names(py_file):
            if cls_name in _SINGLETON_CLASS_NAMES:
                class_registry[cls_name].append(rel)

    violations: list[str] = []
    for cls_name, paths in sorted(class_registry.items()):
        if len(paths) > 1:
            paths_str = ", ".join(sorted(paths))
            violations.append(f"Duplicate singleton class '{cls_name}' defined in: {paths_str}")
    return violations


# ---------------------------------------------------------------------------
# Real-repo structural invariants (§1.8 fail-closed)
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
_SSOT_SCAN_ROOTS = [
    REPO_ROOT / AGENTIC_CORE_DIR,
    REPO_ROOT / SYSTEM_LEARNING_DIR,
]


class TestRealRepoSingletonInvariant:
    """Gateway singleton classes must be defined in exactly one file."""

    @pytest.mark.parametrize(
        "cls_name,expected_stem",
        [
            ("UniversalWriteGateway", "UniversalWriteGateway"),
            ("SovereignLLMGateway", "SovereignLLMGateway"),
        ],
    )
    def test_singleton_class_has_exactly_one_owner(self, cls_name, expected_stem):
        owners: list[str] = []
        for scan_root in _SSOT_SCAN_ROOTS:
            if not scan_root.exists():
                continue
            for py_file in scan_root.rglob("*.py"):
                if py_file.name in _EXCLUDED_FILENAMES:
                    continue
                if cls_name in _extract_class_names(py_file):
                    owners.append(py_file.relative_to(REPO_ROOT).as_posix())

        assert len(owners) == 1, (
            f"Singleton class '{cls_name}' must be defined in exactly one file. "
            f"Found in {len(owners)}: {owners}"
        )


# ---------------------------------------------------------------------------
# Synthetic fixture tests (deterministic, no real-repo dependency)
# ---------------------------------------------------------------------------


class TestDuplicateStringConstantDetection:
    def test_no_duplicates_in_single_file(self, tmp_path):
        (tmp_path / "a.py").write_text('DOCS_REPORTS_PLANS = "docs/reports/plans"\n', encoding="utf-8")
        viols = find_duplicate_string_constants(tmp_path)
        assert viols == []

    def test_two_files_same_name_same_value_detected(self, tmp_path):
        for name in ("a.py", "b.py"):
            (tmp_path / name).write_text('CANONICAL_PATH = "agentic_core/L5_safety"\n', encoding="utf-8")
        viols = find_duplicate_string_constants(tmp_path)
        assert len(viols) == 1
        assert "CANONICAL_PATH" in viols[0]
        assert "a.py" in viols[0]
        assert "b.py" in viols[0]

    def test_three_files_same_constant_detected(self, tmp_path):
        for name in ("a.py", "b.py", "c.py"):
            (tmp_path / name).write_text('DOCS_ROOT = "docs"\n', encoding="utf-8")
        viols = find_duplicate_string_constants(tmp_path)
        assert len(viols) == 1
        assert "DOCS_ROOT" in viols[0]

    def test_same_name_different_value_not_duplicate(self, tmp_path):
        """D3 regression: same constant name with different values is NOT a dup SSOT."""
        (tmp_path / "a.py").write_text('ENV = "prod"\n', encoding="utf-8")
        (tmp_path / "b.py").write_text('ENV = "dev"\n', encoding="utf-8")
        viols = find_duplicate_string_constants(tmp_path)
        # Different values → not the same SSOT → no violation
        assert viols == []

    def test_different_name_same_value_not_duplicate(self, tmp_path):
        (tmp_path / "a.py").write_text('ROOT_A = "docs/reports"\n', encoding="utf-8")
        (tmp_path / "b.py").write_text('ROOT_B = "docs/reports"\n', encoding="utf-8")
        viols = find_duplicate_string_constants(tmp_path)
        # Different names → different constants → no violation
        assert viols == []

    def test_init_py_excluded_from_scan(self, tmp_path):
        (tmp_path / "__init__.py").write_text('CANONICAL_PATH = "some/path"\n', encoding="utf-8")
        (tmp_path / "real.py").write_text('CANONICAL_PATH = "some/path"\n', encoding="utf-8")
        viols = find_duplicate_string_constants(tmp_path)
        # __init__.py excluded → only 1 owner → no violation
        assert viols == []

    def test_empty_root_no_violations(self, tmp_path):
        assert find_duplicate_string_constants(tmp_path) == []

    def test_syntax_error_file_skipped_gracefully(self, tmp_path):
        (tmp_path / "broken.py").write_text("def f(\n", encoding="utf-8")
        (tmp_path / "good.py").write_text('K = "v"\n', encoding="utf-8")
        # Should not raise; broken file is skipped
        viols = find_duplicate_string_constants(tmp_path)
        assert viols == []


class TestDuplicateSingletonClassDetection:
    def test_single_owner_class_no_violation(self, tmp_path):
        (tmp_path / "gateway.py").write_text("class UniversalWriteGateway:\n    pass\n", encoding="utf-8")
        viols = find_duplicate_singleton_classes(tmp_path)
        assert viols == []

    def test_two_files_same_singleton_class_detected(self, tmp_path):
        for name in ("a.py", "b.py"):
            (tmp_path / name).write_text("class UniversalWriteGateway:\n    pass\n", encoding="utf-8")
        viols = find_duplicate_singleton_classes(tmp_path)
        assert len(viols) == 1
        assert "UniversalWriteGateway" in viols[0]

    def test_non_singleton_class_not_flagged(self, tmp_path):
        for name in ("a.py", "b.py"):
            (tmp_path / name).write_text("class MyHelper:\n    pass\n", encoding="utf-8")
        viols = find_duplicate_singleton_classes(tmp_path)
        assert viols == []

    def test_init_py_excluded(self, tmp_path):
        (tmp_path / "__init__.py").write_text("class UniversalWriteGateway:\n    pass\n", encoding="utf-8")
        (tmp_path / "gateway.py").write_text("class UniversalWriteGateway:\n    pass\n", encoding="utf-8")
        viols = find_duplicate_singleton_classes(tmp_path)
        assert viols == []


# ---------------------------------------------------------------------------
# Determinism (§1.7)
# ---------------------------------------------------------------------------


class TestScanDeterminism:
    def test_duplicate_constant_violation_list_is_sorted(self, tmp_path):
        for name in ("z.py", "a.py", "m.py"):
            (tmp_path / name).write_text('K = "v"\n', encoding="utf-8")
        viols = find_duplicate_string_constants(tmp_path)
        assert viols == sorted(viols)

    def test_same_repo_identical_results_across_calls(self, tmp_path):
        for name in ("x.py", "y.py"):
            (tmp_path / name).write_text('SSOT_ROOT = "docs"\n', encoding="utf-8")
        a = find_duplicate_string_constants(tmp_path)
        b = find_duplicate_string_constants(tmp_path)
        assert a == b


# ---------------------------------------------------------------------------
# Matrix: constant-type × owner-count (§1.9)
# ---------------------------------------------------------------------------


class TestOwnerCountMatrix:
    @pytest.mark.parametrize("owner_count", [1, 2, 3, 5])
    def test_string_constant_owner_count(self, owner_count, tmp_path):
        for i in range(owner_count):
            (tmp_path / f"owner_{i}.py").write_text('CANONICAL = "docs/reports/plans"\n', encoding="utf-8")
        viols = find_duplicate_string_constants(tmp_path)
        if owner_count == 1:
            assert viols == []
        else:
            assert len(viols) == 1

    @pytest.mark.parametrize("owner_count", [1, 2, 3])
    def test_singleton_class_owner_count(self, owner_count, tmp_path):
        for i in range(owner_count):
            (tmp_path / f"owner_{i}.py").write_text(
                "class UniversalWriteGateway:\n    pass\n", encoding="utf-8"
            )
        viols = find_duplicate_singleton_classes(tmp_path)
        if owner_count == 1:
            assert viols == []
        else:
            assert len(viols) == 1
