"""Smoke tests for layer_emission_seam — wave 17."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.utils.layer_emission_seam")


def test_module_imports_clean():
    assert mod is not None


def test_LayerEmissionValidator_class_present():
    assert hasattr(mod, "LayerEmissionValidator")
    assert isinstance(mod.LayerEmissionValidator, type)


def test_get_layer_emission_validator_callable():
    assert callable(mod.get_layer_emission_validator)
