"""
Unit tests for L5 CONF_CALIB Risk Gate - structured risk decision.
"""

import pytest

from agentic_core.L5_safety.enforcement.conf_calib_gate import (
    ConfCalibRiskGate,
    RiskDecision,
    RiskLevel,
)


@pytest.mark.unit
class TestConfCalibRiskGate:
    """Test deterministic ConfCalibRiskGate implementation."""

    def test_risk_level_enum_values(self):
        """Test RiskLevel enum has correct values."""
        assert RiskLevel.LOW.value == "LOW"
        assert RiskLevel.MEDIUM.value == "MEDIUM"
        assert RiskLevel.HIGH.value == "HIGH"

    def test_risk_decision_dataclass(self):
        """Test RiskDecision dataclass properties."""
        decision = RiskDecision(allow=True, level=RiskLevel.LOW, reasons=("reason1", "reason2"))

        assert decision.allow is True
        assert decision.level == RiskLevel.LOW
        assert decision.reasons == ("reason1", "reason2")
        assert decision == RiskDecision(allow=True, level=RiskLevel.LOW, reasons=("reason1", "reason2"))

    def test_evaluate_default_low_risk(self):
        """Test default evaluation returns LOW risk with allow=True."""
        gate = ConfCalibRiskGate()

        class SimplePayload:
            sanitized = False
            check_ids = ()

        payload = SimplePayload()
        d0 = "<D0>\n[test] Some content\n</D0>\n"

        result = gate.evaluate(payload_like=payload, d0_injections=d0)

        assert result.allow is True
        assert result.level == RiskLevel.LOW
        assert result.reasons == ()

    def test_sanitized_input_elevates_to_medium(self):
        """Test sanitized input elevates risk to MEDIUM."""
        gate = ConfCalibRiskGate()

        class SimplePayload:
            sanitized = True
            check_ids = ()

        payload = SimplePayload()
        d0 = "<D0>\n[test] Some content\n</D0>\n"

        result = gate.evaluate(payload_like=payload, d0_injections=d0)

        assert result.allow is True
        assert result.level == RiskLevel.MEDIUM
        assert result.reasons == ("SANITIZED_INPUT",)

    def test_many_check_ids_triggers_medium(self):
        """Test many check_ids triggers MEDIUM risk."""
        gate = ConfCalibRiskGate()

        class SimplePayload:
            sanitized = False
            check_ids = ("id1", "id2", "id3", "id4", "id5")

        payload = SimplePayload()
        d0 = "<D0>\n[test] Some content\n</D0>\n"

        result = gate.evaluate(payload_like=payload, d0_injections=d0)

        assert result.allow is True
        assert result.level == RiskLevel.MEDIUM
        assert result.reasons == ("MANY_CHECK_IDS",)

    def test_deny_execution_forces_high_and_disallows(self):
        """Test DENY_EXECUTION forces HIGH risk and disallows execution."""
        gate = ConfCalibRiskGate()

        class SimplePayload:
            sanitized = False
            check_ids = ()

        payload = SimplePayload()
        d0 = "<D0>\n[deny] DENY_EXECUTION\n</D0>\n"

        result = gate.evaluate(payload_like=payload, d0_injections=d0)

        assert result.allow is False
        assert result.level == RiskLevel.HIGH
        assert result.reasons == ("D0_DENY_EXECUTION",)

    def test_determinism_identical_inputs_identical_outputs(self):
        """Test identical inputs produce identical RiskDecision."""
        gate = ConfCalibRiskGate()

        class SimplePayload:
            sanitized = True
            check_ids = ("id1", "id2", "id3", "id4", "id5")

        payload = SimplePayload()
        d0 = "<D0>\n[test] Content\n</D0>\n"

        result1 = gate.evaluate(payload_like=payload, d0_injections=d0)
        result2 = gate.evaluate(payload_like=payload, d0_injections=d0)
        result3 = gate.evaluate(payload_like=payload, d0_injections=d0)

        assert result1 == result2 == result3
        assert result1.reasons == result2.reasons == result3.reasons

    def test_multiple_reasons_sorted_lexicographically(self):
        """Test multiple reasons are sorted lexicographically."""
        gate = ConfCalibRiskGate()

        class SimplePayload:
            sanitized = True
            check_ids = ("id1", "id2", "id3", "id4", "id5")

        payload = SimplePayload()
        d0 = "<D0>\n[test] Content\n</D0>\n"

        result = gate.evaluate(payload_like=payload, d0_injections=d0)

        assert result.level == RiskLevel.MEDIUM
        assert result.allow is True
        assert result.reasons == ("MANY_CHECK_IDS", "SANITIZED_INPUT")

    def test_deny_execution_forces_high_and_disallows(self):
        """Test DENY_EXECUTION forces HIGH risk and disallows execution."""
        gate = ConfCalibRiskGate()

        class SimplePayload:
            sanitized = True
            check_ids = ("id1", "id2", "id3", "id4", "id5")

        payload = SimplePayload()
        d0 = "<D0>\n[deny] DENY_EXECUTION\n</D0>\n"

        result = gate.evaluate(payload_like=payload, d0_injections=d0)

        # DENY_EXECUTION should force HIGH and disallow
        assert result.allow is False
        assert result.level == RiskLevel.HIGH
        # DENY_EXECUTION should be included with other reasons
        expected_reasons = ("D0_DENY_EXECUTION", "MANY_CHECK_IDS", "SANITIZED_INPUT")
        assert result.reasons == expected_reasons

    def test_missing_attributes_default_to_safe(self):
        """Test missing attributes default to safe values."""
        gate = ConfCalibRiskGate()

        # Payload with no sanitized or check_ids attributes
        class MinimalPayload:
            pass

        payload = MinimalPayload()
        d0 = "<D0>\n[test] Content\n</D0>\n"

        result = gate.evaluate(payload_like=payload, d0_injections=d0)

        assert result.allow is True
        assert result.level == RiskLevel.LOW
        assert result.reasons == ()

    def test_payload_like_not_mutated(self):
        """Test payload_like object is not mutated during evaluation."""
        gate = ConfCalibRiskGate()

        class TestPayload:
            def __init__(self):
                self.sanitized = True
                self.check_ids = ("id1", "id2")
                self.extra_field = "unchanged"

        payload = TestPayload()
        original_state = {
            "sanitized": payload.sanitized,
            "check_ids": payload.check_ids,
            "extra_field": payload.extra_field,
        }

        d0 = "<D0>\n[test] Content\n</D0>\n"
        result = gate.evaluate(payload_like=payload, d0_injections=d0)

        # Verify payload was not mutated
        assert payload.sanitized == original_state["sanitized"]
        assert payload.check_ids == original_state["check_ids"]
        assert payload.extra_field == original_state["extra_field"]

        # Verify evaluation worked
        assert result.level == RiskLevel.MEDIUM
        assert result.reasons == ("SANITIZED_INPUT",)
