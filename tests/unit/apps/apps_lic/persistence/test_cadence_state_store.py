"""Unit tests for CadenceStateStore (deferred follow-up #3)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from apps_lic.engines.followup_cadence_engine import FollowupCadenceEngine
from apps_lic.persistence.cadence_state_store import CadenceStateStore
from apps_lic.types.cadence_state_types import (
    DAYS_TO_FOLLOWUP_1,
    CadenceState,
    CadenceStateRecord,
)


@pytest.fixture
def store_path(tmp_path: Path) -> Path:
    return tmp_path / "cadence.sqlite"


@pytest.fixture
def store(store_path: Path) -> CadenceStateStore:
    return CadenceStateStore(store_path)


class TestSchema:
    def test_creates_db(self, store: CadenceStateStore) -> None:
        assert store.db_path.exists()

    def test_creates_parent_dirs(self, tmp_path: Path) -> None:
        nested = tmp_path / "a" / "b" / "c.sqlite"
        CadenceStateStore(nested)
        assert nested.parent.exists()

    def test_load_missing_returns_none(self, store: CadenceStateStore) -> None:
        assert store.load("c1", "r1") is None


class TestSaveLoad:
    def test_roundtrip_initial(self, store: CadenceStateStore) -> None:
        rec = CadenceStateRecord(
            campaign_id="camp",
            recipient_id="recip",
            current_state=CadenceState.INITIAL,
        )
        store.save(rec)
        loaded = store.load("camp", "recip")
        assert loaded is not None
        assert loaded.campaign_id == "camp"
        assert loaded.recipient_id == "recip"
        assert loaded.current_state is CadenceState.INITIAL
        assert loaded.send_count == 0
        assert loaded.replied is False

    def test_roundtrip_with_timestamps(self, store: CadenceStateStore) -> None:
        ts = datetime(2026, 5, 5, 14, 0, 0, tzinfo=timezone.utc)
        rec = CadenceStateRecord(
            campaign_id="c",
            recipient_id="r",
            current_state=CadenceState.FOLLOWUP_1,
            next_action_at_utc=ts + timedelta(days=DAYS_TO_FOLLOWUP_1),
            last_sent_at_utc=ts,
            initial_scheduled_at_utc=ts,
            replied=False,
            send_count=1,
        )
        store.save(rec)
        loaded = store.load("c", "r")
        assert loaded is not None
        assert loaded.next_action_at_utc == ts + timedelta(days=DAYS_TO_FOLLOWUP_1)
        assert loaded.last_sent_at_utc == ts
        assert loaded.send_count == 1

    def test_upsert_idempotent(self, store: CadenceStateStore) -> None:
        rec = CadenceStateRecord(
            campaign_id="c",
            recipient_id="r",
            current_state=CadenceState.INITIAL,
        )
        store.save(rec)
        store.save(rec)
        assert store.count() == 1

    def test_overwrite_on_state_change(self, store: CadenceStateStore) -> None:
        rec = CadenceStateRecord(
            campaign_id="c",
            recipient_id="r",
            current_state=CadenceState.INITIAL,
        )
        store.save(rec)
        rec.current_state = CadenceState.FOLLOWUP_1
        rec.send_count = 1
        store.save(rec)
        loaded = store.load("c", "r")
        assert loaded is not None
        assert loaded.current_state is CadenceState.FOLLOWUP_1
        assert loaded.send_count == 1
        assert store.count() == 1

    def test_terminated_record_roundtrip(self, store: CadenceStateStore) -> None:
        rec = CadenceStateRecord(
            campaign_id="c",
            recipient_id="r",
            current_state=CadenceState.TERMINATED,
            replied=True,
            terminated_reason="replied",
        )
        store.save(rec)
        loaded = store.load("c", "r")
        assert loaded is not None
        assert loaded.current_state is CadenceState.TERMINATED
        assert loaded.replied is True
        assert loaded.terminated_reason == "replied"


class TestLoadOrCreate:
    def test_returns_fresh_when_missing(self, store: CadenceStateStore) -> None:
        rec = store.load_or_create("new_camp", "new_recip")
        assert rec.campaign_id == "new_camp"
        assert rec.recipient_id == "new_recip"
        assert rec.current_state is CadenceState.INITIAL
        # Did NOT persist; load() should still return None.
        assert store.load("new_camp", "new_recip") is None

    def test_returns_existing_when_present(self, store: CadenceStateStore) -> None:
        rec = CadenceStateRecord(
            campaign_id="c",
            recipient_id="r",
            current_state=CadenceState.FOLLOWUP_1,
            send_count=1,
        )
        store.save(rec)
        loaded = store.load_or_create("c", "r")
        assert loaded.send_count == 1
        assert loaded.current_state is CadenceState.FOLLOWUP_1


class TestCadenceLoop:
    """End-to-end: engine + store working together across simulated turns."""

    def test_engine_advances_persisted_record(
        self, store: CadenceStateStore
    ) -> None:
        engine = FollowupCadenceEngine()
        day0 = datetime(2026, 5, 5, 14, 0, 0, tzinfo=timezone.utc)
        rec = store.load_or_create("camp", "recip")
        rec.next_action_at_utc = day0

        # Day 0 — INITIAL send.
        decision = engine.advance(rec, now_utc=day0)
        engine.mark_sent(rec, sent_at_utc=day0)
        store.save(rec)
        assert decision.message_template == "initial"

        # Reload and resume — should be FOLLOWUP_1.
        rec2 = store.load_or_create("camp", "recip")
        assert rec2.current_state is CadenceState.FOLLOWUP_1
        assert rec2.send_count == 1

        # Day 5 — followup_1 send.
        day5 = day0 + timedelta(days=DAYS_TO_FOLLOWUP_1)
        decision2 = engine.advance(rec2, now_utc=day5)
        engine.mark_sent(rec2, sent_at_utc=day5)
        store.save(rec2)
        assert decision2.message_template == "followup_1"
        assert rec2.send_count == 2
