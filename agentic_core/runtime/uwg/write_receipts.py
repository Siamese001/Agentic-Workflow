"""UWG write receipts — StateCommitReceipt and BlockedWriteReceipt.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W10

Emitted by UniversalWriteGate after evaluating a FutureRunPromotionRequest.
  - ADMIT → StateCommitReceipt
  - BLOCK → BlockedWriteReceipt

These receipts are inert data: they record what UWG decided.  They do NOT
trigger any further writes.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

VERDICT_ADMIT = "ADMIT"
VERDICT_BLOCK = "BLOCK"


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(data: dict) -> str:
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return "sha256::" + hashlib.sha256(payload.encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class UWGAdmissionResult:
    """Full UWG admission decision envelope.

    Contains the verdict, reason codes, and receipt refs.
    ``state_commit_receipt_ref`` is populated on ADMIT.
    ``blocked_write_receipt_ref`` is populated on BLOCK.
    """

    admission_id: str = ""
    promotion_request_id: str = ""
    verdict: str = ""                   # ADMIT | BLOCK
    reason_codes: tuple[str, ...] = field(default_factory=tuple)
    policy_ref: str = ""
    required_gate_refs: tuple[str, ...] = field(default_factory=tuple)
    decisive_reason: str = ""
    state_commit_receipt_ref: str = ""  # populated on ADMIT
    blocked_write_receipt_ref: str = "" # populated on BLOCK
    deterministic_digest: str = ""

    schema_version: str = "w10.1"

    def as_dict(self) -> dict:
        return {
            "admission_id": self.admission_id,
            "promotion_request_id": self.promotion_request_id,
            "verdict": self.verdict,
            "reason_codes": list(self.reason_codes),
            "policy_ref": self.policy_ref,
            "required_gate_refs": list(self.required_gate_refs),
            "decisive_reason": self.decisive_reason,
            "state_commit_receipt_ref": self.state_commit_receipt_ref,
            "blocked_write_receipt_ref": self.blocked_write_receipt_ref,
            "deterministic_digest": self.deterministic_digest,
            "schema_version": self.schema_version,
        }


@dataclass(frozen=True, slots=True)
class StateCommitReceipt:
    """Receipt emitted by UWG when a promotion request is ADMITTED and committed.

    ``committed_by`` is always ``"UWG"`` — no other surface may commit.
    """

    commit_id: str = ""
    promotion_request_id: str = ""
    target_store: str = ""
    target_ref: str = ""
    state_diff_digest: str = ""
    committed_by: str = "UWG"           # always UWG
    committed_at: str = ""
    l4_receipt_ref: str = ""            # ref to L4 write confirmation
    deterministic_digest: str = ""

    schema_version: str = "w10.1"

    def __post_init__(self) -> None:
        if self.committed_by != "UWG":
            raise ValueError(
                f"StateCommitReceipt: committed_by must be 'UWG', got {self.committed_by!r}. "
                "Only UWG is authorised to commit durable writes."
            )

    def as_dict(self) -> dict:
        return {
            "commit_id": self.commit_id,
            "promotion_request_id": self.promotion_request_id,
            "target_store": self.target_store,
            "target_ref": self.target_ref,
            "state_diff_digest": self.state_diff_digest,
            "committed_by": self.committed_by,
            "committed_at": self.committed_at,
            "l4_receipt_ref": self.l4_receipt_ref,
            "deterministic_digest": self.deterministic_digest,
            "schema_version": self.schema_version,
        }


@dataclass(frozen=True, slots=True)
class BlockedWriteReceipt:
    """Receipt emitted by UWG when a promotion request is BLOCKED.

    ``blocked_by`` is always ``"UWG"`` — the gate itself issued the block.
    """

    blocked_write_id: str = ""
    promotion_request_id: str = ""
    target_store: str = ""
    target_ref: str = ""
    blocked_by: str = "UWG"             # always UWG
    reason_codes: tuple[str, ...] = field(default_factory=tuple)
    decisive_reason: str = ""
    deterministic_digest: str = ""

    schema_version: str = "w10.1"

    def __post_init__(self) -> None:
        if self.blocked_by != "UWG":
            raise ValueError(
                f"BlockedWriteReceipt: blocked_by must be 'UWG', got {self.blocked_by!r}."
            )

    def as_dict(self) -> dict:
        return {
            "blocked_write_id": self.blocked_write_id,
            "promotion_request_id": self.promotion_request_id,
            "target_store": self.target_store,
            "target_ref": self.target_ref,
            "blocked_by": self.blocked_by,
            "reason_codes": list(self.reason_codes),
            "decisive_reason": self.decisive_reason,
            "deterministic_digest": self.deterministic_digest,
            "schema_version": self.schema_version,
        }


def _make_state_commit_receipt(
    promotion_request_id: str,
    target_store: str,
    target_ref: str,
    state_diff_digest: str,
    l4_receipt_ref: str = "",
) -> StateCommitReceipt:
    commit_id = f"sc::{promotion_request_id}::{uuid.uuid4().hex[:8]}"
    committed_at = _utcnow()
    core = {
        "commit_id": commit_id,
        "promotion_request_id": promotion_request_id,
        "target_store": target_store,
        "committed_at": committed_at,
    }
    return StateCommitReceipt(
        commit_id=commit_id,
        promotion_request_id=promotion_request_id,
        target_store=target_store,
        target_ref=target_ref,
        state_diff_digest=state_diff_digest,
        committed_by="UWG",
        committed_at=committed_at,
        l4_receipt_ref=l4_receipt_ref,
        deterministic_digest=_digest(core),
    )


def _make_blocked_write_receipt(
    promotion_request_id: str,
    target_store: str,
    target_ref: str,
    reason_codes: tuple[str, ...],
    decisive_reason: str,
) -> BlockedWriteReceipt:
    blocked_write_id = f"bw::{promotion_request_id}::{uuid.uuid4().hex[:8]}"
    core = {
        "blocked_write_id": blocked_write_id,
        "promotion_request_id": promotion_request_id,
        "reason_codes": list(reason_codes),
    }
    return BlockedWriteReceipt(
        blocked_write_id=blocked_write_id,
        promotion_request_id=promotion_request_id,
        target_store=target_store,
        target_ref=target_ref,
        blocked_by="UWG",
        reason_codes=reason_codes,
        decisive_reason=decisive_reason,
        deterministic_digest=_digest(core),
    )


__all__ = [
    "UWGAdmissionResult",
    "StateCommitReceipt",
    "BlockedWriteReceipt",
    "VERDICT_ADMIT",
    "VERDICT_BLOCK",
    "_make_state_commit_receipt",
    "_make_blocked_write_receipt",
]
