"""Smoke tests for the live validators that replaced the legacy HOP6 gate.

These tests lock the contract for the three validator helpers that HOP6
used to wrap:
    * archetype length
    * question-ending
    * spam-trigger detection
"""

from __future__ import annotations

from apps_lic.validators.archetype_message_length_validator import validate_length
from apps_lic.validators.question_ending_validator import validate_question_ending
from apps_lic.validators.spam_trigger_phrase_validator import (
    validate_message_for_spam_triggers,
)


class TestCheckArchetypeLength:
    def test_valid_short_message(self) -> None:
        result = validate_length("Worth a quick chat?", "EXECUTIVE")
        assert result.is_valid is True
        assert result.archetype == "EXECUTIVE"
        assert result.cap == 400

    def test_invalid_long_message(self) -> None:
        result = validate_length("x" * 1000, "EXECUTIVE")
        assert result.is_valid is False
        assert result.excess > 0
        assert "exceeds" in result.reason.lower()


class TestCheckQuestionEnding:
    def test_executive_with_question(self) -> None:
        result = validate_question_ending("Worth a quick chat?", "EXECUTIVE")
        assert result.is_valid is True
        assert result.ends_in_question is True
        assert result.required_for_archetype is True

    def test_executive_without_question_fails(self) -> None:
        result = validate_question_ending("Let me know your thoughts.", "EXECUTIVE")
        assert result.is_valid is False
        assert result.required_for_archetype is True
        assert "question" in result.reason.lower()

    def test_recruiter_without_question_passes_soft(self) -> None:
        result = validate_question_ending("Open to discussing a role.", "RECRUITER")
        assert result.is_valid is True
        assert result.required_for_archetype is False


class TestCheckSpamTriggers:
    def test_clean_message_passes(self) -> None:
        result = validate_message_for_spam_triggers(
            "Saw the recent product launch — impressive work."
        )
        assert result.is_valid is True
        assert result.hits == []

    def test_pushy_cta_hard_rejects(self) -> None:
        result = validate_message_for_spam_triggers("Act now! Book a call on calendly.")
        assert result.is_valid is False
        assert result.hits
        assert result.hits[0].severity in {"high", "critical"}

    def test_corporate_cliche_soft_flags(self) -> None:
        result = validate_message_for_spam_triggers("Let's circle back on synergies.")
        # Medium severity phrases are flagged but do not hard-reject.
        assert result.is_valid is True
        assert result.hits
        assert result.hits[0].severity == "medium"

    def test_false_urgency_hard_rejects(self) -> None:
        result = validate_message_for_spam_triggers("Last chance — deadline approaching!")
        assert result.is_valid is False
        assert any(hit.severity == "critical" for hit in result.hits)
