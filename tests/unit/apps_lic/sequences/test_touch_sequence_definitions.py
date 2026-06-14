"""Unit tests for apps_lic.sequences.touch_sequence_definitions.

Wave 4.1 — plan adg-testing-hotspots-wave-plan-a7f3c1
Module fan-in: 30.

Purpose: cover the 3-touch sequence taxonomy (enums), the frozen
TouchDefinition / SequenceDefinition dataclasses (defaults), the three
canonical sequence definitions and registry, and the pure lookup / wake-time
helpers (get_sequence_definition ValueError path, get_touch_definition,
list_sequence_types, calculate_touch_wake_time cumulative-delay math).
No mocks — all real module-level constants.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from apps_lic.sequences.touch_sequence_definitions import (
    EXECUTIVE_3_TOUCH,
    RECRUITER_COMPACT,
    SEQUENCE_REGISTRY,
    STANDARD_3_TOUCH,
    SequenceDefinition,
    SequenceType,
    TouchDefinition,
    TouchStrategy,
    calculate_touch_wake_time,
    get_sequence_definition,
    get_touch_definition,
    list_sequence_types,
)


class TestEnums:
    def test_sequence_type_values(self) -> None:
        assert {s.value for s in SequenceType} == {
            "standard_3_touch",
            "executive_3_touch",
            "recruiter_compact",
        }

    def test_touch_strategy_values(self) -> None:
        assert {s.value for s in TouchStrategy} == {
            "initial",
            "nudge",
            "fresh_angle",
            "close_or_optout",
        }

    def test_str_enum(self) -> None:
        assert isinstance(SequenceType.STANDARD_3_TOUCH, str)


class TestTouchDefinition:
    def test_defaults(self) -> None:
        td = TouchDefinition(
            touch_number=1,
            template_id="t",
            strategy=TouchStrategy.INITIAL,
            delay_days=0,
        )
        assert td.p2_context_required == []
        assert td.content_variation == ""
        assert td.carry_forward_keys == []

    def test_frozen(self) -> None:
        td = TouchDefinition(
            touch_number=1, template_id="t", strategy=TouchStrategy.INITIAL, delay_days=0
        )
        with pytest.raises(Exception):
            td.touch_number = 2  # type: ignore[misc]


class TestSequenceDefinitionDataclass:
    def test_requires_p2_default(self) -> None:
        sd = SequenceDefinition(
            sequence_type=SequenceType.STANDARD_3_TOUCH,
            name="n",
            description="d",
            touches=[],
            max_duration_days=14,
        )
        assert sd.requires_p2 is False


class TestCanonicalSequences:
    @pytest.mark.parametrize(
        "seq,seq_type,max_days,requires_p2",
        [
            (STANDARD_3_TOUCH, SequenceType.STANDARD_3_TOUCH, 14, True),
            (EXECUTIVE_3_TOUCH, SequenceType.EXECUTIVE_3_TOUCH, 21, True),
            (RECRUITER_COMPACT, SequenceType.RECRUITER_COMPACT, 12, False),
        ],
    )
    def test_sequence_headers(
        self,
        seq: SequenceDefinition,
        seq_type: SequenceType,
        max_days: int,
        requires_p2: bool,
    ) -> None:
        assert seq.sequence_type is seq_type
        assert seq.max_duration_days == max_days
        assert seq.requires_p2 is requires_p2

    @pytest.mark.parametrize(
        "seq", [STANDARD_3_TOUCH, EXECUTIVE_3_TOUCH, RECRUITER_COMPACT]
    )
    def test_three_touches_numbered_1_2_3(self, seq: SequenceDefinition) -> None:
        assert len(seq.touches) == 3
        assert [t.touch_number for t in seq.touches] == [1, 2, 3]

    @pytest.mark.parametrize(
        "seq", [STANDARD_3_TOUCH, EXECUTIVE_3_TOUCH, RECRUITER_COMPACT]
    )
    def test_first_touch_is_initial_zero_delay(self, seq: SequenceDefinition) -> None:
        first = seq.touches[0]
        assert first.strategy is TouchStrategy.INITIAL
        assert first.delay_days == 0

    @pytest.mark.parametrize(
        "seq", [STANDARD_3_TOUCH, EXECUTIVE_3_TOUCH, RECRUITER_COMPACT]
    )
    def test_cumulative_delay_within_max_duration(self, seq: SequenceDefinition) -> None:
        total = sum(t.delay_days for t in seq.touches)
        assert total <= seq.max_duration_days


class TestRegistry:
    def test_registry_covers_all_types(self) -> None:
        assert set(SEQUENCE_REGISTRY.keys()) == set(SequenceType)

    def test_list_sequence_types(self) -> None:
        assert set(list_sequence_types()) == set(SequenceType)


class TestGetSequenceDefinition:
    def test_known(self) -> None:
        assert get_sequence_definition(SequenceType.STANDARD_3_TOUCH) is STANDARD_3_TOUCH

    def test_unknown_raises(self) -> None:
        # An enum value not present in the registry. Build by patching the
        # registry would mutate module state; instead assert the ValueError
        # path via a real-but-absent key is unreachable for valid enums, so
        # exercise the guard by temporarily removing a key.
        original = dict(SEQUENCE_REGISTRY)
        try:
            SEQUENCE_REGISTRY.pop(SequenceType.STANDARD_3_TOUCH)
            with pytest.raises(ValueError, match="Unknown sequence type"):
                get_sequence_definition(SequenceType.STANDARD_3_TOUCH)
        finally:
            SEQUENCE_REGISTRY.clear()
            SEQUENCE_REGISTRY.update(original)


class TestGetTouchDefinition:
    def test_existing_touch(self) -> None:
        td = get_touch_definition(SequenceType.STANDARD_3_TOUCH, 2)
        assert td is not None
        assert td.touch_number == 2
        assert td.strategy is TouchStrategy.NUDGE

    def test_missing_touch_returns_none(self) -> None:
        assert get_touch_definition(SequenceType.STANDARD_3_TOUCH, 99) is None


class TestCalculateTouchWakeTime:
    def test_missing_touch_none(self) -> None:
        assert calculate_touch_wake_time(SequenceType.STANDARD_3_TOUCH, 99) is None

    def test_first_touch_is_start(self) -> None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        wake = calculate_touch_wake_time(SequenceType.STANDARD_3_TOUCH, 1, start)
        assert wake == start  # delay_days=0 for touch 1

    def test_cumulative_delay_standard(self) -> None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        # STANDARD delays: touch1=0, touch2=5, touch3=7 -> cumulative t3 = 12 days
        wake3 = calculate_touch_wake_time(SequenceType.STANDARD_3_TOUCH, 3, start)
        assert wake3 == datetime(2026, 1, 13, tzinfo=timezone.utc)

    def test_cumulative_delay_touch2(self) -> None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        wake2 = calculate_touch_wake_time(SequenceType.STANDARD_3_TOUCH, 2, start)
        assert wake2 == datetime(2026, 1, 6, tzinfo=timezone.utc)

    def test_default_start_is_now(self) -> None:
        before = datetime.now(timezone.utc)
        wake = calculate_touch_wake_time(SequenceType.STANDARD_3_TOUCH, 1)
        assert wake is not None
        assert wake >= before
