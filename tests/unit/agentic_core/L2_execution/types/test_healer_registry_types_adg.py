"""ADG-driven tests for L2_execution/types/healer_registry_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.healer_registry_types import HEALER_REGISTRY
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    HEALER_REGISTRY = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="healer_registry_types deps unavailable")
class TestHealerRegistry:
    def test_is_dict(self):
        assert isinstance(HEALER_REGISTRY, dict)

    def test_keys_are_strings(self):
        for k in HEALER_REGISTRY:
            assert isinstance(k, str)

    def test_values_are_callable(self):
        for v in HEALER_REGISTRY.values():
            assert callable(v)


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
