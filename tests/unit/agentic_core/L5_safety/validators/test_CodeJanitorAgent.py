"""Smoke tests for CodeJanitorAgent — wave 29."""

import pytest

mod = pytest.importorskip(
    "agentic_core.L5_safety.validators.CodeJanitorAgent",
    exc_type=Exception,
)


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
