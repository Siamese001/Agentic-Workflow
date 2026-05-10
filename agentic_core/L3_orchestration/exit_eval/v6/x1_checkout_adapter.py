"""X1 Checkout Adapter — AG-5 GateVerdict → X1Item bridge.

Plan: ``ag5-exit-x1-evaluator-wiring-d8e4a2``.

Converts legacy ``GateVerdict`` (Exit-emit layer) to ``X1Item`` (Exit-input
layer) so that ``X1CheckoutResult`` can be populated from existing X1 gate
evaluators without rewriting them.

The bridge preserves:
- Verdict semantics (PASS/FAIL/WARN/UNKNOWN/NOT_APPLICABLE)
- Score/threshold where present
- Evidence refs and policy refs
- Reason code translation to decisive_reason

AG-4 invariants enforced:
- UNKNOWN verdicts carry unknown_reason
- NOT_APPLICABLE verdicts carry not_applicable_reason
"""

from __future__ import annotations

from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    GateResult,
    GateVerdict,
)
from agentic_core.runtime.contracts.x1_checkout_result import (
    X1CheckoutResult,
    X1EvaluatorType,
    X1Item,
    X1Verdict,
)


def _gate_result_to_x1_verdict(result: GateResult) -> X1Verdict:
    """Map GateResult enum to X1Verdict enum (1:1 value match)."""
    mapping: dict[GateResult, X1Verdict] = {
        GateResult.PASS: X1Verdict.PASS,
        GateResult.FAIL: X1Verdict.FAIL,
        GateResult.WARN: X1Verdict.WARN,
        GateResult.UNKNOWN: X1Verdict.UNKNOWN,
        GateResult.NOT_APPLICABLE: X1Verdict.NOT_APPLICABLE,
    }
    return mapping.get(result, X1Verdict.UNKNOWN)


def _grader_type_to_evaluator_type(grader_type: str) -> X1EvaluatorType:
    """Map GateVerdict.grader_type to X1Item.evaluator_type."""
    mapping: dict[str, X1EvaluatorType] = {
        "code": X1EvaluatorType.CODE,
        "LLM-judge": X1EvaluatorType.LLM_JUDGE,
        "hybrid": X1EvaluatorType.HYBRID,
        "human-calibrated": X1EvaluatorType.HUMAN_CALIBRATED,
    }
    return mapping.get(grader_type, X1EvaluatorType.CODE)


def gate_verdict_to_x1_item(verdict: GateVerdict) -> X1Item:
    """Convert a single GateVerdict to X1Item.

    AG-4 invariant preservation:
    - UNKNOWN verdicts get unknown_reason from reason_codes or default
    - NOT_APPLICABLE verdicts get not_applicable_reason from remediation_hint or default
    - Evidence refs forwarded from GateVerdict.evidence_refs
    """
    x1_verdict = _gate_result_to_x1_verdict(verdict.result)

    # Build decisive_reason from reason_codes
    decisive_reason = verdict.remediation_hint or ""
    if verdict.reason_codes and not decisive_reason:
        decisive_reason = "; ".join(verdict.reason_codes)

    # AG-4 invariant: UNKNOWN requires unknown_reason
    unknown_reason = ""
    if x1_verdict == X1Verdict.UNKNOWN:
        unknown_reason = decisive_reason or "Gate evaluator returned UNKNOWN"

    # AG-4 invariant: NOT_APPLICABLE requires not_applicable_reason
    not_applicable_reason = ""
    if x1_verdict == X1Verdict.NOT_APPLICABLE:
        not_applicable_reason = verdict.remediation_hint or decisive_reason or "Gate not applicable for this route"

    return X1Item(
        gate_id=verdict.gate_id,
        verdict=x1_verdict,
        confidence=verdict.confidence,
        evidence_refs=tuple(verdict.evidence_refs),
        evaluator_type=_grader_type_to_evaluator_type(verdict.grader_type),
        decisive_reason=decisive_reason,
        policy_ref="",  # Populated from packet in checkout_build
        threshold_ref="",  # Populated from packet in checkout_build
        unknown_reason=unknown_reason,
        not_applicable_reason=not_applicable_reason,
        score=verdict.score,
        threshold=verdict.threshold,
        intent_ref="",
        output_ref="",
    )


