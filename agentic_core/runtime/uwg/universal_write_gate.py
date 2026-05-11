"""UniversalWriteGate — runtime UWG admission façade for W10.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W10

Single entry point for all post-runtime durable write requests.  L6, Exit,
L0, L2, L3, PA, and C0 MUST NOT write L4 directly — all writes go through
``UniversalWriteGate.admit()``.

Policy enforcement:
  - Requests that carry ``current_run_mutation_allowed=True`` are blocked
    unconditionally (invariant: never true, but guarded here as belt-and-suspenders).
  - Requests without ``policy_ref`` are blocked.
  - Requests without ``evidence_refs`` are blocked.
  - ``semantic_cache_writeback`` is blocked by default unless policy explicitly
    enables it (``semantic_cache_enabled`` in policy).
  - Direct write attempts from non-UWG surfaces are rejected and a
    BlockedWriteReceipt is emitted.

On ADMIT: L4WriteAdapter.commit() is called; a StateCommitReceipt is returned.
On BLOCK: BlockedWriteReceipt is returned; no L4 write occurs.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from typing import Optional

from agentic_core.runtime.contracts.future_run_promotion import (
    FutureRunPromotionRequest,
    PROMOTION_TYPE_SEMANTIC_CACHE_WRITEBACK,
)
from agentic_core.runtime.uwg.write_receipts import (
    VERDICT_ADMIT,
    VERDICT_BLOCK,
    BlockedWriteReceipt,
    StateCommitReceipt,
    UWGAdmissionResult,
    _make_blocked_write_receipt,
    _make_state_commit_receipt,
)


# Sources that are NOT allowed to write L4 directly
_FORBIDDEN_DIRECT_WRITE_SOURCES: frozenset[str] = frozenset({
    "Exit",
    "L0",
    "L1",
    "L2",
    "L3",
    "L6",
    "C0",
    "PromptAssembly",
    "PA",
    "HITL",
    "Tool",
    "Model",
})


class DirectWriteAttemptError(RuntimeError):
    """Raised when a non-UWG surface attempts a direct L4 write."""


class UniversalWriteGate:
    """Runtime UWG admission façade.

    Usage::

        uwg = UniversalWriteGate(policy={"semantic_cache_enabled": False})
        result = uwg.admit(promotion_request)
        if result.verdict == VERDICT_ADMIT:
            commit_receipt = result.state_commit_receipt  # StateCommitReceipt
        else:
            blocked_receipt = result.blocked_write_receipt  # BlockedWriteReceipt

    ``policy`` is a plain dict loaded from the app's learning/policy profile.
    The only external dependency is the L4WriteAdapter injected at construction.
    """

    def __init__(
        self,
        *,
        policy: Optional[dict] = None,
        l4_adapter: Optional["L4WriteAdapter"] = None,  # type: ignore[name-defined]  # noqa: F821
    ) -> None:
        self._policy = policy or {}
        self._l4_adapter = l4_adapter  # may be None in test/stub mode

    # ------------------------------------------------------------------
    # Public admission surface
    # ------------------------------------------------------------------

    def admit(
        self,
        request: FutureRunPromotionRequest,
    ) -> "UWGAdmissionOutcome":
        """Evaluate a FutureRunPromotionRequest.  Returns UWGAdmissionOutcome."""
        reason_codes: list[str] = []
        decisive_reason = ""

        # Gate 1: invariant — current run mutation must never be allowed
        if request.current_run_mutation_allowed:
            reason_codes.append("current_run_mutation_not_allowed")
            decisive_reason = "Promotion requests must never mutate the current run."
            return self._block(request, tuple(reason_codes), decisive_reason)

        # Gate 2: requires_uwg must be True
        if not request.requires_uwg:
            reason_codes.append("requires_uwg_missing")
            decisive_reason = "All durable writes must go through UWG."
            return self._block(request, tuple(reason_codes), decisive_reason)

        # Gate 3: policy_ref required
        if not request.policy_ref:
            reason_codes.append("missing_policy_ref")
            decisive_reason = "Promotion without policy_ref is not allowed."
            return self._block(request, tuple(reason_codes), decisive_reason)

        # Gate 4: evidence_refs required
        if not request.evidence_refs:
            reason_codes.append("missing_evidence_refs")
            decisive_reason = "Promotion without evidence is not allowed."
            return self._block(request, tuple(reason_codes), decisive_reason)

        # Gate 5: semantic cache writeback gated behind policy flag
        if request.promotion_type == PROMOTION_TYPE_SEMANTIC_CACHE_WRITEBACK:
            if not self._policy.get("semantic_cache_enabled", False):
                reason_codes.append("semantic_cache_writeback_disabled_by_policy")
                decisive_reason = (
                    "semantic_cache_writeback is disabled by default. "
                    "Set semantic_cache_enabled=true in policy to enable."
                )
                return self._block(request, tuple(reason_codes), decisive_reason)

        # ADMIT — call L4 adapter if present
        state_diff_digest = _hash_diff(request.proposed_state_diff)
        l4_receipt_ref = ""
        if self._l4_adapter is not None:
            from agentic_core.L4_state.adapters.write_adapters import UWG_WRITE_TOKEN
            l4_receipt_ref = self._l4_adapter.commit(
                request,
                _caller="UWG",
                _uwg_token=UWG_WRITE_TOKEN,
            )

        commit_receipt = _make_state_commit_receipt(
            promotion_request_id=request.promotion_request_id,
            target_store=request.target_store,
            target_ref=request.target_ref,
            state_diff_digest=state_diff_digest,
            l4_receipt_ref=l4_receipt_ref,
        )
        admission_id = f"adm::{request.promotion_request_id}::{uuid.uuid4().hex[:8]}"
        admission = UWGAdmissionResult(
            admission_id=admission_id,
            promotion_request_id=request.promotion_request_id,
            verdict=VERDICT_ADMIT,
            reason_codes=(),
            policy_ref=request.policy_ref,
            required_gate_refs=(),
            decisive_reason="All admission gates passed.",
            state_commit_receipt_ref=commit_receipt.commit_id,
            deterministic_digest=_hash_diff(admission_id + VERDICT_ADMIT),
        )
        return UWGAdmissionOutcome(
            admission=admission,
            state_commit_receipt=commit_receipt,
            blocked_write_receipt=None,
        )

    # ------------------------------------------------------------------
    # Direct-write rejection (belt-and-suspenders)
    # ------------------------------------------------------------------

    @staticmethod
    def reject_direct_write(source: str, target_store: str) -> BlockedWriteReceipt:
        """Emit a BlockedWriteReceipt for a direct-write attempt from ``source``.

        This is a static assertion point.  Callers (L4WriteAdapter) invoke this
        when they detect an attempt to write L4 from a non-UWG surface.
        """
        if source in _FORBIDDEN_DIRECT_WRITE_SOURCES:
            raise DirectWriteAttemptError(
                f"Direct L4 write from {source!r} is forbidden. "
                "All writes must go through UniversalWriteGate.admit()."
            )
        return _make_blocked_write_receipt(
            promotion_request_id="",
            target_store=target_store,
            target_ref="",
            reason_codes=(f"direct_write_rejected:{source}",),
            decisive_reason=f"Direct write from {source!r} is not allowed.",
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _block(
        self,
        request: FutureRunPromotionRequest,
        reason_codes: tuple[str, ...],
        decisive_reason: str,
    ) -> "UWGAdmissionOutcome":
        blocked_receipt = _make_blocked_write_receipt(
            promotion_request_id=request.promotion_request_id,
            target_store=request.target_store,
            target_ref=request.target_ref,
            reason_codes=reason_codes,
            decisive_reason=decisive_reason,
        )
        admission_id = f"adm::{request.promotion_request_id}::{uuid.uuid4().hex[:8]}"
        admission = UWGAdmissionResult(
            admission_id=admission_id,
            promotion_request_id=request.promotion_request_id,
            verdict=VERDICT_BLOCK,
            reason_codes=reason_codes,
            policy_ref=request.policy_ref,
            required_gate_refs=(),
            decisive_reason=decisive_reason,
            blocked_write_receipt_ref=blocked_receipt.blocked_write_id,
            deterministic_digest=_hash_diff(admission_id + VERDICT_BLOCK),
        )
        return UWGAdmissionOutcome(
            admission=admission,
            state_commit_receipt=None,
            blocked_write_receipt=blocked_receipt,
        )


class UWGAdmissionOutcome:
    """Outcome of UniversalWriteGate.admit().

    Carries the UWGAdmissionResult plus the appropriate receipt.
    """

    __slots__ = ("admission", "state_commit_receipt", "blocked_write_receipt")

    def __init__(
        self,
        *,
        admission: UWGAdmissionResult,
        state_commit_receipt: Optional[StateCommitReceipt],
        blocked_write_receipt: Optional[BlockedWriteReceipt],
    ) -> None:
        self.admission = admission
        self.state_commit_receipt = state_commit_receipt
        self.blocked_write_receipt = blocked_write_receipt

    @property
    def verdict(self) -> str:
        return self.admission.verdict

    @property
    def is_admit(self) -> bool:
        return self.admission.verdict == VERDICT_ADMIT

    @property
    def is_blocked(self) -> bool:
        return self.admission.verdict == VERDICT_BLOCK


def _hash_diff(data: str) -> str:
    return "sha256::" + hashlib.sha256(data.encode()).hexdigest()


__all__ = [
    "UniversalWriteGate",
    "UWGAdmissionOutcome",
    "DirectWriteAttemptError",
    "_FORBIDDEN_DIRECT_WRITE_SOURCES",
    "VERDICT_ADMIT",
    "VERDICT_BLOCK",
]
