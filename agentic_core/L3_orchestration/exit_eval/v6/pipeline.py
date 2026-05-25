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
8. ``build_return_payload``       — §5.7 final caller return shape.
9. ``seal_runtime_exhaust``       — §5.7 sealed L6 exhaust manifest.
10. ``close_runtime_boundary``    — §5.7 boundary close.

Each step emits a §5.8 OTEL span via the ``otel`` module so observers can
verify the path actually ran.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L3_orchestration.exit_eval.v6 import otel as v6_otel
from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    build_default_app_evaluator,
)
from agentic_core.L3_orchestration.exit_eval.v6.app_specific_evaluator import (
    AppSpecificEvaluator,
    evaluate_from_packet,
)
from agentic_core.L3_orchestration.exit_eval.v6.preflight import (
    PreflightFailure,
    bind_run_identity,
    normalize_to_packet,
    validate_required_receipts,
)
from agentic_core.L3_orchestration.exit_eval.v6.return_payload import (
    ReturnPayload,
    RuntimeExhaustManifest,
    build_return_payload,
    close_runtime_boundary,
    seal_runtime_exhaust,
    validate_return_payload,
)
from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    GateVerdict,
    V6Disposition,
    X3DenyPacket,
)
from agentic_core.runtime.contracts.x1_checkout_result import X1CheckoutResult
from agentic_core.L3_orchestration.exit_eval.v6.uwg import (
    UwgBackends,
    UwgReceipt,
    process_commit_request,
)
from agentic_core.L3_orchestration.exit_eval.v6.x1_checkout_adapter import (
    build_x1_checkout_result,
)
from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import (
    run_all_x1_gates_with_sub_stages,
)
from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import (
    AggregateDecision,
    aggregate_decision,
)
from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import (
    SPINE_EXIT_V6_PREFLIGHT_DENIAL_CARRIER_REF,
    build_x3_packet,
)

logger = logging.getLogger(__name__)


_X1_SPAN_FOR_GATE: dict[str, str] = {
    "X1A": v6_otel.SPAN_X1A_POLICY,
    "X1B": v6_otel.SPAN_X1B_TASK,
    "X1C": v6_otel.SPAN_X1C_SAFETY,
    "X1D": v6_otel.SPAN_X1D_GROUNDED,
    "X1E": v6_otel.SPAN_X1E_TRAJECTORY,
    "X1F": v6_otel.SPAN_X1F_ADVERSARIAL,
    "X1G": v6_otel.SPAN_X1G_CONSISTENCY,
    "X1H": v6_otel.SPAN_X1H_REPLAY,
    "X1I": v6_otel.SPAN_X1I_OBSERVABILITY,
    "X1J": v6_otel.SPAN_X1J_WRITE_ELIGIBILITY,
}


_X3_EMIT_SPAN_FOR_DISPOSITION: dict[V6Disposition, str] = {
    V6Disposition.DENY: v6_otel.SPAN_X3A_DENY_EMIT,
    V6Disposition.ESCALATE: v6_otel.SPAN_X3B_ESCALATE_EMIT,
    V6Disposition.COMMIT_REQUEST: v6_otel.SPAN_X3C_COMMIT_REQUEST_EMIT,
    V6Disposition.ALLOW: v6_otel.SPAN_X3D_ALLOW_EMIT,
    V6Disposition.SAFE_ABSTAIN: v6_otel.SPAN_X3E_ABSTAIN_EMIT,
}


@dataclass(slots=True)
class ExitEvalResult:
    """End-to-end pipeline output.

    AG-5: Added x1_checkout_result for structured X1 gate carrier.
    """

    disposition: V6Disposition
    x3_packet: Any  # X3{Deny|Escalate|CommitRequest|Allow|SafeAbstain}Packet
    verdicts: list[GateVerdict] = field(default_factory=list)
    decision: AggregateDecision | None = None
    uwg_receipt: UwgReceipt | None = None
    preflight_failures: list[PreflightFailure] = field(default_factory=list)
    packet: ExitReviewPacket | None = None
    rationale: str = ""
    return_payload: ReturnPayload | None = None
    exhaust_manifest: RuntimeExhaustManifest | None = None
    runtime_boundary_closed: bool = False
    return_payload_failures: list[str] = field(default_factory=list)
    x1_sub_stages: list[dict[str, Any]] = field(default_factory=list)
    x1_checkout_result: X1CheckoutResult | None = None


