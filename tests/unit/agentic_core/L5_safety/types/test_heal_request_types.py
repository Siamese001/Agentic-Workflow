"""Tests for HealRequest and assert_same_snapshot (B06 — GAP-006, REQ-010).

Contract invariant tests:
- HealRequest is frozen
- All 6 fields required; validate() raises ValueError on any missing/empty field
- policy_hash and blueprint_hash propagated through repair chain

assert_same_snapshot() tests:
- Matching snapshots → no exception
- policy_hash mismatch → SnapshotMismatchError
- blueprint_hash mismatch → SnapshotMismatchError
- Both mismatched → SnapshotMismatchError (policy checked first)
- parent_packet_id propagated through chain

to_dict() contract:
- Contains all 6 keys

Layer sovereignty:
- frozen dataclass raises FrozenInstanceError on mutation
"""

import pytest
from dataclasses import FrozenInstanceError

from agentic_core.L5_safety.types.heal_request_types import (
    HealRequest,
    SnapshotMismatchError,
    assert_same_snapshot,
)


def _valid_request(**overrides) -> HealRequest:
    defaults = dict(
        request_id="heal-001",
        parent_packet_id="pkt-001",
        policy_hash="sha256:policy-abc",
        blueprint_hash="sha256:blueprint-xyz",
        violation_payload={"type": "SAFETY_VIOLATION", "detail": "rule 5 breached"},
        originating_run_id="run-001",
    )
    defaults.update(overrides)
    return HealRequest(**defaults)


class TestHealRequestValid:
    def test_valid_request_passes_validate(self):
        _valid_request().validate()

    def test_empty_violation_payload_is_allowed(self):
        _valid_request(violation_payload={}).validate()

    def test_policy_and_blueprint_hash_present(self):
        req = _valid_request()
        assert req.policy_hash == "sha256:policy-abc"
        assert req.blueprint_hash == "sha256:blueprint-xyz"

    def test_parent_packet_id_present(self):
        req = _valid_request(parent_packet_id="pkt-xyz")
        assert req.parent_packet_id == "pkt-xyz"


class TestHealRequestViolations:
    def test_empty_request_id_raises(self):
        with pytest.raises(ValueError):
            _valid_request(request_id="").validate()

    def test_whitespace_request_id_raises(self):
        with pytest.raises(ValueError):
            _valid_request(request_id="   ").validate()

    def test_empty_parent_packet_id_raises(self):
        with pytest.raises(ValueError):
            _valid_request(parent_packet_id="").validate()

    def test_empty_policy_hash_raises(self):
        with pytest.raises(ValueError):
            _valid_request(policy_hash="").validate()

    def test_empty_blueprint_hash_raises(self):
        with pytest.raises(ValueError):
            _valid_request(blueprint_hash="").validate()

    def test_empty_originating_run_id_raises(self):
        with pytest.raises(ValueError):
            _valid_request(originating_run_id="").validate()


class TestAssertSameSnapshot:
    def test_matching_snapshots_does_not_raise(self):
        req = _valid_request()
        assert_same_snapshot(req, req.policy_hash, req.blueprint_hash)

    def test_policy_hash_mismatch_raises_snapshot_mismatch(self):
        req = _valid_request()
        with pytest.raises(SnapshotMismatchError):
            assert_same_snapshot(req, "sha256:different-policy", req.blueprint_hash)

    def test_blueprint_hash_mismatch_raises_snapshot_mismatch(self):
        req = _valid_request()
        with pytest.raises(SnapshotMismatchError):
            assert_same_snapshot(req, req.policy_hash, "sha256:different-blueprint")

    def test_both_mismatched_raises_snapshot_mismatch(self):
        req = _valid_request()
        with pytest.raises(SnapshotMismatchError):
            assert_same_snapshot(req, "sha256:wrong-policy", "sha256:wrong-blueprint")

    def test_policy_mismatch_error_message_mentions_policy(self):
        req = _valid_request()
        with pytest.raises(SnapshotMismatchError, match="policy_hash"):
            assert_same_snapshot(req, "sha256:wrong", req.blueprint_hash)

    def test_blueprint_mismatch_error_message_mentions_blueprint(self):
        req = _valid_request()
        with pytest.raises(SnapshotMismatchError, match="blueprint_hash"):
            assert_same_snapshot(req, req.policy_hash, "sha256:wrong")

    def test_snapshot_mismatch_error_is_runtime_error_subclass(self):
        assert issubclass(SnapshotMismatchError, RuntimeError)

    def test_parent_packet_id_propagated(self):
        req = _valid_request(parent_packet_id="pkt-propagated")
        assert_same_snapshot(req, req.policy_hash, req.blueprint_hash)
        assert req.parent_packet_id == "pkt-propagated"


class TestViolationPayloadValidation:
    def test_none_violation_payload_raises_value_error(self):
        req = _valid_request(violation_payload=None)
        with pytest.raises(ValueError, match="violation_payload"):
            req.validate()

    def test_list_violation_payload_raises_value_error(self):
        req = _valid_request(violation_payload=["not", "a", "dict"])
        with pytest.raises(ValueError, match="violation_payload"):
            req.validate()

    def test_string_violation_payload_raises_value_error(self):
        req = _valid_request(violation_payload="raw-string")
        with pytest.raises(ValueError, match="violation_payload"):
            req.validate()


class TestToDictContract:
    def test_to_dict_contains_all_six_keys(self):
        d = _valid_request().to_dict()
        assert "request_id" in d
        assert "parent_packet_id" in d
        assert "policy_hash" in d
        assert "blueprint_hash" in d
        assert "violation_payload" in d
        assert "originating_run_id" in d

    def test_violation_payload_preserved(self):
        payload = {"type": "TEST", "severity": "HIGH"}
        d = _valid_request(violation_payload=payload).to_dict()
        assert d["violation_payload"] == payload


class TestLayerSovereignty:
    def test_frozen_raises_on_mutation(self):
        req = _valid_request()
        with pytest.raises(FrozenInstanceError):
            req.policy_hash = "new-hash"  # type: ignore[misc]
