"""W3A: structure_blueprint package shim re-exports ssot names via PEP 562 (lazy)."""
from __future__ import annotations

import importlib

import pytest

PKG = "agentic_core.L5_safety.config.structure_blueprint"
SSOT = "agentic_core.L5_safety.config.structure_blueprint.ssot"


@pytest.fixture
def pkg_mod():
    return importlib.import_module(PKG)


@pytest.fixture
def ssot_mod():
    return importlib.import_module(SSOT)


@pytest.mark.parametrize(
    "attr",
    [
        "ENFORCED_TERRITORIES",
        "FORBIDDEN_PATTERNS",
        "STANDARD_LAYER_STRUCTURE",
        "validate_no_nested_lcd",
        "get_sovereign_territories",
    ],
)
def test_package_lazy_attrs_match_ssot(pkg_mod, ssot_mod, attr: str) -> None:
    pkg_val = getattr(pkg_mod, attr)
    ssot_val = getattr(ssot_mod, attr)
    assert pkg_val is ssot_val


def test_dir_includes_ssot_exports(pkg_mod) -> None:
    names = dir(pkg_mod)
    assert "ENFORCED_TERRITORIES" in names
    assert "validate_no_nested_lcd" in names
