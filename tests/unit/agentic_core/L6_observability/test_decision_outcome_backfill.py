"""Unit tests for ``agentic_core.L6_observability.decision_outcome_backfill``.

Plan: ``.windsurf/plans/routing-decision-process-enhancement-9c7e4d.md`` Wave W2.
"""

from __future__ import annotations

import sqlite3
import time
import uuid
from collections.abc import Iterator

import pytest

from agentic_core.L6_observability.decision_events_schema import (
    DecisionEventRow,
    ensure_schema,
    insert_decision_event,
)
from agentic_core.L6_observability.decision_outcome_backfill import (
    LAG_BUCKETS_SECONDS,
    DecisionRowMissingError,
    OutcomeBackfillConflictError,
    backfill_outcome,
    lag_summary,
    reset_lag_state,
)


@pytest.fixture(autouse=True)
def _reset_lag_state() -> Iterator[None]:
    reset_lag_state()
    yield
    reset_lag_state()


def _seed(conn: sqlite3.Connection, *, ts: float | None = None) -> str:
    """Insert a decision row and return its decision_id."""
    decision_id = str(uuid.uuid4())
    row = DecisionEventRow(
        decision_id=decision_id,
        timestamp=ts if ts is not None else time.time(),
        decision_layer="L0_routing",
        app_name="test_app",
        request_hash="abc",
        chosen_route="R3",
        policy_hash="p1",
        snapshot_id="s1",
        calibration_version="c1",
        judge_version="j1",
        provenance_digest="d1",
        confidence_score=0.71,
    )
    insert_decision_event(conn, row)
    return decision_id


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    ensure_schema(conn)
    return conn


def test_backfill_first_write_updates_row_and_emits_lag() -> None:
    conn = _conn()
    ts = time.time() - 7.5  # 7.5 s old
    decision_id = _seed(conn, ts=ts)
    result = backfill_outcome(conn, decision_id, True, latency_ms_total=42)
    assert result["updated"] is True
    assert result["no_op"] is False
    assert result["lag_seconds"] == pytest.approx(7.5, abs=0.5)

    summary = lag_summary()
    assert summary.sample_count == 1
    # 7.5 s falls in the 10-s bucket
    assert summary.bucket_counts[10.0] == 1

    fetched = conn.execute(
        "SELECT outcome_success, latency_ms, outcome_backfill_ts FROM decision_events WHERE decision_id = ?",
        (decision_id,),
    ).fetchone()
    assert fetched[0] == 1
    assert fetched[1] == 42
    assert fetched[2] is not None


def test_backfill_idempotent_same_outcome_is_noop() -> None:
    conn = _conn()
    decision_id = _seed(conn)
    first = backfill_outcome(conn, decision_id, True, latency_ms_total=10)
    second = backfill_outcome(conn, decision_id, True, latency_ms_total=10)
    assert first["updated"] is True
    assert second["no_op"] is True
    assert second["updated"] is False
    summary = lag_summary()
    # Only the first call emitted lag
    assert summary.sample_count == 1


def test_backfill_conflict_raises() -> None:
    conn = _conn()
    decision_id = _seed(conn)
    backfill_outcome(conn, decision_id, True)
    with pytest.raises(OutcomeBackfillConflictError):
        backfill_outcome(conn, decision_id, False)


def test_backfill_missing_row_raises() -> None:
    conn = _conn()
    with pytest.raises(DecisionRowMissingError):
        backfill_outcome(conn, "ghost-id", True)


def test_backfill_does_not_overwrite_existing_latency() -> None:
    conn = _conn()
    decision_id = _seed(conn)
    # First backfill writes latency=100
    backfill_outcome(conn, decision_id, False, latency_ms_total=100, error_code="E1")
    # Second backfill (e.g. retry on transient error) tries latency=999, error=E2
    # — both pre-existing values must be preserved.
    backfill_outcome(conn, decision_id, False, latency_ms_total=999, error_code="E2")
    fetched = conn.execute(
        "SELECT latency_ms, error_code FROM decision_events WHERE decision_id = ?",
        (decision_id,),
    ).fetchone()
    assert fetched == (100, "E1")


def test_lag_buckets_match_published_constant() -> None:
    """The fallback histogram must use the documented bucket boundaries."""
    conn = _conn()
    decision_id = _seed(conn, ts=time.time() - 2000.0)  # > 1800 → overflow
    backfill_outcome(conn, decision_id, True)
    summary = lag_summary()
    assert summary.overflow_count == 1
    assert summary.sample_count == 1
    # Sanity — bucket dict has every documented boundary
    assert set(summary.bucket_counts.keys()) == set(LAG_BUCKETS_SECONDS)


def test_lag_summary_mean_seconds() -> None:
    conn = _conn()
    d1 = _seed(conn, ts=time.time() - 1.0)
    d2 = _seed(conn, ts=time.time() - 9.0)
    backfill_outcome(conn, d1, True)
    backfill_outcome(conn, d2, True)
    summary = lag_summary()
    assert summary.sample_count == 2
    assert summary.mean_seconds == pytest.approx(5.0, abs=1.0)
