"""Unit tests for question_ending_validator (W2-P6)."""

from __future__ import annotations

import pytest

from apps_lic.validators.question_ending_validator import (
    REQUIRED_QUESTION_ARCHETYPES,
    QuestionEndingResult,
    QuestionEndingValidator,
    validate_question_ending,
)


class RecordingBus:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def record(self, name: str, payload: dict) -> None:
        self.events.append((name, payload))


class TestRequiredArchetypes:
    @pytest.mark.parametrize("archetype", ["EXECUTIVE", "C_LEVEL", "SENIOR_TA"])
    def test_ends_with_question_passes(self, archetype: str) -> None:
        result = validate_question_ending("Open to a quick chat?", archetype)
        assert result.is_valid
        assert result.ends_in_question
        assert result.required_for_archetype
        assert result.reason == ""

    @pytest.mark.parametrize("archetype", ["EXECUTIVE", "C_LEVEL", "SENIOR_TA"])
    def test_ends_with_statement_fails(self, archetype: str) -> None:
        result = validate_question_ending("Let me know your thoughts.", archetype)
        assert not result.is_valid
        assert not result.ends_in_question
        assert result.required_for_archetype
        assert archetype in result.reason

    @pytest.mark.parametrize(
        "archetype,terminator",
        [
            ("EXECUTIVE", "?"),
            ("EXECUTIVE", "?!"),
            ("EXECUTIVE", "??"),
            ("C_LEVEL", "?"),
            ("SENIOR_TA", "?"),
        ],
    )
    def test_all_question_terminators_accepted(
        self, archetype: str, terminator: str
    ) -> None:
        result = validate_question_ending(
            f"Worth a quick conversation{terminator}", archetype
        )
        assert result.is_valid


class TestNonRequiredArchetypes:
    @pytest.mark.parametrize("archetype", ["RECRUITER", "OTHER"])
    def test_statement_ending_passes(self, archetype: str) -> None:
        result = validate_question_ending("Open to discussing a role.", archetype)
        assert result.is_valid
        assert not result.required_for_archetype

    @pytest.mark.parametrize("archetype", ["RECRUITER", "OTHER"])
    def test_question_ending_still_recognised(self, archetype: str) -> None:
        result = validate_question_ending("Open to discussing a role?", archetype)
        assert result.is_valid
        assert result.ends_in_question

    def test_unknown_archetype_not_required(self) -> None:
        result = validate_question_ending("Just a statement.", "MARTIAN")
        assert result.is_valid
        assert not result.required_for_archetype


class TestSignatureStripping:
    def test_signature_stripped_before_check_question(self) -> None:
        msg = (
            "Hi Priya, would this be worth exploring?\n"
            "\n"
            "Regards,\n"
            "Jane Doe"
        )
        result = validate_question_ending(msg, "EXECUTIVE")
        assert result.is_valid
        assert result.ends_in_question

    def test_signature_stripped_before_check_statement(self) -> None:
        msg = (
            "Let me know your thoughts.\n"
            "\n"
            "Best,\n"
            "Jane"
        )
        result = validate_question_ending(msg, "EXECUTIVE")
        assert not result.is_valid
        # Last char should reflect the body, not the signature.
        assert result.last_char == "."

    @pytest.mark.parametrize(
        "signoff",
        ["Regards,", "Best,", "Thanks,", "Sincerely,", "Cheers,", "Kind regards,"],
    )
    def test_each_signoff_prefix_detected(self, signoff: str) -> None:
        msg = f"Worth a quick chat?\n\n{signoff}\nJane"
        result = validate_question_ending(msg, "EXECUTIVE")
        assert result.is_valid
        assert result.ends_in_question

    def test_message_with_no_signature_uses_full_body(self) -> None:
        result = validate_question_ending("Would this interest you?", "EXECUTIVE")
        assert result.is_valid
        assert result.ends_in_question


class TestEdgeCases:
    def test_empty_text_passes_with_empty_last_char(self) -> None:
        result = validate_question_ending("", "EXECUTIVE")
        assert result.is_valid
        assert result.last_char == ""

    def test_whitespace_only_passes(self) -> None:
        result = validate_question_ending("   \n  ", "EXECUTIVE")
        assert result.is_valid

    def test_trailing_whitespace_does_not_mask_question(self) -> None:
        result = validate_question_ending("Worth a chat?   \n  ", "EXECUTIVE")
        assert result.is_valid
        assert result.ends_in_question


class TestValidatorClass:
    def test_violation_emits_event(self) -> None:
        bus = RecordingBus()
        validator = QuestionEndingValidator(telemetry_bus=bus)
        validator.validate("Statement ending.", "EXECUTIVE")
        assert len(bus.events) == 1
        name, payload = bus.events[0]
        assert name == "question_ending_violation"
        assert payload["archetype"] == "EXECUTIVE"
        assert payload["required_for_archetype"] is True

    def test_no_event_on_success(self) -> None:
        bus = RecordingBus()
        validator = QuestionEndingValidator(telemetry_bus=bus)
        validator.validate("Worth a chat?", "EXECUTIVE")
        assert bus.events == []

    def test_no_event_for_non_required_archetype(self) -> None:
        bus = RecordingBus()
        validator = QuestionEndingValidator(telemetry_bus=bus)
        validator.validate("Just a statement.", "RECRUITER")
        assert bus.events == []


class TestInvariants:
    def test_required_set_contents(self) -> None:
        assert REQUIRED_QUESTION_ARCHETYPES == {"EXECUTIVE", "C_LEVEL", "SENIOR_TA"}

    def test_recruiter_not_in_required_set(self) -> None:
        assert "RECRUITER" not in REQUIRED_QUESTION_ARCHETYPES

    def test_result_is_frozen_dataclass(self) -> None:
        result = validate_question_ending("Worth a chat?", "EXECUTIVE")
        with pytest.raises((AttributeError, TypeError)):
            result.is_valid = False  # type: ignore[misc]
