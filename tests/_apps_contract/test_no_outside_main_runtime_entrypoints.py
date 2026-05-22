"""Shadow dotted paths must be deleted; internal helpers must not run as ``python -m``."""
from __future__ import annotations

import ast
import importlib
import subprocess
import sys
from pathlib import Path

import pytest

from apps_rg.runtime.outside_main_entry_policy import (
    ALLOWED_OUTSIDE_MAIN_MODULE_CLI,
    DELETED_RUNTIME_MODULE_CLI,
    is_allowed_outside_main_module_cli,
    is_deleted_runtime_module_cli,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

INTERNAL_MODULES = (
    "apps_rg.runtime.internal.lane_batch",
    "apps_rg.runtime.internal.resume_package_disposition",
    "apps_rg.runtime.internal.generated_lane_rollup",
    "apps_rg.runtime.internal.final_resume_assembler",
    "apps_rg.runtime.internal.locked_copy_builder",
)

LANE_API_MODULES = (
    "apps_rg.runtime.sections.executive_summary_lane",
    "apps_rg.runtime.sections.competencies_lane_runtime",
    "apps_rg.runtime.sections.unify_bullets_lane",
    "apps_rg.runtime.sections.unify_narrative_lane",
    "apps_rg.runtime.sections.ibm_bullets_lane",
    "apps_rg.runtime.sections.ibm_narrative_lane_runtime",
)


def _module_py_path(module_name: str) -> Path:
    return REPO_ROOT / (module_name.replace(".", "/") + ".py")


def _has_main_guard(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            left = node.test.left
            if (
                isinstance(left, ast.Name)
                and left.id == "__name__"
                and len(node.test.ops) == 1
                and isinstance(node.test.ops[0], ast.Eq)
                and len(node.test.comparators) == 1
                and isinstance(node.test.comparators[0], ast.Constant)
                and node.test.comparators[0].value == "__main__"
            ):
                return True
    return False


@pytest.mark.parametrize("module_name", sorted(DELETED_RUNTIME_MODULE_CLI))
def test_deleted_runtime_module_cli_missing(module_name: str) -> None:
    assert is_deleted_runtime_module_cli(module_name)
    assert not _module_py_path(module_name).is_file(), module_name
    proc = subprocess.run(
        [sys.executable, "-m", module_name],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode != 0, (module_name, proc.stdout, proc.stderr)
    blob = (proc.stderr or "") + (proc.stdout or "")
    assert "No module named" in blob or "cannot find" in blob.lower()


@pytest.mark.parametrize("module_name", sorted(INTERNAL_MODULES + LANE_API_MODULES))
def test_internal_modules_reject_python_m(module_name: str) -> None:
    path = _module_py_path(module_name)
    assert path.is_file(), module_name
    assert _has_main_guard(path), f"{module_name} missing __main__ ImportError guard"
    proc = subprocess.run(
        [sys.executable, "-m", module_name],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode != 0, (module_name, proc.stdout, proc.stderr)
    assert "not an operator CLI entrypoint" in (proc.stderr or "") + (proc.stdout or "")


@pytest.mark.parametrize("module_name", sorted(INTERNAL_MODULES))
def test_internal_modules_have_no_main_function(module_name: str) -> None:
    path = _module_py_path(module_name)
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            pytest.fail(f"{module_name} still defines main() at line {node.lineno}")


@pytest.mark.parametrize("module_name", sorted(DELETED_RUNTIME_MODULE_CLI))
def test_deleted_modules_import_raises(module_name: str) -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(module_name)


@pytest.mark.parametrize("module_name", sorted(ALLOWED_OUTSIDE_MAIN_MODULE_CLI))
def test_allowed_modules_are_not_deleted(module_name: str) -> None:
    assert is_allowed_outside_main_module_cli(module_name)
    assert not is_deleted_runtime_module_cli(module_name)
