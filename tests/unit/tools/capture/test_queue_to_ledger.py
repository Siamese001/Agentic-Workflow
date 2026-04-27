"""Unit tests for tools.capture.queue_to_ledger.

Exercises every disposition (captured, skipped_dup, deferred_scope, next_step,
failed), malformed input handling, missing / empty queue, dry-run mode, and
the microsecond+counter rotation collision fix.
"""

# pylint: disable=redefined-outer-name,unused-argument

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO))

from tools.capture import queue_to_ledger as qtl


# ---------------------------------------------------------------------------
# load_queue
# ---------------------------------------------------------------------------

class TestLoadQueue:
    def test_missing_file_returns_empty(self, tmp_path):
        assert qtl.load_queue(tmp_path / "does_not_exist.jsonl") == []

    def test_empty_file_returns_empty(self, tmp_path):
        p = tmp_path / "empty.jsonl"
        p.write_text("", encoding="utf-8")
        assert qtl.load_queue(p) == []

    def test_valid_rows_loaded(self, tmp_path):
        p = tmp_path / "q.jsonl"
        rows = [
            {"raw": "DECISION_CAPTURED: type=a, x=1", "marker_type": "DECISION_CAPTURED"},
            {"raw": "NEXT_STEP: plan=foo title=x priority=P3 est_tokens=1 reason=x",
             "marker_type": "NEXT_STEP"},
        ]
        p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        out = qtl.load_queue(p)
        assert len(out) == 2
        assert out[0]["marker_type"] == "DECISION_CAPTURED"

    def test_malformed_json_line_skipped_with_warn(self, tmp_path, capsys):
        p = tmp_path / "q.jsonl"
        p.write_text(
            json.dumps({"raw": "DECISION_CAPTURED: type=x, a=b", "marker_type": "DECISION_CAPTURED"})
            + "\nnot-json-at-all\n"
            + json.dumps({"raw": "DECISION_CAPTURED: type=y, a=c", "marker_type": "DECISION_CAPTURED"})
            + "\n",
            encoding="utf-8",
        )
        out = qtl.load_queue(p)
        assert len(out) == 2  # the malformed line is skipped, not fatal
        err = capsys.readouterr().err
        assert "malformed JSON" in err

    def test_missing_raw_field_skipped(self, tmp_path, capsys):
        p = tmp_path / "q.jsonl"
        p.write_text(json.dumps({"marker_type": "DECISION_CAPTURED"}) + "\n", encoding="utf-8")
        out = qtl.load_queue(p)
        assert out == []
        assert "missing 'raw'" in capsys.readouterr().err

    def test_non_dict_json_skipped(self, tmp_path, capsys):
        p = tmp_path / "q.jsonl"
        p.write_text("[1,2,3]\n", encoding="utf-8")
        out = qtl.load_queue(p)
        assert out == []

    def test_blank_lines_tolerated(self, tmp_path):
        p = tmp_path / "q.jsonl"
        row = json.dumps({"raw": "DECISION_CAPTURED: type=x, a=b",
                          "marker_type": "DECISION_CAPTURED"})
        p.write_text("\n\n" + row + "\n\n", encoding="utf-8")
        assert len(qtl.load_queue(p)) == 1


# ---------------------------------------------------------------------------
# drain — disposition accounting
# ---------------------------------------------------------------------------

