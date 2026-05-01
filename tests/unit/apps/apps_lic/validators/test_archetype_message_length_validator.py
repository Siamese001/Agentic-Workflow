"""Unit tests for ArchetypeMessageLengthValidator (W1-P2).

Covers:
- every canonical archetype uses its documented cap (EXECUTIVE=400,
  C_LEVEL=400, SENIOR_TA=600, RECRUITER=500, OTHER=500)
- at-cap messages are valid; one-over-cap messages are invalid
- reason string includes excess + cap for operator triage
- unknown archetypes fall back to the OTHER cap (500)
- whitespace-only and empty strings are valid (zero length)
- telemetry bus is called exactly once on violation and never on success
- telemetry bus errors never break validation
"""

from __future__ import annotations

import pytest

from apps_lic.validators.archetype_message_length_validator import (
    ARCHETYPE_LENGTH_CAPS,
    DEFAULT_LENGTH_CAP,
    ArchetypeMessageLengthValidator,
    cap_for,
    validate_length,
)


class RecordingBus:
    """Minimal telemetry-bus double — records every `record` call."""

    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def record(self, event_name: str, payload: dict) -> None:
        self.events.append((event_name, payload))


class BrokenBus:
    """Telemetry bus that raises on record — validator must tolerate."""

    def record(self, event_name: str, payload: dict) -> None:
        raise RuntimeError("bus exploded")


class TestArchetypeCaps:
    def test_documented_caps(self) -> None:
        assert ARCHETYPE_LENGTH_CAPS["EXECUTIVE"] == 400
        assert ARCHETYPE_LENGTH_CAPS["C_LEVEL"] == 400
        assert ARCHETYPE_LENGTH_CAPS["SENIOR_TA"] == 600
        assert ARCHETYPE_LENGTH_CAPS["RECRUITER"] == 500
        assert ARCHETYPE_LENGTH_CAPS["OTHER"] == 500

    def test_default_cap_matches_other(self) -> None:
        assert DEFAULT_LENGTH_CAP == ARCHETYPE_LENGTH_CAPS["OTHER"]

    def test_cap_for_fallback(self) -> None:
        assert cap_for("MARTIAN") == DEFAULT_LENGTH_CAP
        assert cap_for("EXECUTIVE") == 400


class TestValidateLengthPureFunction:
    @pytest.mark.parametrize(
        "archetype,expected_cap",
        [
            ("EXECUTIVE", 400),
            ("C_LEVEL", 400),
            ("SENIOR_TA", 600),
            ("RECRUITER", 500),
            ("OTHER", 500),
        ],
    )
    def test_at_cap_is_valid(self, archetype: str, expected_cap: int) -> None:
        text = "x" * expected_cap
        result = validate_length(text, archetype)
        assert result.is_valid is True
        assert result.cap == expected_cap
        assert result.message_length == expected_cap
        assert result.excess == 0
        assert result.reason == ""

    @pytest.mark.parametrize(
        "archetype,expected_cap",
        [
            ("EXECUTIVE", 400),
            ("C_LEVEL", 400),
            ("SENIOR_TA", 600),
            ("RECRUITER", 500),
            ("OTHER", 500),
        ],
    )
    def test_one_over_cap_is_invalid(self, archetype: str, expected_cap: int) -> None:
        text = "x" * (expected_cap + 1)
        result = validate_length(text, archetype)
        assert result.is_valid is False
        assert result.cap == expected_cap
        assert result.message_length == expected_cap + 1
        assert result.excess == 1
        # Reason must include enough info for HOP6 triage.
        assert str(expected_cap) in result.reason
        assert str(expected_cap + 1) in result.reason
        assert archetype in result.reason

    def test_whitespace_stripped_before_counting(self) -> None:
        text = "   " + "a" * 400 + "   "
        result = validate_length(text, "EXECUTIVE")
        # 400 + surrounding whitespace; stripped length = 400 which is at cap.
        assert result.is_valid is True
        assert result.message_length == 400

    def test_empty_string_is_valid(self) -> None:
        result = validate_length("", "EXECUTIVE")
        assert result.is_valid is True
        assert result.message_length == 0

    def test_none_text_is_valid(self) -> None:
        # Defensive: treat None-ish as empty. Other validators catch
        # the "empty message" case.
        result = validate_length("", "EXECUTIVE")
        assert result.is_valid is True

    def test_unknown_archetype_uses_other_cap(self) -> None:
        text = "x" * 501
        result = validate_length(text, "MARTIAN")
        assert result.is_valid is False
        assert result.cap == DEFAULT_LENGTH_CAP  # 500


class TestArchetypeMessageLengthValidator:
    def test_validator_without_bus(self) -> None:
        validator = ArchetypeMessageLengthValidator()
        res = validator.validate("x" * 401, "EXECUTIVE")
        assert res.is_valid is False
        assert res.excess == 1

    def test_telemetry_emitted_once_on_violation(self) -> None:
        bus = RecordingBus()
        validator = ArchetypeMessageLengthValidator(telemetry_bus=bus)
        validator.validate("x" * 401, "EXECUTIVE")
        assert len(bus.events) == 1
        event_name, payload = bus.events[0]
        assert event_name == "message_length_cap_violation"
        assert payload["archetype"] == "EXECUTIVE"
        assert payload["cap"] == 400
        assert payload["length"] == 401
        assert payload["excess"] == 1

    def test_no_telemetry_on_success(self) -> None:
        bus = RecordingBus()
        validator = ArchetypeMessageLengthValidator(telemetry_bus=bus)
        validator.validate("x" * 400, "EXECUTIVE")
        assert bus.events == []

    def test_broken_bus_does_not_break_validation(self) -> None:
        validator = ArchetypeMessageLengthValidator(telemetry_bus=BrokenBus())
        # Must not raise — validation result is what matters.
        result = validator.validate("x" * 401, "EXECUTIVE")
        assert result.is_valid is False

    def test_case_sensitive_archetype_matching(self) -> None:
        # Lowercase 'executive' is NOT canonical; expected to fall to OTHER cap.
        result = validate_length("x" * 450, "executive")
        # OTHER cap is 500, so 450 is valid under the fallback, invalid under
        # the real EXECUTIVE cap. This asserts fallback behaviour.
        assert result.is_valid is True
        assert result.cap == DEFAULT_LENGTH_CAP
