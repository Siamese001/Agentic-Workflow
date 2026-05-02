"""Unit tests for reply_ledger_store (W4 follow-up persistence)."""

from __future__ import annotations

import sqlite3
import warnings
from datetime import datetime, timezone
from pathlib import Path

import pytest

from apps_lic.config.outreach_experiment_cells import (
    LATTICE_FINGERPRINT,
    cell_id,
)
from apps_lic.engines.reply_signal_feedback_engine import (
    CellPosterior,
    ReplyFeedbackLedger,
    ReplySignalFeedbackEngine,
)
from apps_lic.persistence.reply_ledger_store import (
    LatticeFingerprintDrift,
    ReplyLedgerStore,
)


@pytest.fixture
def store_path(tmp_path: Path) -> Path:
    return tmp_path / "reply_ledger.sqlite"


@pytest.fixture
def store(store_path: Path) -> ReplyLedgerStore:
    return ReplyLedgerStore(store_path)


@pytest.fixture
def populated_ledger() -> ReplyFeedbackLedger:
    ledger = ReplyFeedbackLedger()
    engine = ReplySignalFeedbackEngine()
    for _ in range(50):
        engine.record_event(
            ledger,
            archetype="EXECUTIVE",
            template="initial",
            subject_variant="question",
            replied=True,
        )
    for _ in range(150):
        engine.record_event(
            ledger,
            archetype="EXECUTIVE",
            template="initial",
            subject_variant="question",
            replied=False,
        )
    for _ in range(75):
        engine.record_event(
            ledger,
            archetype="SENIOR_TA",
            template="followup_1",
            subject_variant="pipeline",
            replied=False,
        )
    return ledger


class TestSchemaAndPath:
    def test_creates_db_file(self, store: ReplyLedgerStore) -> None:
        assert store.db_path.exists()

    def test_creates_parent_dirs(self, tmp_path: Path) -> None:
        nested = tmp_path / "deep" / "nested" / "ledger.sqlite"
        ReplyLedgerStore(nested)
        assert nested.parent.exists()

    def test_empty_load_returns_empty_ledger(self, store: ReplyLedgerStore) -> None:
        ledger = store.load()
        assert ledger.posteriors == {}
        assert ledger.lattice_fingerprint == LATTICE_FINGERPRINT


class TestSaveLoad:
    def test_save_returns_row_count(
        self, store: ReplyLedgerStore, populated_ledger: ReplyFeedbackLedger
    ) -> None:
        n = store.save(populated_ledger)
        assert n == 2

    def test_roundtrip_preserves_counts(
        self, store: ReplyLedgerStore, populated_ledger: ReplyFeedbackLedger
    ) -> None:
        store.save(populated_ledger)
        loaded = store.load()
        cid = cell_id("EXECUTIVE", "initial", "question")
        assert loaded.posteriors[cid].sends == 200
        assert loaded.posteriors[cid].replies == 50

    def test_save_is_idempotent(
        self, store: ReplyLedgerStore, populated_ledger: ReplyFeedbackLedger
    ) -> None:
        store.save(populated_ledger)
        store.save(populated_ledger)
        assert store.cell_count() == 2

    def test_save_overwrites_existing(
        self, store: ReplyLedgerStore, populated_ledger: ReplyFeedbackLedger
    ) -> None:
        store.save(populated_ledger)
        # Mutate one cell.
        cid = cell_id("EXECUTIVE", "initial", "question")
        populated_ledger.posteriors[cid].sends = 999
        populated_ledger.posteriors[cid].replies = 200
        store.save(populated_ledger)
        loaded = store.load()
        assert loaded.posteriors[cid].sends == 999
        assert loaded.posteriors[cid].replies == 200

    def test_empty_ledger_save_writes_zero(self, store: ReplyLedgerStore) -> None:
        empty = ReplyFeedbackLedger()
        assert store.save(empty) == 0

    def test_timestamp_roundtrip(self, store: ReplyLedgerStore) -> None:
        ts = datetime(2026, 5, 1, 12, 0, 0, tzinfo=timezone.utc)
        ledger = ReplyFeedbackLedger()
        cid = cell_id("EXECUTIVE", "initial", "question")
        ledger.posteriors[cid] = CellPosterior(
            cell_id=cid, sends=10, replies=2, last_updated_utc=ts
        )
        store.save(ledger)
        loaded = store.load()
        assert loaded.posteriors[cid].last_updated_utc == ts


class TestInvalidCells:
    def test_invalid_cells_are_skipped_on_save(self, store: ReplyLedgerStore) -> None:
        ledger = ReplyFeedbackLedger()
        # Inject an invalid cell directly (bypassing record_event guard).
        ledger.posteriors["BOGUS.cell.id"] = CellPosterior(
            cell_id="BOGUS.cell.id", sends=10, replies=5
        )
        valid = cell_id("EXECUTIVE", "initial", "question")
        ledger.posteriors[valid] = CellPosterior(cell_id=valid, sends=20, replies=4)
        n = store.save(ledger)
        assert n == 1
        assert store.cell_count() == 1

    def test_invalid_cells_skipped_on_load(
        self, store: ReplyLedgerStore, store_path: Path
    ) -> None:
        # Manually inject an invalid row into the on-disk SQLite.
        with sqlite3.connect(store_path) as conn:
            conn.execute(
                "INSERT INTO reply_feedback_ledger VALUES (?, ?, ?, ?, ?)",
                ("BOGUS.cell.id", 5, 1, None, LATTICE_FINGERPRINT),
            )
            valid = cell_id("EXECUTIVE", "initial", "question")
            conn.execute(
                "INSERT INTO reply_feedback_ledger VALUES (?, ?, ?, ?, ?)",
                (valid, 10, 3, None, LATTICE_FINGERPRINT),
            )
            conn.commit()
        loaded = store.load()
        assert "BOGUS.cell.id" not in loaded.posteriors
        valid = cell_id("EXECUTIVE", "initial", "question")
        assert valid in loaded.posteriors


class TestFingerprintDrift:
    def test_drift_warning_emitted(
        self, store: ReplyLedgerStore, store_path: Path
    ) -> None:
        # Inject a row with a stale fingerprint.
        with sqlite3.connect(store_path) as conn:
            valid = cell_id("EXECUTIVE", "initial", "question")
            conn.execute(
                "INSERT INTO reply_feedback_ledger VALUES (?, ?, ?, ?, ?)",
                (valid, 5, 1, None, "stale_fingerprint_abc123"),
            )
            conn.commit()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            store.load()
            assert any(issubclass(rec.category, LatticeFingerprintDrift) for rec in w)

    def test_no_warning_when_fingerprint_matches(
        self,
        store: ReplyLedgerStore,
        populated_ledger: ReplyFeedbackLedger,
    ) -> None:
        store.save(populated_ledger)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            store.load()
            drift_warnings = [
                rec for rec in w if issubclass(rec.category, LatticeFingerprintDrift)
            ]
            assert drift_warnings == []
