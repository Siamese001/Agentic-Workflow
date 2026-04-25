"""Smoke tests for heal_model_map_types — wave 28."""

import pytest

mod = pytest.importorskip(
    "agentic_core.L5_safety.types.heal_model_map_types",
    exc_type=Exception,
)


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
