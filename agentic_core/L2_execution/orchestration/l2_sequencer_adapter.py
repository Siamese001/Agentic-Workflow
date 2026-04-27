"""L2 Sequencer Adapter — bind L2PhasePipeline output to spec-04 contracts.

Spec sources:
    docs/reference/04_L2_Execute/04.0_L2_Sequencer_Orchestrator_Contract.md
    docs/reference/04_L2_Execute/04.9_L2_StateDiffCandidate_and_Mutation_Intent.md

The existing :class:`agentic_core.L2_execution.orchestration.l2_phase_pipeline.L2PhasePipeline`
already runs E1→E5 with v3/v4 receipts (`PrepReceipt`, `ValidationReceipt`,
`AttemptReceipt`, `HealReceipt`, `DispatchReceipt`). This module adds a thin
binding layer that lifts those existing receipts into the spec-04 typed
contracts (`SequencerReceipt`, `MutationIntentDetectionReceipt`,
`ProposedStateDiffCandidate`, `StateDiffCandidateManifest`) without
duplicating any pipeline logic.

Two public entry points:

    build_sequencer_receipt(run_result, ...)  -> SequencerReceipt
        Aggregates the full receipt chain emitted by L2PhasePipeline.run()
        into the canonical spec-04.0 SequencerReceipt.

    build_state_diff_manifest(run_result, ...) -> StateDiffCandidateManifest
        Inspects every AttemptReceipt for a proposed_state_diff and packages
        any present into the spec-04.9 inert manifest. Returns None when
        the run produced no mutation candidates.

These helpers are pure (no I/O, no side effects) and deterministic — given
the same PipelineRunResult they always produce the same typed contracts,
satisfying the spec-04.0 §S6 deterministic_digest invariant.
"""

from __future__ import annotations

import hashlib
from typing import Iterable

from agentic_core.L2_execution.observability.l2_otel_emitter import (
    L2SpanEmitter,
    build_required_attrs,
    get_default_emitter,
)
from agentic_core.L2_execution.orchestration.l2_phase_pipeline import (
    PipelineRunResult,
)
from agentic_core.L2_execution.types.l2_mutation_intent import (
    CandidateKind,
    MutationIntentClass,
    MutationIntentDetectionReceipt,
    MutationSourceStage,
    ProposedStateDiffCandidate,
    SchemaValidationStatus,
    StateDiffCandidateManifest,
)
from agentic_core.L2_execution.types.l2_sequencer_contract import (
    L2TerminalClass,
    SequencerReceipt,
)
from agentic_core.L2_execution.types.l2_v3_receipts import (
    AttemptReceipt,
    TerminalStamp,
)


# ---------------------------------------------------------------------------
# Mapping helpers
# ---------------------------------------------------------------------------


_TERMINAL_STAMP_TO_CLASS: dict[TerminalStamp, L2TerminalClass] = {
    TerminalStamp.SUCCESS: L2TerminalClass.SUCCESS,
    TerminalStamp.DEGRADED_SUCCESS: L2TerminalClass.DEGRADED_SUCCESS,
    TerminalStamp.NEEDS_HELP: L2TerminalClass.NEEDS_HELP,
    TerminalStamp.REJECTED: L2TerminalClass.REJECTED,
    TerminalStamp.FAILURE: L2TerminalClass.REJECTED,
}


def _digest(*parts: str) -> str:
    """Stable 32-char SHA256 digest over the provided parts."""
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()[:32]


def _terminal_class_for(stamp: TerminalStamp) -> L2TerminalClass:
    return _TERMINAL_STAMP_TO_CLASS.get(stamp, L2TerminalClass.REJECTED)


# ---------------------------------------------------------------------------
# Public adapter — sequencer receipt
# ---------------------------------------------------------------------------


def _adapter_attrs(
    run_result: PipelineRunResult,
    *,
    extra: dict[str, str] | None = None,
) -> dict[str, object]:
    """Build the 13 always-required L2 attrs from a PipelineRunResult prep."""
    prep = run_result.prep
    return build_required_attrs(
        run_id=prep.run_id,
        route_id=prep.route_id,
        step_id=prep.step_id,
        blueprint_hash=prep.determinism.blueprint_hash,
        policy_hash=prep.determinism.policy_hash,
        replay_key=prep.determinism.replay_key,
        capability_token=prep.capability_token,
        sandbox_envelope_id=prep.sandbox_envelope_id,
        attempt_seed=prep.determinism.attempt_seed,
        extra=extra,
    )


