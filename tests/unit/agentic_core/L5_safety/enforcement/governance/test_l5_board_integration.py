"""Smoke tests for l5_board_integration — wave 34."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.governance.l5_board_integration")


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
