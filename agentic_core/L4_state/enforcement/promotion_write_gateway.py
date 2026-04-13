"""Promotion write gateway — concrete UWG-backed durable write path for PromotionAuthority.

Routes approved future-run pointer updates through the full UWG pipeline:

    PromotionAuthority.update_pointer_via_gateway()
        → PromotionWriteGateway.update_pointer()
            → UWGClerk.submit()       [serialized write queue, 10C-REQ-122]
            → UWGCommitter.commit()   [durable JSONL hash-chain ledger, 10C-REQ-126]
            → ProofOfLedger.seal()    [five-field audit proof, REQ-024]

Layer authority: L4_state (state sovereignty plane).
Only write path for PromotionAuthority pointer commits.
No live-run mutation.  Future-run only.
"""

from __future__ import annotations

import hashlib
import threading
from pathlib import Path
from typing import Any

from agentic_core.L4_state.enforcement.proof_of_ledger import ProofOfLedger
from agentic_core.L4_state.enforcement.uwg_clerk import UWGClerk, WriteRequest
from agentic_core.L4_state.enforcement.uwg_committer import UWGCommitter

_DEFAULT_LEDGER_PATH = Path("data/promotion_ledger.jsonl")


class PromotionWriteGateway:
    """UWG-backed durable write gateway for PromotionAuthority.

    Thread-safe: UWGClerk is a singleton with its own write lock.
    A single PromotionWriteGateway instance may be shared across threads.

    Usage (wired automatically by get_promotion_authority()):
        authority = get_promotion_authority()   # gateway already set
        authority.update_pointer_via_gateway(new_pointer, token)
    """

    def __init__(self, ledger_path: Path | None = None) -> None:
        self._clerk = UWGClerk()
        self._committer = UWGCommitter(ledger_path or _DEFAULT_LEDGER_PATH)
        self._proofs: dict[str, ProofOfLedger] = {}
        self._prev_hash: str = "0" * 64
        self._lock = threading.Lock()

    def update_pointer(
        self,
        namespace: str,
        old_pointer: str,
        new_pointer: str,
        capability_token: Any,
    ) -> ProofOfLedger:
        """Commit a pointer update durably through the UWG pipeline.

        Execution order:
            1. Build WriteRequest from pointer update + token metadata.
            2. Submit to UWGClerk (serialized queue, single write path).
            3. Durably append CommitRecord to JSONL ledger via UWGCommitter.
            4. Seal five-field ProofOfLedger with chain link to previous proof.
            5. Store proof per namespace; return it to caller.

        Args:
            namespace:        Target namespace (PromotionToken.target_namespace).
            old_pointer:      Previous pointer value.
            new_pointer:      New pointer value (PromotionPacket.packet_id).
            capability_token: PromotionToken — scoped, single-use nonce.

        Returns:
            ProofOfLedger — sealed five-field audit proof for this commit.

        Raises:
            RuntimeError: If UWGClerk rejects the request (returns None receipt).
        """
        token_id = getattr(capability_token, "token_id", str(capability_token))
        replay_digest = getattr(capability_token, "replay_digest_binding", "") or ""
        guardian_sig = getattr(capability_token, "guardian_signature", "") or ""

        policy_hash = hashlib.sha256(f"{guardian_sig}:{namespace}".encode("utf-8")).hexdigest()[:32]

        request = WriteRequest(
            actor_id="promotion_authority",
            run_id=new_pointer,
            operation="update_pointer",
            path=namespace,
            data=f"{old_pointer}->{new_pointer}".encode("utf-8"),
            signature=token_id,
            policy_hash=policy_hash,
            capability_token=token_id,
            replay_key=replay_digest,
        )

        receipt = self._clerk.submit(request)
        if receipt is None:
            raise RuntimeError(
                f"PromotionWriteGateway: UWGClerk rejected write "
                f"for namespace={namespace!r} new_pointer={new_pointer!r}"
            )

        commit_record = self._committer.commit(request, receipt)

        knowledge_state_digest = hashlib.sha256(
            f"{namespace}:{new_pointer}:{commit_record.timestamp}".encode("utf-8")
        ).hexdigest()
        write_authority_hash = hashlib.sha256(token_id.encode("utf-8")).hexdigest()

        with self._lock:
            proof = ProofOfLedger.seal(
                commit_id=receipt.commit_hash,
                knowledge_state_digest=knowledge_state_digest,
                write_authority_hash=write_authority_hash,
                policy_hash=policy_hash,
                prev_hash=self._prev_hash,
            )
            self._prev_hash = proof.hash_chain_entry
            self._proofs[namespace] = proof

        return proof

    def get_proof(self, namespace: str) -> ProofOfLedger | None:
        """Return the latest ProofOfLedger for the given namespace, or None."""
        return self._proofs.get(namespace)

    def verify_chain(self) -> bool:
        """Verify integrity of the underlying UWG ledger hash chain.

        Returns True if the chain is intact, False if any link is broken.
        """
        return self._committer.verify_chain()
