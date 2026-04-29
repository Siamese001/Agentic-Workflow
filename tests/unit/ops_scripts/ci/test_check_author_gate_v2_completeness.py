"""Tests for ops_scripts.ci.check_author_gate_v2_completeness (plan 1f4c8a W5)."""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve()
_GATE_PATH = _HERE.parents[4] / "ops_scripts" / "ci" / "check_author_gate_v2_completeness.py"
_spec = importlib.util.spec_from_file_location("_v2_gate", _GATE_PATH)
assert _spec is not None and _spec.loader is not None
_gate = importlib.util.module_from_spec(_spec)
sys.modules["_v2_gate"] = _gate
_spec.loader.exec_module(_gate)


def _bootstrap(db: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db))
    conn.execute(
        """
        CREATE TABLE decisions (
            decision_id TEXT PRIMARY KEY,
            created_at TEXT,
            decision_type TEXT,
            confidence_top REAL,
            confidence_dominance_gap REAL,
            principle_at_stake TEXT,
            precedent_verdict TEXT,
            sig_alg TEXT,
            signature TEXT,
            status TEXT
        )
        """
    )
    conn.commit()
    return conn


def _insert(
    conn: sqlite3.Connection,
    *,
    decision_id: str,
    days_ago: float,
    decision_type: str = "architecture_choice",
    confidence_top: float | None = 0.85,
    gap: float | None = 0.20,
    principle: str | None = "test-principle",
    precedent: str | None = "none",
    sig_alg: str | None = "hmac-sha256",
    signature: str | None = "abc123",
    status: str = "executed",
) -> None:
    ts = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
    conn.execute(
        "INSERT INTO decisions VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            decision_id,
            ts,
            decision_type,
            confidence_top,
            gap,
            principle,
            precedent,
            sig_alg,
            signature,
            status,
        ),
    )
    conn.commit()


def test_pass_when_all_fields_present(tmp_path: Path) -> None:
    db = tmp_path / "ledger.sqlite"
    conn = _bootstrap(db)
    _insert(conn, decision_id="dec_1", days_ago=1)
    conn.close()
    rc, _ = _gate.check(db, window_days=7)
    assert rc == 0


def test_fail_when_principle_missing(tmp_path: Path) -> None:
    db = tmp_path / "ledger.sqlite"
    conn = _bootstrap(db)
    _insert(conn, decision_id="dec_2", days_ago=1, principle=None)
    conn.close()
    rc, msgs = _gate.check(db, window_days=7)
    assert rc == 1
    assert any("principle_at_stake" in m for m in msgs)


def test_fail_when_precedent_missing(tmp_path: Path) -> None:
    db = tmp_path / "ledger.sqlite"
    conn = _bootstrap(db)
    _insert(conn, decision_id="dec_3", days_ago=1, precedent=None)
    conn.close()
    rc, msgs = _gate.check(db, window_days=7)
    assert rc == 1
    assert any("precedent_verdict" in m for m in msgs)


def test_fail_when_signature_missing(tmp_path: Path) -> None:
    db = tmp_path / "ledger.sqlite"
    conn = _bootstrap(db)
    _insert(conn, decision_id="dec_4", days_ago=1, signature=None, sig_alg=None)
    conn.close()
    rc, msgs = _gate.check(db, window_days=7)
    assert rc == 1
    assert any("signature/sig_alg" in m for m in msgs)


def test_fail_when_executed_lacks_confidence(tmp_path: Path) -> None:
    db = tmp_path / "ledger.sqlite"
    conn = _bootstrap(db)
    _insert(conn, decision_id="dec_5", days_ago=1, confidence_top=None)
    conn.close()
    rc, msgs = _gate.check(db, window_days=7)
    assert rc == 1
    assert any("confidence_top" in m for m in msgs)


def test_pass_when_surfaced_lacks_confidence(tmp_path: Path) -> None:
    """Non-executed (status='surfaced') rows don't require confidence — silent-marker exemption."""
    db = tmp_path / "ledger.sqlite"
    conn = _bootstrap(db)
    _insert(conn, decision_id="dec_6", days_ago=1, status="surfaced", confidence_top=None, gap=None)
    conn.close()
    rc, _ = _gate.check(db, window_days=7)
    assert rc == 0


def test_skip_pre_v2_landing_rows(tmp_path: Path) -> None:
    """Rows older than 2026-04-23 are exempt regardless of window."""
    db = tmp_path / "ledger.sqlite"
    conn = _bootstrap(db)
    # 2026-04-15 is before V2 landing 2026-04-23 — should be skipped even with no fields
    days_ago = (datetime.now(timezone.utc) - datetime(2026, 4, 15, tzinfo=timezone.utc)).days
    _insert(
        conn,
        decision_id="dec_old",
        days_ago=days_ago,
        confidence_top=None,
        gap=None,
        principle=None,
        precedent=None,
    )
    conn.close()
    rc, _ = _gate.check(db, window_days=window_days_for(days_ago + 5))
    assert rc == 0  # window starts at landing date, not cutoff


def test_skip_non_refactor_class(tmp_path: Path) -> None:
    """Non-refactor-class decision_types are not checked."""
    db = tmp_path / "ledger.sqlite"
    conn = _bootstrap(db)
    _insert(conn, decision_id="dec_q", days_ago=1, decision_type="question_answer", principle=None)
    conn.close()
    rc, _ = _gate.check(db, window_days=7)
    assert rc == 0


def test_missing_db_returns_2(tmp_path: Path) -> None:
    db = tmp_path / "missing.sqlite"
    rc, msgs = _gate.check(db, window_days=7)
    assert rc == 2
    assert any("not found" in m for m in msgs)


def test_bypass_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = tmp_path / "ledger.sqlite"
    conn = _bootstrap(db)
    _insert(conn, decision_id="dec_b", days_ago=1, principle=None)  # would fail
    conn.close()
    monkeypatch.setenv("AUTHOR_GATE_V2_BYPASS", "1")
    monkeypatch.setattr(_gate, "DB_PATH", db)
    monkeypatch.setattr(_gate, "BYPASS_LOG", tmp_path / "bypass.jsonl")
    monkeypatch.setattr(sys, "argv", ["check_author_gate_v2_completeness.py"])
    assert _gate.main() == 0


def window_days_for(days: int) -> int:
    """Helper: window large enough to include rows N days ago."""
    return max(days, 7)
