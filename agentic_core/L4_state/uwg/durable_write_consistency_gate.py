"""L4/UWG Durable-Write Consistency Gate — cross-stage digest equality.

Maps to: docs/reference/00B_L4_State_Archive_and_UWG/00B.7a_L4_UWG_Durable_Write_Context_Invariant.md

This module is the single chokepoint enforcing INV-DW-1..10 from 00B.7a.
It is pure: no I/O, no logging side effects beyond the explicit OTEL
emission (which goes through `agentic_core.L4_state.otel.uwg_write_spans`),
no HITL, no durable write of its own.

Public surface:
  - `DurableWriteContextMismatchError` — raised on any mismatch
  - `assert_durable_write_chain_match` — the gate function
  - `UWG_COMMIT_BLOCKED_RULE_ID` — re-exported constant

Behavior (in canonical order):
  1. Reject if exit_commit_request_digest is missing or malformed
     (UWG cannot admit without an upstream Exit CommitRequest).
  2. Reject if l5_certification_packet_hash is empty (L5 must have
     certified the packet first — INV-DW-7).
  3. Reject if any emitted stage digest is malformed.
  4. Reject if l5_certification_packet_hash != aggregate_governance_digest
     (when the latter is provided — composes 00A.7a with this invariant).
  5. Reject if any stage digest != canonical durable_write_digest
     (bit-for-bit, INV-DW-1).
  6. Reject if stages emitted out of canonical order (INV-DW-10).
  7. Reject if idempotency replay arrives with a different
     state_diff_candidate_hash (INV-DW-8).
  8. Compute rollback_required = whether commit_transaction_digest
     was emitted before the mismatch was detected.

The gate does NOT validate L5 cross-child equality — that lives in
`agentic_core.L5_safety.enforcement.governance_consistency_gate`. Callers
should run the L5 gate first, capture its returned aggregate digest, and
pass it as `aggregate_governance_digest` to this gate.
"""

from __future__ import annotations

import re
import uuid

from agentic_core.L4_state.types.durable_write_context import (
    WRITE_STAGE_ORDER,
    DurableWriteContext,
    WriteStage,
)
from agentic_core.L4_state.types.no_durable_mutation_receipt import (
    DURABLE_WRITE_CONTEXT_MISMATCH_RULE_ID,
    UWG_COMMIT_BLOCKED_RULE_ID,
    DurableWriteContextMismatchError,
    NoDurableMutationReceipt,
    StageDigests,
)

_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")


def _looks_like_digest(value: str) -> bool:
    return isinstance(value, str) and bool(_HEX64_RE.match(value))


def _build_receipt(
    *,
    canonical_context: DurableWriteContext,
    stage_digests: StageDigests,
    first_mismatched_stage: str,
    reason: str,
    rollback_required: bool,
) -> NoDurableMutationReceipt:
    return NoDurableMutationReceipt(
        decisive_rule_id=UWG_COMMIT_BLOCKED_RULE_ID,
        terminal_stamp=DURABLE_WRITE_CONTEXT_MISMATCH_RULE_ID,
        committed=False,
        first_mismatched_stage=first_mismatched_stage,
        stage_digests=stage_digests,
        trace_id=canonical_context.trace_id,
        request_id=canonical_context.request_id,
        run_id=canonical_context.run_id,
        tenant_id=canonical_context.tenant_id,
        principal_id=canonical_context.principal_id,
        exit_disposition_id=canonical_context.exit_disposition_id,
        commit_request_id=canonical_context.commit_request_id,
        idempotency_key=canonical_context.idempotency_key,
        replay_key=canonical_context.replay_key,
        sealed_receipt_id=f"uwg-receipt-{uuid.uuid4().hex}",
        reason=reason,
        dispatch_target="EXIT_CONTROL",
        rollback_required=rollback_required,
    )


def _commit_txn_already_emitted(stage_digests: StageDigests) -> bool:
    """True if commit_transaction_digest was emitted (rollback may be needed)."""
    return stage_digests.commit_transaction_digest != ""


