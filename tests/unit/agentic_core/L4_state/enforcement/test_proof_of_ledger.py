"""Tests for ProofOfLedger (B07 — GAP-013, REQ-024).

Contract invariant tests:
- ProofOfLedger is frozen
- All 5 fields required; validate() raises LedgerProofMissing on any missing/empty field

seal() factory tests:
- seal() computes hash_chain_entry deterministically
- knowledge_state_digest change → different hash_chain_entry
- empty prev_hash is valid (genesis commit)
- seal() validates on creation

verify() tests:
- correct prev_hash → verify() returns True
- wrong prev_hash → verify() returns False
- verify() is deterministic

to_dict() contract:
- Contains all 5 keys

LedgerProofMissing tests:
- is RuntimeError subclass

Layer sovereignty:
- frozen dataclass raises FrozenInstanceError on mutation
"""

import hashlib
import pytest
from dataclasses import FrozenInstanceError

from agentic_core.L4_state.enforcement.proof_of_ledger import (
    LedgerProofMissing,
    ProofOfLedger,
)


def _seal(**overrides) -> ProofOfLedger:
    defaults = dict(
        commit_id="cmt-001",
        knowledge_state_digest="sha256:state-abc",
        write_authority_hash="sha256:auth-xyz",
        policy_hash="sha256:policy-abc",
        prev_hash="sha256:prev-000",
    )
    defaults.update(overrides)
    return ProofOfLedger.seal(**defaults)


class TestProofOfLedgerValid:
    def test_seal_returns_proof_of_ledger(self):
        proof = _seal()
        assert isinstance(proof, ProofOfLedger)

    def test_all_five_fields_populated(self):
        proof = _seal()
        assert proof.commit_id
        assert proof.knowledge_state_digest
        assert proof.write_authority_hash
        assert proof.policy_hash
        assert proof.hash_chain_entry

    def test_genesis_commit_empty_prev_hash(self):
        proof = _seal(prev_hash="")
        assert isinstance(proof, ProofOfLedger)

    def test_validate_passes_on_valid_proof(self):
        _seal().validate()


class TestProofOfLedgerViolations:
    def test_missing_commit_id_raises(self):
        with pytest.raises(LedgerProofMissing):
            ProofOfLedger(
                commit_id="",
                knowledge_state_digest="sha256:state",
                write_authority_hash="sha256:auth",
                policy_hash="sha256:policy",
                hash_chain_entry="sha256:chain",
            ).validate()

    def test_missing_knowledge_state_digest_raises(self):
        with pytest.raises(LedgerProofMissing):
            ProofOfLedger(
                commit_id="cmt-001",
                knowledge_state_digest="",
                write_authority_hash="sha256:auth",
                policy_hash="sha256:policy",
                hash_chain_entry="sha256:chain",
            ).validate()

    def test_missing_write_authority_hash_raises(self):
        with pytest.raises(LedgerProofMissing):
            ProofOfLedger(
                commit_id="cmt-001",
                knowledge_state_digest="sha256:state",
                write_authority_hash="",
                policy_hash="sha256:policy",
                hash_chain_entry="sha256:chain",
            ).validate()

    def test_missing_policy_hash_raises(self):
        with pytest.raises(LedgerProofMissing):
            ProofOfLedger(
                commit_id="cmt-001",
                knowledge_state_digest="sha256:state",
                write_authority_hash="sha256:auth",
                policy_hash="",
                hash_chain_entry="sha256:chain",
            ).validate()

    def test_missing_hash_chain_entry_raises(self):
        with pytest.raises(LedgerProofMissing):
            ProofOfLedger(
                commit_id="cmt-001",
                knowledge_state_digest="sha256:state",
                write_authority_hash="sha256:auth",
                policy_hash="sha256:policy",
                hash_chain_entry="",
            ).validate()

    def test_ledger_proof_missing_is_runtime_error_subclass(self):
        assert issubclass(LedgerProofMissing, RuntimeError)

    def test_whitespace_commit_id_raises_ledger_proof_missing(self):
        with pytest.raises(LedgerProofMissing):
            ProofOfLedger.seal(
                commit_id="   ",
                knowledge_state_digest="sha256:state",
                write_authority_hash="sha256:auth",
                policy_hash="sha256:policy",
                prev_hash="sha256:prev",
            )

    def test_whitespace_policy_hash_raises_ledger_proof_missing(self):
        with pytest.raises(LedgerProofMissing):
            ProofOfLedger.seal(
                commit_id="cmt-001",
                knowledge_state_digest="sha256:state",
                write_authority_hash="sha256:auth",
                policy_hash="   ",
                prev_hash="sha256:prev",
            )


class TestHashChain:
    def test_hash_chain_is_deterministic(self):
        p1 = _seal(commit_id="cmt-001", knowledge_state_digest="sha256:stateA", prev_hash="sha256:prev")
        p2 = _seal(commit_id="cmt-001", knowledge_state_digest="sha256:stateA", prev_hash="sha256:prev")
        assert p1.hash_chain_entry == p2.hash_chain_entry

    def test_different_knowledge_state_digest_different_chain(self):
        p1 = _seal(knowledge_state_digest="sha256:stateA")
        p2 = _seal(knowledge_state_digest="sha256:stateB")
        assert p1.hash_chain_entry != p2.hash_chain_entry

    def test_different_prev_hash_different_chain(self):
        p1 = _seal(prev_hash="sha256:prev-A")
        p2 = _seal(prev_hash="sha256:prev-B")
        assert p1.hash_chain_entry != p2.hash_chain_entry

    def test_different_commit_id_different_chain(self):
        p1 = _seal(commit_id="cmt-001")
        p2 = _seal(commit_id="cmt-002")
        assert p1.hash_chain_entry != p2.hash_chain_entry


class TestVerify:
    def test_verify_with_correct_prev_hash_returns_true(self):
        prev = "sha256:prev-000"
        proof = _seal(prev_hash=prev)
        assert proof.verify(prev) is True

    def test_verify_with_wrong_prev_hash_returns_false(self):
        proof = _seal(prev_hash="sha256:prev-000")
        assert proof.verify("sha256:wrong") is False

    def test_verify_is_deterministic(self):
        prev = "sha256:prev-abc"
        proof = _seal(prev_hash=prev)
        assert proof.verify(prev) is True
        assert proof.verify(prev) is True

    def test_verify_genesis_empty_prev_hash(self):
        proof = _seal(prev_hash="")
        assert proof.verify("") is True


class TestToDictContract:
    def test_to_dict_contains_all_five_keys(self):
        d = _seal().to_dict()
        assert "commit_id" in d
        assert "knowledge_state_digest" in d
        assert "write_authority_hash" in d
        assert "policy_hash" in d
        assert "hash_chain_entry" in d

    def test_to_dict_preserves_values(self):
        proof = _seal(commit_id="cmt-test", policy_hash="sha256:pol-test")
        d = proof.to_dict()
        assert d["commit_id"] == "cmt-test"
        assert d["policy_hash"] == "sha256:pol-test"


class TestLayerSovereignty:
    def test_frozen_raises_on_mutation(self):
        proof = _seal()
        with pytest.raises(FrozenInstanceError):
            proof.commit_id = "new-id"  # type: ignore[misc]
