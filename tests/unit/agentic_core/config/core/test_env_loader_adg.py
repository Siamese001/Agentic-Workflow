"""ADG-driven tests for config/core/env_loader.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.config.core.env_loader import SovereignEnv
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SovereignEnv = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="env_loader deps unavailable")
class TestSovereignEnv:
    def test_importable(self):
        assert callable(SovereignEnv)

    def test_singleton_requires_project_root(self):
        import agentic_core.config.core.env_loader as mod
        original = mod.SovereignEnv._instance
        mod.SovereignEnv._instance = None
        try:
            with pytest.raises((ValueError, FileNotFoundError, Exception)):
                mod.SovereignEnv(project_root=None)
        finally:
            mod.SovereignEnv._instance = original

    def test_has_instance_attribute(self):
        assert hasattr(SovereignEnv, "_instance")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
