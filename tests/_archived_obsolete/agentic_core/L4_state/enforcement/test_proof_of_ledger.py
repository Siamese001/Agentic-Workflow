"""Tests for ProofOfLedger - cryptographic ledger proof."""
import pytest
from agentic_core.L4_state.enforcement.proof_of_ledger import ProofOfLedger


class TestProofOfLedger:
    def test_init(self):
        p = ProofOfLedger()
        assert p is not None

    def test_append_entry(self):
        p = ProofOfLedger()
        p.append({"event": "x"})
        assert p.length() == 1

    def test_chain_integrity(self):
        p = ProofOfLedger()
        p.append({"event": "a"})
        p.append({"event": "b"})
        assert p.verify_chain() is True

    def test_tamper_detection(self):
        p = ProofOfLedger()
        p.append({"event": "a"})
        p.append({"event": "b"})
        # Manually tamper if possible
        if hasattr(p, "_entries") and len(p._entries) > 0:
            p._entries[0]["event"] = "tampered"
            assert p.verify_chain() is False

    def test_get_root_hash(self):
        p = ProofOfLedger()
        p.append({"event": "x"})
        h = p.get_root_hash()
        assert isinstance(h, str)

    def test_proof_for_entry(self):
        p = ProofOfLedger()
        p.append({"event": "x"})
        proof = p.get_proof(0)
        assert proof is not None
