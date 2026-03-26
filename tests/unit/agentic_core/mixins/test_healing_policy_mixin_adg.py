"""ADG-driven tests for mixins/healing_policy_mixin.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: from agentic_core.mixins.healing_policy_mixin import HealingPolicyMixin


class TestHealingPolicyMixin:
    def test_importable(self):
                from agentic_core.mixins.healing_policy_mixin import HealingPolicyMixin
                assert callable(HealingPolicyMixin)

        assert callable(HealingPolicyMixin)

    def test_max_healing_operations_default(self):
        assert HealingPolicyMixin._max_healing_operations == 100

    def test_has_heal_repository(self):
        assert hasattr(HealingPolicyMixin, "heal_repository")

    def test_is_class(self):
        assert isinstance(HealingPolicyMixin, type)
