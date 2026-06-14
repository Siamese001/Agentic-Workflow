"""W4 safeguards for author_gate_calibrator — min-n, degenerate NOOP, disputed skip, lineage."""

import json
import sqlite3
from pathlib import Path

import pytest

from ops_scripts.calibration.decision_ledger_calibrator import (
    NOOP_DEGENERATE_LABELS,
    NOOP_STALE_SCHEMA,
    fit_class,
)


def _mk_conn(tmp_path: Path) -> sqlite3.Connection:
    db = tmp_path / "ledger.sqlite"
    conn = sqlite3.connect(str(db))
    conn.executescript(
        """
        CREATE TABLE decisions (
            decision_id TEXT PRIMARY KEY,
            decision_type TEXT,
            confidence_top REAL,
            confidence_calibrated REAL,
            calibrator_version TEXT
        );
        CREATE TABLE decision_outcomes (
            decision_id TEXT PRIMARY KEY,
            promote_to_pattern INTEGER DEFAULT 0,
            rollback_required INTEGER DEFAULT 0,
            regression_found INTEGER DEFAULT 0,
            bind_disputed INTEGER DEFAULT 0,
            outcome_bind_tier TEXT
        );
        CREATE TABLE decision_calibration_snapshots (
            snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            calibrator_version TEXT NOT NULL,
            decision_type TEXT NOT NULL,
            n_outcomes INTEGER NOT NULL,
            brier_score REAL,
            ece_score REAL,
            reliability_json TEXT,
            isotonic_points_json TEXT
        );
        """
    )
    return conn


def _seed_row(
    conn: sqlite3.Connection,
    did: str,
    *,
    x: float,
    prom: int,
    roll: int = 0,
    reg: int = 0,
    disputed: int = 0,
    tier: str | None = None,
) -> None:
    conn.execute(
        "INSERT INTO decisions (decision_id, decision_type, confidence_top) VALUES (?,?,?)",
        (did, "refactor_scope", x),
    )
    conn.execute(
        """INSERT INTO decision_outcomes
           (decision_id, promote_to_pattern, rollback_required, regression_found,
            bind_disputed, outcome_bind_tier)
           VALUES (?,?,?,?,?,?)""",
        (did, prom, roll, reg, disputed, tier),
    )


def test_degenerate_all_success_emits_noop_not_fitted(tmp_path):
    conn = _mk_conn(tmp_path)
    for i in range(5):
        _seed_row(conn, f"d{i}", x=0.5 + i * 0.01, prom=1, roll=0, reg=0)
    conn.commit()

    s = fit_class(
        conn,
        "refactor_scope",
        "iso_test_v1",
        min_n=3,
        apply=False,
        min_positive=1,
        min_negative=1,
        strict_schema=False,
    )
    assert s.get("noop_reason") == NOOP_DEGENERATE_LABELS
    assert s.get("fitted") is False
    conn.close()


def test_degenerate_all_failure_emits_noop(tmp_path):
    conn = _mk_conn(tmp_path)
    for i in range(5):
        _seed_row(conn, f"d{i}", x=0.4, prom=0, roll=0, reg=0)
    conn.commit()

    s = fit_class(
        conn,
        "refactor_scope",
        "iso_test_v1",
        min_n=3,
        apply=False,
        min_positive=1,
        min_negative=1,
        strict_schema=False,
    )
    assert s.get("noop_reason") == NOOP_DEGENERATE_LABELS
    assert s.get("fitted") is False
    conn.close()


def test_min_n_cold_start(tmp_path):
    conn = _mk_conn(tmp_path)
    _seed_row(conn, "d0", x=0.5, prom=1, reg=0, roll=0)
    _seed_row(conn, "d1", x=0.6, prom=0, reg=0, roll=0)
    conn.commit()

    s = fit_class(
        conn,
        "refactor_scope",
        "iso_test_v1",
        min_n=10,
        apply=False,
        min_positive=1,
        min_negative=1,
        strict_schema=False,
    )
    assert s.get("cold_start") is True
    assert s.get("fitted") is False
    conn.close()


def test_mixed_labels_fit_and_lineage_in_summary(tmp_path):
    conn = _mk_conn(tmp_path)
    for i, (x, prom) in enumerate([(0.2, 1), (0.3, 0), (0.7, 1), (0.8, 0), (0.9, 1)]):
        _seed_row(conn, f"d{i}", x=x, prom=prom, roll=0, reg=0)
    conn.commit()

    s = fit_class(
        conn,
        "refactor_scope",
        "iso_test_v1",
        min_n=3,
        apply=False,
        min_positive=1,
        min_negative=1,
        strict_schema=False,
    )
    assert s.get("fitted") is True
    assert s.get("noop_reason") is None
    lj = json.loads(str(s.get("lineage_json")))
    assert lj["policy_version"]
    assert lj["dataset_digest_sha256_16"]
    assert lj["split_policy"] == "full_dataset_isotonic_v1"
    assert lj["disputed_training_rows_excluded"] is True
    conn.close()


def test_disputed_rows_not_used_for_training(tmp_path):
    conn = _mk_conn(tmp_path)
    _seed_row(conn, "clean0", x=0.5, prom=1, roll=0, reg=0, disputed=0, tier="strong_bind")
    _seed_row(conn, "clean1", x=0.5, prom=0, roll=0, reg=0, disputed=0, tier="weak_bind")
    _seed_row(conn, "disp0", x=0.5, prom=1, roll=0, reg=0, disputed=1, tier=None)
    conn.commit()

    s = fit_class(
        conn,
        "refactor_scope",
        "iso_test_v1",
        min_n=3,
        apply=False,
        min_positive=1,
        min_negative=1,
        strict_schema=False,
    )
    assert s["n_outcomes"] == 2
    assert s.get("cold_start") is True


def test_strict_schema_noop_when_outcomes_incomplete(tmp_path):
    db = tmp_path / "partial.sqlite"
    conn = sqlite3.connect(str(db))
    conn.executescript(
        """
        CREATE TABLE decisions (
            decision_id TEXT PRIMARY KEY,
            decision_type TEXT,
            confidence_top REAL
        );
        CREATE TABLE decision_outcomes (
            decision_id TEXT PRIMARY KEY,
            promote_to_pattern INTEGER DEFAULT 0
        );
        """
    )
    conn.execute(
        "INSERT INTO decisions VALUES ('a','refactor_scope',0.5)"
    )
    conn.execute(
        "INSERT INTO decision_outcomes (decision_id, promote_to_pattern) VALUES ('a',1)"
    )
    conn.commit()

    s = fit_class(
        conn,
        "refactor_scope",
        "iso_test_v1",
        min_n=1,
        apply=False,
        min_positive=1,
        min_negative=1,
        strict_schema=True,
    )
    assert s.get("noop_reason") == NOOP_STALE_SCHEMA
    conn.close()
