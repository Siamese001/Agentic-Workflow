"""Retired r1b_uwg_gateway_shim — canonical gateway lives in r1b_uwg_promotion."""
from __future__ import annotations

import importlib

import pytest


def test_r1b_uwg_gateway_shim_module_absent() -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("apps_rg.cache.r1b_uwg_gateway_shim")


def test_canonical_gateway_importable_from_promotion() -> None:
    mod = importlib.import_module("apps_rg.cache.r1b_uwg_promotion")
    assert hasattr(mod, "R1bUwgPromotionGateway")
    assert hasattr(mod, "AppsRgR1BUwgGateway")
    assert hasattr(mod, "default_r1b_promotion_gateway")
    assert mod.AppsRgR1BUwgGateway is mod.R1bUwgPromotionGateway
