"""L4/UWG NO_DURABLE_MUTATION receipt — sealed record on chain mismatch.

Maps to: docs/reference/00B_L4_State_Archive_and_UWG/00B.7a_L4_UWG_Durable_Write_Context_Invariant.md
Phase 6 SEALED NO_DURABLE_MUTATION RECEIPT.

Contains:
  - `DURABLE_WRITE_CONTEXT_MISMATCH_RULE_ID` constant (= terminal stamp)
  - `UWG_COMMIT_BLOCKED_RULE_ID` constant (= decisive rule id)
  - `StageDigests` frozen dataclass (snapshot of all 8 stages)
  - `NoDurableMutationReceipt` frozen dataclass (sealed receipt body)
  - `DurableWriteContextMismatchError` exception
"""

from __future__ import annotations

from dataclasses import dataclass

DURABLE_WRITE_CONTEXT_MISMATCH_RULE_ID: str = "DURABLE_WRITE_CONTEXT_MISMATCH"
UWG_COMMIT_BLOCKED_RULE_ID: str = "UWG_COMMIT_BLOCKED"


@dataclass(frozen=True, slots=True)
class StageDigests:
    """Snapshot of every per-stage digest seen during the chain.

    Each field is the hex digest emitted by the corresponding stage,
    or "" when that stage has not yet emitted.
    """

    exit_commit_request_digest: str
    uwg_validation_digest: str
    write_lock_digest: str
    commit_transaction_digest: str
    l4_state_receipt_digest: str
    audit_ledger_digest: str
    replay_snapshot_digest: str
    retrieval_cache_invalidation_digest: str

    def to_dict(self) -> dict[str, str]:
        return {
            "exit_commit_request_digest": self.exit_commit_request_digest,
            "uwg_validation_digest": self.uwg_validation_digest,
            "write_lock_digest": self.write_lock_digest,
            "commit_transaction_digest": self.commit_transaction_digest,
            "l4_state_receipt_digest": self.l4_state_receipt_digest,
            "audit_ledger_digest": self.audit_ledger_digest,
            "replay_snapshot_digest": self.replay_snapshot_digest,
            "retrieval_cache_invalidation_digest": self.retrieval_cache_invalidation_digest,
        }

    def stages_emitted(self) -> int:
        """Count of stages whose digest is non-empty."""
        return sum(
            1
            for value in (
                self.exit_commit_request_digest,
                self.uwg_validation_digest,
                self.write_lock_digest,
                self.commit_transaction_digest,
                self.l4_state_receipt_digest,
                self.audit_ledger_digest,
                self.replay_snapshot_digest,
                self.retrieval_cache_invalidation_digest,
            )
            if value != ""
        )


@dataclass(frozen=True, slots=True)
class NoDurableMutationReceipt:
    """Sealed durable-write receipt — fail-closed on cross-stage mismatch.

    Every field is what 00B.7a Phase 6 requires the sealed receipt to
    include. `rollback_required` is true if any stage past
    `commit_transaction_digest` emitted before the mismatch was detected.
    """

    decisive_rule_id: str  # = UWG_COMMIT_BLOCKED_RULE_ID
    terminal_stamp: str  # = DURABLE_WRITE_CONTEXT_MISMATCH_RULE_ID
    committed: bool  # always False for evidence emitted on mismatch
    first_mismatched_stage: str
    stage_digests: StageDigests
    trace_id: str
    request_id: str
    run_id: str
    tenant_id: str
    principal_id: str
    exit_disposition_id: str
    commit_request_id: str
    idempotency_key: str
    replay_key: str
    sealed_receipt_id: str
    reason: str
    dispatch_target: str  # "EXIT_CONTROL"
    rollback_required: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "decisive_rule_id": self.decisive_rule_id,
            "terminal_stamp": self.terminal_stamp,
            "committed": self.committed,
            "first_mismatched_stage": self.first_mismatched_stage,
            "stage_digests": self.stage_digests.to_dict(),
            "trace_id": self.trace_id,
            "request_id": self.request_id,
            "run_id": self.run_id,
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
            "exit_disposition_id": self.exit_disposition_id,
            "commit_request_id": self.commit_request_id,
            "idempotency_key": self.idempotency_key,
            "replay_key": self.replay_key,
            "sealed_receipt_id": self.sealed_receipt_id,
            "reason": self.reason,
            "dispatch_target": self.dispatch_target,
            "rollback_required": self.rollback_required,
        }


class DurableWriteContextMismatchError(Exception):
    """Raised by the UWG durable-write consistency gate on any INV-DW-* violation.

    Upstream pipelines catch this and seal a NO_DURABLE_MUTATION receipt
    with terminal_stamp = DURABLE_WRITE_CONTEXT_MISMATCH and decisive_rule_id
    = UWG_COMMIT_BLOCKED.
    """

    def __init__(self, receipt: NoDurableMutationReceipt) -> None:
        super().__init__(
            f"{receipt.decisive_rule_id}: {receipt.reason} "
            f"first_mismatched_stage={receipt.first_mismatched_stage!r} "
            f"trace_id={receipt.trace_id!r} "
            f"rollback_required={receipt.rollback_required}"
        )
        self.receipt = receipt


__all__ = [
    "DURABLE_WRITE_CONTEXT_MISMATCH_RULE_ID",
    "DurableWriteContextMismatchError",
    "NoDurableMutationReceipt",
    "StageDigests",
    "UWG_COMMIT_BLOCKED_RULE_ID",
]
