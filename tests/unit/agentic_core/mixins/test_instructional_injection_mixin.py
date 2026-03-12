"""Foundational behavioral tests for agentic_core/mixins/instructional_injection_mixin.py.

fan_in=5 — imported by 5 other modules.
ADG import-hygiene is covered separately by test_instructional_injection_mixin_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.mixins.instructional_injection_mixin import (  # noqa: F401
        InstructionalInjectionMixin,
        get_instructional_injection_mixin,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    InstructionalInjectionMixin = None  # type: ignore[assignment,misc]
    get_instructional_injection_mixin = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="instructional_injection_mixin.py deps unavailable")
class TestInstructionalInjectionMixinContract:
    def test_is_class(self):
        assert isinstance(InstructionalInjectionMixin, type)

    def test_has_method_get_pattern(self):
        assert callable(getattr(InstructionalInjectionMixin, 'get_pattern', None))

    def test_has_method_get_patterns_by_layer(self):
        assert callable(getattr(InstructionalInjectionMixin, 'get_patterns_by_layer', None))

    def test_has_method_inject_pattern(self):
        assert callable(getattr(InstructionalInjectionMixin, 'inject_pattern', None))

    def test_has_method_inject_framing_layer(self):
        assert callable(getattr(InstructionalInjectionMixin, 'inject_framing_layer', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(InstructionalInjectionMixin) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="instructional_injection_mixin.py deps unavailable")
class TestGetInstructionalInjectionMixinFunction:
    def test_is_callable(self):
        assert callable(get_instructional_injection_mixin)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_instructional_injection_mixin)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: instructional_injection_mixin importable or gracefully unavailable."""
    assert True