class TestDrainAccounting:
    def test_empty_queue_returns_zero_counts(self, tmp_path):
        counts = qtl.drain(tmp_path / "missing.jsonl")
        assert counts == {
            "total": 0, "captured": 0, "skipped_dup": 0,
            "deferred_scope": 0, "next_step": 0, "failed": 0,
        }

    def test_deferred_scope_tracked_separately(self, tmp_path, monkeypatch):
        p = tmp_path / "q.jsonl"
        p.write_text(
            json.dumps({"raw": "DEFERRED_SCOPE: plan=foo wave=W1 phase=P1",
                        "marker_type": "DEFERRED_SCOPE"}) + "\n",
            encoding="utf-8",
        )
        # Stub _init_db with an in-memory conn so we don't touch the real ledger.
        monkeypatch.setattr(qtl, "_init_db", lambda: sqlite3.connect(":memory:"))
        # detect_and_capture must never be called for DEFERRED_SCOPE markers.
        called = {"n": 0}

        def _fail_if_called(*_a, **_kw):
            called["n"] += 1
            return False

        monkeypatch.setattr(qtl, "detect_and_capture", _fail_if_called)
        counts = qtl.drain(p)
        assert counts["deferred_scope"] == 1
        assert counts["captured"] == 0
        assert counts["skipped_dup"] == 0
        assert called["n"] == 0  # drain must not call detect_and_capture for DEFERRED

    def test_next_step_tracked_separately(self, tmp_path, monkeypatch):
        p = tmp_path / "q.jsonl"
        p.write_text(
            json.dumps({
                "raw": "NEXT_STEP: plan=foo title=x priority=P3 est_tokens=1 reason=x",
                "marker_type": "NEXT_STEP",
            }) + "\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(qtl, "_init_db", lambda: sqlite3.connect(":memory:"))
        monkeypatch.setattr(qtl, "detect_and_capture", lambda *_a, **_kw: False)
        counts = qtl.drain(p)
        assert counts["next_step"] == 1

    def test_captured_vs_skipped_dup(self, tmp_path, monkeypatch):
        p = tmp_path / "q.jsonl"
        p.write_text(
            json.dumps({"raw": "DECISION_CAPTURED: type=a, x=1",
                        "marker_type": "DECISION_CAPTURED"}) + "\n"
            + json.dumps({"raw": "DECISION_CAPTURED: type=a, x=1",
                          "marker_type": "DECISION_CAPTURED"}) + "\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(qtl, "_init_db", lambda: sqlite3.connect(":memory:"))
        call_count = {"n": 0}

        def alt(*_a, **_kw):
            call_count["n"] += 1
            return call_count["n"] == 1  # first is new, second is dup

        monkeypatch.setattr(qtl, "detect_and_capture", alt)
        counts = qtl.drain(p)
        assert counts["captured"] == 1
        assert counts["skipped_dup"] == 1

    def test_failed_row_isolated(self, tmp_path, monkeypatch):
        p = tmp_path / "q.jsonl"
        p.write_text(
            json.dumps({"raw": "DECISION_CAPTURED: type=a, x=1",
                        "marker_type": "DECISION_CAPTURED"}) + "\n"
            + json.dumps({"raw": "DECISION_CAPTURED: type=b, x=2",
                          "marker_type": "DECISION_CAPTURED"}) + "\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(qtl, "_init_db", lambda: sqlite3.connect(":memory:"))

        def mixed(text, *_a, **_kw):
            if "type=b" in text:
                raise sqlite3.Error("forced failure for test")
            return True

        monkeypatch.setattr(qtl, "detect_and_capture", mixed)
        counts = qtl.drain(p)
        assert counts["captured"] == 1
        assert counts["failed"] == 1
        # failed rows leave queue in place (not rotated)
        assert p.exists(), "queue should not be rotated on failure"

    def test_dry_run_no_db_write_no_rotation(self, tmp_path, monkeypatch):
        p = tmp_path / "q.jsonl"
        p.write_text(
            json.dumps({"raw": "DECISION_CAPTURED: type=a, x=1",
                        "marker_type": "DECISION_CAPTURED"}) + "\n",
            encoding="utf-8",
        )
        called = {"n": 0}
        monkeypatch.setattr(qtl, "_init_db",
                            lambda: (called.__setitem__("n", called["n"] + 1) or sqlite3.connect(":memory:")))
        monkeypatch.setattr(qtl, "detect_and_capture", lambda *_a, **_kw: True)
        counts = qtl.drain(p, dry_run=True)
        assert counts["total"] == 1
        assert counts["captured"] == 0
        assert called["n"] == 0  # _init_db not called in dry-run
        assert p.exists()  # no rotation


# ---------------------------------------------------------------------------
# Rotation collision regression
# ---------------------------------------------------------------------------

class TestRotationCollision:
    def test_two_rapid_drains_do_not_collide(self, tmp_path, monkeypatch):
        """Regression: two drains in the same UTC second must not raise."""
        monkeypatch.setattr(qtl, "_init_db", lambda: sqlite3.connect(":memory:"))
        monkeypatch.setattr(qtl, "detect_and_capture", lambda *_a, **_kw: True)

        def write_and_drain():
            p = tmp_path / "markers.jsonl"
            p.write_text(
                json.dumps({"raw": "DECISION_CAPTURED: type=x, a=b",
                            "marker_type": "DECISION_CAPTURED"}) + "\n",
                encoding="utf-8",
            )
            return qtl.drain(p)

        # Call twice in rapid succession
        c1 = write_and_drain()
        c2 = write_and_drain()
        assert c1["captured"] == 1
        assert c2["captured"] == 1
        # Two distinct rotated files should now exist
        rotated = list(tmp_path.glob("markers.*.processed.jsonl"))
        assert len(rotated) == 2