def _preflight_deny_packet(
    receipts: dict[str, Any],
    failures: list[PreflightFailure],
) -> X3DenyPacket:
    """Build an X3A packet for receipts that fail §5.0 immediate-fail checks."""
    reason_codes = sorted({f.reason_code for f in failures})
    failed_fields = sorted({f.field for f in failures})
    refs = receipts.get("l5_certification_refs")
    carriers: list[str] = []
    if isinstance(refs, (list, tuple)):
        carriers = [str(x).strip() for x in refs if str(x).strip()]
    carrier0 = str(receipts.get("l5_certification_ref") or "").strip()
    l5_ref = carrier0 or (carriers[0] if carriers else SPINE_EXIT_V6_PREFLIGHT_DENIAL_CARRIER_REF)
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
        l5_certification_ref=l5_ref,
    )


@dataclass(slots=True)
class ExitEvalPipeline:
    """Configurable pipeline. ``uwg_backends`` is optional; when None, COMMIT_REQUEST
    paths return the X3C packet without invoking UWG.

    OTEL emission is always on; when no SDK is installed, spans are recorded
    in-memory on the packet (used by §5.8 anti-bypass tests).
    """

    uwg_backends: UwgBackends | None = None
    skip_identity_binding: bool = False
    seal_exhaust: bool = True
    build_payload: bool = True
    # W1.P1 — app-specific evaluator (optional). When None, the pipeline
    # uses build_default_app_evaluator() which reads per-dim scores from
    # packet.output.dim_scores. Runs with no rubric_ref/threshold_profile_ref
    # pass through unbound (fall-through to generic V6 grading) — existing
    # non-app-bound callers are untouched.
    app_evaluator: AppSpecificEvaluator | None = None

    def run(self, receipts: dict[str, Any]) -> ExitEvalResult:
        """Run the full v6 pipeline against a receipts dict."""
        # 1. §5.0 immediate-fail (emit input spans even on failure)
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

        # 3. normalize → ExitReviewPacket (we now have a target for span recording)
        review = normalize_to_packet(receipts)

        # §5.8 input/normalization spans
        v6_otel.record_span(v6_otel.SPAN_INPUT_RECEIVE, review)
        v6_otel.record_span(
            v6_otel.SPAN_INPUT_CLASSIFY_SOURCE,
            review,
            attributes={"source_type": review.source_type.value},
        )
        v6_otel.record_span(v6_otel.SPAN_INPUT_VALIDATE_RECEIPTS, review)
        v6_otel.record_span(v6_otel.SPAN_INPUT_BIND_IDENTITY, review)
        v6_otel.record_span(v6_otel.SPAN_INPUT_PRESERVE_AUTHORITY_LABELS, review)
        v6_otel.record_span(v6_otel.SPAN_INPUT_NORMALIZE_REVIEW_PACKET, review)

        # 4. X1 verdicts — record one span per gate, capture sub-stage timing
        verdicts, x1_sub_stages = run_all_x1_gates_with_sub_stages(review)
        for verdict in verdicts:
            span_name = _X1_SPAN_FOR_GATE.get(verdict.gate_id)
            if span_name is None:
                continue
            v6_otel.record_span(
                span_name,
                review,
                attributes={
                    "gate_id": verdict.gate_id,
                    "result": verdict.result.value,
                    "reason_codes": list(verdict.reason_codes),
                    "score": verdict.score,
                    "threshold": verdict.threshold,
                    "grader_type": verdict.grader_type,
                    "abstain_flag": verdict.abstain_flag,
                },
            )

        # 4b. W1.P1 — App-specific (Fort Knox domain rubric) evaluation.
        # Runs only when the route was bound by L0 app_domain_resolver
        # (rubric_ref + threshold_profile_ref present on the packet).
        # Result is serialized into review.app_specific_eval so X2/X3 can
        # read domain metrics. Non-app-bound runs return bound=False and
        # leave review.app_specific_eval empty (existing behavior preserved).
        evaluator = self.app_evaluator or build_default_app_evaluator()
        try:
            app_eval = evaluate_from_packet(
                evaluator=evaluator,
                app_id=review.app_id,
                task_class=review.task_class,
                rubric_ref=review.rubric_ref,
                threshold_profile_ref=review.threshold_profile_ref,
                run_context={
                    "output": review.output or {},
                    "evidence_bundle": review.evidence_bundle or {},
                    "final_evidence_contract": review.final_evidence_contract or {},
                    "state_diff": review.state_diff or {},
                    "route_contract": review.route_contract or {},
                    "trace_root": review.trace_root,
                },
            )
        except (RuntimeError, OSError, ValueError, KeyError) as exc:
            # guardian: allow-log-and-swallow -- any eval-pipeline exception is
            # treated as unbound (falls through to generic V6). Never crashes
            # Exit. Logged for operator visibility.
            logger.warning("pipeline: app_specific_eval raised %s: %s", type(exc).__name__, exc)
            from agentic_core.L3_orchestration.exit_eval.v6.app_specific_evaluator import (
                AppSpecificEvalResult,
            )
            app_eval = AppSpecificEvalResult(bound=False)

        if app_eval.bound:
            review.app_specific_eval = app_eval.to_packet_dict()
            # W4.P3 — domain-metric span attrs (counts by outcome).
            # W4.P4 — tracked_metrics (Anthropic canonical keys) from
            # run_context.output.tracked_metrics when upstream producers
            # populate it. Absence is fine — the span still carries the
            # core attrs below.
            _dim_pass = sum(1 for d in app_eval.dimensions if d.status == "PASS")
            _dim_fail = sum(1 for d in app_eval.dimensions if d.status == "FAIL")
            _dim_unknown = sum(1 for d in app_eval.dimensions if d.status == "UNKNOWN")
            _tracked = (review.output or {}).get("tracked_metrics") or {}
            _tracked = _tracked if isinstance(_tracked, dict) else {}
            v6_otel.record_span(
                "exit.app_specific_eval",
                review,
                attributes={
                    "app_id": app_eval.app_id,
                    "task_class": app_eval.task_class,
                    "rubric_ref": app_eval.rubric_ref,
                    "threshold_profile_ref": app_eval.threshold_profile_ref,
                    "overall_score": app_eval.overall_score,
                    "overall_pass_threshold": app_eval.overall_pass_threshold,
                    "passed": app_eval.passed,
                    "fail_reasons": list(app_eval.fail_reasons),
                    "dimension_count": len(app_eval.dimensions),
                    "hitl_policy": app_eval.hitl_policy,
                    # W4.P3 counts by outcome
                    "dim_pass_count": _dim_pass,
                    "dim_fail_count": _dim_fail,
                    "dim_unknown_count": _dim_unknown,
                    # W4.P4 canonical tracked_metrics (present if producer emits)
                    "ttft_ms": float(_tracked.get("ttft_ms", 0.0)) or None,
                    "ttlt_ms": float(_tracked.get("ttlt_ms", 0.0)) or None,
                    "output_tokens_per_sec": float(_tracked.get("output_tokens_per_sec", 0.0)) or None,
                    "n_total_tokens": int(_tracked.get("n_total_tokens", 0)) or None,
                    "cost_usd": float(_tracked.get("cost_usd", 0.0)) or None,
                },
            )

        # AG-5: Build X1CheckoutResult from gate verdicts + packet
        x1_checkout = build_x1_checkout_result(verdicts, review)

        # 5. X2 aggregate
        decision = aggregate_decision(verdicts, review, x1_checkout_result=x1_checkout)

        # 5b. W5.P7 — Emit eval_harness_outcome ledger row. Fail-soft: any
        # exception is swallowed so the ledger cannot crash the Exit pipeline.
        # The writer itself is best-effort (see tools.ledgers.hook_helpers).
        try:
            _emit_eval_harness_outcome(review, app_eval, decision)
        except Exception as exc:  # noqa: BLE001  # guardian: allow-log-and-swallow -- P1 ADG burndown  # guardian: allow-broad-exception -- P1 ADG burndown
            # guardian: allow-broad-except -- telemetry path MUST never break
            # Exit; any ledger failure is logged but ignored.
            logger.warning(
                "pipeline: eval_harness_outcome ledger emit raised %s: %s",
                type(exc).__name__, exc,
            )
        v6_otel.record_span(
            v6_otel.SPAN_X2_AGGREGATE,
            review,
            attributes={
                "x3_disposition": decision.disposition.value,
                "rationale": decision.rationale,
                "reason_codes": list(decision.reason_codes),
                "failed_gate_ids": list(decision.failed_gate_ids),
            },
        )

        # 6. X3 packet
        x3_packet = build_x3_packet(
            review,
            decision,
            grader_verdict_bundle=verdicts,
        )
        v6_otel.record_span(
            v6_otel.SPAN_X3_SELECT,
            review,
            attributes={"x3_disposition": decision.disposition.value},
        )
        emit_span = _X3_EMIT_SPAN_FOR_DISPOSITION.get(decision.disposition)
        if emit_span is not None:
            v6_otel.record_span(emit_span, review, attributes={"x3_disposition": decision.disposition.value})

        result = ExitEvalResult(
            disposition=decision.disposition,
            x3_packet=x3_packet,
            verdicts=verdicts,
            decision=decision,
            packet=review,
            rationale=decision.rationale,
            x1_sub_stages=x1_sub_stages,
            x1_checkout_result=decision.x1_checkout_result,
        )

        # 7. UWG handoff for COMMIT_REQUEST
        if decision.disposition is V6Disposition.COMMIT_REQUEST and self.uwg_backends is not None:
            v6_otel.record_span(
                v6_otel.SPAN_X3C_COMMIT_REQUEST_BUILD,
                review,
                attributes={"commit_request_id": getattr(x3_packet, "commit_request_id", "")},
            )
            v6_otel.record_span(v6_otel.SPAN_X3C_UWG_HANDOFF_EMIT, review)
            try:
                result.uwg_receipt = process_commit_request(x3_packet, self.uwg_backends)
                v6_otel.record_span(
                    v6_otel.SPAN_UWG_RESPONSE_RECEIVE,
                    review,
                    attributes={
                        "uwg_outcome": result.uwg_receipt.outcome.value if result.uwg_receipt else "",
                    },
                )
            except (RuntimeError, OSError) as exc:
                logger.warning("pipeline: UWG handoff failed: %s", exc)
                result.uwg_receipt = None

        # 8. §5.7 build return payload
        if self.build_payload:
            payload = build_return_payload(review, x3_packet, uwg_receipt=result.uwg_receipt)
            v6_otel.record_span(v6_otel.SPAN_RETURN_BUILD, review)
            failures_list = validate_return_payload(payload, review, uwg_receipt=result.uwg_receipt)
            v6_otel.record_span(
                v6_otel.SPAN_RETURN_VALIDATE,
                review,
                attributes={"reason_codes": failures_list},
            )
            result.return_payload = payload
            result.return_payload_failures = list(failures_list)

        # 9. §5.7 seal exhaust manifest
        if self.seal_exhaust:
            manifest = seal_runtime_exhaust(review, x3_packet, verdicts, uwg_receipt=result.uwg_receipt)
            v6_otel.record_span(
                v6_otel.SPAN_EXHAUST_SEAL,
                review,
                attributes={"exhaust_manifest_id": manifest.exhaust_manifest_id},
            )
            result.exhaust_manifest = manifest

            # 10. close runtime boundary
            if result.return_payload is not None:
                closed = close_runtime_boundary(result.return_payload, manifest)
                v6_otel.record_span(
                    v6_otel.SPAN_RUNTIME_BOUNDARY_CLOSE,
                    review,
                    attributes={"closed": closed},
                )
                result.runtime_boundary_closed = closed

        return result


