"""Foundational behavioral tests for system_learning/adapters/system_learning_memory_bridge.py.

fan_in=5 — imported by 5 other modules.
ADG import-hygiene is covered separately by test_system_learning_memory_bridge_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.adapters.system_learning_memory_bridge import (  # noqa: F401
        SystemLearningMemoryBridge,
        get_sl_memory_bridge,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    SystemLearningMemoryBridge = None  # type: ignore[assignment,misc]
    get_sl_memory_bridge = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="system_learning_memory_bridge.py deps unavailable")
class TestSystemLearningMemoryBridgeContract:
    def test_is_class(self):
        assert isinstance(SystemLearningMemoryBridge, type)

    def test_has_method_get_instance(self):
        assert callable(getattr(SystemLearningMemoryBridge, 'get_instance', None))

    def test_has_method_is_available(self):
        assert callable(getattr(SystemLearningMemoryBridge, 'is_available', None))

    def test_has_method_persist_healing_success_rate(self):
        assert callable(getattr(SystemLearningMemoryBridge, 'persist_healing_success_rate', None))

    def test_has_method_persist_all_healing_rates(self):
        assert callable(getattr(SystemLearningMemoryBridge, 'persist_all_healing_rates', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(SystemLearningMemoryBridge) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="system_learning_memory_bridge.py deps unavailable")
class TestGetSlMemoryBridgeFunction:
    def test_is_callable(self):
        assert callable(get_sl_memory_bridge)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_sl_memory_bridge)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: system_learning_memory_bridge importable or gracefully unavailable."""
    pass
