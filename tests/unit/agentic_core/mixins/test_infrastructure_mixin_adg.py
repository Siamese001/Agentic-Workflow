"""ADG-driven tests for mixins/infrastructure_mixin.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.mixins.infrastructure_mixin import infrastructure_mixin
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    infrastructure_mixin = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="infrastructure_mixin deps unavailable")
class TestInfrastructureMixin:
    def test_importable(self):
        assert callable(infrastructure_mixin)

    def test_is_class(self):
        assert isinstance(infrastructure_mixin, type)

    def test_has_verify_state(self):
        assert hasattr(infrastructure_mixin, "verify_state")


def test_module_importable():
    import agentic_core.mixins.infrastructure_mixin as m
    assert m is not None
