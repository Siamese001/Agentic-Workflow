"""Unit tests for mutual_connection_resolver (W2-P5)."""

from __future__ import annotations

import pytest

from apps_lic.engines.mutual_connection_resolver import (
    PRIMING_LINE_MAX_CHARS,
    RECENT_THRESHOLD_DAYS,
    MutualConnectionCandidate,
    MutualConnectionResolver,
)


class RecordingBus:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def record(self, name: str, payload: dict) -> None:
        self.events.append((name, payload))


class BrokenBus:
    def record(self, name: str, payload: dict) -> None:
        raise RuntimeError("bus broke")


class TestResolverBasic:
    def test_empty_candidates_yields_empty_string(self) -> None:
        res = MutualConnectionResolver()
        assert res.resolve_priming_line([]) == ""

    def test_single_recent_candidate_with_topic(self) -> None:
        res = MutualConnectionResolver()
        line = res.resolve_priming_line(
            [{"name": "Dana Lee", "topic": "AI infrastructure", "last_seen_days": 5}]
        )
        assert "Dana Lee" in line
        assert "AI infrastructure" in line
        assert "recently" in line.lower()

    def test_single_recent_candidate_no_topic(self) -> None:
        res = MutualConnectionResolver()
        line = res.resolve_priming_line(
            [{"name": "Dana Lee", "last_seen_days": 5}]
        )
        assert "Dana Lee" in line
        assert "recently" in line.lower()
        assert "{" not in line

    def test_older_candidate_uses_earlier_template(self) -> None:
        res = MutualConnectionResolver()
        line = res.resolve_priming_line(
            [{"name": "Sam Patel", "topic": "product strategy", "last_seen_days": 120}]
        )
        assert "earlier this year" in line.lower()


class TestRanking:
    def test_most_recent_wins(self) -> None:
        res = MutualConnectionResolver()
        candidates = [
            {"name": "Old Friend", "topic": "X", "last_seen_days": 300},
            {"name": "Recent Friend", "topic": "Y", "last_seen_days": 7},
        ]
        line = res.resolve_priming_line(candidates)
        assert "Recent Friend" in line
        assert "Old Friend" not in line

    def test_relevance_boost_overrides_recency(self) -> None:
        res = MutualConnectionResolver()
        candidates = [
            {"name": "Recent Friend", "topic": "X", "last_seen_days": 3},
            {
                "name": "Warm Introducer",
                "topic": "Y",
                "last_seen_days": 200,
                "relevance_boost": 10.0,
            },
        ]
        line = res.resolve_priming_line(candidates)
        assert "Warm Introducer" in line

    def test_dataclass_candidates_accepted(self) -> None:
        res = MutualConnectionResolver()
        line = res.resolve_priming_line(
            [
                MutualConnectionCandidate(
                    name="Priya Nair", topic="data infra", last_seen_days=10
                )
            ]
        )
        assert "Priya Nair" in line
        assert "data infra" in line


class TestEdgeCases:
    def test_invalid_inputs_ignored(self) -> None:
        res = MutualConnectionResolver()
        # Empty name disqualifies; non-mapping items skipped.
        line = res.resolve_priming_line(
            [
                "not a dict",  # type: ignore[list-item]
                {"name": ""},
                {"name": "   "},
                {"name": "Valid Person", "topic": "x", "last_seen_days": 5},
            ]
        )
        assert "Valid Person" in line

    def test_bad_last_seen_defaults_to_999(self) -> None:
        res = MutualConnectionResolver()
        line = res.resolve_priming_line(
            [{"name": "Test", "topic": "x", "last_seen_days": "not-a-number"}]
        )
        # Falls to older-template since default 999 > RECENT_THRESHOLD_DAYS.
        assert "earlier this year" in line.lower()

    def test_negative_last_seen_treated_as_zero(self) -> None:
        res = MutualConnectionResolver()
        candidate = MutualConnectionCandidate(
            name="Test", topic="x", last_seen_days=-5
        )
        # Dataclass default preserves the raw value; the iter normaliser is
        # only exercised via mapping input. Use mapping to confirm.
        line = res.resolve_priming_line(
            [{"name": "Test", "topic": "x", "last_seen_days": -5}]
        )
        assert "recently" in line.lower()

    def test_priming_line_respects_max_chars(self) -> None:
        res = MutualConnectionResolver()
        very_long_topic = "x" * 200
        line = res.resolve_priming_line(
            [{"name": "Person", "topic": very_long_topic, "last_seen_days": 1}]
        )
        assert len(line) <= PRIMING_LINE_MAX_CHARS

    def test_recent_threshold_boundary(self) -> None:
        res = MutualConnectionResolver()
        # Exactly at threshold should use "recently".
        line = res.resolve_priming_line(
            [{"name": "A", "topic": "t", "last_seen_days": RECENT_THRESHOLD_DAYS}]
        )
        assert "recently" in line.lower()
        # One over should use "earlier this year".
        line2 = res.resolve_priming_line(
            [{"name": "A", "topic": "t", "last_seen_days": RECENT_THRESHOLD_DAYS + 1}]
        )
        assert "earlier this year" in line2.lower()


class TestTelemetry:
    def test_rendered_event_on_success(self) -> None:
        bus = RecordingBus()
        res = MutualConnectionResolver(telemetry_bus=bus)
        res.resolve_priming_line([{"name": "Dana", "topic": "x", "last_seen_days": 5}])
        assert len(bus.events) == 1
        name, payload = bus.events[0]
        assert name == "mutual_connection_rendered"
        assert payload["mutual_name"] == "Dana"
        assert payload["has_topic"] is True

    def test_empty_event_on_no_candidates(self) -> None:
        bus = RecordingBus()
        res = MutualConnectionResolver(telemetry_bus=bus)
        res.resolve_priming_line([])
        assert len(bus.events) == 1
        assert bus.events[0][0] == "mutual_connection_no_candidates"

    def test_broken_bus_tolerated(self) -> None:
        res = MutualConnectionResolver(telemetry_bus=BrokenBus())
        # Must not raise.
        line = res.resolve_priming_line(
            [{"name": "A", "topic": "t", "last_seen_days": 5}]
        )
        assert "A" in line


class TestBestCandidate:
    def test_returns_dataclass_instance(self) -> None:
        res = MutualConnectionResolver()
        best = res.best_candidate(
            [{"name": "Z", "topic": "t", "last_seen_days": 20}]
        )
        assert isinstance(best, MutualConnectionCandidate)
        assert best.name == "Z"

    def test_returns_none_when_no_candidates(self) -> None:
        res = MutualConnectionResolver()
        assert res.best_candidate([]) is None
