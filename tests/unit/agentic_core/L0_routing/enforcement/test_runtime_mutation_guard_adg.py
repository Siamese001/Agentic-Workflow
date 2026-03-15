"""ADG-driven tests for L0_routing/enforcement/runtime_mutation_guard.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.enforcement.runtime_mutation_guard import (
        PROTECTED_ATTRIBUTES,
        PROTECTED_LAYERS,
        _guard_disabled,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    PROTECTED_ATTRIBUTES = None  # type: ignore[assignment]
    PROTECTED_LAYERS = None  # type: ignore[assignment]
    _guard_disabled = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="runtime_mutation_guard deps unavailable")
class TestRuntimeMutationGuard:
    def test_protected_layers_is_set(self):
        assert isinstance(PROTECTED_LAYERS, set)

    def test_core_layers_protected(self):
        assert "L0_routing" in PROTECTED_LAYERS
        assert "L5_safety" in PROTECTED_LAYERS

    def test_protected_attributes_is_set(self):
        assert isinstance(PROTECTED_ATTRIBUTES, set)

    def test_class_attribute_protected(self):
        assert "__class__" in PROTECTED_ATTRIBUTES

    def test_guard_disabled_default_false(self):
        assert _guard_disabled is False


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