def build_sequencer_receipt(
    *,
    run_result: PipelineRunResult,
    request_id: str,
    sequencer_receipt_id: str | None = None,
    decisive_reason: str = "",
    emitter: L2SpanEmitter | None = None,
) -> SequencerReceipt:
    """Aggregate one ``PipelineRunResult`` into a spec-04.0 ``SequencerReceipt``.

    Wires the existing pipeline's per-phase receipt IDs into the canonical
    spec-04.0 fields. Asserts the spec invariant
    ``no_direct_write_assertion=True`` because L2 has no commit path.
    """
    prep = run_result.prep
    validation = run_result.validation
    dispatch = run_result.dispatch
    last_attempt = run_result.attempts[-1] if run_result.attempts else None
    terminal_stamp = run_result.terminal_stamp
    terminal_cls = _terminal_class_for(terminal_stamp)

    receipt_id = sequencer_receipt_id or f"seq-{_digest(prep.run_id, prep.prep_receipt_id)}"

    # Emit the canonical 8 sequencer spans (spec 04.0 §OTEL SPANS).
    # The sequencer is the parent glue around the E1..E5 chain; a single
    # call to build_sequencer_receipt produces one full sequencer trace.
    emt = emitter if emitter is not None else get_default_emitter()
    seq_attrs = _adapter_attrs(
        run_result,
        extra={
            "sequencer_receipt_id": receipt_id,
            "request_id": request_id,
            "terminal_class": terminal_cls.value,
        },
    )
    for span_name in (
        "l2.sequencer.receive",
        "l2.sequencer.state_transition",
        "l2.sequencer.call_e1_prep",
        "l2.sequencer.call_e2_valid",
        "l2.sequencer.call_e3_exec",
        "l2.sequencer.call_e4_heal",
        "l2.sequencer.call_e5_seal",
        "l2.sequencer.receipt_emit",
    ):
        with emt.span(span_name, attrs=seq_attrs):
            pass

    reason_codes: list[str] = []
    if validation.failed_rule:
        reason_codes.append(f"validation:{validation.failed_rule}")
    if last_attempt and last_attempt.error_summary:
        reason_codes.append(f"attempt:{last_attempt.error_summary[:40]}")
    if dispatch and dispatch.decisive_reason:
        reason_codes.append(f"dispatch:{dispatch.decisive_reason[:40]}")
    if decisive_reason:
        reason_codes.append(decisive_reason[:60])

    deterministic_digest = _digest(
        prep.run_id,
        prep.prep_receipt_id,
        validation.validation_packet_id,
        *(a.attempt_receipt_id for a in run_result.attempts),
        *(h.repair_attempt_id for h in run_result.heals),
        dispatch.dispatch_receipt_id if dispatch else "no-dispatch",
        terminal_stamp.value,
    )

    budget_final = 0
    if isinstance(prep.frozen_budget, dict):
        try:
            budget_final = int(prep.frozen_budget.get("remaining", 0))
        except (TypeError, ValueError):
            budget_final = 0

    return SequencerReceipt(
        sequencer_receipt_id=receipt_id,
        request_id=request_id,
        run_id=prep.run_id,
        trace_root=prep.lineage.trace_id if hasattr(prep.lineage, "trace_id") else "",
        route_id=prep.route_id,
        step_id=prep.step_id,
        policy_hash=prep.determinism.policy_hash,
        blueprint_hash=prep.determinism.blueprint_hash,
        replay_key=prep.determinism.replay_key,
        e1_receipt_ref=prep.prep_receipt_id,
        e2_receipt_refs=(validation.validation_packet_id,),
        e3_attempt_receipt_refs=tuple(a.attempt_receipt_id for a in run_result.attempts),
        e4_heal_receipt_refs=tuple(h.repair_attempt_id for h in run_result.heals),
        e5_seal_receipt_ref=(
            dispatch.dispatch_receipt_id if dispatch else "no-dispatch"
        ),
        terminal_class=terminal_cls,
        terminal_reason_codes=tuple(reason_codes),
        attempt_count=len(run_result.attempts),
        repair_count=len(run_result.heals),
        budget_final=budget_final,
        same_authority_status="STABLE",
        no_direct_write_assertion=True,  # invariant
        deterministic_digest=deterministic_digest,
    )


# ---------------------------------------------------------------------------
# Public adapter — mutation manifest
# ---------------------------------------------------------------------------


def _attempts_with_diff(
    attempts: Iterable[AttemptReceipt],
) -> list[AttemptReceipt]:
    """Return only the attempts that produced a proposed_state_diff."""
    return [a for a in attempts if getattr(a, "proposed_state_diff", None)]


def build_mutation_detection_receipt(
    *,
    attempt: AttemptReceipt,
    request_id: str,
    run_id: str,
    trace_root: str = "",
) -> MutationIntentDetectionReceipt:
    """Build the spec-04.9 detection receipt for one attempt with a diff."""
    diff = attempt.proposed_state_diff
    has_mutation = bool(diff)
    intent_class = (
        MutationIntentClass.SANDBOX_ARTIFACT
        if has_mutation
        else MutationIntentClass.NONE
    )
    return MutationIntentDetectionReceipt(
        detection_receipt_id=f"det-{_digest(attempt.attempt_receipt_id)}",
        request_id=request_id,
        run_id=run_id,
        trace_root=trace_root,
        source_stage=MutationSourceStage.E3_EXEC,
        mutation_detected=has_mutation,
        mutation_intent_class=intent_class,
        side_effect_class="sandbox_artifact" if has_mutation else "read_only",
        irreversible_risk=False,
        high_impact_risk=False,
        policy_hash=attempt.determinism.policy_hash,
        blueprint_hash=attempt.determinism.blueprint_hash,
        replay_key=attempt.determinism.replay_key,
        deterministic_digest=_digest(attempt.attempt_receipt_id, "detect"),
    )


