"""Tests for ask_user_question weekly calibration report — D2.

Plan: ask-user-question-shadow-loop-wiring-b4e1f7, D2.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from ops_scripts.calibration.ask_user_question_weekly_report import (
    ConfidenceBand,
    ContextBreakdown,
    WeeklyReport,
    generate_report,
    render_markdown,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_db(tmp_path: Path) -> Path:
    """Create a temporary SQLite DB with ask_user_question_decisions table."""
    db = tmp_path / "test_weekly.sqlite"
    conn = sqlite3.connect(str(db))
    conn.execute("""
        CREATE TABLE ask_user_question_decisions (
            decision_id TEXT PRIMARY KEY,
            context TEXT,
            question TEXT,
            option_count INTEGER,
            recommended_index INTEGER,
            selected_index INTEGER,
            confidence_source TEXT,
            confidence_score REAL,
            invariants TEXT,
            packet_json TEXT,
            created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
        )
    """)
    conn.commit()
    conn.close()
    return db


def _insert(
    db: Path,
    decision_id: str,
    context: str,
    rec: int,
    sel: int | None,
    conf: float,
    created_at: str | None = None,
) -> None:
    conn = sqlite3.connect(str(db))
    ts = created_at or datetime.now(timezone.utc).isoformat()
    conn.execute(
        """INSERT INTO ask_user_question_decisions
           (decision_id, context, question, option_count, recommended_index,
            selected_index, confidence_source, confidence_score, invariants, created_at)
           VALUES (?, ?, 'Which?', 2, ?, ?, 'explicit', ?, '["confidence_prefix"]', ?)""",
        (decision_id, context, rec, sel, conf, ts),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Empty / missing DB
# ---------------------------------------------------------------------------


class TestEmptyReport:
    def test_missing_db_returns_zero_report(self, tmp_path: Path):
        r = generate_report(db_path=tmp_path / "nope.sqlite")
        assert r.total_decisions == 0
        assert r.acceptance_rate == 0.0

    def test_empty_table_returns_zero(self, tmp_db: Path):
        r = generate_report(db_path=tmp_db)
        assert r.total_decisions == 0


# ---------------------------------------------------------------------------
# Core metrics
# ---------------------------------------------------------------------------


class TestCoreMetrics:
    def test_all_accepted(self, tmp_db: Path):
        now = datetime.now(timezone.utc)
        for i in range(5):
            ts = (now - timedelta(hours=i + 1)).isoformat()
            _insert(tmp_db, f"d{i}", "ctx", rec=0, sel=0, conf=0.85, created_at=ts)
        r = generate_report(db_path=tmp_db, reference_date=now)
        assert r.total_decisions == 5
        assert r.total_accepted == 5
        assert r.total_overridden == 0
        assert r.acceptance_rate == 1.0

    def test_all_overridden(self, tmp_db: Path):
        now = datetime.now(timezone.utc)
        for i in range(3):
            ts = (now - timedelta(hours=i + 1)).isoformat()
            _insert(tmp_db, f"d{i}", "ctx", rec=0, sel=1, conf=0.70, created_at=ts)
        r = generate_report(db_path=tmp_db, reference_date=now)
        assert r.total_overridden == 3
        assert r.override_rate == 1.0

    def test_pending_tracked_separately(self, tmp_db: Path):
        now = datetime.now(timezone.utc)
        ts = (now - timedelta(hours=1)).isoformat()
        _insert(tmp_db, "d0", "ctx", rec=0, sel=None, conf=0.8, created_at=ts)
        r = generate_report(db_path=tmp_db, reference_date=now)
        assert r.total_pending == 1
        assert r.total_accepted == 0
        assert r.acceptance_rate == 0.0

    def test_mixed(self, tmp_db: Path):
        now = datetime.now(timezone.utc)
        _insert(tmp_db, "d0", "ctx", rec=0, sel=0, conf=0.85, created_at=(now - timedelta(hours=1)).isoformat())
        _insert(tmp_db, "d1", "ctx", rec=0, sel=1, conf=0.70, created_at=(now - timedelta(hours=2)).isoformat())
        _insert(tmp_db, "d2", "ctx", rec=0, sel=None, conf=0.60, created_at=(now - timedelta(hours=3)).isoformat())
        r = generate_report(db_path=tmp_db, reference_date=now)
        assert r.total_decisions == 3
        assert r.total_accepted == 1
        assert r.total_overridden == 1
        assert r.total_pending == 1
        assert r.acceptance_rate == 0.5  # 1 of 2 resolved

    def test_avg_confidence(self, tmp_db: Path):
        now = datetime.now(timezone.utc)
        _insert(tmp_db, "d0", "ctx", rec=0, sel=0, conf=0.80, created_at=(now - timedelta(hours=1)).isoformat())
        _insert(tmp_db, "d1", "ctx", rec=0, sel=0, conf=0.90, created_at=(now - timedelta(hours=2)).isoformat())
        r = generate_report(db_path=tmp_db, reference_date=now)
        assert abs(r.avg_confidence - 0.85) < 0.01


# ---------------------------------------------------------------------------
# Time window filtering
# ---------------------------------------------------------------------------


class TestTimeWindow:
    def test_old_rows_excluded(self, tmp_db: Path):
        now = datetime.now(timezone.utc)
        old_ts = (now - timedelta(days=10)).isoformat()
        recent_ts = (now - timedelta(hours=1)).isoformat()
        _insert(tmp_db, "old", "ctx", rec=0, sel=0, conf=0.8, created_at=old_ts)
        _insert(tmp_db, "recent", "ctx", rec=0, sel=0, conf=0.9, created_at=recent_ts)
        r = generate_report(db_path=tmp_db, reference_date=now)
        assert r.total_decisions == 1


# ---------------------------------------------------------------------------
# Confidence bands
# ---------------------------------------------------------------------------


class TestConfidenceBands:
    def test_bands_populated(self, tmp_db: Path):
        now = datetime.now(timezone.utc)
        _insert(tmp_db, "d0", "ctx", rec=0, sel=0, conf=0.65, created_at=(now - timedelta(hours=1)).isoformat())
        _insert(tmp_db, "d1", "ctx", rec=0, sel=1, conf=0.85, created_at=(now - timedelta(hours=2)).isoformat())
        r = generate_report(db_path=tmp_db, reference_date=now)
        assert len(r.confidence_bands) == 2
        labels = {b.band_label for b in r.confidence_bands}
        assert "0.60-0.70" in labels
        assert "0.80-0.90" in labels

    def test_band_acceptance_rate(self, tmp_db: Path):
        now = datetime.now(timezone.utc)
        for i in range(4):
            sel = 0 if i < 3 else 1
            _insert(tmp_db, f"d{i}", "ctx", rec=0, sel=sel, conf=0.85, created_at=(now - timedelta(hours=i + 1)).isoformat())
        r = generate_report(db_path=tmp_db, reference_date=now)
        band = [b for b in r.confidence_bands if b.band_label == "0.80-0.90"][0]
        assert band.total == 4
        assert band.accepted == 3
        assert band.overridden == 1
        assert band.acceptance_rate == 0.75


# ---------------------------------------------------------------------------
# Context breakdown
# ---------------------------------------------------------------------------


class TestContextBreakdown:
    def test_multiple_contexts(self, tmp_db: Path):
        now = datetime.now(timezone.utc)
        _insert(tmp_db, "d0", "alpha", rec=0, sel=0, conf=0.8, created_at=(now - timedelta(hours=1)).isoformat())
        _insert(tmp_db, "d1", "alpha", rec=0, sel=1, conf=0.7, created_at=(now - timedelta(hours=2)).isoformat())
        _insert(tmp_db, "d2", "beta", rec=0, sel=0, conf=0.9, created_at=(now - timedelta(hours=3)).isoformat())
        r = generate_report(db_path=tmp_db, reference_date=now)
        assert len(r.context_breakdown) == 2
        alpha = [c for c in r.context_breakdown if c.context == "alpha"][0]
        assert alpha.total == 2
        assert alpha.accepted == 1
        assert alpha.acceptance_rate == 0.5


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


class TestMarkdownRender:
    def test_contains_header(self, tmp_db: Path):
        r = generate_report(db_path=tmp_db)
        md = render_markdown(r)
        assert "# Ask-User-Question Weekly Calibration" in md

    def test_contains_summary_table(self, tmp_db: Path):
        now = datetime.now(timezone.utc)
        _insert(tmp_db, "d0", "ctx", rec=0, sel=0, conf=0.8, created_at=(now - timedelta(hours=1)).isoformat())
        r = generate_report(db_path=tmp_db, reference_date=now)
        md = render_markdown(r)
        assert "Total decisions" in md
        assert "Acceptance rate" in md

    def test_contains_confidence_curve_when_data(self, tmp_db: Path):
        now = datetime.now(timezone.utc)
        _insert(tmp_db, "d0", "ctx", rec=0, sel=0, conf=0.85, created_at=(now - timedelta(hours=1)).isoformat())
        r = generate_report(db_path=tmp_db, reference_date=now)
        md = render_markdown(r)
        assert "Confidence Calibration Curve" in md

    def test_contains_context_breakdown_when_data(self, tmp_db: Path):
        now = datetime.now(timezone.utc)
        _insert(tmp_db, "d0", "ctx", rec=0, sel=0, conf=0.85, created_at=(now - timedelta(hours=1)).isoformat())
        r = generate_report(db_path=tmp_db, reference_date=now)
        md = render_markdown(r)
        assert "Per-Context Calibration Curve" in md


# ---------------------------------------------------------------------------
# JSON serialization
# ---------------------------------------------------------------------------


class TestJsonSerialization:
    def test_to_dict_serializable(self, tmp_db: Path):
        now = datetime.now(timezone.utc)
        _insert(tmp_db, "d0", "ctx", rec=0, sel=0, conf=0.85, created_at=(now - timedelta(hours=1)).isoformat())
        r = generate_report(db_path=tmp_db, reference_date=now)
        d = r.to_dict()
        serialized = json.dumps(d)
        assert '"week_label"' in serialized
        assert '"confidence_bands"' in serialized
        assert '"context_breakdown"' in serialized

    def test_to_dict_keys(self, tmp_db: Path):
        r = generate_report(db_path=tmp_db)
        d = r.to_dict()
        expected_keys = {
            "week_label", "period_start", "period_end",
            "total_decisions", "total_accepted", "total_overridden", "total_pending",
            "acceptance_rate", "override_rate", "avg_confidence",
            "confidence_bands", "context_breakdown",
        }
        assert set(d.keys()) == expected_keys
