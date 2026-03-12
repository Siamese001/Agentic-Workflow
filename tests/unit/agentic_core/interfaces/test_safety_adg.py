"""ADG-driven tests for interfaces/safety.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.interfaces.safety as m


class TestSafetyInterface:
    def test_importable(self):
        assert m is not None

    def test_unified_cst_healer_present(self):
        assert hasattr(m, "UnifiedCSTHealer")

    def test_all_exports(self):
        assert "UnifiedCSTHealer" in m.__all__

    def test_healer_is_class_or_none(self):
        assert m.UnifiedCSTHealer is None or isinstance(m.UnifiedCSTHealer, type)
