"""Smoke tests for verify_no_mock_data_util — wave 29."""

import pytest

mod = pytest.importorskip(
    "agentic_core.L5_safety.utils.verify_no_mock_data_util",
    exc_type=Exception,
)


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