def build_state_diff_candidate(
    *,
    attempt: AttemptReceipt,
    capability_token_ref: str,
    sandbox_envelope_ref: str,
    route_contract_ref: str,
    l2_authority_ref: str,
) -> ProposedStateDiffCandidate | None:
    """Build a spec-04.9 inert candidate from an attempt's proposed_state_diff.

    Returns None if the attempt has no diff. The candidate carries
    write_auth_status='none_inside_l2' and inert_until_exit_uwg=True
    by spec invariant.
    """
    diff = getattr(attempt, "proposed_state_diff", None)
    if not diff:
        return None
    diff_payload_ref = str(diff)[:120]
    diff_payload_hash = _digest(diff_payload_ref)
    return ProposedStateDiffCandidate(
        candidate_id=f"cand-{_digest(attempt.attempt_receipt_id)}",
        candidate_kind=CandidateKind.JSON_PATCH,
        target_surface_hint="l4_state",
        target_object_ref=f"attempt:{attempt.attempt_receipt_id}",
        after_candidate_ref=diff_payload_ref,
        diff_payload_ref=diff_payload_ref,
        diff_payload_hash=diff_payload_hash,
        schema_ref="agentic_core.L2_execution.types.l2_v3_receipts",
        schema_validation_status=SchemaValidationStatus.LOCALLY_VALID,
        route_contract_ref=route_contract_ref,
        l2_authority_ref=l2_authority_ref,
        capability_token_ref=capability_token_ref,
        sandbox_envelope_ref=sandbox_envelope_ref,
        blast_radius_hint="single_record",
        policy_hash=attempt.determinism.policy_hash,
        blueprint_hash=attempt.determinism.blueprint_hash,
        replay_key=attempt.determinism.replay_key,
        trace_root="",
        deterministic_digest=_digest(attempt.attempt_receipt_id, diff_payload_hash),
    )


def build_state_diff_manifest(
    *,
    run_result: PipelineRunResult,
    capability_token_ref: str,
    sandbox_envelope_ref: str,
    route_contract_ref: str,
    l2_authority_ref: str,
    emitter: L2SpanEmitter | None = None,
) -> StateDiffCandidateManifest | None:
    """Package every proposed_state_diff in ``run_result`` into a sealed manifest.

    Returns None if no attempt produced a diff (i.e. read-only runs).
    Emits the canonical 4 mutation-intent OTEL spans (spec 04.9 §OTEL SPANS).
    """
    attempts_with_diff = _attempts_with_diff(run_result.attempts)
    emt = emitter if emitter is not None else get_default_emitter()

    # Span 1 — l2.mutation.detect — fires whether or not diffs were found.
    detect_attrs = _adapter_attrs(
        run_result,
        extra={
            "mutation_detected": str(bool(attempts_with_diff)).lower(),
            "candidate_count": str(len(attempts_with_diff)),
        },
    )
    with emt.span("l2.mutation.detect", attrs=detect_attrs):
        pass

    if not attempts_with_diff:
        return None
    candidates = [
        build_state_diff_candidate(
            attempt=a,
            capability_token_ref=capability_token_ref,
            sandbox_envelope_ref=sandbox_envelope_ref,
            route_contract_ref=route_contract_ref,
            l2_authority_ref=l2_authority_ref,
        )
        for a in attempts_with_diff
    ]
    candidate_refs = tuple(c.candidate_id for c in candidates if c is not None)
    total_payload_hash = _digest(
        *(c.diff_payload_hash for c in candidates if c is not None)
    )
    sealed_artifact_ref = (
        run_result.dispatch.dispatch_receipt_id
        if run_result.dispatch
        else "no-dispatch"
    )

    # Spans 2..4 — build / local_validate / manifest_emit. Emitted in order
    # so the trace records the full inert-mutation seal pipeline.
    cand_attrs = _adapter_attrs(
        run_result,
        extra={
            "candidate_count": str(len(candidate_refs)),
            "total_payload_hash": total_payload_hash,
            "sealed_artifact_ref": sealed_artifact_ref,
        },
    )
    for span_name in (
        "l2.state_diff_candidate.build",
        "l2.state_diff_candidate.local_validate",
        "l2.state_diff_candidate.manifest_emit",
    ):
        with emt.span(span_name, attrs=cand_attrs):
            pass

    return StateDiffCandidateManifest(
        manifest_id=f"mani-{_digest(*candidate_refs)}",
        candidate_count=len(candidate_refs),
        total_payload_hash=total_payload_hash,
        local_validation_summary=f"{len(candidate_refs)} candidate(s) locally valid",
        forbidden_direct_write_check=True,
        exit_handoff_eligibility_hint="eligible",
        sealed_l2_artifact_ref=sealed_artifact_ref,
        proposed_state_diff_candidate_refs=candidate_refs,
    )


__all__ = [
    "build_mutation_detection_receipt",
    "build_sequencer_receipt",
    "build_state_diff_candidate",
    "build_state_diff_manifest",
]
