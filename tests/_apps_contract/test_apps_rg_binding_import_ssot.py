"""Import SSOT: production code must not import legacy agentic_core apps_rg shims."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

FORBIDDEN_IMPORT_ROOTS: tuple[str, ...] = (
    "agentic_core.L0_routing.apps_rg_l0_binding",
    "agentic_core.L1_cognition.apps_rg_l1_binding",
    "agentic_core.runtime.c0.apps_rg_c0_binding",
    "agentic_core.prompt_governance.apps_rg_pa_binding",
    "agentic_core.runtime.exit.apps_rg_exit_binding",
    "agentic_core.runtime.entry.u0_apps_rg_binding",
)

LEGACY_SHIM_FILES: frozenset[str] = frozenset(
    {
        "agentic_core/L0_routing/apps_rg_l0_binding.py",
        "agentic_core/L1_cognition/apps_rg_l1_binding.py",
        "agentic_core/runtime/c0/apps_rg_c0_binding.py",
        "agentic_core/prompt_governance/apps_rg_pa_binding.py",
        "agentic_core/runtime/exit/apps_rg_exit_binding.py",
        "agentic_core/runtime/entry/u0_apps_rg_binding.py",
    }
)

SCAN_SKIP_PARTS: frozenset[str] = frozenset(
    {
        "tests",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        ".venv",
    }
)

SCAN_SKIP_FILE_SUFFIXES: frozenset[str] = frozenset(
    {
        "test_apps_rg_binding_import_ssot.py",
    }
)


def _imports_in_file(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
    return out


def _should_scan(path: Path) -> bool:
    rel = path.relative_to(REPO).as_posix()
    if rel in LEGACY_SHIM_FILES:
        return False
    if path.name in SCAN_SKIP_FILE_SUFFIXES:
        return False
    if any(part in SCAN_SKIP_PARTS for part in path.parts):
        return False
    if rel.startswith("artifacts/archives/"):
        return False
    return True


def test_production_apps_rg_tree_has_no_legacy_shim_imports() -> None:
    violations: list[str] = []
    for path in (REPO / "apps_rg").rglob("*.py"):
        if any(part in SCAN_SKIP_PARTS for part in path.parts):
            continue
        rel = path.relative_to(REPO).as_posix()
        imports = _imports_in_file(path)
        for forbidden in FORBIDDEN_IMPORT_ROOTS:
            if forbidden in imports:
                violations.append(f"{rel}: imports {forbidden}")
    assert not violations, "Legacy shim imports in apps_rg production tree:\n" + "\n".join(
        sorted(violations)
    )


def test_ag2_dispatch_imports_canonical_bindings() -> None:
    src = (REPO / "agentic_core/runtime/entry/apps_rg_dispatch.py").read_text(encoding="utf-8")
    assert "apps_rg.runtime.bindings.c0_binding" in src
    assert "apps_rg.runtime.bindings.pa_binding" in src
    assert "agentic_core.runtime.c0.apps_rg_c0_binding" not in src
    assert "agentic_core.prompt_governance.apps_rg_pa_binding" not in src


def test_repo_has_no_legacy_shim_imports_outside_deleted_shims() -> None:
    """After burndown, no Python module may import agentic_core apps_rg binding shims."""
    violations: list[str] = []
    for path in REPO.rglob("*.py"):
        if not _should_scan(path):
            continue
        rel = path.relative_to(REPO).as_posix()
        imports = _imports_in_file(path)
        for forbidden in FORBIDDEN_IMPORT_ROOTS:
            if forbidden in imports:
                violations.append(f"{rel}: imports {forbidden}")
    assert not violations, "Legacy shim imports remain:\n" + "\n".join(sorted(violations))


def test_legacy_shim_files_removed_from_agentic_core() -> None:
    present = sorted(p for p in LEGACY_SHIM_FILES if (REPO / p).is_file())
    assert not present, f"Delete legacy shims still on disk: {present}"
