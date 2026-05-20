"""Retired shim modules, tombstones, and shadow pipeline artifacts must be absent."""
from __future__ import annotations

import importlib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]

DELETED_MODULE_PATHS: tuple[str, ...] = (
    "apps_rg.cache.r1b_uwg_gateway_shim",
    "agentic_core.runtime.entrypoints.apps_rg_integrated_pipeline",
    "agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run",
    "apps_rg.runtime.dispatch.headline_dispatch",
    "apps_rg.runtime.dispatch.executive_summary_dispatch",
    "apps_rg.runtime._offline.lane_batch",
    "apps_rg.runtime.orchestrate_full_resume",
)

DELETED_FILE_PATHS: tuple[str, ...] = (
    "apps_rg/cache/r1b_uwg_gateway_shim.py",
    "agentic_core/runtime/entrypoints/apps_rg_integrated_pipeline.py",
    "agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py",
    "tools/cursor/migrate_shadow_import_paths.py",
    "artifacts/_tmp_w2b_shim.py",
    "artifacts/_tmp_w2c_shim.py",
    "ops_scripts/ci/prove_apps_rg_e2e_runtime.py",
    "ops_scripts/apps_rg/narrative_pass.py",
)


@pytest.mark.parametrize("module_path", DELETED_MODULE_PATHS)
def test_shim_or_shadow_module_not_importable(module_path: str) -> None:
    with pytest.raises((ModuleNotFoundError, ImportError)):
        importlib.import_module(module_path)


@pytest.mark.parametrize("rel_path", DELETED_FILE_PATHS)
def test_shim_or_shadow_file_absent(rel_path: str) -> None:
    path = REPO_ROOT / rel_path
    if rel_path.endswith("/"):
        assert not path.is_dir(), rel_path
    else:
        assert not path.is_file(), rel_path


def test_r1b_core_receipt_gap_fixture_replaces_shim_fixture() -> None:
    fixtures = REPO_ROOT / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w10b_fixtures"
    assert (fixtures / "r1b_uwg_core_receipt_gap.json").is_file()
    assert not (fixtures / "shim_vs_core_gap.json").is_file()
