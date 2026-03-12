"""ADG-driven tests for mixins/runtime_safety_mixin.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.mixins.runtime_safety_mixin import RuntimeSafetyMixin


class TestRuntimeSafetyMixin:
    def test_importable(self):
        assert callable(RuntimeSafetyMixin)

    def test_has_cleanup_processes(self):
        assert hasattr(RuntimeSafetyMixin, "cleanup_processes")

    def test_has_safe_run(self):
        assert hasattr(RuntimeSafetyMixin, "safe_run")

    def test_is_class(self):
        assert isinstance(RuntimeSafetyMixin, type)
