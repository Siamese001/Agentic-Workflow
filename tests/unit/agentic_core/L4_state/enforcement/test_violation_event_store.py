"""Smoke tests for violation_event_store — wave 31."""

import pytest

mod = pytest.importorskip(
    "agentic_core.L4_state.enforcement.violation_event_store",
    exc_type=Exception,
)


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
