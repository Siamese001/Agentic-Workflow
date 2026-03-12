"""ADG-driven tests for interfaces/orchestration.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.interfaces.orchestration as m


class TestOrchestrationInterface:
    def test_importable(self):
        assert m is not None

    def test_action_router_present(self):
        assert hasattr(m, "ActionRouter")

    def test_all_exports_list(self):
        assert "ActionRouter" in m.__all__
