"""Durable L4 write is gated by UWG and nothing else.

These tests use a temp DB so they never touch the real ledger. They prove:
  - an approved run writes exactly one row,
  - the write is idempotent on replay,
  - a run with no UWG-approved commit is REFUSED (fail-closed),
  - the persisted row matches the trace's L4ArchiveRecord.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.runtime import run_workflow  # noqa: E402
from src.runtime.ledger import WriteGateError, commit_run, read_all  # noqa: E402


def test_approved_run_writes_one_row(tmp_path):
    db = tmp_path / "l4.sqlite"
    t = run_workflow("A")
    result = commit_run(t, db_path=db)
    assert result["inserted"] is True
    rows = read_all(db)
    assert len(rows) == 1
    assert rows[0]["archive_id"] == t.l4_archive_record.archive_id
    assert rows[0]["created_by"] == "UWG_APPROVED_COMMIT"
    assert rows[0]["scenario_id"] == "A"


def test_commit_is_idempotent_on_replay(tmp_path):
    db = tmp_path / "l4.sqlite"
    t = run_workflow("A")
    first = commit_run(t, db_path=db)
    second = commit_run(t, db_path=db)  # same deterministic archive_id
    assert first["inserted"] is True
    assert second["inserted"] is False  # OR IGNORE — no duplicate
    assert len(read_all(db)) == 1


def test_b_approved_writes(tmp_path):
    db = tmp_path / "l4.sqlite"
    t = run_workflow("B", "approve")
    commit_run(t, db_path=db)
    rows = read_all(db)
    assert len(rows) == 1
    assert rows[0]["scenario_id"] == "B"


@pytest.mark.parametrize(
    "sid,dec",
    [
        ("C", None),            # conflicted -> abstain, no UWG
        ("B", None),            # awaiting reviewer -> no UWG
        ("B", "reject"),        # reviewer rejected -> no UWG
        ("B", "request_more_evidence"),  # -> abstain, no UWG
    ],
)
def test_no_uwg_means_write_refused(tmp_path, sid, dec):
    db = tmp_path / "l4.sqlite"
    t = run_workflow(sid, dec)
    assert t.uwg_validation_result is None
    with pytest.raises(WriteGateError):
        commit_run(t, db_path=db)
    assert read_all(db) == []


def test_empty_ledger_reads_clean(tmp_path):
    assert read_all(tmp_path / "does_not_exist.sqlite") == []
