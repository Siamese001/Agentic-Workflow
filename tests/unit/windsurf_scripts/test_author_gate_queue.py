"""Tests for .claude/governance/scripts/_legacy_windsurf/_author_gate_queue.py"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
HELPER_PATH = REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf" / "_author_gate_queue.py"


def _load_helper(monkeypatch, tmp_path):
    """Load the helper module and redirect STATE_DIR to tmp_path."""
    spec = importlib.util.spec_from_file_location("_ag_queue_test", HELPER_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_ag_queue_test"] = mod
    spec.loader.exec_module(mod)
    # Redirect STATE_DIR
    monkeypatch.setattr(mod, "STATE_DIR", tmp_path / "ag_queue")
    return mod


def test_enqueue_creates_row(monkeypatch, tmp_path):
    ag = _load_helper(monkeypatch, tmp_path)
    ag.enqueue("plan-a", {"id": "P1", "title": "first"})
    assert ag.pending_count("plan-a") == 1
    nxt = ag.next_packet("plan-a")
    assert nxt is not None and nxt["id"] == "P1"
    assert nxt["status"] == "pending"


def test_enqueue_idempotent(monkeypatch, tmp_path):
    ag = _load_helper(monkeypatch, tmp_path)
    ag.enqueue("plan-a", {"id": "P1", "title": "first"})
    ag.enqueue("plan-a", {"id": "P1", "title": "first-dup"})
    assert ag.pending_count("plan-a") == 1


def test_enqueue_requires_id_and_title(monkeypatch, tmp_path):
    ag = _load_helper(monkeypatch, tmp_path)
    with pytest.raises(ValueError):
        ag.enqueue("plan-a", {"title": "no id"})
    with pytest.raises(ValueError):
        ag.enqueue("plan-a", {"id": "P1"})


def test_invalid_slug_rejected(monkeypatch, tmp_path):
    ag = _load_helper(monkeypatch, tmp_path)
    for bad in ("../evil", "a/b", "a\\b", ""):
        with pytest.raises(ValueError):
            ag.enqueue(bad, {"id": "P1", "title": "x"})


def test_next_packet_respects_depends_on(monkeypatch, tmp_path):
    ag = _load_helper(monkeypatch, tmp_path)
    ag.enqueue("plan-a", {"id": "P1", "title": "first"})
    ag.enqueue("plan-a", {"id": "P2", "title": "second", "depends_on": ["P1"]})
    ag.enqueue("plan-a", {"id": "P3", "title": "third", "depends_on": ["P2"]})
    # Head should be P1 (no deps)
    assert ag.next_packet("plan-a")["id"] == "P1"
    ag.mark_answered("plan-a", "P1", "option-a")
    # Now P2 eligible
    assert ag.next_packet("plan-a")["id"] == "P2"
    ag.mark_answered("plan-a", "P2", "option-b")
    assert ag.next_packet("plan-a")["id"] == "P3"
    ag.mark_answered("plan-a", "P3", "option-c")
    assert ag.next_packet("plan-a") is None
    assert ag.pending_count("plan-a") == 0


def test_next_packet_score_tiebreak(monkeypatch, tmp_path):
    ag = _load_helper(monkeypatch, tmp_path)
    ag.enqueue("plan-a", {"id": "A", "title": "a", "score": 0.50})
    ag.enqueue("plan-a", {"id": "B", "title": "b", "score": 0.90})
    ag.enqueue("plan-a", {"id": "C", "title": "c", "score": 0.70})
    # Highest score wins among eligible
    assert ag.next_packet("plan-a")["id"] == "B"


def test_mark_answered_noop_if_not_found(monkeypatch, tmp_path):
    ag = _load_helper(monkeypatch, tmp_path)
    ag.enqueue("plan-a", {"id": "P1", "title": "first"})
    ag.mark_answered("plan-a", "NOPE", "x")
    assert ag.pending_count("plan-a") == 1


def test_missing_file_returns_empty(monkeypatch, tmp_path):
    ag = _load_helper(monkeypatch, tmp_path)
    assert ag.pending_count("never-seen") == 0
    assert ag.next_packet("never-seen") is None
    assert ag.list_plans_with_pending() == []


def test_corrupt_row_skipped(monkeypatch, tmp_path):
    ag = _load_helper(monkeypatch, tmp_path)
    ag.enqueue("plan-a", {"id": "P1", "title": "ok"})
    # Corrupt the state file
    state_dir = tmp_path / "ag_queue"
    f = state_dir / "plan-a.jsonl"
    with f.open("a", encoding="utf-8") as fh:
        fh.write("not-json\n")
        fh.write(json.dumps({"no_id_field": "x"}) + "\n")
        fh.write(json.dumps({"id": "P2", "title": "recovered", "status": "pending"}) + "\n")
    assert ag.pending_count("plan-a") == 2
    ids = {ag.next_packet("plan-a")["id"]}
    # first eligible — P1 (enqueue order, default score 0)
    assert "P1" in ids or "P2" in ids


def test_list_plans_with_pending(monkeypatch, tmp_path):
    ag = _load_helper(monkeypatch, tmp_path)
    ag.enqueue("plan-a", {"id": "P1", "title": "a"})
    ag.enqueue("plan-b", {"id": "P1", "title": "b"})
    ag.enqueue("plan-c", {"id": "P1", "title": "c"})
    ag.mark_answered("plan-b", "P1", "opt")
    plans = ag.list_plans_with_pending()
    assert "plan-a" in plans
    assert "plan-c" in plans
    assert "plan-b" not in plans


def test_dependency_on_missing_packet_treated_as_satisfied(monkeypatch, tmp_path):
    """If depends_on references an id not in queue, treat as satisfied (partial seed)."""
    ag = _load_helper(monkeypatch, tmp_path)
    ag.enqueue("plan-a", {"id": "P2", "title": "depends on ghost", "depends_on": ["GHOST"]})
    assert ag.next_packet("plan-a")["id"] == "P2"
