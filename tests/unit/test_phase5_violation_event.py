"""
Phase 5 — Wave 1 Tests: ViolationEvent schema, hashing, emission.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.types.violation_event_types import (
    ViolationEvent,
    emit_violation_event,
)

pytestmark = pytest.mark.unit_min_deps

_TS = "2026-02-21T00:00:00Z"


def _make_event(**overrides) -> ViolationEvent:
    defaults: dict = {
        "schema_version": 1,
        "mission_id": "mission-abc",
        "commit_tick": 5,
        "guardian_decision": "block",
        "violation_codes": ["SCOPE_VIOLATION", "IMPORT_ERROR"],
        "severity_score": 0.9,
        "created_at_utc": _TS,
    }
    defaults.update(overrides)
    return ViolationEvent(**defaults)


class TestViolationEventHash:
    def test_violation_event_hash_stable(self):
        """Same inputs produce the same event_hash on repeated construction."""
        e1 = _make_event()
        e2 = _make_event()
        assert e1.event_hash == e2.event_hash
        assert len(e1.event_hash) == 64

    def test_hash_changes_with_mission_id(self):
        e1 = _make_event(mission_id="mission-A")
        e2 = _make_event(mission_id="mission-B")
        assert e1.event_hash != e2.event_hash

    def test_hash_changes_with_commit_tick(self):
        e1 = _make_event(commit_tick=1)
        e2 = _make_event(commit_tick=2)
        assert e1.event_hash != e2.event_hash

    def test_hash_changes_with_decision(self):
        e1 = _make_event(guardian_decision="allow")
        e2 = _make_event(guardian_decision="block")
        assert e1.event_hash != e2.event_hash

    def test_hash_changes_with_severity(self):
        e1 = _make_event(severity_score=0.5)
        e2 = _make_event(severity_score=0.9)
        assert e1.event_hash != e2.event_hash

    def test_event_hash_excluded_from_canonical_bytes(self):
        """canonical_bytes must not contain the string 'event_hash'."""
        e = _make_event()
        assert b"event_hash" not in e.canonical_bytes()

    def test_canonical_bytes_deterministic(self):
        e1 = _make_event()
        e2 = _make_event()
        assert e1.canonical_bytes() == e2.canonical_bytes()


class TestViolationEventCodesSorted:
    def test_violation_event_codes_sorted_in_canonical_bytes(self):
        """
        violation_codes in canonical_bytes must be sorted regardless of
        the order passed to the constructor.
        """
        e_unsorted = _make_event(violation_codes=["Z_CODE", "A_CODE", "M_CODE"])
        e_sorted = _make_event(violation_codes=["A_CODE", "M_CODE", "Z_CODE"])
        assert e_unsorted.event_hash == e_sorted.event_hash
        assert e_unsorted.violation_codes == ["A_CODE", "M_CODE", "Z_CODE"]

    def test_violation_codes_stored_sorted(self):
        e = _make_event(violation_codes=["Z", "A", "M"])
        assert e.violation_codes == ["A", "M", "Z"]

    def test_empty_violation_codes_allowed(self):
        e = _make_event(violation_codes=[])
        assert e.violation_codes == []
        assert len(e.event_hash) == 64


class TestSeverityScoreRange:
    def test_severity_score_range_enforced_zero(self):
        e = _make_event(severity_score=0.0)
        assert e.severity_score == 0.0

    def test_severity_score_range_enforced_one(self):
        e = _make_event(severity_score=1.0)
        assert e.severity_score == 1.0

    def test_severity_score_below_zero_raises(self):
        with pytest.raises(ValueError, match="severity_score"):
            _make_event(severity_score=-0.01)

    def test_severity_score_above_one_raises(self):
        with pytest.raises(ValueError, match="severity_score"):
            _make_event(severity_score=1.001)

    def test_severity_score_midpoint(self):
        e = _make_event(severity_score=0.5)
        assert e.severity_score == 0.5


class TestViolationEventValidation:
    def test_invalid_schema_version_raises(self):
        with pytest.raises(ValueError, match="schema_version"):
            _make_event(schema_version=99)

    def test_empty_mission_id_raises(self):
        with pytest.raises(ValueError, match="mission_id"):
            _make_event(mission_id="")

    def test_negative_commit_tick_raises(self):
        with pytest.raises(ValueError, match="commit_tick"):
            _make_event(commit_tick=-1)

    def test_invalid_guardian_decision_raises(self):
        with pytest.raises(ValueError, match="guardian_decision"):
            _make_event(guardian_decision="deny")

    def test_valid_decisions_accepted(self):
        for decision in ("allow", "block", "escalate"):
            e = _make_event(guardian_decision=decision)
            assert e.guardian_decision == decision

    def test_non_list_violation_codes_raises(self):
        with pytest.raises(TypeError, match="violation_codes"):
            _make_event(violation_codes="SCOPE_VIOLATION")


class TestEmitViolationEvent:
    def test_emit_returns_violation_event(self):
        e = emit_violation_event(
            mission_id="m1",
            commit_tick=3,
            guardian_decision="escalate",
            violation_codes=["CODE_A"],
            severity_score=0.8,
            created_at_utc=_TS,
        )
        assert isinstance(e, ViolationEvent)
        assert e.guardian_decision == "escalate"

    def test_emit_appends_to_registry(self):
        registry: list[ViolationEvent] = []
        emit_violation_event(
            mission_id="m1",
            commit_tick=1,
            guardian_decision="block",
            violation_codes=[],
            severity_score=0.5,
            created_at_utc=_TS,
            _registry=registry,
        )
        emit_violation_event(
            mission_id="m1",
            commit_tick=2,
            guardian_decision="allow",
            violation_codes=[],
            severity_score=0.1,
            created_at_utc=_TS,
            _registry=registry,
        )
        assert len(registry) == 2

    def test_emit_does_not_alter_decision(self):
        """Emission is pure recording — decision field is unchanged."""
        e = emit_violation_event(
            mission_id="m1",
            commit_tick=7,
            guardian_decision="allow",
            violation_codes=[],
            severity_score=0.0,
            created_at_utc=_TS,
        )
        assert e.guardian_decision == "allow"

    def test_to_dict_round_trip(self):
        e = _make_event()
        d = e.to_dict()
        e2 = ViolationEvent.from_dict(d)
        assert e2.event_hash == e.event_hash
        assert e2.violation_codes == e.violation_codes