def assert_durable_write_chain_match(
    *,
    canonical_context: DurableWriteContext,
    exit_commit_request_digest: str,
    uwg_validation_digest: str,
    write_lock_digest: str,
    commit_transaction_digest: str,
    l4_state_receipt_digest: str,
    audit_ledger_digest: str,
    replay_snapshot_digest: str,
    retrieval_cache_invalidation_digest: str,
    aggregate_governance_digest: str = "",
    emitted_stage_order: tuple[WriteStage, ...] | None = None,
) -> str:
    """Raise `DurableWriteContextMismatchError` unless every INV-DW-* holds.

    On success returns the canonical `durable_write_digest` (which every
    stage digest must equal).

    All keyword-only so callers cannot accidentally swap stages.

    Parameters:
      `aggregate_governance_digest` — the hex digest returned by
        `assert_l5_cross_child_match`. When non-empty, the gate enforces
        l5_certification_packet_hash == aggregate_governance_digest. When
        empty, this composition check is skipped (used by tests that
        exercise the L4 gate in isolation).
      `emitted_stage_order` — optional tuple of WriteStage values in the
        order stages actually emitted. When provided the gate enforces
        canonical-order emission (INV-DW-10). When None this check is
        skipped.
    """
    canonical_digest = canonical_context.digest()

    stage_digests = StageDigests(
        exit_commit_request_digest=exit_commit_request_digest,
        uwg_validation_digest=uwg_validation_digest,
        write_lock_digest=write_lock_digest,
        commit_transaction_digest=commit_transaction_digest,
        l4_state_receipt_digest=l4_state_receipt_digest,
        audit_ledger_digest=audit_ledger_digest,
        replay_snapshot_digest=replay_snapshot_digest,
        retrieval_cache_invalidation_digest=retrieval_cache_invalidation_digest,
    )

    # 1. Exit CommitRequest must be present & well-formed (anti-bypass)
    if not _looks_like_digest(exit_commit_request_digest):
        raise DurableWriteContextMismatchError(
            _build_receipt(
                canonical_context=canonical_context,
                stage_digests=stage_digests,
                first_mismatched_stage="exit_commit_request_digest",
                reason="exit_commit_request_digest absent or malformed (UWG bypass attempt)",
                rollback_required=False,
            )
        )

    # 2. L5 certification must be present (INV-DW-7, anti-bypass)
    if canonical_context.l5_certification_packet_hash == "":
        raise DurableWriteContextMismatchError(
            _build_receipt(
                canonical_context=canonical_context,
                stage_digests=stage_digests,
                first_mismatched_stage="l5_certification_packet_hash",
                reason="l5_certification_packet_hash empty (L5 not certified)",
                rollback_required=False,
            )
        )

    # 3. All emitted stage digests must be well-formed
    stage_pairs: tuple[tuple[str, str], ...] = (
        ("uwg_validation_digest", uwg_validation_digest),
        ("write_lock_digest", write_lock_digest),
        ("commit_transaction_digest", commit_transaction_digest),
        ("l4_state_receipt_digest", l4_state_receipt_digest),
        ("audit_ledger_digest", audit_ledger_digest),
        ("replay_snapshot_digest", replay_snapshot_digest),
        ("retrieval_cache_invalidation_digest", retrieval_cache_invalidation_digest),
    )
    for name, value in stage_pairs:
        if not _looks_like_digest(value):
            raise DurableWriteContextMismatchError(
                _build_receipt(
                    canonical_context=canonical_context,
                    stage_digests=stage_digests,
                    first_mismatched_stage=name,
                    reason=f"{name} is not a 64-char hex SHA-256",
                    rollback_required=_commit_txn_already_emitted(stage_digests),
                )
            )

    # 4. L5 certification packet hash must equal the L5 aggregate digest
    #    (compose 00A.7a invariant with this invariant)
    if aggregate_governance_digest != "":
        if not _looks_like_digest(aggregate_governance_digest):
            raise DurableWriteContextMismatchError(
                _build_receipt(
                    canonical_context=canonical_context,
                    stage_digests=stage_digests,
                    first_mismatched_stage="aggregate_governance_digest",
                    reason="aggregate_governance_digest is not a 64-char hex SHA-256",
                    rollback_required=False,
                )
            )
        if canonical_context.l5_certification_packet_hash != aggregate_governance_digest:
            raise DurableWriteContextMismatchError(
                _build_receipt(
                    canonical_context=canonical_context,
                    stage_digests=stage_digests,
                    first_mismatched_stage="l5_certification_packet_hash",
                    reason=(
                        "l5_certification_packet_hash != aggregate_governance_digest "
                        "(L5 certification mismatch)"
                    ),
                    rollback_required=False,
                )
            )

    # 5. Canonical equality across all stages (INV-DW-1)
    equality_pairs: tuple[tuple[str, str], ...] = (
        ("exit_commit_request_digest", exit_commit_request_digest),
        ("uwg_validation_digest", uwg_validation_digest),
        ("write_lock_digest", write_lock_digest),
        ("commit_transaction_digest", commit_transaction_digest),
        ("l4_state_receipt_digest", l4_state_receipt_digest),
        ("audit_ledger_digest", audit_ledger_digest),
        ("replay_snapshot_digest", replay_snapshot_digest),
        ("retrieval_cache_invalidation_digest", retrieval_cache_invalidation_digest),
    )
    canonical_stage_index = {name: idx for idx, name in enumerate(s for s, _ in equality_pairs)}
    for name, value in equality_pairs:
        if value != canonical_digest:
            raise DurableWriteContextMismatchError(
                _build_receipt(
                    canonical_context=canonical_context,
                    stage_digests=stage_digests,
                    first_mismatched_stage=name,
                    reason=f"{name} != durable_write_digest",
                    # rollback required when mismatch detected at-or-after commit_txn
                    rollback_required=(
                        canonical_stage_index[name] >= canonical_stage_index["commit_transaction_digest"]
                    )
                    or _commit_txn_already_emitted(stage_digests),
                )
            )

    # 6. Canonical-order emission (INV-DW-10)
    if emitted_stage_order is not None:
        expected = list(WRITE_STAGE_ORDER)
        actual = list(emitted_stage_order)
        if actual != expected:
            # Identify first stage that emitted out of order.
            first_bad = "<unknown>"
            for idx, stage in enumerate(actual):
                if idx >= len(expected) or stage is not expected[idx]:
                    first_bad = stage.value if isinstance(stage, WriteStage) else str(stage)
                    break
            # Map enum-name to digest-field-name for the receipt.
            stage_to_digest_field = {
                WriteStage.EXIT_COMMIT_REQUEST.value: "exit_commit_request_digest",
                WriteStage.UWG_VALIDATION.value: "uwg_validation_digest",
                WriteStage.WRITE_LOCK.value: "write_lock_digest",
                WriteStage.COMMIT_TXN.value: "commit_transaction_digest",
                WriteStage.L4_STATE_RECEIPT.value: "l4_state_receipt_digest",
                WriteStage.AUDIT_LEDGER.value: "audit_ledger_digest",
                WriteStage.REPLAY_SNAPSHOT.value: "replay_snapshot_digest",
                WriteStage.RETRIEVAL_CACHE_INVALIDATION.value: "retrieval_cache_invalidation_digest",
            }
            first_field = stage_to_digest_field.get(first_bad, first_bad)
            raise DurableWriteContextMismatchError(
                _build_receipt(
                    canonical_context=canonical_context,
                    stage_digests=stage_digests,
                    first_mismatched_stage=first_field,
                    reason=f"stage {first_bad} emitted out of canonical order",
                    rollback_required=_commit_txn_already_emitted(stage_digests),
                )
            )

    # All checks passed.
    return canonical_digest


