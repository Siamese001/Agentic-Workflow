"""Unit tests for apps_lic.signals.types — Wave 4.1 (ADG hotspots, fan-in 24).

Purpose: lock the pure signal taxonomy + ResurfacingSignal / SignalDetectionResult
behavior (enums, frozen dataclasses, defaults, confidence mapping, cadence-boost
logic, action recommendations, priority sorting). No mocks — all surfaces are
pure and deterministic.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from apps_lic.signals.types import (
    SIGNAL_PRIORITY,
    ResurfacingSignal,
    SignalDetectionResult,
    SignalSource,
    SignalStrength,
    SignalType,
    sort_signals_by_priority,
)


def _sig(
    signal_type: SignalType = SignalType.FUNDING_ROUND,
    strength: SignalStrength = SignalStrength.STRONG,
    source: SignalSource = SignalSource.CRUNCHBASE,
    detected_at: datetime | None = None,
    **kw,
) -> ResurfacingSignal:
    return ResurfacingSignal(
        signal_id=kw.pop("signal_id", "sig-001"),
        signal_type=signal_type,
        strength=strength,
        source=source,
        detected_at=detected_at or datetime(2026, 1, 1, tzinfo=timezone.utc),
        **kw,
    )


class TestEnums:
    def test_signal_type_values_are_str(self):
        assert SignalType.FUNDING_ROUND == "funding_round"
        assert isinstance(SignalType.FUNDING_ROUND.value, str)

    def test_signal_type_full_membership(self):
        expected = {
            "hiring_surge", "exec_role_open", "team_expansion",
            "funding_round", "ipo_announcement", "acquisition",
            "competitor_launch", "market_shift", "regulatory_change",
            "profile_view", "content_engagement",
        }
        assert {m.value for m in SignalType} == expected

    def test_strength_membership(self):
        assert {m.value for m in SignalStrength} == {"strong", "moderate", "weak"}

    def test_source_membership(self):
        assert {m.value for m in SignalSource} == {
            "linkedin", "crunchbase", "news",
            "company_website", "research", "manual",
        }


class TestResurfacingSignalConstruction:
    def test_defaults(self):
        s = _sig()
        assert s.company_id is None
        assert s.recipient_id is None
        assert s.raw_text == ""
        assert s.metadata == {}

    def test_frozen(self):
        s = _sig()
        with pytest.raises((AttributeError, TypeError)):
            s.signal_id = "other"  # type: ignore[misc]

    def test_metadata_default_is_independent(self):
        a = _sig(signal_id="a")
        b = _sig(signal_id="b")
        assert a.metadata is not b.metadata


class TestStrengthToConfidence:
    @pytest.mark.parametrize(
        "strength,expected",
        [
            (SignalStrength.STRONG, 0.9),
            (SignalStrength.MODERATE, 0.7),
            (SignalStrength.WEAK, 0.4),
        ],
    )
    def test_confidence_mapping(self, strength, expected):
        assert _sig(strength=strength)._strength_to_confidence() == expected

    def test_to_wake_trigger_shape(self):
        s = _sig(metadata={"series": "B"})
        trig = s.to_wake_trigger()
        assert trig["trigger_signal"] == "funding_round"
        assert trig["trigger_confidence"] == 0.9
        assert trig["trigger_source"] == "crunchbase"
        assert trig["trigger_metadata"] == {"series": "B"}
        # detected_at is ISO-serialized
        assert trig["trigger_detected_at"] == s.detected_at.isoformat()


class TestShouldBoostCadence:
    @pytest.mark.parametrize(
        "stype",
        [
            SignalType.FUNDING_ROUND,
            SignalType.EXEC_ROLE_OPEN,
            SignalType.COMPETITOR_LAUNCH,
            SignalType.ACQUISITION,
        ],
    )
    def test_strong_boost_triggers(self, stype):
        assert _sig(signal_type=stype, strength=SignalStrength.STRONG).should_boost_cadence()

    def test_non_strong_never_boosts(self):
        assert not _sig(
            signal_type=SignalType.FUNDING_ROUND, strength=SignalStrength.MODERATE
        ).should_boost_cadence()

    def test_strong_but_non_boost_type(self):
        assert not _sig(
            signal_type=SignalType.PROFILE_VIEW, strength=SignalStrength.STRONG
        ).should_boost_cadence()


class TestRecommendedAction:
    @pytest.mark.parametrize(
        "stype,action",
        [
            (SignalType.HIRING_SURGE, "reference_role_expansion"),
            (SignalType.EXEC_ROLE_OPEN, "reference_leadership_search"),
            (SignalType.FUNDING_ROUND, "reference_growth_trajectory"),
            (SignalType.COMPETITOR_LAUNCH, "reference_competitive_differentiation"),
            (SignalType.PROFILE_VIEW, "light_nudge"),
            (SignalType.CONTENT_ENGAGEMENT, "value_add_followup"),
        ],
    )
    def test_known_actions(self, stype, action):
        assert _sig(signal_type=stype).recommended_action() == action

    def test_unmapped_falls_back_to_standard(self):
        # MARKET_SHIFT has no explicit mapping
        assert _sig(signal_type=SignalType.MARKET_SHIFT).recommended_action() == "standard_resurface"


class TestSignalDetectionResult:
    def test_defaults(self):
        r = SignalDetectionResult(target_id="acme")
        assert r.signals == []
        assert r.sources_checked == []
        assert r.error is None
        assert isinstance(r.checked_at, datetime)

    def test_has_strong_signals_false_when_empty(self):
        assert not SignalDetectionResult(target_id="x").has_strong_signals

    def test_has_strong_signals_true(self):
        r = SignalDetectionResult(
            target_id="x",
            signals=[_sig(strength=SignalStrength.WEAK), _sig(strength=SignalStrength.STRONG)],
        )
        assert r.has_strong_signals

    def test_strongest_signal_none_when_empty(self):
        assert SignalDetectionResult(target_id="x").strongest_signal is None

    def test_strongest_signal_by_strength(self):
        weak = _sig(signal_id="w", strength=SignalStrength.WEAK)
        strong = _sig(signal_id="s", strength=SignalStrength.STRONG)
        r = SignalDetectionResult(target_id="x", signals=[weak, strong])
        assert r.strongest_signal is strong

    def test_strongest_signal_tiebreak_by_recency(self):
        older = _sig(
            signal_id="old",
            strength=SignalStrength.STRONG,
            detected_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        newer = _sig(
            signal_id="new",
            strength=SignalStrength.STRONG,
            detected_at=datetime(2026, 2, 1, tzinfo=timezone.utc),
        )
        r = SignalDetectionResult(target_id="x", signals=[older, newer])
        assert r.strongest_signal is newer


class TestSignalPriority:
    def test_priority_table_covers_all_types(self):
        assert set(SIGNAL_PRIORITY.keys()) == set(SignalType)

    def test_funding_highest_priority(self):
        assert SIGNAL_PRIORITY[SignalType.FUNDING_ROUND] == 1

    def test_sort_orders_by_priority_current_behavior(self):
        # ⚠️ SOURCE BUG (asserted as-is, not edited): sort_signals_by_priority
        # docstrings "high priority first" but uses reverse=True over the tuple
        # (priority_number, detected_at). reverse=True inverts BOTH keys, so the
        # *largest* priority number (lowest-priority signal, e.g.
        # CONTENT_ENGAGEMENT=11) sorts BEFORE the smallest (FUNDING_ROUND=1).
        # The author intended reverse only for recency; the priority key needs
        # ascending sort. This test locks the actual (inverted) behavior so the
        # bug is visible and a fix will break this test on purpose.
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        low = _sig(signal_id="low", signal_type=SignalType.CONTENT_ENGAGEMENT, detected_at=base)
        high = _sig(signal_id="high", signal_type=SignalType.FUNDING_ROUND, detected_at=base)
        out = sort_signals_by_priority([low, high])
        # Documented intent would be [high, low]; actual current behavior is [low, high].
        assert out[0] is low
        assert out[1] is high

    def test_sort_empty(self):
        assert sort_signals_by_priority([]) == []

    def test_sort_same_priority_recency_first(self):
        older = _sig(
            signal_id="old",
            signal_type=SignalType.FUNDING_ROUND,
            detected_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        newer = _sig(
            signal_id="new",
            signal_type=SignalType.FUNDING_ROUND,
            detected_at=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(days=10),
        )
        out = sort_signals_by_priority([older, newer])
        assert out[0] is newer
