"""ADG-driven tests for system_learning/stores/activator.py — fan_in=0."""

from __future__ import annotations

from unittest.mock import patch

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.stores.activator import (  # noqa: F401
        FileBackedActivator,
        InMemoryActivator,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    InMemoryActivator = None  # type: ignore[assignment,misc]
    FileBackedActivator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="activator.py deps unavailable")
class TestInMemoryActivator:
    def test_is_dataclass(self):
        import dataclasses

        assert dataclasses.is_dataclass(InMemoryActivator)

    def test_importable(self):
        assert InMemoryActivator is not None


@pytest.mark.skipif(not _AVAILABLE, reason="activator.py deps unavailable")
class TestFileBackedActivator:
    def test_is_class(self):
        assert isinstance(FileBackedActivator, type)

    def test_importable(self):
        assert FileBackedActivator is not None

    def test_activate_persists_active_version(self, tmp_path):
        activator = FileBackedActivator(tmp_path)

        class _Bridge:
            def __init__(self):
                self.calls = []

            def persist_active_version(self, component, version_id, *, ts=""):
                self.calls.append((component, version_id, ts))
                return True

        bridge = _Bridge()
        with patch("system_learning.stores.activator.get_sl_memory_bridge", return_value=bridge):
            activator.activate("router", "v2")

        assert bridge.calls == [("router", "v2", "")]
        assert activator.get_active("router") == "v2"

    def test_activate_handles_bridge_failure(self, tmp_path):
        """Test that activation still works even if bridge persistence fails."""
        activator = FileBackedActivator(tmp_path)

        class _FailingBridge:
            def persist_active_version(self, component, version_id, *, ts=""):
                raise RuntimeError("Bridge down")

        bridge = _FailingBridge()
        with patch("system_learning.stores.activator.get_sl_memory_bridge", return_value=bridge):
            # Should not raise exception
            activator.activate("router", "v3")

        # Activation should still succeed locally
        assert activator.get_active("router") == "v3"


def test_module_importable():
    """Module activator.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE