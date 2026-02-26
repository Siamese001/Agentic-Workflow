"""Tests for HealingPatternAdvisor port (Phase 3)."""

from __future__ import annotations

from agentic_core.L2_execution.healers.healing_tier_types import HealingInput
from system_learning.ports.healing_pattern_advisor import (
    _MAX_PATTERN_BOOST,
    HealingPatternAdvisor,
    NullHealingPatternAdvisor,
    PatternAdvice,
)


class MockHealingPatternAdvisor:
    """Mock advisor with configurable pattern advice."""

    def __init__(self, advice: dict[str, PatternAdvice]) -> None:
        self._advice = advice

    def advise(self, healing_input) -> PatternAdvice:
        return self._advice.get(
            healing_input.error_signature,
            {
                "pattern_match": False,
                "pattern_name": None,
                "pattern_boost": 0.0,
                "extra_reason_codes": (),
            },
        )


def test_null_healing_pattern_advisor() -> None:
    """NullHealingPatternAdvisor returns no pattern match."""
    advisor = NullHealingPatternAdvisor()

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
        agent_id="test-agent",
    )

    advice = advisor.advise(healing_input)

    assert advice["pattern_match"] is False
    assert advice["pattern_name"] is None
    assert advice["pattern_boost"] == 0.0
    assert advice["extra_reason_codes"] == ()


def test_pattern_advice_structure() -> None:
    """PatternAdvice has correct structure and constraints."""
    advice: PatternAdvice = {
        "pattern_match": True,
        "pattern_name": "test_pattern",
        "pattern_boost": 0.05,
        "extra_reason_codes": ("pattern_boost=0.05",),
    }

    assert advice["pattern_match"] is True
    assert advice["pattern_name"] == "test_pattern"
    assert advice["pattern_boost"] == 0.05
    assert advice["extra_reason_codes"] == ("pattern_boost=0.05",)


def test_pattern_boost_limit() -> None:
    """Pattern boost is capped at _MAX_PATTERN_BOOST."""
    assert _MAX_PATTERN_BOOST == 0.10


def test_mock_healing_pattern_advisor() -> None:
    """Mock advisor returns configured advice."""
    advice_map = {
        "sig1": {
            "pattern_match": True,
            "pattern_name": "pattern_a",
            "pattern_boost": 0.08,
            "extra_reason_codes": ("pattern_boost=0.08",),
        },
        "sig2": {
            "pattern_match": False,
            "pattern_name": None,
            "pattern_boost": 0.0,
            "extra_reason_codes": (),
        },
    }

    advisor = MockHealingPatternAdvisor(advice_map)

    healing_input1 = HealingInput(
        error_signature="sig1",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
        agent_id="test-agent",
    )

    healing_input2 = HealingInput(
        error_signature="sig2",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
        agent_id="test-agent",
    )

    advice1 = advisor.advise(healing_input1)
    advice2 = advisor.advise(healing_input2)

    assert advice1["pattern_match"] is True
    assert advice1["pattern_name"] == "pattern_a"
    assert advice1["pattern_boost"] == 0.08

    assert advice2["pattern_match"] is False
    assert advice2["pattern_boost"] == 0.0


def test_healing_pattern_advisor_protocol() -> None:
    """Mock advisor satisfies HealingPatternAdvisor protocol."""
    advisor = MockHealingPatternAdvisor({})
    assert isinstance(advisor, HealingPatternAdvisor)


def test_pattern_advice_reason_codes() -> None:
    """Pattern advice can include extra reason codes."""
    advice: PatternAdvice = {
        "pattern_match": True,
        "pattern_name": "test_pattern",
        "pattern_boost": 0.07,
        "extra_reason_codes": (
            "pattern_boost=0.07",
            "pattern_match=test_pattern",
        ),
    }

    assert "pattern_boost=0.07" in advice["extra_reason_codes"]
    assert "pattern_match=test_pattern" in advice["extra_reason_codes"]
    assert len(advice["extra_reason_codes"]) == 2


def test_pattern_advice_no_match() -> None:
    """No pattern match returns neutral values."""
    advice: PatternAdvice = {
        "pattern_match": False,
        "pattern_name": None,
        "pattern_boost": 0.0,
        "extra_reason_codes": (),
    }

    assert advice["pattern_match"] is False
    assert advice["pattern_name"] is None
    assert advice["pattern_boost"] == 0.0
    assert advice["extra_reason_codes"] == ()
