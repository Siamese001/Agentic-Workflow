"""ADG-driven tests for L5_safety/reasoning/SafetyDetectorAgent.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.SafetyDetectorAgent import (
    SafetyDetectorAgent,
    SafetyThreatType,
    ThreatSeverity,
)


class TestSafetyThreatType:
    def test_bias_member(self):
        assert hasattr(SafetyThreatType, "BIAS")

    def test_hallucination_member(self):
        assert hasattr(SafetyThreatType, "HALLUCINATION")

    def test_prompt_injection_member(self):
        assert hasattr(SafetyThreatType, "PROMPT_INJECTION")

    def test_jailbreak_member(self):
        assert hasattr(SafetyThreatType, "JAILBREAK")


class TestThreatSeverity:
    def test_low_value_0(self):
        assert ThreatSeverity.LOW.value == 0

    def test_critical_highest(self):
        assert ThreatSeverity.CRITICAL.value > ThreatSeverity.HIGH.value


class TestSafetyDetectorAgent:
    def test_creates(self):
        agent = SafetyDetectorAgent()
        assert agent is not None

    def test_has_heal_repository(self):
        assert hasattr(SafetyDetectorAgent, "heal_repository")
