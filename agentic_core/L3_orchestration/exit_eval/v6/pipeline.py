"""v6 §5.0 -> §X3 end-to-end pipeline orchestrator.

Single entry point that takes raw runtime receipts and returns the final X3
disposition packet plus an optional UWG receipt for commit paths.

Sequence:
1. ``validate_required_receipts`` — §5.0 immediate-fail check.
2. ``bind_run_identity``         — §5.1 N3 cross-field coherence.
3. ``normalize_to_packet``       — §5.1 N2/N5 normalization.
4. ``run_all_x1_gates``          — 10 X1 verdicts.
5. ``aggregate_decision``        — X2 matrix.
6. ``build_x3_packet``           — X3* packet builder.
7. If COMMIT_REQUEST and ``UwgBackends`` provided: ``process_commit_request``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L3_orchestration.exit_eval.v6.preflight import (
    PreflightFailure,
    bind_run_identity,
    normalize_to_packet,
    validate_required_receipts,
)
from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    GateVerdict,
    V6Disposition,
    X3DenyPacket,
)
from agentic_core.L3_orchestration.exit_eval.v6.uwg import (
    UwgBackends,
    UwgReceipt,
    process_commit_request,
)
from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import run_all_x1_gates
from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import (
    AggregateDecision,
    aggregate_decision,
)
from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import build_x3_packet

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ExitEvalResult:
    """End-to-end pipeline output."""

    disposition: V6Disposition
    x3_packet: Any  # X3{Deny|Escalate|CommitRequest|Allow|SafeAbstain}Packet
    verdicts: list[GateVerdict] = field(default_factory=list)
    decision: AggregateDecision | None = None
    uwg_receipt: UwgReceipt | None = None
    preflight_failures: list[PreflightFailure] = field(default_factory=list)
    packet: ExitReviewPacket | None = None
    rationale: str = ""


def _preflight_deny_packet(
    receipts: dict[str, Any],
    failures: list[PreflightFailure],
) -> X3DenyPacket:
    """Build an X3A packet for receipts that fail §5.0 immediate-fail checks."""
    reason_codes = sorted({f.reason_code for f in failures})
    failed_fields = sorted({f.field for f in failures})
    return X3DenyPacket(
        sub_disposition="DENY_STOP",
        reason_codes=reason_codes,
        failed_gate_ids=["preflight"],
        user_safe_message=(
            "Your request could not be processed safely. Required runtime receipts were missing or invalid."
        ),
        l6_failure_packet={
            "rationale": "preflight_immediate_fail",
            "failed_fields": failed_fields,
            "details": [{"field": f.field, "code": f.reason_code, "detail": f.detail} for f in failures],
        },
        trace_root=str(receipts.get("trace_root", "")),
    )


@dataclass(slots=True)
class ExitEvalPipeline:
    """Configurable pipeline. ``uwg_backends`` is optional; when None, COMMIT_REQUEST
    paths return the X3C packet without invoking UWG."""

    uwg_backends: UwgBackends | None = None
    skip_identity_binding: bool = False

    def run(self, receipts: dict[str, Any]) -> ExitEvalResult:
        """Run the full v6 pipeline against a receipts dict."""
        # 1. §5.0 immediate-fail
        failures = validate_required_receipts(receipts)
        if failures:
            packet = _preflight_deny_packet(receipts, failures)
            return ExitEvalResult(
                disposition=V6Disposition.DENY,
                x3_packet=packet,
                preflight_failures=list(failures),
                rationale="preflight_immediate_fail",
            )

        # 2. §5.1 N3 identity binding (optional)
        if not self.skip_identity_binding:
            id_failures = bind_run_identity(receipts)
            if id_failures:
                packet = _preflight_deny_packet(receipts, id_failures)
                return ExitEvalResult(
                    disposition=V6Disposition.DENY,
                    x3_packet=packet,
                    preflight_failures=list(id_failures),
                    rationale="identity_binding_failed",
                )

        # 3. normalize
        review = normalize_to_packet(receipts)

        # 4. X1 verdicts
        verdicts = run_all_x1_gates(review)

        # 5. X2 aggregate
        decision = aggregate_decision(verdicts, review)

        # 6. X3 packet
        x3_packet = build_x3_packet(
            review,
            decision,
            grader_verdict_bundle=verdicts,
        )

        result = ExitEvalResult(
            disposition=decision.disposition,
            x3_packet=x3_packet,
            verdicts=verdicts,
            decision=decision,
            packet=review,
            rationale=decision.rationale,
        )

        # 7. UWG handoff for COMMIT_REQUEST
        if decision.disposition is V6Disposition.COMMIT_REQUEST and self.uwg_backends is not None:
            try:
                result.uwg_receipt = process_commit_request(x3_packet, self.uwg_backends)
            except (RuntimeError, OSError) as exc:
                logger.warning("pipeline: UWG handoff failed: %s", exc)
                result.uwg_receipt = None

        return result


def run_exit_eval(
    receipts: dict[str, Any],
    *,
    uwg_backends: UwgBackends | None = None,
) -> ExitEvalResult:
    """Convenience wrapper around ``ExitEvalPipeline.run``."""
    return ExitEvalPipeline(uwg_backends=uwg_backends).run(receipts)


__all__ = ["ExitEvalPipeline", "ExitEvalResult", "run_exit_eval"]
