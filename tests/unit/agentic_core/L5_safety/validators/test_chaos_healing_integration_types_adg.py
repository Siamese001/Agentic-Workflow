"""ADG-driven tests for agentic_core/L5_safety/validators/chaos_healing_integration_types.py — fan_in=2.

Contract tests: HealingStrategyProtocol, ChaosResilienceStrategy constants and can_heal.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.validators.chaos_healing_integration_types import (
    ChaosResilienceStrategy,
    HealingStrategyProtocol,
)


class TestHealingStrategyProtocol:
    def test_protocol_importable(self):
        assert callable(HealingStrategyProtocol)

    def test_protocol_is_runtime_checkable_or_protocol(self):
        from typing import Protocol
        assert issubclass(HealingStrategyProtocol, Protocol)


class TestChaosResilienceStrategyConstants:
    def test_supported_violations_nonempty(self):
        assert len(ChaosResilienceStrategy.SUPPORTED_VIOLATIONS) > 0

    def test_is_frozenset(self):
        assert isinstance(ChaosResilienceStrategy.SUPPORTED_VIOLATIONS, frozenset)

    def test_resilience_check_supported(self):
        assert "resilience_check" in ChaosResilienceStrategy.SUPPORTED_VIOLATIONS


class TestChaosResilienceStrategyInit:
    def test_creates_without_args(self):
        s = ChaosResilienceStrategy()
        assert s is not None

    def test_not_initialized_on_create(self):
        s = ChaosResilienceStrategy()
        assert s._initialized is False

    def test_agent_none_on_create(self):
        s = ChaosResilienceStrategy()
        assert s._agent is None


class TestChaosResilienceStrategyCanHeal:
    def test_can_heal_supported_violation(self):
        s = ChaosResilienceStrategy()
        assert s.can_heal({"type": "resilience_check"}) is True

    def test_can_heal_unsupported_violation(self):
        s = ChaosResilienceStrategy()
        assert s.can_heal({"type": "unknown_violation_type_xyz"}) is False

    def test_can_heal_empty_dict(self):
        s = ChaosResilienceStrategy()
        assert s.can_heal({}) is False
