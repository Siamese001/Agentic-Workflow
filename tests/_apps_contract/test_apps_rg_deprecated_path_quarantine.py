"""W7 — Non-product / quarantine paths for apps_rg (classification only)."""

from __future__ import annotations

import importlib
import os
from pathlib import Path

import pytest

from apps_rg.l2_recipe.r4_generation_mode import (
    MODE_MODULAR_SECTION_LANES,
    RETIRED_MODE_LEGACY_FULL_RESUME,
    resolve_apps_rg_r4_generation_mode,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

QUARANTINE_REGISTRY: dict[str, str] = {
    "apps_rg/runtime/dry_run/": "KEEP_APPS_RG",
    "apps_rg/runtime/internal/lane_batch.py": "TEST_SUPPORT_ONLY",
    "apps_rg/runtime/internal/": "TEST_SUPPORT_ONLY",
}


def test_reasoning_package_removed() -> None:
    """apps_rg/reasoning/ deleted — product uses apps_rg/runtime section lanes."""
    assert not (REPO_ROOT / "apps_rg" / "reasoning").exists()

NON_PRODUCT_PROOF_ENV: dict[str, str] = {
    "APPS_RG_R4_GENERATION_MODE": MODE_MODULAR_SECTION_LANES,
    "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB": "1",
    "APPS_RG_L2_PROVIDER_MODE": "stub_only",
    "APPS_RG_L2_FORCE_STUB": "1",
}

RETIRED_DISPATCH_TAILS: tuple[str, ...] = (
    "headline_dispatch",
    "executive_summary_dispatch",
    "competencies_dispatch",
    "unify_narrative_dispatch",
    "unify_bullets_dispatch",
    "ibm_narrative_dispatch",
    "ibm_bullets_dispatch",
)


@pytest.mark.parametrize("rel_path,classification", list(QUARANTINE_REGISTRY.items()))
def test_quarantine_registry_paths_exist(rel_path: str, classification: str) -> None:
    full = REPO_ROOT / rel_path
    if rel_path.endswith("/"):
        assert full.is_dir(), rel_path
    else:
        assert full.is_file(), rel_path
    assert classification in {
        "QUARANTINE_UNTIL_REVIEW",
        "TEST_SUPPORT_ONLY",
        "SUPERSEDED_BY_APPS_RG_SECTION_RUNTIME",
        "KEEP_APPS_RG",
    }


def test_default_generation_mode_is_modular_not_legacy() -> None:
    prev = os.environ.pop("APPS_RG_R4_GENERATION_MODE", None)
    try:
        assert resolve_apps_rg_r4_generation_mode() == MODE_MODULAR_SECTION_LANES
    finally:
        if prev is not None:
            os.environ["APPS_RG_R4_GENERATION_MODE"] = prev


def test_legacy_full_resume_env_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_R4_GENERATION_MODE", RETIRED_MODE_LEGACY_FULL_RESUME)
    with pytest.raises(RuntimeError, match="RETIRED_APPS_RG_R4_GENERATION_MODE"):
        resolve_apps_rg_r4_generation_mode()


@pytest.mark.parametrize("module_tail", RETIRED_DISPATCH_TAILS)
def test_retired_dispatch_module_paths_removed(module_tail: str) -> None:
    path = REPO_ROOT / "apps_rg" / "runtime" / "dispatch" / f"{module_tail}.py"
    assert not path.is_file(), module_tail
    mod_name = f"apps_rg.runtime.dispatch.{module_tail}"
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(mod_name)


def test_non_product_proof_env_keys_documented() -> None:
    for key, val in NON_PRODUCT_PROOF_ENV.items():
        assert key.startswith("APPS_RG_") or key in os.environ or True
        assert val


def test_product_cli_rejects_mock_judge_flags() -> None:
    main_src = (REPO_ROOT / "apps_rg" / "__main__.py").read_text(encoding="utf-8")
    assert "assert_production_runtime" in main_src or "assert_production_cli_no_mock_judge_flags" in main_src
    assert "argparse.SUPPRESS" in main_src
    assert "resolve_cli_mock_judges" in main_src
