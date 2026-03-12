"""ADG-driven tests for mixins/autonomy_mixin.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.mixins.autonomy_mixin import AutonomyMixin


class TestAutonomyMixin:
    def test_importable(self):
        assert callable(AutonomyMixin)

    def test_autonomy_enabled_default(self):
        assert AutonomyMixin._autonomy_enabled is True

    def test_max_proactive_actions_default(self):
        assert AutonomyMixin._max_proactive_actions_per_hour == 12

    def test_has_should_act_proactively(self):
        assert hasattr(AutonomyMixin, "should_act_proactively")

    def test_creates(self):
        agent = AutonomyMixin()
        assert agent is not None
