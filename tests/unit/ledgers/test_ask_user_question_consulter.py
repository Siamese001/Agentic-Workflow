"""Tests for AskUserQuestionConsulter — D1 integration.

Plan: ask-user-question-shadow-loop-wiring-b4e1f7, D1.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from tools.ledgers.consulter import AskUserQuestionConsulter, AskUserQuestionVerdict


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_db(tmp_path: Path) -> Path:
    """Create a temporary SQLite DB with ask_user_question_decisions table."""
    db = tmp_path / "test_auq.sqlite"
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


def _insert(db: Path, decision_id: str, context: str, rec: int, sel: int | None, conf: float) -> None:
    conn = sqlite3.connect(str(db))
    conn.execute(
        """INSERT INTO ask_user_question_decisions
           (decision_id, context, question, option_count, recommended_index,
            selected_index, confidence_source, confidence_score, invariants)
           VALUES (?, ?, 'Which?', 2, ?, ?, 'explicit', ?, '["confidence_prefix"]')""",
        (decision_id, context, rec, sel, conf),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# LedgerSpec registration
# ---------------------------------------------------------------------------


class TestLedgerSpecRegistration:
    """Verify ask_user_question is registered in the schema registry."""

    def test_spec_registered(self):
        from tools.ledgers.schema_registry import LEDGER_REGISTRY
        names = [s.name for s in LEDGER_REGISTRY]
        assert "ask_user_question" in names

    def test_spec_schema_file_exists(self):
        from tools.ledgers.schema_registry import get
        spec = get("ask_user_question")
        assert spec.schema_path.exists(), f"Missing: {spec.schema_path}"

    def test_spec_fields(self):
        from tools.ledgers.schema_registry import get
        spec = get("ask_user_question")
        assert spec.writer_hook == "tools/ledgers/ask_user_question_ledger.py"
        assert "ledger-consulter-ask-user-question" in spec.consulting_skill
        assert spec.purpose


# ---------------------------------------------------------------------------
# AskUserQuestionConsulter
# ---------------------------------------------------------------------------


class TestAskUserQuestionConsulterEmpty:
    """Edge cases — empty or missing DB."""

    def test_missing_db_returns_none_verdict(self, tmp_path: Path):
        c = AskUserQuestionConsulter(db_path=tmp_path / "nonexistent.sqlite")
        v = c.lookup()
        assert v.strength == "none"
        assert v.matches == []
        assert v.acceptance_rate == 0.0

    def test_empty_table_returns_none(self, tmp_db: Path):
        c = AskUserQuestionConsulter(db_path=tmp_db)
        v = c.lookup()
        assert v.strength == "none"
        assert v.total_rows_examined == 0


class TestAskUserQuestionConsulterAcceptance:
    """Acceptance rate calculations."""

    def test_all_accepted(self, tmp_db: Path):
        for i in range(5):
            _insert(tmp_db, f"d{i}", "ctx-a", rec=0, sel=0, conf=0.85)
        c = AskUserQuestionConsulter(db_path=tmp_db)
        v = c.lookup(context="ctx-a")
        assert v.acceptance_rate == 1.0
        assert v.override_rate == 0.0
        assert v.strength == "strong"

    def test_all_overridden(self, tmp_db: Path):
        for i in range(5):
            _insert(tmp_db, f"d{i}", "ctx-b", rec=0, sel=1, conf=0.75)
        c = AskUserQuestionConsulter(db_path=tmp_db)
        v = c.lookup(context="ctx-b")
        assert v.acceptance_rate == 0.0
        assert v.override_rate == 1.0

    def test_mixed_acceptance(self, tmp_db: Path):
        _insert(tmp_db, "d0", "ctx-c", rec=0, sel=0, conf=0.8)
        _insert(tmp_db, "d1", "ctx-c", rec=0, sel=1, conf=0.7)
        _insert(tmp_db, "d2", "ctx-c", rec=1, sel=1, conf=0.9)
        c = AskUserQuestionConsulter(db_path=tmp_db)
        v = c.lookup(context="ctx-c")
        # 2 out of 3 accepted
        assert abs(v.acceptance_rate - 2 / 3) < 0.01

    def test_pending_selections_excluded(self, tmp_db: Path):
        _insert(tmp_db, "d0", "ctx-d", rec=0, sel=0, conf=0.8)
        _insert(tmp_db, "d1", "ctx-d", rec=0, sel=None, conf=0.8)
        c = AskUserQuestionConsulter(db_path=tmp_db)
        v = c.lookup(context="ctx-d")
        # Only d0 has both rec and sel
        assert v.acceptance_rate == 1.0


class TestAskUserQuestionConsulterGrading:
    """Verdict strength grading."""

    def test_strong_verdict_requires_volume_and_alignment(self, tmp_db: Path):
        for i in range(6):
            _insert(tmp_db, f"d{i}", "ctx", rec=0, sel=0, conf=0.85)
        c = AskUserQuestionConsulter(db_path=tmp_db)
        v = c.lookup(context="ctx")
        assert v.strength == "strong"

    def test_suggestive_with_few_rows(self, tmp_db: Path):
        _insert(tmp_db, "d0", "ctx", rec=0, sel=0, conf=0.85)
        _insert(tmp_db, "d1", "ctx", rec=0, sel=0, conf=0.85)
        c = AskUserQuestionConsulter(db_path=tmp_db)
        v = c.lookup(context="ctx")
        assert v.strength == "suggestive"

    def test_suggestive_with_low_acceptance(self, tmp_db: Path):
        for i in range(10):
            sel = 0 if i < 3 else 1
            _insert(tmp_db, f"d{i}", "ctx", rec=0, sel=sel, conf=0.7)
        c = AskUserQuestionConsulter(db_path=tmp_db)
        v = c.lookup(context="ctx")
        assert v.strength == "suggestive"


class TestAskUserQuestionConsulterConfidence:
    """Average confidence calculation."""

    def test_avg_confidence(self, tmp_db: Path):
        _insert(tmp_db, "d0", "ctx", rec=0, sel=0, conf=0.80)
        _insert(tmp_db, "d1", "ctx", rec=0, sel=0, conf=0.90)
        c = AskUserQuestionConsulter(db_path=tmp_db)
        v = c.lookup(context="ctx")
        assert abs(v.avg_confidence - 0.85) < 0.01


class TestAskUserQuestionConsulterFiltering:
    """Context filtering."""

    def test_context_filter(self, tmp_db: Path):
        _insert(tmp_db, "d0", "alpha", rec=0, sel=0, conf=0.8)
        _insert(tmp_db, "d1", "beta", rec=0, sel=1, conf=0.7)
        c = AskUserQuestionConsulter(db_path=tmp_db)
        v = c.lookup(context="alpha")
        assert len(v.matches) == 1
        assert v.matches[0]["context"] == "alpha"

    def test_no_context_returns_all(self, tmp_db: Path):
        _insert(tmp_db, "d0", "alpha", rec=0, sel=0, conf=0.8)
        _insert(tmp_db, "d1", "beta", rec=0, sel=1, conf=0.7)
        c = AskUserQuestionConsulter(db_path=tmp_db)
        v = c.lookup()
        assert len(v.matches) == 2

    def test_limit_respected(self, tmp_db: Path):
        for i in range(20):
            _insert(tmp_db, f"d{i}", "ctx", rec=0, sel=0, conf=0.8)
        c = AskUserQuestionConsulter(db_path=tmp_db)
        v = c.lookup(context="ctx", limit=5)
        assert len(v.matches) == 5
        assert v.total_rows_examined == 20


class TestAskUserQuestionVerdictShape:
    """Verdict as_dict shape."""

    def test_as_dict_keys(self):
        v = AskUserQuestionVerdict(strength="none")
        d = v.as_dict()
        assert set(d.keys()) == {
            "strength", "match_count", "total_rows_examined",
            "acceptance_rate", "override_rate", "avg_confidence", "matches",
        }

    def test_as_dict_round_trips(self, tmp_db: Path):
        for i in range(3):
            _insert(tmp_db, f"d{i}", "ctx", rec=0, sel=0, conf=0.85)
        c = AskUserQuestionConsulter(db_path=tmp_db)
        v = c.lookup(context="ctx")
        d = v.as_dict()
        assert d["strength"] == "suggestive"
        assert d["match_count"] == 3
        assert d["acceptance_rate"] == 1.0
        # Verify JSON-serializable
        json.dumps(d)