def build_x1_checkout_result(
    verdicts: list[GateVerdict],
    packet: ExitReviewPacket,
) -> X1CheckoutResult:
    """Build X1CheckoutResult from GateVerdict list + ExitReviewPacket.

    This is the main AG-5 bridge: takes the existing X1 gate outputs
    (GateVerdict list) and produces the AG-4 structured carrier
    (X1CheckoutResult) that downstream X2/X3 stages should consume.

    Args:
        verdicts: List of GateVerdict from run_all_x1_gates()
        packet: ExitReviewPacket for ref extraction

    Returns:
        X1CheckoutResult with all 10 X1Item slots populated

    AG-4 invariant enforcement:
    - UNKNOWN verdicts carry unknown_reason (from gate_verdict_to_x1_item)
    - NOT_APPLICABLE verdicts carry not_applicable_reason
    - X1G PASS implies replay_manifest_ref from packet.replay_key
    - X1H PASS implies otel_span_refs from packet.otel_spans
    - X1D PASS implies intent_ref/output_ref/evidence_refs from packet
    """
    # Map verdicts by gate_id
    by_gate: dict[str, GateVerdict] = {v.gate_id: v for v in verdicts}

    # Helper to get X1Item for a gate (default UNKNOWN if missing)
    def _get_x1_item(gate_id: str) -> X1Item:
        v = by_gate.get(gate_id)
        if v is None:
            # Gate missing from verdicts — produce explicit UNKNOWN
            return X1Item(
                gate_id=gate_id,
                verdict=X1Verdict.UNKNOWN,
                decisive_reason="Gate evaluator did not produce verdict",
                unknown_reason="Missing gate verdict in X1 run",
                evaluator_type=X1EvaluatorType.UNKNOWN,
            )
        return gate_verdict_to_x1_item(v)

    # Build all X1Items
    x1a = _get_x1_item("X1A")
    x1b = _get_x1_item("X1B")
    x1c = _get_x1_item("X1C")
    x1d = _get_x1_item("X1D")
    x1e = _get_x1_item("X1E")
    x1f = _get_x1_item("X1F")
    x1g = _get_x1_item("X1G")
    x1h = _get_x1_item("X1H")
    x1i = _get_x1_item("X1I")
    x1j = _get_x1_item("X1J")

    # Forward refs from packet for AG-4 invariant checking
    # X1G: replay_manifest_ref from replay_key
    replay_manifest_ref = packet.replay_key if packet.replay_key else ""

    # X1H: otel_span_refs from packet.otel_spans
    otel_refs: list[str] = []
    if packet.otel_spans:
        spans = packet.otel_spans.get("spans", {})
        if isinstance(spans, dict):
            otel_refs = list(spans.keys())
        if packet.trace_root:
            otel_refs.append(f"trace:{packet.trace_root}")

    # X1D: evidence_refs from packet
    evidence_refs: list[str] = []
    if packet.final_evidence_contract:
        fec = packet.final_evidence_contract
        if isinstance(fec, dict):
            items = fec.get("evidence_items", [])
            for i, item in enumerate(items):
                if isinstance(item, dict) and item.get("source"):
                    evidence_refs.append(f"evidence:{i}:{item['source']}")
            if fec.get("compilation_hash"):
                evidence_refs.append(f"fec:{fec['compilation_hash']}")
    if packet.evidence_bundle:
        eb = packet.evidence_bundle
        if isinstance(eb, dict) and eb.get("bundle_id"):
            evidence_refs.append(f"bundle:{eb['bundle_id']}")

    # X1D: intent_ref from route_contract
    intent_ref = ""
    if packet.route_contract:
        rc = packet.route_contract
        if isinstance(rc, dict):
            if rc.get("intent_text"):
                intent_ref = f"intent:{hash(rc['intent_text']) & 0xFFFFFF:06x}"
            elif rc.get("user_query"):
                intent_ref = f"intent:{hash(rc['user_query']) & 0xFFFFFF:06x}"

    # X1D: output_ref from packet.output
    output_ref = ""
    if packet.output:
        out = packet.output
        if isinstance(out, dict) and out.get("output_id"):
            output_ref = f"output:{out['output_id']}"
        elif packet.run_id:
            output_ref = f"output:{packet.run_id}"

    # Build final X1CheckoutResult with all fields
    return X1CheckoutResult(
        request_id=packet.request_id,
        run_id=packet.run_id,
        trace_root=packet.trace_root,
        x1a_todays_rules=x1a,
        x1b_answered_it=x1b,
        x1c_safe_to_leave=x1c,
        x1d_answer_good=x1d,
        x1e_trajectory_ok=x1e,
        x1f_story_adds_up=x1f,
        x1g_replay_eligible=x1g,
        x1h_observable=x1h,
        x1i_consistent_across_runs=x1i,
        x1j_write_eligibility=x1j,
        replay_manifest_ref=replay_manifest_ref,
        otel_span_refs=tuple(otel_refs),
        evidence_refs=tuple(evidence_refs),
        intent_ref=intent_ref,
        output_ref=output_ref,
    )


def x1_checkout_to_gate_verdicts(checkout: X1CheckoutResult) -> list[GateVerdict]:
    """Convert X1CheckoutResult back to GateVerdict list for legacy consumers.

    This allows X2 aggregation to work with either representation.
    Round-trip preserves verdict semantics but may lose some GateVerdict
    fields that don't exist in X1Item (e.g., severity, metadata).
    """
    verdicts: list[GateVerdict] = []
    for item in checkout.items():
        # Map X1Verdict back to GateResult
        result_map: dict[X1Verdict, GateResult] = {
            X1Verdict.PASS: GateResult.PASS,
            X1Verdict.FAIL: GateResult.FAIL,
            X1Verdict.WARN: GateResult.WARN,
            X1Verdict.UNKNOWN: GateResult.UNKNOWN,
            X1Verdict.NOT_APPLICABLE: GateResult.NOT_APPLICABLE,
        }
        result = result_map.get(item.verdict, GateResult.UNKNOWN)

        # Build reason_codes from decisive_reason
        reason_codes = []
        if item.decisive_reason:
            reason_codes = item.decisive_reason.split("; ")

        verdicts.append(
            GateVerdict(
                gate_id=item.gate_id,
                result=result,
                severity="info" if result == GateResult.PASS else "warn",
                reason_codes=reason_codes,
                score=item.score,
                threshold=item.threshold,
                grader_type=item.evaluator_type.value,
                evidence_refs=list(item.evidence_refs),
                confidence=item.confidence,
                abstain_flag=item.verdict == X1Verdict.UNKNOWN,
                remediation_hint=item.not_applicable_reason if item.verdict == X1Verdict.NOT_APPLICABLE else "",
                metadata={},
            )
        )
    return verdicts


__all__ = [
    "gate_verdict_to_x1_item",
    "build_x1_checkout_result",
    "x1_checkout_to_gate_verdicts",
]
