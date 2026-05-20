"""Shared fixtures for apps_rg contract tests."""

from __future__ import annotations

import pytest

from apps_rg.l2_recipe.r4_generation_mode import (
    ENV_APPS_RG_R4_GENERATION_MODE,
    MODE_LEGACY_FULL_RESUME,
)


@pytest.fixture(autouse=True)
def _default_apps_rg_r4_generation_mode_legacy(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unless a test overrides env, pin legacy envelope for contract tests that stub ``run_apps_rg_l2_envelope``."""
    monkeypatch.setenv(ENV_APPS_RG_R4_GENERATION_MODE, MODE_LEGACY_FULL_RESUME)


@pytest.fixture(autouse=True)
def _contract_tests_proof_pool_fixture_dev_bypass() -> None:
    """Direct ``resolve_section_proof_pool`` contract tests: non-product-certified bypass."""
    from apps_rg.runtime.section_front_spine_bridge import (
        activate_fixture_dev_bypass,
        deactivate_fixture_dev_bypass,
    )

    activate_fixture_dev_bypass(non_product_certified=True)
    yield
    deactivate_fixture_dev_bypass()
