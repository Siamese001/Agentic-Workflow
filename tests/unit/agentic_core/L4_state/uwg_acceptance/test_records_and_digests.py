"""L4 canonical record and deterministic-digest tests.

Doctrine refs:
- 00.1 §"Validation rules" — required identity/hash fields
- 00.5 §PHASE 2 — deterministic digest input rules
"""

from __future__ import annotations

from agentic_core.L4_state.contracts import (
    BlueprintRecord,
    CommitRequest,
    L4UWGProofPacket,
    PolicyManifest,
    RegistrySnapshot,
    canonical_json_dumps,
    compute_deterministic_digest,
)
from agentic_core.L4_state.contracts.records import stamp_digest
from agentic_core.L4_state.contracts.proof import stamp_proof_digest


class TestCanonicalJsonAndDigest:
    """Canonical encoding rules per 00.5."""

    def test_canonical_json_keys_are_sorted(self) -> None:
        # Same payload, different key order -> identical encoding
        a = {"b": 1, "a": 2, "c": [3, 2, 1]}
        b = {"a": 2, "c": [3, 2, 1], "b": 1}
        assert canonical_json_dumps(a) == canonical_json_dumps(b)

    def test_canonical_json_lists_keep_order(self) -> None:
        # Lists are caller-ordered — DO NOT auto-sort list items
        a = canonical_json_dumps({"k": [3, 1, 2]})
        b = canonical_json_dumps({"k": [1, 2, 3]})
        assert a != b

    def test_digest_is_deterministic(self) -> None:
        payload = {"x": 1, "y": [1, 2, 3], "z": {"a": 1, "b": 2}}
        d1 = compute_deterministic_digest(payload)
        d2 = compute_deterministic_digest(payload)
        assert d1 == d2
        assert len(d1) == 64  # SHA-256 hex


class TestStampDigest:
    """``stamp_digest`` populates ``deterministic_digest`` idempotently."""

    def test_stamps_empty_digest(self) -> None:
        record = PolicyManifest(
            policy_manifest_id="pm:1",
            policy_version="v1",
            policy_hash="phash:1",
        )
        stamped = stamp_digest(record)
        assert stamped.deterministic_digest != ""
        assert len(stamped.deterministic_digest) == 64

    def test_idempotent(self) -> None:
        record = PolicyManifest(
            policy_manifest_id="pm:1",
            policy_version="v1",
            policy_hash="phash:1",
        )
        once = stamp_digest(record)
        twice = stamp_digest(once)
        assert once.deterministic_digest == twice.deterministic_digest

    def test_different_records_have_different_digests(self) -> None:
        a = stamp_digest(PolicyManifest(policy_manifest_id="pm:1", policy_version="v1", policy_hash="h1"))
        b = stamp_digest(PolicyManifest(policy_manifest_id="pm:1", policy_version="v1", policy_hash="h2"))
        assert a.deterministic_digest != b.deterministic_digest

    def test_blueprint_and_registry_stamp(self) -> None:
        bp = stamp_digest(BlueprintRecord(blueprint_id="bp:1", blueprint_hash="bh:1", blueprint_type="route"))
        rs = stamp_digest(
            RegistrySnapshot(
                registry_snapshot_id="rs:1",
                registry_digest="rd:1",
                policy_hash="ph:1",
                blueprint_hash="bh:1",
            )
        )
        assert bp.deterministic_digest
        assert rs.deterministic_digest


class TestRecordImmutability:
    """All records must be ``frozen=True`` (parent doctrine §Hard Write Law)."""

    def test_policy_manifest_is_immutable(self) -> None:
        record = PolicyManifest(policy_manifest_id="pm:1", policy_version="v1", policy_hash="ph:1")
        try:
            record.policy_hash = "tampered"  # type: ignore[misc]
        except (AttributeError, TypeError) as exc:
            assert "frozen" in str(exc).lower() or "can't" in str(exc).lower() or "cannot" in str(exc).lower()
        else:
            raise AssertionError("frozen dataclass allowed mutation")

    def test_commit_request_is_immutable(self) -> None:
        record = CommitRequest(
            commit_request_id="cr:1",
            cleared_exit_review_packet_ref="exr:1",
            request_id="req:1",
            run_id="run:1",
            trace_root="trace:1",
            tenant_id="t:1",
            policy_hash="ph:1",
            blueprint_hash="bh:1",
            route_contract_ref="rc:1",
            replay_key="rk:1",
            rollback_plan_ref="rp:1",
            blast_radius="single_surface",
        )
        try:
            record.source_surface = "L2"  # type: ignore[misc]
        except (AttributeError, TypeError):
            pass
        else:
            raise AssertionError("CommitRequest must be frozen — Exit-only source guarantee broken")


class TestProofPacketDigest:
    """L4UWGProofPacket digest stamping."""

    def test_stamp_proof_digest(self) -> None:
        packet = L4UWGProofPacket(
            proof_packet_id="proof:1",
            trace_root="trace:1",
            policy_hash="ph:1",
            blueprint_hash="bh:1",
            replay_key="rk:1",
            acceptance_summary="all gates green",
        )
        stamped = stamp_proof_digest(packet)
        assert stamped.deterministic_digest
        assert stamp_proof_digest(stamped).deterministic_digest == stamped.deterministic_digest
