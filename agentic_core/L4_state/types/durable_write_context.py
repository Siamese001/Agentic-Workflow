"""L4/UWG Durable Write Context — canonical end-to-end mutation binding.

Maps to: docs/reference/00B_L4_State_Archive_and_UWG/00B.7a_L4_UWG_Durable_Write_Context_Invariant.md

Invariant (00B.7a INV-DW-1..10):
  For any durable mutation that reaches L4, every stage in the equality
  chain (Exit CommitRequest -> UWG admission -> write-lock -> commit txn
  -> L4 state receipt -> audit ledger -> replay snapshot ->
  retrieval/cache invalidation) MUST emit the same SHA-256 digest of
  the same DurableWriteContext, bit-for-bit. Mismatch is fail-closed via
  `agentic_core.L4_state.uwg.durable_write_consistency_gate`.

This module provides:
  - `MutationIntentClass`, `WriteStage` enums
  - `DurableWriteContext` frozen dataclass
  - `compute_durable_write_digest()` — canonical-JSON SHA-256
  - `DurableWriteContextField` enum naming every field for mismatch reporting

Determinism mirrors the L2/L5 pattern.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class MutationIntentClass(str, Enum):
    """Frozen mutation intent — see 00B.7a Phase 1."""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    UPSERT = "UPSERT"
    TOMBSTONE = "TOMBSTONE"


class WriteStage(str, Enum):
    """Canonical-order stages in the durable-write equality chain.

    Order is significant — see 00B.7a Phase 3 EQUALITY CHAIN.
    """

    EXIT_COMMIT_REQUEST = "EXIT_COMMIT_REQUEST"
    UWG_VALIDATION = "UWG_VALIDATION"
    WRITE_LOCK = "WRITE_LOCK"
    COMMIT_TXN = "COMMIT_TXN"
    L4_STATE_RECEIPT = "L4_STATE_RECEIPT"
    AUDIT_LEDGER = "AUDIT_LEDGER"
    REPLAY_SNAPSHOT = "REPLAY_SNAPSHOT"
    RETRIEVAL_CACHE_INVALIDATION = "RETRIEVAL_CACHE_INVALIDATION"


# Canonical chain ordering — used by the consistency gate to detect
# out-of-order emission (INV-DW-10).
WRITE_STAGE_ORDER: tuple[WriteStage, ...] = (
    WriteStage.EXIT_COMMIT_REQUEST,
    WriteStage.UWG_VALIDATION,
    WriteStage.WRITE_LOCK,
    WriteStage.COMMIT_TXN,
    WriteStage.L4_STATE_RECEIPT,
    WriteStage.AUDIT_LEDGER,
    WriteStage.REPLAY_SNAPSHOT,
    WriteStage.RETRIEVAL_CACHE_INVALIDATION,
)


class DurableWriteContextField(str, Enum):
    """Field names used in mismatch reporting. Names match dataclass fields."""

    REQUEST_ID = "request_id"
    RUN_ID = "run_id"
    TRACE_ID = "trace_id"
    TENANT_ID = "tenant_id"
    PRINCIPAL_ID = "principal_id"
    EXIT_DISPOSITION_ID = "exit_disposition_id"
    COMMIT_REQUEST_ID = "commit_request_id"
    UWG_RECEIPT_ID = "uwg_receipt_id"
    TARGET_STORE_ID = "target_store_id"
    TARGET_OBJECT_REF = "target_object_ref"
    MUTATION_INTENT_CLASS = "mutation_intent_class"
    STATE_DIFF_CANDIDATE_HASH = "state_diff_candidate_hash"
    BEFORE_SNAPSHOT_HASH = "before_snapshot_hash"
    AFTER_CANDIDATE_HASH = "after_candidate_hash"
    SCHEMA_HASH = "schema_hash"
    POLICY_HASH = "policy_hash"
    BLUEPRINT_HASH = "blueprint_hash"
    CAPABILITY_SCOPE_HASH = "capability_scope_hash"
    SANDBOX_ENVELOPE_HASH = "sandbox_envelope_hash"
    L5_CERTIFICATION_PACKET_HASH = "l5_certification_packet_hash"
    REPLAY_KEY = "replay_key"
    IDEMPOTENCY_KEY = "idempotency_key"
    WRITE_LOCK_ID = "write_lock_id"
    TRANSACTION_ID = "transaction_id"
    AUDIT_MANIFEST_HASH = "audit_manifest_hash"
    ROLLBACK_PLAN_HASH = "rollback_plan_hash"
    REPLAY_SNAPSHOT_HASH = "replay_snapshot_hash"
    RETRIEVAL_INVALIDATION_PLAN_HASH = "retrieval_invalidation_plan_hash"
    CACHE_INVALIDATION_PLAN_HASH = "cache_invalidation_plan_hash"
    READ_SURFACE_REFRESH_PLAN_HASH = "read_surface_refresh_plan_hash"
    FROZEN_DURABLE_WRITE_CONTEXT_HASH = "frozen_durable_write_context_hash"
    UWG_RESOLVER_DIGEST = "uwg_resolver_digest"


_DIGEST_FIELD_ORDER: tuple[str, ...] = tuple(f.value for f in DurableWriteContextField)


@dataclass(frozen=True, slots=True)
class DurableWriteContext:
    """Canonical durable-write context binding all 8 stages — see 00B.7a Phase 1.

    Frozen at Exit CommitRequest emission; consumed by every downstream
    stage. Each stage emits a digest of THIS object — never a re-resolved
    variant.

    Forbidden patterns (enforced upstream by the consistency gate):
      - Mutating any field after construction (frozen=True, slots=True).
      - Re-resolving mutation_intent_class or any *_hash field inside a
        downstream stage (drives widening — caught as a mismatch).
      - Reusing replay_key or idempotency_key across requests.
    """

    # Identity
    request_id: str
    run_id: str
    trace_id: str
    tenant_id: str
    principal_id: str

    # Linkage (Exit ↔ UWG ↔ L4)
    exit_disposition_id: str
    commit_request_id: str
    uwg_receipt_id: str

    # Mutation surface
    target_store_id: str
    target_object_ref: str
    mutation_intent_class: MutationIntentClass
    state_diff_candidate_hash: str
    before_snapshot_hash: str
    after_candidate_hash: str
    schema_hash: str

    # Authority surface (composed with L5 / L2)
    policy_hash: str
    blueprint_hash: str
    capability_scope_hash: str
    sandbox_envelope_hash: str
    l5_certification_packet_hash: str

    # Idempotency / lock / transaction
    replay_key: str
    idempotency_key: str
    write_lock_id: str
    transaction_id: str

    # Audit / replay / rollback
    audit_manifest_hash: str
    rollback_plan_hash: str
    replay_snapshot_hash: str
    retrieval_invalidation_plan_hash: str
    cache_invalidation_plan_hash: str
    read_surface_refresh_plan_hash: str

    # Frozen-context surface
    frozen_durable_write_context_hash: str
    uwg_resolver_digest: str

    def __post_init__(self) -> None:
        raw = asdict(self)
        for name in _DIGEST_FIELD_ORDER:
            value = raw[name]
            if name == "mutation_intent_class":
                if not isinstance(self.mutation_intent_class, MutationIntentClass):
                    raise TypeError(
                        "DurableWriteContext.mutation_intent_class must be a "
                        f"MutationIntentClass enum; got {type(self.mutation_intent_class).__name__}"
                    )
                continue
            if not isinstance(value, str) or value == "":
                raise ValueError(
                    f"DurableWriteContext.{name} must be a non-empty string; "
                    f"uwg_resolver_digest={self.uwg_resolver_digest!r}"
                )

    # ------------------------------------------------------------------ #
    # Canonical serialization + digest
    # ------------------------------------------------------------------ #

    def to_canonical_dict(self) -> dict[str, Any]:
        """Return the deterministic dict used for digest computation."""
        raw = asdict(self)
        canonical: dict[str, Any] = {}
        for name in _DIGEST_FIELD_ORDER:
            value = raw[name]
            if isinstance(value, Enum):
                canonical[name] = value.value
            else:
                canonical[name] = value
        return canonical

    def digest(self) -> str:
        """Stable SHA-256 hex digest of the canonical representation."""
        return compute_durable_write_digest(self)

    def first_mismatched_field(self, other: DurableWriteContext) -> str:
        """Return the first field name that differs between self and other."""
        a = self.to_canonical_dict()
        b = other.to_canonical_dict()
        for name in _DIGEST_FIELD_ORDER:
            if a[name] != b[name]:
                return name
        return ""


def compute_durable_write_digest(ctx: DurableWriteContext) -> str:
    """Compute the canonical SHA-256 digest of a DurableWriteContext."""
    canonical = ctx.to_canonical_dict()
    body = json.dumps(
        canonical,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


__all__ = [
    "DurableWriteContext",
    "DurableWriteContextField",
    "MutationIntentClass",
    "WRITE_STAGE_ORDER",
    "WriteStage",
    "compute_durable_write_digest",
]
