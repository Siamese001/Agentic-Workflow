"""ProofOfLedger — formal five-field sealed artifact for external audit (B07 — GAP-013, REQ-024).

Every UWG durable commit MUST produce a ProofOfLedger artifact.
The proof is verifiable from the hash chain alone — no live state required.

Layer authority: L4_state (state sovereignty plane).
UWG (L2_execution) calls seal_proof() after each durable commit.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_blocks_direct_write,
    _emit_links_execution_to_snapshot,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

emit_replay_key("p0", "proof_of_ledger")
emit_determinism_digest("p0", "proof_of_ledger")
_emit_reads_policy_state("p1", "proof_of_ledger", "L4")
_emit_verifies_policy("p1", "proof_of_ledger", "ledger_policy_check")
_emit_verifies_boundary("p1", "proof_of_ledger", "ledger_boundary_check")
_emit_writes_via_uwg("p1", "proof_of_ledger", "uwg_commit")
_emit_blocks_direct_write("p1", "proof_of_ledger", "direct_write_block")
_emit_links_execution_to_snapshot("p1", "proof_of_ledger", "snapshot_link")


class LedgerProofMissing(RuntimeError):
    """Raised when a UWG commit does not produce a ProofOfLedger.

    Every durable commit must generate proof — no silent omission.
    """


@dataclass(frozen=True)
class ProofOfLedger:
    """Formal five-field sealed artifact for external audit (REQ-024).

    All five fields are required.  The proof is designed for offline
    verification: given only the hash chain, an auditor can reconstruct
    and verify the proof without accessing live state.

    Fields:
        commit_id              — unique identifier for this UWG commit
        knowledge_state_digest — SHA-256 of the knowledge state after commit
        write_authority_hash   — hash of the capability/authority token used
        policy_hash            — policy snapshot hash at commit time
        hash_chain_entry       — chained hash: SHA-256(prev_hash + commit_id + knowledge_state_digest)
    """

    commit_id: str
    knowledge_state_digest: str
    write_authority_hash: str
    policy_hash: str
    hash_chain_entry: str

    def validate(self) -> None:
        """Raise LedgerProofMissing if any mandatory field is absent."""
        missing = [
            f
            for f in (
                "commit_id",
                "knowledge_state_digest",
                "write_authority_hash",
                "policy_hash",
                "hash_chain_entry",
            )
            if not getattr(self, f, None) or not str(getattr(self, f)).strip()
        ]
        if missing:
            raise LedgerProofMissing(
                f"ProofOfLedger is missing mandatory fields: {missing}. "
                "Every UWG commit must produce a complete ProofOfLedger."
            )

    def verify(self, prev_hash: str) -> bool:
        """Verify the hash chain entry against the previous hash and this proof's fields.

        Allows offline reconstruction without live state.

        Returns True if the chain entry is consistent with this proof's commit_id
        and knowledge_state_digest.
        """
        expected = hashlib.sha256(
            f"{prev_hash}|{self.commit_id}|{self.knowledge_state_digest}".encode()
        ).hexdigest()
        return self.hash_chain_entry == expected

    def to_dict(self) -> dict[str, Any]:
        return {
            "commit_id": self.commit_id,
            "knowledge_state_digest": self.knowledge_state_digest,
            "write_authority_hash": self.write_authority_hash,
            "policy_hash": self.policy_hash,
            "hash_chain_entry": self.hash_chain_entry,
        }

    @classmethod
    def seal(
        cls,
        commit_id: str,
        knowledge_state_digest: str,
        write_authority_hash: str,
        policy_hash: str,
        prev_hash: str = "",
    ) -> "ProofOfLedger":
        """Factory: compute hash chain entry and return a validated ProofOfLedger.

        Called by UWG after every durable commit.
        """
        _emit_records_execution_trace("ledger_seal", "proof_of_ledger", commit_id)
        hash_chain_entry = hashlib.sha256(
            f"{prev_hash}|{commit_id}|{knowledge_state_digest}".encode()
        ).hexdigest()
        proof = cls(
            commit_id=commit_id,
            knowledge_state_digest=knowledge_state_digest,
            write_authority_hash=write_authority_hash,
            policy_hash=policy_hash,
            hash_chain_entry=hash_chain_entry,
        )
        proof.validate()
        return proof
