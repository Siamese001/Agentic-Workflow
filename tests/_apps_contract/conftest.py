"""Shared fixtures for apps_rg contract tests."""

from __future__ import annotations

import pytest

from apps_rg.l2_recipe.r4_generation_mode import ENV_APPS_RG_R4_GENERATION_MODE


@pytest.fixture(autouse=True)
def _default_apps_rg_r4_generation_mode_legacy(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unless a test sets ``APPS_RG_R4_GENERATION_MODE``, keep legacy envelope path."""
    monkeypatch.delenv(ENV_APPS_RG_R4_GENERATION_MODE, raising=False)
