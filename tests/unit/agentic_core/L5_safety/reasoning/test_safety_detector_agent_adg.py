"""ADG-driven tests for L5_safety/reasoning/SafetyDetectorAgent.py — fan_in=1."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_safety_detector_agent_adg")
_emit_applies_guardrail("p0", "test_safety_detector_agent_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_safety_detector_agent_adg", "policy_binding")
_emit_snapshots_state("p0", "test_safety_detector_agent_adg", "state_snapshot")
emit_replay_key("p0", "test_safety_detector_agent_adg")
emit_determinism_digest("p0", "test_safety_detector_agent_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
