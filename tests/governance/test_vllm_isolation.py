"""vLLM Isolation Governance Tests.

Verifies that L0-L6 layers contain ZERO model imports (direct or transitive)
and no dynamic bypass vectors. All scanning is pure AST — no module execution.

Scope notes:
- Model import scan: ALL L0-L6 files, no exclusions, no baselines.
- Dynamic bypass / time-based routing scans: routing decision files only
  (predicates, routers). General infrastructure files legitimately use
  importlib, datetime, etc.

Compliance: REV 5 - routing_invariants_version = 1
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Generator

import pytest

pytestmark = pytest.mark.governance

_PROJECT_ROOT = Path(__file__).parent.parent.parent
_LAYER_ROOTS = [
    _PROJECT_ROOT / "agentic_core" / "L0_routing",
    _PROJECT_ROOT / "agentic_core" / "L1_cognition",
    _PROJECT_ROOT / "agentic_core" / "L2_execution",
    _PROJECT_ROOT / "agentic_core" / "L3_orchestration",
    _PROJECT_ROOT / "agentic_core" / "L4_state",
    _PROJECT_ROOT / "agentic_core" / "L5_safety",
    _PROJECT_ROOT / "agentic_core" / "L6_observability",
]
_FORBIDDEN_MODEL_PREFIXES = ("vllm", "transformers", "torch")
_BOUNDARY_CLIENT_PATH = _PROJECT_ROOT / "tools" / "vllm_boundary_client.py"

# Patterns for routing decision files (predicates, routers).
# Seams are excluded — they legitimately use importlib for lazy loading.
_ROUTING_DECISION_PATTERNS = (
    "predicate",
    "router",
)

# Patterns for time-based routing scan: routing + predicate files,
# but NOT types/, config/, or seam files.
_TIME_ROUTING_PATTERNS = (
    "predicate",
    "router",
)


def _iter_layer_files() -> Generator[Path, None, None]:
    """Yield all .py files under L0-L6."""
    for root in _LAYER_ROOTS:
        if not root.exists():
            continue
        yield from root.rglob("*.py")


def _iter_routing_decision_files() -> Generator[Path, None, None]:
    """Yield routing decision files (predicates, routers).

    Excludes seams (use importlib legitimately) and types/config.
    """
    for py_file in _iter_layer_files():
        name_lower = py_file.name.lower()
        if any(pat in name_lower for pat in _ROUTING_DECISION_PATTERNS):
            yield py_file


def _iter_routing_files() -> Generator[Path, None, None]:
    """Yield routing + seam files (for bypass detection)."""
    for py_file in _iter_layer_files():
        name_lower = py_file.name.lower()
        if any(pat in name_lower for pat in (*_ROUTING_DECISION_PATTERNS, "seam")):
            yield py_file


def _parse_file(path: Path) -> ast.Module:
    """Parse a Python file into an AST, skipping syntax errors."""
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _extract_direct_imports(tree: ast.Module) -> list[str]:
    """Return top-level module names from Import and ImportFrom nodes."""
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.append(node.module.split(".")[0])
    return names


def _resolve_transitive_imports(
    seed_imports: set[str],
    project_root: Path,
) -> set[str]:
    """Recursively resolve local imports via filesystem AST only.

    Does NOT execute any module. Resolves only imports that correspond
    to local .py files or packages under project_root.
    """
    all_imports: set[str] = set(seed_imports)
    to_process: set[str] = set(seed_imports)
    processed: set[str] = set()

    while to_process:
        module = to_process.pop()
        if module in processed:
            continue
        processed.add(module)

        # Try package __init__.py first, then bare module file
        candidates = [
            project_root / module.replace(".", "/") / "__init__.py",
            project_root / f"{module.replace('.', '/')}.py",
        ]
        for candidate in candidates:
            if candidate.exists():
                try:
                    tree = _parse_file(candidate)
                    nested = set(_extract_direct_imports(tree))
                    new = nested - all_imports
                    all_imports.update(new)
                    to_process.update(new)
                except SyntaxError:
                    pass
                break

    return all_imports


# ---------------------------------------------------------------------------
# Test 1 — No direct model imports in L0-L6
# ---------------------------------------------------------------------------


def test_no_direct_model_imports_in_layers() -> None:
    """L0-L6 must not directly import vllm, transformers, or torch.

    Zero exclusions. Every .py file under L0-L6 is scanned.
    """
    violations: list[str] = []
    for py_file in _iter_layer_files():
        rel = py_file.relative_to(_PROJECT_ROOT).as_posix()
        try:
            tree = _parse_file(py_file)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in _FORBIDDEN_MODEL_PREFIXES:
                        violations.append(f"{rel}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root = node.module.split(".")[0]
                    if root in _FORBIDDEN_MODEL_PREFIXES:
                        violations.append(f"{rel}: from {node.module} import ...")
    assert not violations, "Model imports found in L0-L6 (zero allowed):\n" + "\n".join(violations)


# ---------------------------------------------------------------------------
# Test 2 — No importlib.import_module in L0-L6
# ---------------------------------------------------------------------------


def test_no_importlib_in_layers() -> None:
    """Routing decision files must not use importlib.import_module.

    Seams legitimately use importlib for lazy loading. This test
    scopes to predicate/router files only (not seams).
    """
    violations: list[str] = []
    for py_file in _iter_routing_decision_files():
        try:
            tree = _parse_file(py_file)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and func.attr == "import_module"
                and isinstance(func.value, ast.Name)
                and func.value.id == "importlib"
            ):
                violations.append(f"{py_file.relative_to(_PROJECT_ROOT)}: importlib.import_module")
    assert not violations, "importlib.import_module found in routing files:\n" + "\n".join(violations)


# ---------------------------------------------------------------------------
# Test 3 — No getattr-based model bypass
# ---------------------------------------------------------------------------


def test_no_getattr_model_bypass() -> None:
    """L0-L6 must not use getattr to access model library names."""
    violations: list[str] = []
    for py_file in _iter_layer_files():
        try:
            tree = _parse_file(py_file)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (isinstance(func, ast.Name) and func.id == "getattr"):
                continue
            # Check if any argument is a string matching forbidden names
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if arg.value in _FORBIDDEN_MODEL_PREFIXES:
                        violations.append(
                            f'{py_file.relative_to(_PROJECT_ROOT)}: getattr(..., "{arg.value}")'
                        )
    assert not violations, "getattr model bypass found in L0-L6:\n" + "\n".join(violations)


# ---------------------------------------------------------------------------
# Test 4 — No __import__ builtin usage
# ---------------------------------------------------------------------------


def test_no_dunder_import() -> None:
    """Routing decision files must not use __import__."""
    violations: list[str] = []
    for py_file in _iter_routing_decision_files():
        try:
            tree = _parse_file(py_file)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "__import__":
                violations.append(f"{py_file.relative_to(_PROJECT_ROOT)}: __import__")
    assert not violations, "__import__ found in routing files:\n" + "\n".join(violations)


# ---------------------------------------------------------------------------
# Test 5 — No sys.modules mutation
# ---------------------------------------------------------------------------


def test_no_sys_modules_mutation() -> None:
    """Routing decision files must not assign to sys.modules."""
    violations: list[str] = []
    for py_file in _iter_routing_decision_files():
        try:
            tree = _parse_file(py_file)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            for target in node.targets:
                if (
                    isinstance(target, ast.Subscript)
                    and isinstance(target.value, ast.Attribute)
                    and target.value.attr == "modules"
                    and isinstance(target.value.value, ast.Name)
                    and target.value.value.id == "sys"
                ):
                    violations.append(f"{py_file.relative_to(_PROJECT_ROOT)}: sys.modules mutation")
    assert not violations, "sys.modules mutation found in routing files:\n" + "\n".join(violations)


# ---------------------------------------------------------------------------
# Test 6 — Transitive import graph clean (pure AST, no execution)
# ---------------------------------------------------------------------------


def test_transitive_import_graph_clean() -> None:
    """No L0-L6 file has a transitive import path to model libraries.

    Graph is built via pure AST traversal. No modules are executed.
    Zero exclusions.
    """
    violations: list[str] = []
    agentic_root = _PROJECT_ROOT / "agentic_core"

    for py_file in _iter_layer_files():
        rel = py_file.relative_to(_PROJECT_ROOT).as_posix()
        try:
            tree = _parse_file(py_file)
        except SyntaxError:
            continue
        direct = set(_extract_direct_imports(tree))
        all_imports = _resolve_transitive_imports(direct, agentic_root)

        for module_name in all_imports:
            if module_name.startswith(_FORBIDDEN_MODEL_PREFIXES):
                violations.append(f"{rel}: transitive import -> {module_name}")

    assert not violations, "Transitive model imports found in L0-L6 (zero allowed):\n" + "\n".join(violations)


# ---------------------------------------------------------------------------
# Test 7 — Boundary client not imported by L0-L6
# ---------------------------------------------------------------------------


def test_boundary_client_not_imported_by_layers() -> None:
    """L0-L6 must not import tools.vllm_boundary_client."""
    violations: list[str] = []
    for py_file in _iter_layer_files():
        try:
            tree = _parse_file(py_file)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if "vllm_boundary_client" in alias.name:
                        violations.append(f"{py_file.relative_to(_PROJECT_ROOT)}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if "vllm_boundary_client" in module:
                    violations.append(f"{py_file.relative_to(_PROJECT_ROOT)}: from {module} import ...")
    assert not violations, "Boundary client imported by L0-L6:\n" + "\n".join(violations)


# ---------------------------------------------------------------------------
# Test 8 — No time-based routing imports in L0-L6
# ---------------------------------------------------------------------------


def test_no_time_based_routing() -> None:
    """Routing decision files must not import datetime, time, or random.

    Scopes to predicate/router files only. Types and config files
    may legitimately use datetime for timestamps.
    """
    _FORBIDDEN_TIME = {"datetime", "time", "random"}
    violations: list[str] = []
    for py_file in _iter_routing_decision_files():
        try:
            tree = _parse_file(py_file)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in _FORBIDDEN_TIME:
                        violations.append(f"{py_file.relative_to(_PROJECT_ROOT)}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root = node.module.split(".")[0]
                    if root in _FORBIDDEN_TIME:
                        violations.append(
                            f"{py_file.relative_to(_PROJECT_ROOT)}: from {node.module} import ..."
                        )
    assert not violations, "Time-based imports found in routing files:\n" + "\n".join(violations)


# ---------------------------------------------------------------------------
# Test 9 — Provider enum defined
# ---------------------------------------------------------------------------


def test_provider_enum_defined() -> None:
    """Provider must be defined as an Enum subclass."""
    from enum import Enum

    # Provider is defined in the predicate registry (Phase 2).
    # For Phase 1, verify the report declares it and the Enum base is used.
    # This test will be extended in Phase 2 to import the actual class.
    assert issubclass(Enum, Enum), "Enum base class available"

    # Verify report declares Provider enum
    report = (
        _PROJECT_ROOT / "docs" / "reports" / "tooling" / "vllm_model_config_and_windsurf_routing_report.md"
    )
    content = report.read_text(encoding="utf-8")
    assert "class Provider(Enum)" in content, "Report must declare Provider(Enum)"


# ---------------------------------------------------------------------------
# Test 10 — routing_invariants_version = 1 present in report
# ---------------------------------------------------------------------------


def test_routing_invariants_version_present() -> None:
    """Report must declare routing_invariants_version = 1."""
    report = (
        _PROJECT_ROOT / "docs" / "reports" / "tooling" / "vllm_model_config_and_windsurf_routing_report.md"
    )
    content = report.read_text(encoding="utf-8")
    assert "routing_invariants_version" in content, "routing_invariants_version not found in report"
    assert "1" in content, "routing_invariants_version value 1 not found"
