"""Hard-delete negative proofs — shadow pipelines must not exist or import."""

from __future__ import annotations

import ast
import importlib
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MAIN_PY = REPO_ROOT / "apps_lic" / "__main__.py"

_DELETED_MODULES = (
    "agentic_core.runtime.entrypoints.integrated_r4_lic_pipeline_run",
    "agentic_core.runtime.u0.apps_lic_u0_adapter",
    "apps_lic.runtime.legacy.r4_single_action",
    "apps_lic.integrations.governed_lic_run",
    "apps_lic.integrations.spine_handoff",
    "apps_lic.integrations.lic_l2_recipe_registry",
    "apps_lic.integrations.lic_l2_step_adapters",
    "apps_lic.integrations.campaign_batch_orchestrator",
    "apps_lic.reasoning.enterprise_campaign_orchestrator",
)

_DELETED_FILES = (
    "apps_lic/tools/run_workflow_lic.py",
    "apps_lic/reasoning/HOPPipelineExecutor.py",
    "apps_lic/scripts/run_charles_truist_outreach.py",
    "apps_lic/config/apps_lic_static_dag.yaml",
    "apps_lic/config/apps_lic_managed_dag.yaml",
    "agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py",
    "agentic_core/runtime/u0/apps_lic_u0_adapter.py",
)


@pytest.mark.parametrize("module_name", _DELETED_MODULES)
def test_deleted_module_not_importable(module_name: str) -> None:
    with pytest.raises((ModuleNotFoundError, ImportError)):
        importlib.import_module(module_name)


@pytest.mark.parametrize("rel_path", _DELETED_FILES)
def test_deleted_file_absent(rel_path: str) -> None:
    assert not (REPO_ROOT / rel_path).exists(), f"Shadow file still exists: {rel_path}"


def test_apps_e2e_live_flag_removed() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "apps_lic", "--apps-e2e-live"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 2
    assert "removed" in (proc.stderr + proc.stdout).lower()


def test_main_canonical_dispatch_only() -> None:
    src = MAIN_PY.read_text(encoding="utf-8")
    tree = ast.parse(src)
    forbidden_roots = {
        "governed_lic_run",
        "spine_handoff",
        "integrated_r4_lic_pipeline_run",
        "lic_l2_recipe_registry",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".")[0]
            assert root not in forbidden_roots, node.module
        elif isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                assert root not in forbidden_roots, alias.name
    assert "run_canonical_apps_lic_spine" in src
    assert "APPS_LIC_ALLOW_LEGACY_R4" not in src
    assert "_run_legacy_integrated_r4" not in src


def test_apps_rg_resolver_has_no_apps_lic() -> None:
    from agentic_core.runtime.l2_recipe_resolver import _register_builtin_recipes

    registry = _register_builtin_recipes()
    assert "apps_lic" not in registry


def test_l0_emits_canonical_managed_workflow_casing() -> None:
    from tests._apps_contract.test_ag8_apps_lic_golden_path import _make_route_contract

    route = _make_route_contract()
    assert route.execution_form == "managed_workflow"


def test_main_has_no_send_email_import() -> None:
    src = MAIN_PY.read_text(encoding="utf-8")
    assert "send_email" not in src
