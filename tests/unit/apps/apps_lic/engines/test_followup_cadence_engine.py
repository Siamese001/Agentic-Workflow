"""Unit tests for followup_cadence_engine (W3-P9)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from apps_lic.engines.followup_cadence_engine import FollowupCadenceEngine
from apps_lic.types.cadence_state_types import (
    DAYS_TO_FOLLOWUP_1,
    DAYS_TO_FOLLOWUP_2,
    TOTAL_SEQUENCE_DAYS,
    CadenceAction,
    CadenceState,
    CadenceStateRecord,
)


@pytest.fixture
def day0() -> datetime:
    return datetime(2026, 5, 5, 14, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def record(day0) -> CadenceStateRecord:
    return CadenceStateRecord(
        campaign_id="c1",
        recipient_id="r1",
        current_state=CadenceState.INITIAL,
        next_action_at_utc=day0,
    )


@pytest.fixture
def engine() -> FollowupCadenceEngine:
    return FollowupCadenceEngine()


class TestHappyPath:
    def test_day0_triggers_initial_send(
        self, engine: FollowupCadenceEngine, record: CadenceStateRecord, day0: datetime
    ) -> None:
        decision = engine.advance(record, now_utc=day0)
        assert decision.action is CadenceAction.SEND
        assert decision.message_template == "initial"
        assert decision.next_state is CadenceState.FOLLOWUP_1
        assert record.current_state is CadenceState.FOLLOWUP_1
        assert decision.next_check_at_utc == day0 + timedelta(days=DAYS_TO_FOLLOWUP_1)
        assert record.initial_scheduled_at_utc == day0

    def test_day5_triggers_followup_1(
        self, engine: FollowupCadenceEngine, record: CadenceStateRecord, day0: datetime
    ) -> None:
        engine.advance(record, now_utc=day0)  # Day 0 send
        day5 = day0 + timedelta(days=DAYS_TO_FOLLOWUP_1)
        decision = engine.advance(record, now_utc=day5)
        assert decision.action is CadenceAction.SEND
        assert decision.message_template == "followup_1"
        assert decision.next_state is CadenceState.FOLLOWUP_2
        assert record.current_state is CadenceState.FOLLOWUP_2

    def test_day12_triggers_final_and_terminates(
        self, engine: FollowupCadenceEngine, record: CadenceStateRecord, day0: datetime
    ) -> None:
        engine.advance(record, now_utc=day0)
        engine.advance(record, now_utc=day0 + timedelta(days=DAYS_TO_FOLLOWUP_1))
        day12 = day0 + timedelta(days=TOTAL_SEQUENCE_DAYS)
        decision = engine.advance(record, now_utc=day12)
        assert decision.action is CadenceAction.SEND
        assert decision.message_template == "followup_2"
        assert decision.next_state is CadenceState.TERMINATED
        assert record.terminated_reason == "sequence_complete"
        assert record.next_action_at_utc is None


class TestWait:
    def test_before_day0_waits(
        self, engine: FollowupCadenceEngine, record: CadenceStateRecord, day0: datetime
    ) -> None:
        before = day0 - timedelta(hours=1)
        decision = engine.advance(record, now_utc=before)
        assert decision.action is CadenceAction.WAIT
        assert decision.next_state is CadenceState.INITIAL  # no transition
        assert record.current_state is CadenceState.INITIAL

    def test_between_day0_and_day5_waits(
        self, engine: FollowupCadenceEngine, record: CadenceStateRecord, day0: datetime
    ) -> None:
        engine.advance(record, now_utc=day0)  # send initial, transition to F1
        between = day0 + timedelta(days=2)
        decision = engine.advance(record, now_utc=between)
        assert decision.action is CadenceAction.WAIT
        assert decision.next_state is CadenceState.FOLLOWUP_1


class TestReplyShortCircuit:
    def test_reply_before_day0_terminates(
        self, engine: FollowupCadenceEngine, record: CadenceStateRecord, day0: datetime
    ) -> None:
        engine.mark_replied(record)
        decision = engine.advance(record, now_utc=day0)
        assert decision.action is CadenceAction.NO_ACTION
        assert record.current_state is CadenceState.TERMINATED
        assert record.terminated_reason == "replied"

    def test_reply_between_touches_terminates(
        self, engine: FollowupCadenceEngine, record: CadenceStateRecord, day0: datetime
    ) -> None:
        engine.advance(record, now_utc=day0)  # initial send → FOLLOWUP_1
        engine.mark_replied(record)
        decision = engine.advance(record, now_utc=day0 + timedelta(days=2))
        assert decision.action is CadenceAction.NO_ACTION
        assert record.current_state is CadenceState.TERMINATED
        assert record.terminated_reason == "replied"

    def test_reply_after_followup_1_prevents_followup_2(
        self, engine: FollowupCadenceEngine, record: CadenceStateRecord, day0: datetime
    ) -> None:
        engine.advance(record, now_utc=day0)
        engine.advance(record, now_utc=day0 + timedelta(days=DAYS_TO_FOLLOWUP_1))
        engine.mark_replied(record)
        decision = engine.advance(
            record, now_utc=day0 + timedelta(days=TOTAL_SEQUENCE_DAYS)
        )
        assert decision.action is CadenceAction.NO_ACTION
        assert record.current_state is CadenceState.TERMINATED


class TestTerminated:
    def test_terminated_is_no_action(
        self, engine: FollowupCadenceEngine, record: CadenceStateRecord, day0: datetime
    ) -> None:
        engine.terminate(record, reason="operator_stop")
        decision = engine.advance(record, now_utc=day0)
        assert decision.action is CadenceAction.NO_ACTION
        assert "operator_stop" in decision.reason

    def test_terminate_clears_next_action(
        self, engine: FollowupCadenceEngine, record: CadenceStateRecord
    ) -> None:
        engine.terminate(record)
        assert record.next_action_at_utc is None
        assert record.current_state is CadenceState.TERMINATED


class TestMarkSent:
    def test_mark_sent_increments_count(
        self, engine: FollowupCadenceEngine, record: CadenceStateRecord, day0: datetime
    ) -> None:
        engine.advance(record, now_utc=day0)
        engine.mark_sent(record, sent_at_utc=day0)
        assert record.send_count == 1
        assert record.last_sent_at_utc == day0

    def test_mark_sent_default_now(
        self, engine: FollowupCadenceEngine, record: CadenceStateRecord
    ) -> None:
        before = datetime.now(timezone.utc)
        engine.mark_sent(record)
        assert record.last_sent_at_utc is not None
        assert record.last_sent_at_utc >= before


class TestInvariants:
    def test_total_sequence_matches_individual_intervals(self) -> None:
        assert TOTAL_SEQUENCE_DAYS == DAYS_TO_FOLLOWUP_1 + DAYS_TO_FOLLOWUP_2

    def test_next_action_none_does_not_block_send(
        self, engine: FollowupCadenceEngine, day0: datetime
    ) -> None:
        # A record with no next_action_at_utc should send immediately.
        rec = CadenceStateRecord(
            campaign_id="c", recipient_id="r", current_state=CadenceState.INITIAL
        )
        decision = engine.advance(rec, now_utc=day0)
        assert decision.action is CadenceAction.SEND

    def test_engine_is_thread_safe_stateless(
        self, engine: FollowupCadenceEngine
    ) -> None:
        # No mutable engine state — two records advance independently.
        r1 = CadenceStateRecord(campaign_id="c", recipient_id="r1")
        r2 = CadenceStateRecord(campaign_id="c", recipient_id="r2")
        now = datetime.now(timezone.utc)
        d1 = engine.advance(r1, now_utc=now)
        d2 = engine.advance(r2, now_utc=now)
        assert d1.action is CadenceAction.SEND
        assert d2.action is CadenceAction.SEND
        assert r1.current_state is CadenceState.FOLLOWUP_1
        assert r2.current_state is CadenceState.FOLLOWUP_1
