"""Tests for PromotionWriteGateway and PromotionAuthority gateway auto-wiring."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def _make_token(
    namespace: str = "evidence_threshold.generic",
    token_id: str = "tok-test-001",
    replay_digest: str = "digest-abc",
    guardian_sig: str = "governed_handoff:pkt-001",
) -> MagicMock:
    """Build a minimal mock PromotionToken."""
    tok = MagicMock()
    tok.token_id = token_id
    tok.target_namespace = namespace
    tok.replay_digest_binding = replay_digest
    tok.guardian_signature = guardian_sig
    return tok


# ── TestPromotionWriteGateway ─────────────────────────────────────────────────


class TestPromotionWriteGateway:
    """Durable write gateway — happy path and error cases."""

    def test_update_pointer_returns_proof_of_ledger(self, tmp_path: Path) -> None:
        """update_pointer() returns a ProofOfLedger on success."""
        from agentic_core.L4_state.enforcement.proof_of_ledger import ProofOfLedger
        from agentic_core.L4_state.enforcement.promotion_write_gateway import PromotionWriteGateway

        gw = PromotionWriteGateway(ledger_path=tmp_path / "ledger.jsonl")
        proof = gw.update_pointer(
            namespace="evidence_threshold.generic",
            old_pointer="old-ptr-001",
            new_pointer="pkt-new-001",
            capability_token=_make_token(),
        )

        assert isinstance(proof, ProofOfLedger)

    def test_proof_has_all_five_fields(self, tmp_path: Path) -> None:
        """Returned ProofOfLedger has all five non-empty fields."""
        from agentic_core.L4_state.enforcement.promotion_write_gateway import PromotionWriteGateway

        gw = PromotionWriteGateway(ledger_path=tmp_path / "ledger.jsonl")
        proof = gw.update_pointer(
            namespace="evidence_threshold.generic",
            old_pointer="old-ptr-002",
            new_pointer="pkt-new-002",
            capability_token=_make_token(token_id="tok-002"),
        )

        assert proof.commit_id, "commit_id must be non-empty"
        assert proof.knowledge_state_digest, "knowledge_state_digest must be non-empty"
        assert proof.write_authority_hash, "write_authority_hash must be non-empty"
        assert proof.policy_hash, "policy_hash must be non-empty"
        assert proof.hash_chain_entry, "hash_chain_entry must be non-empty"

    def test_proof_validates_successfully(self, tmp_path: Path) -> None:
        """Returned ProofOfLedger passes its own validate() without raising."""
        from agentic_core.L4_state.enforcement.promotion_write_gateway import PromotionWriteGateway

        gw = PromotionWriteGateway(ledger_path=tmp_path / "ledger.jsonl")
        proof = gw.update_pointer(
            namespace="rubric.generic",
            old_pointer="old-003",
            new_pointer="new-003",
            capability_token=_make_token(token_id="tok-003"),
        )

        proof.validate()

    def test_proof_chain_entry_is_verifiable(self, tmp_path: Path) -> None:
        """proof.verify(prev_hash) returns True for the genesis (prev="0"*64) case."""
        from agentic_core.L4_state.enforcement.promotion_write_gateway import PromotionWriteGateway

        gw = PromotionWriteGateway(ledger_path=tmp_path / "ledger.jsonl")
        proof = gw.update_pointer(
            namespace="rubric.generic",
            old_pointer="old-004",
            new_pointer="new-004",
            capability_token=_make_token(token_id="tok-004"),
        )

        genesis_prev = "0" * 64
        assert proof.verify(genesis_prev), "First proof must be verifiable against the genesis prev_hash"

    def test_get_proof_returns_latest_after_commit(self, tmp_path: Path) -> None:
        """get_proof(namespace) returns the proof produced by the last update."""
        from agentic_core.L4_state.enforcement.promotion_write_gateway import PromotionWriteGateway

        gw = PromotionWriteGateway(ledger_path=tmp_path / "ledger.jsonl")
        ns = "evidence_threshold.generic"
        proof = gw.update_pointer(
            namespace=ns,
            old_pointer="old-005",
            new_pointer="new-005",
            capability_token=_make_token(token_id="tok-005"),
        )

        assert gw.get_proof(ns) is proof

    def test_get_proof_returns_none_for_unknown_namespace(self, tmp_path: Path) -> None:
        """get_proof(unknown) returns None before any commit to that namespace."""
        from agentic_core.L4_state.enforcement.promotion_write_gateway import PromotionWriteGateway

        gw = PromotionWriteGateway(ledger_path=tmp_path / "ledger.jsonl")
        assert gw.get_proof("nonexistent.namespace") is None

    def test_clerk_rejection_raises_runtime_error(self, tmp_path: Path) -> None:
        """RuntimeError raised when UWGClerk.submit() returns None."""
        from agentic_core.L4_state.enforcement.promotion_write_gateway import PromotionWriteGateway

        gw = PromotionWriteGateway(ledger_path=tmp_path / "ledger.jsonl")
        with patch.object(gw._clerk, "submit", return_value=None):
            with pytest.raises(RuntimeError, match="UWGClerk rejected write"):
                gw.update_pointer(
                    namespace="evidence_threshold.generic",
                    old_pointer="old-006",
                    new_pointer="new-006",
                    capability_token=_make_token(token_id="tok-006"),
                )

    def test_verify_chain_returns_true_after_commit(self, tmp_path: Path) -> None:
        """verify_chain() returns True after a clean commit."""
        from agentic_core.L4_state.enforcement.promotion_write_gateway import PromotionWriteGateway

        gw = PromotionWriteGateway(ledger_path=tmp_path / "ledger.jsonl")
        gw.update_pointer(
            namespace="evidence_threshold.generic",
            old_pointer="old-007",
            new_pointer="new-007",
            capability_token=_make_token(token_id="tok-007"),
        )

        assert gw.verify_chain() is True

    def test_sequential_commits_chain_prev_hashes(self, tmp_path: Path) -> None:
        """Second proof's hash_chain_entry differs from first (chain grows)."""
        from agentic_core.L4_state.enforcement.promotion_write_gateway import PromotionWriteGateway

        gw = PromotionWriteGateway(ledger_path=tmp_path / "ledger.jsonl")
        proof_a = gw.update_pointer(
            namespace="ns-a",
            old_pointer="old-a",
            new_pointer="new-a",
            capability_token=_make_token(namespace="ns-a", token_id="tok-a"),
        )
        proof_b = gw.update_pointer(
            namespace="ns-b",
            old_pointer="old-b",
            new_pointer="new-b",
            capability_token=_make_token(namespace="ns-b", token_id="tok-b"),
        )

        assert proof_a.hash_chain_entry != proof_b.hash_chain_entry, (
            "Chained proofs must have different hash_chain_entry values"
        )
        assert proof_b.verify(proof_a.hash_chain_entry), (
            "Second proof must be verifiable against the first proof's chain entry"
        )

    def test_ledger_file_created_on_disk(self, tmp_path: Path) -> None:
        """After commit, the JSONL ledger file exists on disk."""
        from agentic_core.L4_state.enforcement.promotion_write_gateway import PromotionWriteGateway

        ledger = tmp_path / "ledger.jsonl"
        gw = PromotionWriteGateway(ledger_path=ledger)
        gw.update_pointer(
            namespace="evidence_threshold.generic",
            old_pointer="old-008",
            new_pointer="new-008",
            capability_token=_make_token(token_id="tok-008"),
        )

        assert ledger.exists(), "JSONL ledger file must be created after commit"
        assert ledger.stat().st_size > 0, "Ledger file must be non-empty after commit"