def run_exit_eval(
    receipts: dict[str, Any],
    *,
    uwg_backends: UwgBackends | None = None,
) -> ExitEvalResult:
    """Convenience wrapper around ``ExitEvalPipeline.run``."""
    return ExitEvalPipeline(uwg_backends=uwg_backends).run(receipts)


# ---------------------------------------------------------------------------
# W5.P7 — eval_harness_outcome ledger writer
# ---------------------------------------------------------------------------


def _score_band_for_ase(
    app_eval: "AppSpecificEvalResult",  # noqa: F821 -- forward ref; real import below
    decision: "AggregateDecision",  # noqa: F821
) -> str:
    """Collapse the ASE + X2 decision into a single band for the ledger."""
    if not app_eval.bound:
        return "unbound"
    if app_eval.passed:
        return "pass"
    # Bound and not passed. Use the X2 disposition to split.
    disp_value = getattr(decision.disposition, "value", "")
    if disp_value == "X3B":  # ESCALATE
        return "escalate"
    # Check whether any fail reason looks like UNKNOWN (guardrail closed on UNKNOWN)
    for r in app_eval.fail_reasons:
        if "unknown_fail_closed" in str(r):
            return "unknown"
    return "deny"


def _emit_eval_harness_outcome(
    review: "ExitReviewPacket",  # noqa: F821
    app_eval: "AppSpecificEvalResult",  # noqa: F821
    decision: "AggregateDecision",  # noqa: F821
) -> str:
    """Emit one eval_harness_outcome ledger row per Exit pipeline run.

    Invariants:
      - Fail-soft: any writer error returns "" (handled by hook_helpers)
      - event_kind = "app_eval_bound" | "app_eval_unbound"
      - prediction_json carries the full ASE snapshot; outcome_json carries
        the X2 disposition + rationale
      - repo_area = app_id when bound, else the route_contract route_id
    """
    from tools.ledgers.hook_helpers import emit_ledger_event

    dim_count = len(app_eval.dimensions)
    dim_fail_count = sum(1 for d in app_eval.dimensions if d.status == "FAIL")
    dim_unknown_count = sum(1 for d in app_eval.dimensions if d.status == "UNKNOWN")
    prediction = {
        "bound": app_eval.bound,
        "app_id": app_eval.app_id,
        "task_class": app_eval.task_class,
        "rubric_ref": app_eval.rubric_ref,
        "threshold_profile_ref": app_eval.threshold_profile_ref,
        "overall_score": app_eval.overall_score,
        "overall_pass_threshold": app_eval.overall_pass_threshold,
        "hitl_policy": app_eval.hitl_policy,
        "dim_count": dim_count,
        "dim_fail_count": dim_fail_count,
        "dim_unknown_count": dim_unknown_count,
        "fail_reasons": list(app_eval.fail_reasons),
    }
    outcome = {
        "disposition": getattr(decision.disposition, "value", str(decision.disposition)),
        "rationale": decision.rationale,
        "failed_gate_ids": list(decision.failed_gate_ids),
        "reason_codes": list(decision.reason_codes),
    }
    repo_area = app_eval.app_id or str(
        (review.route_contract or {}).get("route_id", "") or ""
    )
    return emit_ledger_event(
        ledger="eval_harness_outcome",
        event_kind="app_eval_bound" if app_eval.bound else "app_eval_unbound",
        prediction=prediction,
        outcome=outcome,
        score_band=_score_band_for_ase(app_eval, decision),
        score_numeric=float(app_eval.overall_score),
        repo_area=repo_area,
        metadata={
            "trace_root": review.trace_root,
            "run_id": review.run_id,
        },
    )


__all__ = ["ExitEvalPipeline", "ExitEvalResult", "run_exit_eval"]
