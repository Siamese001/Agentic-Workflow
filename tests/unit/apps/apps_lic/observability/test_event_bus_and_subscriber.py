"""Unit tests for JsonlEventBus + OutreachLearningSubscriber (deferred #2)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_lic.observability.event_bus import InMemoryEventBus, JsonlEventBus
from apps_lic.observability.outreach_learning_subscriber import (
    KNOWN_EVENTS,
    OutreachLearningRollup,
    OutreachLearningSubscriber,
)


@pytest.fixture
def log_path(tmp_path: Path) -> Path:
    return tmp_path / "events.jsonl"


class TestJsonlEventBus:
    def test_record_creates_log(self, log_path: Path) -> None:
        bus = JsonlEventBus(log_path)
        bus.record("test_event", {"foo": "bar"})
        assert log_path.exists()
        content = log_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(content) == 1
        row = json.loads(content[0])
        assert row["event"] == "test_event"
        assert row["payload"]["foo"] == "bar"

    def test_records_session_id(self, log_path: Path) -> None:
        bus = JsonlEventBus(log_path, session_id="custom-session")
        bus.record("e", {})
        row = json.loads(log_path.read_text(encoding="utf-8").strip())
        assert row["session_id"] == "custom-session"

    def test_autogenerates_session_id(self, log_path: Path) -> None:
        bus = JsonlEventBus(log_path)
        assert bus.session_id  # non-empty hex
        assert len(bus.session_id) == 32

    def test_creates_parent_dir(self, tmp_path: Path) -> None:
        nested = tmp_path / "deep" / "nested" / "events.jsonl"
        bus = JsonlEventBus(nested)
        bus.record("e", {})
        assert nested.exists()

    def test_swallows_serialization_errors(self, log_path: Path) -> None:
        bus = JsonlEventBus(log_path)

        # Non-JSON-serialisable object — bus must NOT raise.
        class NotSerialisable:
            pass

        bus.record("e", {"obj": NotSerialisable()})
        # Default str fallback writes <object ...> string; one line emitted.
        assert log_path.exists()
        content = log_path.read_text(encoding="utf-8").strip().splitlines()
        # Exactly one line attempt — may have written, may have been
        # caught by the OSError/TypeError/ValueError guard. Either way,
        # no exception escaped.
        assert len(content) <= 1

    def test_multiple_records_appended(self, log_path: Path) -> None:
        bus = JsonlEventBus(log_path)
        for i in range(5):
            bus.record("e", {"i": i})
        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 5


class TestInMemoryEventBus:
    def test_records_in_list(self) -> None:
        bus = InMemoryEventBus()
        bus.record("a", {"x": 1})
        bus.record("b", {"y": 2})
        assert bus.events == [("a", {"x": 1}), ("b", {"y": 2})]

    def test_clear(self) -> None:
        bus = InMemoryEventBus()
        bus.record("a", {})
        bus.clear()
        assert bus.events == []


class TestOutreachLearningSubscriber:
    def test_aggregate_missing_log_returns_empty(self, tmp_path: Path) -> None:
        sub = OutreachLearningSubscriber(tmp_path / "no_such.jsonl")
        rollup = sub.aggregate()
        assert rollup.total_events == 0
        assert rollup.events_by_name == {}

    def test_aggregate_archetype_violations(self, log_path: Path) -> None:
        bus = JsonlEventBus(log_path)
        bus.record("message_length_cap_violation", {"archetype": "EXECUTIVE"})
        bus.record("message_length_cap_violation", {"archetype": "EXECUTIVE"})
        bus.record("message_length_cap_violation", {"archetype": "C_LEVEL"})
        bus.record("question_ending_violation", {"archetype": "SENIOR_TA"})
        rollup = OutreachLearningSubscriber(log_path).aggregate()
        assert rollup.total_events == 4
        assert rollup.length_violations_by_archetype == {
            "EXECUTIVE": 2,
            "C_LEVEL": 1,
        }
        assert rollup.question_ending_violations_by_archetype == {"SENIOR_TA": 1}

    def test_aggregate_spam_categories(self, log_path: Path) -> None:
        bus = JsonlEventBus(log_path)
        bus.record(
            "spam_trigger_hits",
            {
                "is_valid": False,
                "total_hits": 3,
                "categories": {"corporate_cliche": 2, "pushy_cta": 1},
            },
        )
        bus.record(
            "spam_trigger_hits",
            {"is_valid": True, "total_hits": 1, "categories": {"corporate_cliche": 1}},
        )
        rollup = OutreachLearningSubscriber(log_path).aggregate()
        assert rollup.spam_trigger_total_messages_with_hits == 2
        assert rollup.spam_trigger_hits_by_category == {
            "corporate_cliche": 3,
            "pushy_cta": 1,
        }

    def test_aggregate_priming_rate(self, log_path: Path) -> None:
        bus = JsonlEventBus(log_path)
        for _ in range(8):
            bus.record("mutual_connection_rendered", {"mutual_name": "X"})
        for _ in range(2):
            bus.record("mutual_connection_no_candidates", {})
        rollup = OutreachLearningSubscriber(log_path).aggregate()
        assert rollup.mutual_connection_priming_rate == pytest.approx(0.8)

    def test_session_filter(self, log_path: Path) -> None:
        bus_a = JsonlEventBus(log_path, session_id="alpha")
        bus_b = JsonlEventBus(log_path, session_id="beta")
        bus_a.record("question_ending_violation", {"archetype": "EXECUTIVE"})
        bus_b.record("question_ending_violation", {"archetype": "EXECUTIVE"})
        bus_b.record("question_ending_violation", {"archetype": "EXECUTIVE"})
        sub = OutreachLearningSubscriber(log_path)
        rollup_a = sub.aggregate(session_id="alpha")
        rollup_b = sub.aggregate(session_id="beta")
        assert sum(rollup_a.question_ending_violations_by_archetype.values()) == 1
        assert sum(rollup_b.question_ending_violations_by_archetype.values()) == 2

    def test_unknown_events_recorded(self, log_path: Path) -> None:
        bus = JsonlEventBus(log_path)
        bus.record("some_unknown_event", {})
        rollup = OutreachLearningSubscriber(log_path).aggregate()
        assert "some_unknown_event" in rollup.unknown_events

    def test_malformed_lines_tolerated(self, log_path: Path) -> None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            "{not json}\n{\"event\":\"question_ending_violation\",\"payload\":{}}\n",
            encoding="utf-8",
        )
        rollup = OutreachLearningSubscriber(log_path).aggregate()
        assert rollup.total_events == 1

    def test_known_events_match_module_constant(self) -> None:
        # Sanity: every event the W1-W4 validators emit appears in KNOWN_EVENTS.
        for expected in (
            "message_length_cap_violation",
            "mutual_connection_rendered",
            "mutual_connection_no_candidates",
            "question_ending_violation",
            "spam_trigger_hits",
        ):
            assert expected in KNOWN_EVENTS


class TestEndToEndValidatorWiring:
    def test_validator_emits_through_bus_subscriber_aggregates(
        self, log_path: Path
    ) -> None:
        from apps_lic.validators.spam_trigger_phrase_validator import (
            SpamTriggerPhraseValidator,
        )
        from apps_lic.validators.question_ending_validator import (
            QuestionEndingValidator,
        )

        bus = JsonlEventBus(log_path)
        sv = SpamTriggerPhraseValidator(telemetry_bus=bus)
        qev = QuestionEndingValidator(telemetry_bus=bus)

        # Trigger 1 spam hit + 1 question-ending violation.
        sv.validate("Let's circle back on synergies.")
        qev.validate("Let me know your thoughts.", "EXECUTIVE")

        rollup = OutreachLearningSubscriber(log_path).aggregate()
        # Spam (cliche, soft-pass) should still be recorded.
        assert rollup.spam_trigger_total_messages_with_hits == 1
        assert rollup.question_ending_violations_by_archetype.get("EXECUTIVE") == 1