def assert_idempotency_replay_consistent(
    *,
    canonical_context: DurableWriteContext,
    prior_state_diff_candidate_hash: str,
    prior_l4_state_receipt_digest: str,
) -> str:
    """Validate INV-DW-8 idempotency replay.

    When a second admission arrives with the same idempotency_key as a
    prior admission:
      - If state_diff_candidate_hash matches → return the prior
        l4_state_receipt_digest (deduplicated no-op).
      - If state_diff_candidate_hash differs → raise
        DurableWriteContextMismatchError with first_mismatched_stage =
        "state_diff_candidate_hash".
    """
    if not _looks_like_digest(prior_l4_state_receipt_digest):
        empty_stages = StageDigests("", "", "", "", "", "", "", "")
        raise DurableWriteContextMismatchError(
            _build_receipt(
                canonical_context=canonical_context,
                stage_digests=empty_stages,
                first_mismatched_stage="prior_l4_state_receipt_digest",
                reason="prior l4_state_receipt_digest is not a 64-char hex SHA-256",
                rollback_required=False,
            )
        )
    if canonical_context.state_diff_candidate_hash != prior_state_diff_candidate_hash:
        empty_stages = StageDigests("", "", "", "", "", "", "", "")
        raise DurableWriteContextMismatchError(
            _build_receipt(
                canonical_context=canonical_context,
                stage_digests=empty_stages,
                first_mismatched_stage="state_diff_candidate_hash",
                reason=(
                    "idempotency_key replayed with different state_diff_candidate_hash "
                    "(INV-DW-8 violation)"
                ),
                rollback_required=False,
            )
        )
    return prior_l4_state_receipt_digest


__all__ = [
    "DurableWriteContextMismatchError",
    "UWG_COMMIT_BLOCKED_RULE_ID",
    "assert_durable_write_chain_match",
    "assert_idempotency_replay_consistent",
]
