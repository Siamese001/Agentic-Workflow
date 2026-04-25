"""Tests for ViolationEventStore - violation event persistence."""
import pytest
from agentic_core.L4_state.enforcement.violation_event_store import ViolationEventStore


class TestViolationEventStore:
    def test_init(self, tmp_path):
        store = ViolationEventStore(path=str(tmp_path / "violations.jsonl"))
        assert store is not None

    def test_record_violation(self, tmp_path):
        store = ViolationEventStore(path=str(tmp_path / "violations.jsonl"))
        store.record({"type": "antipattern", "severity": "P1"})
        events = store.list_violations()
        assert len(events) == 1

    def test_filter_by_severity(self, tmp_path):
        store = ViolationEventStore(path=str(tmp_path / "violations.jsonl"))
        store.record({"type": "x", "severity": "P1"})
        store.record({"type": "y", "severity": "P2"})
        p1 = store.filter_by_severity("P1")
        assert len(p1) == 1

    def test_filter_by_type(self, tmp_path):
        store = ViolationEventStore(path=str(tmp_path / "violations.jsonl"))
        store.record({"type": "antipattern", "severity": "P1"})
        store.record({"type": "policy", "severity": "P1"})
        ap = store.filter_by_type("antipattern")
        assert len(ap) == 1

    def test_count_violations(self, tmp_path):
        store = ViolationEventStore(path=str(tmp_path / "violations.jsonl"))
        store.record({"type": "x", "severity": "P1"})
        store.record({"type": "y", "severity": "P2"})
        assert store.count() == 2

    def test_persistence(self, tmp_path):
        path = str(tmp_path / "violations.jsonl")
        s1 = ViolationEventStore(path=path)
        s1.record({"type": "x", "severity": "P1"})
        s2 = ViolationEventStore(path=path)
        assert s2.count() >= 1

    def test_clear(self, tmp_path):
        store = ViolationEventStore(path=str(tmp_path / "violations.jsonl"))
        store.record({"type": "x", "severity": "P1"})
        store.clear()
        assert store.count() == 0