# ── TestPromotionAuthorityGatewayAutoWire ─────────────────────────────────────


class TestPromotionAuthorityGatewayAutoWire:
    """PromotionAuthority singleton auto-wires PromotionWriteGateway."""

    def test_get_promotion_authority_has_write_gateway(self) -> None:
        """get_promotion_authority() returns an authority with a non-None write gateway."""
        import agentic_core.L4_state.enforcement.promotion_authority as _pa_mod
        from agentic_core.L4_state.enforcement.promotion_write_gateway import PromotionWriteGateway

        old = _pa_mod._promotion_authority
        try:
            _pa_mod._promotion_authority = None
            authority = _pa_mod.get_promotion_authority()
            assert authority._write_gateway is not None, (
                "get_promotion_authority() must auto-wire a PromotionWriteGateway"
            )
            assert isinstance(authority._write_gateway, PromotionWriteGateway)
        finally:
            _pa_mod._promotion_authority = old

    def test_update_pointer_via_gateway_no_longer_raises(self, tmp_path: Path) -> None:
        """update_pointer_via_gateway() completes without RuntimeError when gateway is set."""
        from agentic_core.L4_state.enforcement.promotion_authority import PromotionAuthority
        from agentic_core.L4_state.enforcement.promotion_write_gateway import PromotionWriteGateway

        authority = PromotionAuthority()
        authority.set_write_gateway(PromotionWriteGateway(ledger_path=tmp_path / "ledger.jsonl"))

        token = _make_token()
        token.validate_scope_and_use = MagicMock(return_value=True)

        record = authority.update_pointer_via_gateway(
            new_pointer="pkt-auto-001",
            capability_token=token,
        )

        assert record is not None, "PromotionPointerUpdate must be returned"
        assert record.new_pointer == "pkt-auto-001"
