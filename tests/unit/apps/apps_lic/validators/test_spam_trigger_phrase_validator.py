"""Unit tests for spam_trigger_phrase_validator (W3-P8)."""

from __future__ import annotations

import pytest

from apps_lic.config.spam_trigger_phrases import (
    ALL_PHRASES,
    CATEGORY_SEVERITY,
    SPAM_TRIGGER_PHRASES,
    category_for_phrase,
    phrases_in_category,
)
from apps_lic.validators.spam_trigger_phrase_validator import (
    SpamTriggerHit,
    SpamTriggerPhraseValidator,
    SpamTriggerValidationResult,
    validate_message_for_spam_triggers,
)


class RecordingBus:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def record(self, name: str, payload: dict) -> None:
        self.events.append((name, payload))


class TestConfigInvariants:
    def test_all_categories_have_severity(self) -> None:
        for category in SPAM_TRIGGER_PHRASES:
            assert category in CATEGORY_SEVERITY

    def test_all_phrases_flattened_correctly(self) -> None:
        total_phrases = sum(len(v) for v in SPAM_TRIGGER_PHRASES.values())
        assert len(ALL_PHRASES) == total_phrases

    def test_phrase_count_exceeds_threshold(self) -> None:
        # Plan promised ~40 phrases.
        assert len(ALL_PHRASES) >= 40

    def test_category_for_phrase_roundtrip(self) -> None:
        for phrase, category in ALL_PHRASES:
            assert category_for_phrase(phrase) == category

    def test_category_for_unknown_phrase(self) -> None:
        assert category_for_phrase("absolutely benign text") is None

    def test_phrases_in_category_returns_tuple(self) -> None:
        for category in SPAM_TRIGGER_PHRASES:
            assert isinstance(phrases_in_category(category), tuple)

    def test_phrases_in_unknown_category_empty(self) -> None:
        assert phrases_in_category("does_not_exist") == ()


class TestPureFunctionBasic:
    def test_clean_message_is_valid(self) -> None:
        result = validate_message_for_spam_triggers(
            "Hi Priya, saw the recent Series C announcement. Would this be worth a chat?"
        )
        assert result.is_valid
        assert result.hits == []
        assert result.total_hit_count == 0

    def test_empty_message_is_valid(self) -> None:
        assert validate_message_for_spam_triggers("").is_valid
        assert validate_message_for_spam_triggers(None).is_valid  # type: ignore[arg-type]

    def test_corporate_cliche_flagged_soft(self) -> None:
        result = validate_message_for_spam_triggers(
            "Let's circle back next week to discuss synergies."
        )
        assert not result.is_valid or result.is_valid  # medium = soft
        # Severity should be medium, so is_valid remains True (soft reject).
        assert result.is_valid is True
        assert len(result.hits) == 2
        phrases = {h.phrase for h in result.hits}
        assert "circle back" in phrases
        assert "synergies" in phrases

    def test_pushy_cta_hard_rejects(self) -> None:
        result = validate_message_for_spam_triggers(
            "Act now! Book a call on my calendly."
        )
        assert not result.is_valid
        assert result.total_hit_count >= 3

    def test_false_urgency_hard_rejects(self) -> None:
        result = validate_message_for_spam_triggers(
            "Last chance to take advantage of this offer - deadline approaching."
        )
        assert not result.is_valid
        severities = {h.severity for h in result.hits}
        assert "critical" in severities

    def test_generic_opener_flagged_soft(self) -> None:
        result = validate_message_for_spam_triggers(
            "Hope this finds you well. Quick question about your initiatives."
        )
        # Both phrases are medium severity → soft reject (is_valid=True).
        assert result.is_valid is True
        assert len(result.hits) == 2


class TestWordBoundaryMatching:
    def test_substring_match_does_not_trigger(self) -> None:
        # "circled" should NOT match "circle".
        result = validate_message_for_spam_triggers(
            "The team circled the problem carefully."
        )
        assert result.is_valid
        assert result.hits == []

    def test_case_insensitive(self) -> None:
        result = validate_message_for_spam_triggers("LET'S CIRCLE BACK NEXT WEEK.")
        phrases = {h.phrase for h in result.hits}
        assert "circle back" in phrases

    def test_hyphenated_variant(self) -> None:
        result = validate_message_for_spam_triggers(
            "This is a game-changer for the industry."
        )
        phrases = {h.phrase for h in result.hits}
        assert "game-changer" in phrases


class TestMultipleHits:
    def test_occurrence_count_tracks_repeats(self) -> None:
        result = validate_message_for_spam_triggers(
            "Synergy synergy synergy - let's leverage synergies too."
        )
        synergy_hit = next(h for h in result.hits if h.phrase == "synergy")
        assert synergy_hit.occurrence_count == 3

    def test_hits_sorted_critical_first(self) -> None:
        result = validate_message_for_spam_triggers(
            "Let's circle back. Last chance to act now."
        )
        # false_urgency (critical) before corporate_cliche (medium).
        assert result.hits
        severities = [h.severity for h in result.hits]
        # Sorted ascending by rank: critical=0, high=1, medium=2.
        rank_map = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        for i in range(len(severities) - 1):
            assert rank_map[severities[i]] <= rank_map[severities[i + 1]]

    def test_reason_mentions_top_hit(self) -> None:
        result = validate_message_for_spam_triggers(
            "Last chance! Let's circle back."
        )
        assert "last chance" in result.reason.lower()


class TestValidatorClass:
    def test_telemetry_on_hits(self) -> None:
        bus = RecordingBus()
        validator = SpamTriggerPhraseValidator(telemetry_bus=bus)
        validator.validate("Let's circle back on synergies.")
        assert len(bus.events) == 1
        name, payload = bus.events[0]
        assert name == "spam_trigger_hits"
        assert payload["total_hits"] >= 2
        assert "corporate_cliche" in payload["categories"]

    def test_no_telemetry_on_clean(self) -> None:
        bus = RecordingBus()
        validator = SpamTriggerPhraseValidator(telemetry_bus=bus)
        result = validator.validate("Saw the recent product launch - impressive!")
        assert result.is_valid
        assert bus.events == []

    def test_broken_bus_tolerated(self) -> None:
        class Broken:
            def record(self, *args, **kwargs):
                raise RuntimeError("broke")

        validator = SpamTriggerPhraseValidator(telemetry_bus=Broken())
        # Must not raise.
        result = validator.validate("Let's circle back.")
        assert isinstance(result, SpamTriggerValidationResult)
