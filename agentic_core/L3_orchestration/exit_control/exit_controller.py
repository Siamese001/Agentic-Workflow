"""Runtime HITL exit controller — step [5] dispatch primitive.

Per ADR-023 §3.2, ``classify_exit(sealed_folder, policy)`` is the single
runtime decision primitive for v30 step [5]. Every governed runner must call
it immediately after sealing (E5) and before any UWG invocation.

Returns one of:

- ``ExitAction.DENY``           — envelope blocks unconditionally
- ``ExitAction.COMMIT``         — envelope passes policy; proceed to UWG
- ``ExitAction.ESCALATE_HITL``  — envelope routes through runtime HITL

For ESCALATE_HITL, the controller:

1. Classifies the escalation via L5 (``classify_escalation_class``)
2. Resolves approver pool, timeout, fallback via L5
3. Records a PENDING entry in the runtime HITL ledger (L3)
4. Emits ``hitl.escalate`` OTel span

Resume path (``record_approval`` / ``record_denial`` / ``record_timeout``)
updates the ledger and emits the corresponding outcome span. The orchestrator
thread does NOT block; adapters call back into the controller asynchronously.

Idempotency (plan P2.1 pain point): resuming on an already-resolved ledger
entry is a hard error — callers must check state first.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Mapping

from agentic_core.L3_orchestration.exit_control import hitl_spans
from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    LedgerEntry,
    LedgerState,
    RuntimeHitlLedger,
)
from agentic_core.L5_safety.exit_control.hitl_classes import HitlClass
from agentic_core.L5_safety.exit_control.hitl_policy import (
    HitlPolicy,
    classify_escalation_class,
    resolve_approver_pool,
    set_fallback,
    set_timeout,
)


class ExitAction(str, Enum):
    """The three outcomes of ``classify_exit``."""

    DENY = "DENY"
    COMMIT = "COMMIT"
    ESCALATE_HITL = "ESCALATE_HITL"


@dataclass(frozen=True)
class ExitDecision:
    """Result of ``classify_exit``.

    For DENY/COMMIT, ``hitl_class`` and ``ledger_id`` are ``None``.
    For ESCALATE_HITL, both are populated and a ``hitl.escalate`` span was emitted.
    """

    action: ExitAction
    hitl_class: HitlClass | None = None
    ledger_id: str | None = None
    approver_pool: str | None = None
    timeout_s: int | None = None
    fallback: str | None = None
    deny_reason: str | None = None


def classify_exit(
    sealed_folder: Mapping[str, Any],
    policy: HitlPolicy,
    *,
    run_id: str,
    trace_id: str,
    ledger: RuntimeHitlLedger,
) -> ExitDecision:
    """Classify a sealed-folder envelope per ADR-023 §3.2.

    Envelope contract (all fields optional; see ``hitl_policy`` for the
    classification-relevant fields):

    - ``deny`` (bool) — if True, decision is ``DENY`` regardless of policy
    - ``deny_reason`` (str) — optional rationale attached to ``DENY``
    - plus the classification fields consumed by
      :func:`classify_escalation_class`
    """
    if not isinstance(sealed_folder, Mapping):
        raise TypeError("sealed_folder must be a mapping")

    if bool(sealed_folder.get("deny")):
        return ExitDecision(
            action=ExitAction.DENY,
            deny_reason=str(sealed_folder.get("deny_reason", "")) or None,
        )

    hitl_class = classify_escalation_class(sealed_folder, policy)
    if hitl_class is None:
        return ExitDecision(action=ExitAction.COMMIT)

    approver_pool = resolve_approver_pool(hitl_class, policy)
    timeout_s = set_timeout(hitl_class, policy)
    fallback = set_fallback(hitl_class, policy)

    entry = ledger.record_escalation(
        run_id=run_id,
        trace_id=trace_id,
        hitl_class=hitl_class,
        approver_pool=approver_pool,
        timeout_s=timeout_s,
        policy_snapshot=policy.policy_snapshot,
        envelope=dict(sealed_folder),
    )

    hitl_spans.emit_escalate(
        run_id=run_id,
        trace_id=trace_id,
        hitl_class=hitl_class.value,
        approver_pool=approver_pool,
        timeout_s=timeout_s,
        policy_snapshot=policy.policy_snapshot,
    )

    return ExitDecision(
        action=ExitAction.ESCALATE_HITL,
        hitl_class=hitl_class,
        ledger_id=entry.ledger_id,
        approver_pool=approver_pool,
        timeout_s=timeout_s,
        fallback=fallback,
    )


class ExitController:
    """Stateful wrapper providing resume-path operations on a shared ledger."""

    def __init__(
        self,
        policy: HitlPolicy,
        ledger: RuntimeHitlLedger,
        *,
        now: Callable[[], float] | None = None,
    ) -> None:
        self._policy = policy
        self._ledger = ledger
        self._now = now or time.time

    def classify(
        self,
        sealed_folder: Mapping[str, Any],
        *,
        run_id: str,
        trace_id: str,
    ) -> ExitDecision:
        return classify_exit(
            sealed_folder,
            self._policy,
            run_id=run_id,
            trace_id=trace_id,
            ledger=self._ledger,
        )

    def record_approval(
        self,
        ledger_id: str,
        *,
        approver_id: str,
        rationale: str | None = None,
    ) -> LedgerEntry:
        entry = self._require_pending(ledger_id)
        updated = self._ledger.record_approved(
            ledger_id, approver_id=approver_id, rationale=rationale
        )
        hitl_spans.emit_approved(
            run_id=entry.run_id,
            trace_id=entry.trace_id,
            approver_id=approver_id,
            latency_ms=_latency_ms(entry.created_at, updated.resolved_at),
            rationale_len=len(rationale or ""),
        )
        return updated

    def record_denial(
        self,
        ledger_id: str,
        *,
        approver_id: str,
        reason_code: str,
        rationale: str | None = None,
    ) -> LedgerEntry:
        entry = self._require_pending(ledger_id)
        updated = self._ledger.record_denied(
            ledger_id,
            approver_id=approver_id,
            reason_code=reason_code,
            rationale=rationale,
        )
        hitl_spans.emit_denied(
            run_id=entry.run_id,
            trace_id=entry.trace_id,
            approver_id=approver_id,
            latency_ms=_latency_ms(entry.created_at, updated.resolved_at),
            reason_code=reason_code,
        )
        return updated

    def record_timeout(self, ledger_id: str) -> LedgerEntry:
        entry = self._require_pending(ledger_id)
        updated = self._ledger.record_timeout(ledger_id)
        hitl_spans.emit_timeout(
            run_id=entry.run_id,
            trace_id=entry.trace_id,
            timeout_s=entry.timeout_s,
            fallback_taken=set_fallback(entry.hitl_class, self._policy),
        )
        return updated

    def _require_pending(self, ledger_id: str) -> LedgerEntry:
        entry = self._ledger.get(ledger_id)
        if entry is None:
            raise KeyError(f"ledger entry not found: {ledger_id}")
        if entry.state is not LedgerState.PENDING:
            raise ValueError(
                f"ledger entry {ledger_id} already resolved as {entry.state.value}"
            )
        return entry


def _latency_ms(created_at: float, resolved_at: float | None) -> int:
    if resolved_at is None:
        return 0
    return int(max(0.0, (resolved_at - created_at) * 1000.0))


__all__ = [
    "ExitAction",
    "ExitController",
    "ExitDecision",
    "classify_exit",
]
