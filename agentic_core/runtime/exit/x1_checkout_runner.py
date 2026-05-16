"""AG-5 X1 checkout — deterministic evaluator wiring over ExitReviewPacket."""

from __future__ import annotations

from agentic_core.L3_orchestration.exit_eval.v6.types import ExitReviewPacket, SourceType
from agentic_core.runtime.contracts.x1_checkout_result import (
    X1CheckoutResult,
    X1Item,
    X1Verdict,
)


def run_ag5_x1_checkout(packet: ExitReviewPacket) -> X1CheckoutResult:
    """Run structured X1 gates for certification / native-core envelopes."""
    na_reason = "neutral compatibility envelope"

    def na(gid: str) -> X1Item:
        return X1Item(
            gate_id=gid,
            verdict=X1Verdict.NOT_APPLICABLE,
            not_applicable_reason=na_reason,
        )

    rc_pol = ""
    if isinstance(packet.route_contract, dict):
        rc_pol = str(packet.route_contract.get("policy_hash") or "")
    pol_aligned = bool(packet.policy_hash) and packet.policy_hash == rc_pol

    x1a = X1Item(
        gate_id="X1A",
        verdict=X1Verdict.PASS if pol_aligned else X1Verdict.FAIL,
        decisive_reason="policy_hash_route_contract_alignment",
    )

    has_output = bool(packet.output)
    x1b = X1Item(
        gate_id="X1B",
        verdict=X1Verdict.PASS if has_output else X1Verdict.FAIL,
        decisive_reason="terminal_output_present",
    )

    neutral_binding = packet.source_type == SourceType.APP_BINDING_COMPATIBILITY_PACKAGE
    neutral_terminal = packet.terminal_class == "answer_only"
    x1c = X1Item(
        gate_id="X1C",
        verdict=X1Verdict.PASS if (neutral_binding and neutral_terminal) else X1Verdict.FAIL,
        decisive_reason="safe_to_leave_neutral_envelope" if neutral_binding else "envelope_requires_review",
    )

    spans_obj = packet.otel_spans.get("spans") if isinstance(packet.otel_spans, dict) else {}
    required_span_keys = frozenset({
        "trace_root",
        "route_contract",
        "tool_invocations",
        "evidence_contracts",
        "step_outputs",
        "exit_disposition",
    })
    span_ok = isinstance(spans_obj, dict) and required_span_keys.issubset(spans_obj.keys())
    x1h = X1Item(
        gate_id="X1H",
        verdict=X1Verdict.PASS if span_ok else X1Verdict.FAIL,
        decisive_reason="otel_span_coverage",
    )

    exec_ok = isinstance(packet.exec_trace, dict) and bool(packet.exec_trace.get("replay_receipts_present"))
    x1g = X1Item(
        gate_id="X1G",
        verdict=X1Verdict.PASS if exec_ok else X1Verdict.FAIL,
        decisive_reason="replay_receipt_marker",
    )

    replay_manifest_ref = "replay-manifest:native-proof" if exec_ok else ""
    otel_span_refs: tuple[str, ...] = ("otel:span-bundle-present",) if span_ok else ()

    return X1CheckoutResult(
        request_id=packet.request_id,
        run_id=packet.run_id,
        trace_root=packet.trace_root,
        x1a_todays_rules=x1a,
        x1b_answered_it=x1b,
        x1c_safe_to_leave=x1c,
        x1d_answer_good=na("X1D"),
        x1e_trajectory_ok=na("X1E"),
        x1f_story_adds_up=na("X1F"),
        x1g_replay_eligible=x1g,
        x1h_observable=x1h,
        x1i_consistent_across_runs=na("X1I"),
        x1j_write_eligibility=na("X1J"),
        replay_manifest_ref=replay_manifest_ref,
        otel_span_refs=otel_span_refs,
    )


__all__ = ["run_ag5_x1_checkout"]
