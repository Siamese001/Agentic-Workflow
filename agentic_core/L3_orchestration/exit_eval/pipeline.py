"""Evaluation pipeline — run gates, derive disposition, emit BUS + spans.

Implements the v4 X1 → X3 control flow:

1. Run X1A-X1F gates in order.
2. If any gate denies on a hard/binary failure → X3A.
3. If any gate abstains on a model-based dimension → X3B (HITL,
   ``JUDGE_ABSTAINED``).
4. If all gates pass and run is commit-path → run X1G consistency; failure
   routes to X3B with ``CONSISTENCY_FAIL`` / ``INSUFFICIENT_HISTORY``.
5. Otherwise → X3C (commit candidate) or X3D (allow/finish) per the
   caller's ``commit_candidate`` flag.
6. Break-glass (X3E) is invoked separately by the caller; this module
   accepts the resulting invocation and short-circuits the bypassed
   gates.

The pipeline produces a ``DispositionEnvelope`` consumable by
``exit_control.classify_exit`` (ADR-023).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from agentic_core.L3_orchestration.exit_eval.break_glass import (
    BreakGlassInvocation,
)
from agentic_core.L3_orchestration.exit_eval.bus import BusEmitter, BusWriteError
from agentic_core.L3_orchestration.exit_eval.consistency import (
    BucketKey,
    ConsistencyCheck,
    PassKStore,
)
from agentic_core.L3_orchestration.exit_eval.disposition import (
    Disposition,
    DispositionEnvelope,
    ReasonCode,
)
from agentic_core.L3_orchestration.exit_eval.gates import (
    Gate,
    GateContext,
    GateResult,
)
from agentic_core.L3_orchestration.exit_eval.otel_spans import (
    NoOpSpanSink,
    SpanSink,
    build_disposition_span,
    build_gate_span,
)


@dataclass
class EvaluationResult:
    """Full output of ``EvaluationPipeline.run``."""

    envelope: DispositionEnvelope
    gate_results: tuple[GateResult, ...]
    consistency: ConsistencyCheck | None = None
    bypassed_gates: tuple[str, ...] = ()
    bus_write_failed: bool = False
    extras: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConsistencyPolicy:
    """Parameters for X1G consistency gating on commit-path runs."""

    k: int = 5
    theta: float = 0.95
    # If True, consistency gate applies only when ``commit_candidate=True``.
    # Non-commit runs skip X1G (per v4 §X1G non-commit scope).
    commit_path_only: bool = True


class EvaluationPipeline:
    """Runs gates in order and produces a disposition envelope.

    The pipeline is fail-closed per H8:

    - BUS write failure → X3B (``AUDIT_UNAVAILABLE``).
    - Grader exception → X3A (``GRADER_EXCEPTION``).
    - Judge timeout → X3B (``JUDGE_TIMEOUT``).
    - Judge abstain → X3B (``JUDGE_ABSTAINED``).
    - X1G INSUFFICIENT_HISTORY → X3B.
    """

    def __init__(
        self,
        gates: list[Gate],
        *,
        bus_emitter: BusEmitter,
        consistency_store: PassKStore | None = None,
        consistency_policy: ConsistencyPolicy | None = None,
        span_sink: SpanSink | None = None,
    ) -> None:
        if not gates:
            raise ValueError("EvaluationPipeline requires at least one gate")
        self._gates = gates
        self._bus = bus_emitter
        self._consistency_store = consistency_store
        self._consistency_policy = consistency_policy or ConsistencyPolicy()
        self._spans: SpanSink = span_sink or NoOpSpanSink()

    def run(
        self,
        context: GateContext,
        *,
        commit_candidate: bool,
        consistency_bucket: BucketKey | None = None,
        break_glass: BreakGlassInvocation | None = None,
    ) -> EvaluationResult:
        """Evaluate all gates and produce a disposition.

        Args:
            context: Evaluation context passed to graders.
            commit_candidate: If True, a passing run routes to X3C (commit
                via UWG). If False, passing routes to X3D (allow/finish).
            consistency_bucket: Required for commit-path runs when the
                pipeline has a ``consistency_store``. Missing bucket on a
                commit path routes to X3B ``INSUFFICIENT_HISTORY``.
            break_glass: If supplied and valid, gates in
                ``invocation.bypassed_gates`` are skipped. X1A and X1C
                cannot be bypassed — the ``BreakGlassAuthority`` refuses
                such requests upstream.
        """
        bypassed = frozenset(break_glass.bypassed_gates) if break_glass else frozenset()
        gate_results: list[GateResult] = []
        gate_span_ids: list[str] = []
        bus_write_failed = False

        deny_codes: list[ReasonCode] = []
        escalate_codes: list[ReasonCode] = []

        for gate in self._gates:
            if gate.rubric.gate in bypassed:
                continue
            result = gate.evaluate(context)
            gate_results.append(result)

            # Emit BUS P row. If bus write fails, flag AUDIT_UNAVAILABLE
            # but continue collecting results so HITL gets full picture.
            try:
                self._bus.emit(
                    result.to_bus_row(
                        run_id=context.run_id,
                        track=context.track,
                        trajectory_class=context.trajectory_class,
                    )
                )
            except BusWriteError:
                bus_write_failed = True
                escalate_codes.append(ReasonCode.AUDIT_UNAVAILABLE)

            # OTel gate span.
            disposition_hint = (
                "X3A"
                if (not result.passed and not result.abstained)
                else "X3B"
                if result.abstained
                else "X3C_pending"
                if commit_candidate
                else "X3D"
            )
            span = build_gate_span(
                result,
                run_id=context.run_id,
                track=context.track,
                trajectory_class=context.trajectory_class,
                disposition_hint=disposition_hint,
                bypass_audit_id=break_glass.audit_id if break_glass else None,
            )
            gate_span_ids.append(self._spans.emit_gate(span))

            if result.abstained:
                # Abstain → HITL regardless of aggregate; keep evaluating
                # remaining gates for full diagnostic packet.
                escalate_codes.extend(rc for rc in result.reason_codes if rc not in escalate_codes)
            elif not result.passed:
                # Hard failure on any gate denies the run (v4 §X1 binary
                # invariants for X1A/X1C; §X1F hard sub-gates).
                deny_codes.extend(rc for rc in result.reason_codes if rc not in deny_codes)

        # Consistency gate (X1G) — commit-path only when applicable.
        consistency: ConsistencyCheck | None = None
        if (
            not deny_codes
            and commit_candidate
            and self._consistency_store is not None
            and self._consistency_policy.commit_path_only
            and "X1G" not in bypassed
        ):
            if consistency_bucket is None:
                escalate_codes.append(ReasonCode.INSUFFICIENT_HISTORY)
            else:
                try:
                    consistency = self._consistency_store.check(
                        consistency_bucket,
                        k=self._consistency_policy.k,
                        theta=self._consistency_policy.theta,
                    )
                except (KeyError, ValueError, RuntimeError):
                    # H8: history read failure → escalate with dedicated code.
                    escalate_codes.append(ReasonCode.CONSISTENCY_HISTORY_UNAVAILABLE)
                else:
                    if not consistency.has_history:
                        escalate_codes.append(ReasonCode.INSUFFICIENT_HISTORY)
                    elif not consistency.passed:
                        escalate_codes.append(ReasonCode.CONSISTENCY_FAIL)

        disposition = self._derive_disposition(
            deny_codes=deny_codes,
            escalate_codes=escalate_codes,
            commit_candidate=commit_candidate,
            break_glass=break_glass,
        )

        envelope = self._build_envelope(
            context=context,
            disposition=disposition,
            deny_codes=deny_codes,
            escalate_codes=escalate_codes,
            break_glass=break_glass,
        )

        # Disposition span closes out the trace.
        disp_span = build_disposition_span(envelope, gate_span_ids=tuple(gate_span_ids))
        self._spans.emit_disposition(disp_span)

        return EvaluationResult(
            envelope=envelope,
            gate_results=tuple(gate_results),
            consistency=consistency,
            bypassed_gates=tuple(sorted(bypassed)),
            bus_write_failed=bus_write_failed,
        )

    def _derive_disposition(
        self,
        *,
        deny_codes: list[ReasonCode],
        escalate_codes: list[ReasonCode],
        commit_candidate: bool,
        break_glass: BreakGlassInvocation | None,
    ) -> Disposition:
        # Break-glass short-circuits to X3E, regardless of bypassed-gate
        # outcomes (the un-bypassed gates still produce deny/escalate
        # codes which are carried as advisory in the envelope — §H3.2
        # requires audit + downstream review). X3E is still subject to
        # the bypass forbiddance — X1A and X1C deny codes DO force X3A.
        if break_glass is not None:
            mandatory_deny_codes = {
                ReasonCode.POLICY_CONFLICT,
                ReasonCode.SANDBOX_BREACH,
                ReasonCode.UNAUTHORIZED_MUTATION,
                ReasonCode.ENV_CONTAMINATED,
                ReasonCode.TRIAL_STATE_LEAK,
            }
            if any(rc in mandatory_deny_codes for rc in deny_codes):
                return Disposition.DENY
            return Disposition.BREAK_GLASS
        if deny_codes:
            return Disposition.DENY
        if escalate_codes:
            return Disposition.ESCALATE
        return Disposition.COMMIT if commit_candidate else Disposition.ALLOW

    def _build_envelope(
        self,
        *,
        context: GateContext,
        disposition: Disposition,
        deny_codes: list[ReasonCode],
        escalate_codes: list[ReasonCode],
        break_glass: BreakGlassInvocation | None,
    ) -> DispositionEnvelope:
        if disposition is Disposition.DENY:
            return DispositionEnvelope(
                disposition=disposition,
                deny=True,
                deny_reason=", ".join(rc.value for rc in deny_codes),
                reason_codes=tuple(deny_codes),
                run_id=context.run_id,
                track=context.track,
                trajectory_class=context.trajectory_class,
            )
        if disposition is Disposition.ESCALATE:
            return DispositionEnvelope(
                disposition=disposition,
                deny=False,
                deny_reason=None,
                reason_codes=tuple(escalate_codes),
                hitl_reason=", ".join(rc.value for rc in escalate_codes),
                run_id=context.run_id,
                track=context.track,
                trajectory_class=context.trajectory_class,
            )
        if disposition is Disposition.BREAK_GLASS:
            assert break_glass is not None
            return DispositionEnvelope(
                disposition=disposition,
                deny=False,
                deny_reason=None,
                reason_codes=(ReasonCode.BREAK_GLASS_INVOKED, *escalate_codes),
                run_id=context.run_id,
                track=context.track,
                trajectory_class=context.trajectory_class,
                break_glass_audit_id=break_glass.audit_id,
                extras={
                    "break_glass_identity": break_glass.identity,
                    "break_glass_justification": break_glass.justification,
                    "break_glass_expires_at": break_glass.expires_at,
                    "break_glass_bypassed_gates": list(break_glass.bypassed_gates),
                },
            )
        # COMMIT / ALLOW: clean exit.
        return DispositionEnvelope(
            disposition=disposition,
            deny=False,
            deny_reason=None,
            reason_codes=(),
            run_id=context.run_id,
            track=context.track,
            trajectory_class=context.trajectory_class,
        )


__all__ = ["ConsistencyPolicy", "EvaluationPipeline", "EvaluationResult"]
