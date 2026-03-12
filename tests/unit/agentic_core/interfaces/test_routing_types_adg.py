"""ADG-driven tests for interfaces/routing_types.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.interfaces.routing_types as m


class TestRoutingTypesInterface:
    def test_importable(self):
        assert m is not None

    def test_reasoning_intensity_profile_present(self):
        assert hasattr(m, "ReasoningIntensityProfile")

    def test_all_exports(self):
        assert "ReasoningIntensityProfile" in m.__all__

    def test_profile_is_class_or_none(self):
        # Either successfully imported or gracefully set to None
        assert m.ReasoningIntensityProfile is None or isinstance(m.ReasoningIntensityProfile, type)
