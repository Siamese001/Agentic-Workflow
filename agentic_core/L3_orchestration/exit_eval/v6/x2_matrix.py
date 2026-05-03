"""v6 §X2 — Aggregate Decision Matrix.

Combines a list of X1 gate verdicts into a single ``AggregateDecision`` that
selects exactly one X3 path (DENY, ESCALATE, COMMIT_REQUEST, ALLOW, or
SAFE_ABSTAIN).

Spec §X2 priority:
1. Hard fail conditions -> X3A DENY.
2. Escalation conditions -> X3B ESCALATE.
3. Commit-request conditions -> X3C COMMIT_REQUEST.
4. Allow conditions -> X3D ALLOW.
5. Otherwise (e.g. evidence empty, ambiguous) -> X3E SAFE_ABSTAIN.

The matrix is deterministic: given the same verdicts and packet, the same
decision is always returned.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    GateResult,
    GateVerdict,
    V6Disposition,
)

# Reason codes that always force X3A regardless of any other clearance.
_HARD_FAIL_CODES: frozenset[str] = frozenset(
    {
        "SANDBOX_BREACH",
        "UNAUTHORIZED_MUTATION",
        "ENV_CONTAMINATED",
        "TRIAL_STATE_LEAK",
        "HIDDEN_EGRESS",
        "POLICY_HASH_MISMATCH",
        "BLUEPRINT_HASH_MISMATCH",
        "SYSTEM_PROMPT_LEAK",
        "PROMPT_INJECTION_DETECTED",
        "TOOL_OUTPUT_INJECTION",
        "JAILBREAK_DETECTED",
        "DIRECT_L4_WRITE_ATTEMPT",
        "UNGROUNDED",  # material unsupported claim in grounded answer
        "NON_REPLAYABLE",  # high-impact only - re-checked below
    }
)

# Codes that route to X3B (escalation) when present and material.
_ESCALATE_CODES: frozenset[str] = frozenset(
    {
        "JUDGE_ABSTAINED",
        "CONFLICT_NOT_HANDLED",
        "CONSISTENCY_FAIL",
        "TRAJECTORY_CLASS_DRIFT",
        "INSUFFICIENT_HISTORY",
        "HIGH_IMPACT_NEEDS_HITL",
        "ROLLBACK_MISSING",
        "WRITE_SCOPE_AMBIGUOUS",
        "TRACE_GAP_MATERIAL",
        "TRAJECTORY_SUSPECT",
        "BIAS_DELTA_EXCEEDED",
        "HUMAN_REQUIRED",
        "LIVE_BELL_SIGNAL_UNCONSUMED",
    }
)

# Codes that route to X3E (safe abstain) — evidence-class issues that don't
# require human review yet but are not safe to answer.
_SAFE_ABSTAIN_CODES: frozenset[str] = frozenset(
    {
        "EVIDENCE_EMPTY",
        "WEAK_EVIDENCE_NO_CAVEAT",
    }
)


@dataclass(slots=True)
class AggregateDecision:
    """Output of X2 — exactly one X3 disposition with full provenance."""

    disposition: V6Disposition
    failed_gate_ids: list[str] = field(default_factory=list)
    reason_codes: list[str] = field(default_factory=list)
    triggering_verdicts: list[GateVerdict] = field(default_factory=list)
    rationale: str = ""
    requires_uwg_handoff: bool = False


def _collect_codes(verdicts: list[GateVerdict], result: GateResult) -> list[tuple[GateVerdict, str]]:
    """Return [(verdict, code), ...] for verdicts with a given result."""
    return [(v, c) for v in verdicts if v.result is result for c in v.reason_codes]


def _app_specific_eval_failure(packet: ExitReviewPacket) -> tuple[bool, list[str]]:
    """W1.P3 — Extract app-specific eval failure signal for X2 aggregation.

    Returns ``(is_bound_and_failed, reason_codes)``. When the packet carries
    a bound app-specific eval result that did not pass, we synthesize
    reason codes of the form ``APP_DIM_FAIL::<reason>`` for each entry in
    ``fail_reasons``. X2 treats any bound-and-failed result as a hard fail
    that forces X3A DENY — a Fort Knox domain rubric violation is not
    recoverable via re-route or safe-abstain.
    """
    ase = packet.app_specific_eval or {}
    if not isinstance(ase, dict):
        return False, []
    if not ase.get("bound"):
        return False, []
    if ase.get("passed") is True:
        return False, []
    raw_reasons = ase.get("fail_reasons") or []
    if not isinstance(raw_reasons, (list, tuple)):
        return True, ["APP_DIM_FAIL"]
    codes = [f"APP_DIM_FAIL::{r}" for r in raw_reasons] or ["APP_DIM_FAIL"]
    return True, codes


# W2.P5 — Substrings considered "hard" guardrail violations. Checked FIRST
# because fail_reasons carry a "dimension_fail::<dim_id>::<inner>" shape that
# would otherwise always look soft if we matched only on top-level prefix.
# If any of these appears anywhere in a fail_reason, DENY regardless of
# hitl_policy — a human must never be asked to approve a run where a hard
# guardrail (no_fabrication / factual_grounding / no_sensitive_targeting)
# came back UNKNOWN or produced an out-of-range score.
_APP_HARD_FAIL_SUBSTRINGS: tuple[str, ...] = (
    "unknown_fail_closed",
    "evidence_required_but_empty",
    "score_out_of_range",
    "unknown_app_contract",
)

# W2.P5 — Substrings considered "soft" threshold-class fails. Only when
# every fail_reason is soft and none is hard does hitl_policy=required_on_low
# escalate to a human review. Kept for forward-compatibility; the primary
# decision is made by the hard-check above.
_APP_SOFT_FAIL_SUBSTRINGS: tuple[str, ...] = (
    "threshold_min",
    "overall_below_threshold",
    "below_rubric_min",
)


def _app_hitl_routing(packet: ExitReviewPacket) -> tuple[bool, str, list[str]]:
    """W2.P5 — Compute HITL routing for a bound app-specific eval.

    Returns ``(should_escalate, rationale, reason_codes)``.

    - ``hitl_policy == "required_always"`` and bound + not passed: ESCALATE
      (human reviews any below-threshold bound run).
    - ``hitl_policy == "required_on_low"`` and bound + not passed + ALL
      fail_reasons are "soft" (threshold-class, not guardrail): ESCALATE.
    - Any guardrail-class fail_reason present: NOT escalated — falls through
      to DENY via ``_app_specific_eval_failure``.
    - ``hitl_policy == "none"`` (default): NOT escalated.
    """
    ase = packet.app_specific_eval or {}
    if not isinstance(ase, dict):
        return False, "", []
    if not ase.get("bound"):
        return False, "", []
    if ase.get("passed") is True:
        return False, "", []

    policy = str(ase.get("hitl_policy", "none") or "none").lower()
    if policy not in {"required_on_low", "required_always"}:
        return False, "", []

    raw_reasons = ase.get("fail_reasons") or []
    reasons = [str(r) for r in raw_reasons] if isinstance(raw_reasons, (list, tuple)) else []

    # If any hard guardrail fail is present, do NOT escalate — DENY path.
    for r in reasons:
        if any(sub in r for sub in _APP_HARD_FAIL_SUBSTRINGS):
            return False, "", []

    if policy == "required_always":
        rationale = "hitl_required_always"
    else:
        # required_on_low — escalate only when failures are present and
        # every failure matches a known soft substring (no unclassified
        # reasons). Empty reasons list also escalates — the run is "low"
        # simply because overall_score < overall_pass_threshold.
        if reasons:
            all_soft = all(
                any(sub in r for sub in _APP_SOFT_FAIL_SUBSTRINGS) for r in reasons
            )
            if not all_soft:
                return False, "", []
        rationale = "hitl_required_on_low"

    codes = [f"APP_DIM_FAIL::{r}" for r in reasons] or ["APP_DIM_FAIL"]
    codes.append("HUMAN_REQUIRED")
    return True, rationale, codes


def aggregate_decision(
    verdicts: list[GateVerdict],
    packet: ExitReviewPacket,
) -> AggregateDecision:
    """Apply the X2 aggregate decision matrix."""
    # Index verdicts by gate_id for lookups.
    by_id: dict[str, GateVerdict] = {v.gate_id: v for v in verdicts}

    fail_pairs = _collect_codes(verdicts, GateResult.FAIL)
    warn_pairs = _collect_codes(verdicts, GateResult.WARN)
    unknown_pairs = _collect_codes(verdicts, GateResult.UNKNOWN)

    # W2.P5 — HITL routing: when the resolved threshold profile declares
    # hitl_policy=required_on_low or required_always and the bound app eval
    # failed with only soft (threshold-class) reasons, ESCALATE instead of
    # DENY. Guardrail-class failures always DENY (checked below).
    should_escalate, hitl_rationale, hitl_codes = _app_hitl_routing(packet)
    if should_escalate:
        return AggregateDecision(
            disposition=V6Disposition.ESCALATE,
            failed_gate_ids=["APP_DOMAIN"],
            reason_codes=hitl_codes,
            triggering_verdicts=[],
            rationale=hitl_rationale,
        )

    # W1.P3 — App-specific eval failure is a hard-fail. Checked before the
    # generic X1-gate hard-fail logic so that a Fort Knox domain rubric
    # violation (e.g. no_fabrication below 0.99) DENIES even if all 10 X1
    # gates PASS. Audit BLOCKERs #1, #2, #5, #6 close here.
    app_failed, app_reason_codes = _app_specific_eval_failure(packet)
    if app_failed:
        return AggregateDecision(
            disposition=V6Disposition.DENY,
            failed_gate_ids=["APP_DOMAIN"],
            reason_codes=app_reason_codes,
            triggering_verdicts=[],
            rationale="app_specific_eval_failed",
        )

    # ---- 1. HARD FAILS — X3A ----
    hard_fail_hits = [(v, c) for v, c in fail_pairs if c in _HARD_FAIL_CODES]
    # Special case: NON_REPLAYABLE is hard-fail only for high-impact.
    is_high_impact = packet.terminal_class in {
        "with_state_diff",
        "external_action",
        "durable_write",
        "action",
    }
    if not is_high_impact:
        hard_fail_hits = [(v, c) for v, c in hard_fail_hits if c != "NON_REPLAYABLE"]
    if hard_fail_hits:
        gate_ids = sorted({v.gate_id for v, _ in hard_fail_hits})
        codes = sorted({c for _, c in hard_fail_hits})
        return AggregateDecision(
            disposition=V6Disposition.DENY,
            failed_gate_ids=gate_ids,
            reason_codes=codes,
            triggering_verdicts=[v for v, _ in hard_fail_hits],
            rationale="hard_fail_condition",
        )

    # Any FAIL on a non-hard code that didn't bubble up → still treat as DENY
    # unless it is an evidence-class issue handled below (safe abstain).
    other_fail_pairs = [
        (v, c) for v, c in fail_pairs if c not in _HARD_FAIL_CODES and c not in _SAFE_ABSTAIN_CODES
    ]

    # ---- 2. SAFE ABSTAIN — X3E ----
    abstain_hits = [(v, c) for v, c in (fail_pairs + warn_pairs) if c in _SAFE_ABSTAIN_CODES]
    if abstain_hits and not other_fail_pairs:
        gate_ids = sorted({v.gate_id for v, _ in abstain_hits})
        codes = sorted({c for _, c in abstain_hits})
        return AggregateDecision(
            disposition=V6Disposition.SAFE_ABSTAIN,
            failed_gate_ids=gate_ids,
            reason_codes=codes,
            triggering_verdicts=[v for v, _ in abstain_hits],
            rationale="safe_abstain_evidence_class",
        )

    # ---- 3. ESCALATE — X3B ----
    escalate_hits = [(v, c) for v, c in (fail_pairs + warn_pairs + unknown_pairs) if c in _ESCALATE_CODES]
    # UNKNOWN on any material gate also escalates per spec invariant 25.
    material_unknown = [
        v
        for v in verdicts
        if v.result is GateResult.UNKNOWN and v.gate_id in {"X1A", "X1C", "X1D", "X1F", "X1G", "X1H", "X1J"}
    ]
    if escalate_hits or material_unknown:
        gate_ids = sorted({v.gate_id for v, _ in escalate_hits} | {v.gate_id for v in material_unknown})
        codes = sorted(
            {c for _, c in escalate_hits} | {"UNKNOWN_MATERIAL_GATE"}
            if material_unknown
            else {c for _, c in escalate_hits}
        )
        return AggregateDecision(
            disposition=V6Disposition.ESCALATE,
            failed_gate_ids=gate_ids,
            reason_codes=codes,
            triggering_verdicts=[v for v, _ in escalate_hits] + material_unknown,
            rationale="escalation_required",
        )

    # ---- 4. Remaining FAILs (non-hard, non-escalate) → X3A ----
    if other_fail_pairs:
        gate_ids = sorted({v.gate_id for v, _ in other_fail_pairs})
        codes = sorted({c for _, c in other_fail_pairs})
        return AggregateDecision(
            disposition=V6Disposition.DENY,
            failed_gate_ids=gate_ids,
            reason_codes=codes,
            triggering_verdicts=[v for v, _ in other_fail_pairs],
            rationale="gate_fail_non_hard",
        )

    # ---- 5. COMMIT REQUEST — X3C ----
    requires_commit = packet.terminal_class in {
        "with_state_diff",
        "external_action",
        "durable_write",
        "action",
    }
    if requires_commit:
        # Spec §X3C required preconditions: X1A-F PASS (or D=N/A), X1G PASS,
        # X1H PASS, X1I PASS-or-allowed-WARN, X1J PASS.
        required_pass = ("X1A", "X1B", "X1C", "X1E", "X1F", "X1G", "X1H", "X1J")
        ok = True
        codes_blocking: list[str] = []
        for gid in required_pass:
            v = by_id.get(gid)
            if v is None or v.result is GateResult.PASS:
                continue
            if v.result is GateResult.NOT_APPLICABLE and gid in {"X1G"}:
                # X1G N/A is unexpected for commit path; treat as block.
                ok = False
                codes_blocking.append(f"{gid}_NOT_PASS")
            elif v.result is not GateResult.PASS:
                ok = False
                codes_blocking.append(f"{gid}_NOT_PASS")
        # X1D PASS or NOT_APPLICABLE
        v_d = by_id.get("X1D")
        if v_d and v_d.result not in {GateResult.PASS, GateResult.NOT_APPLICABLE}:
            ok = False
            codes_blocking.append("X1D_NOT_PASS")
        # X1I PASS or WARN allowed
        v_i = by_id.get("X1I")
        if v_i and v_i.result not in {GateResult.PASS, GateResult.WARN, GateResult.NOT_APPLICABLE}:
            ok = False
            codes_blocking.append("X1I_NOT_PASS")
        if not ok:
            return AggregateDecision(
                disposition=V6Disposition.DENY,
                failed_gate_ids=[c.replace("_NOT_PASS", "") for c in codes_blocking],
                reason_codes=codes_blocking,
                triggering_verdicts=[],
                rationale="commit_path_preconditions_unmet",
            )
        return AggregateDecision(
            disposition=V6Disposition.COMMIT_REQUEST,
            failed_gate_ids=[],
            reason_codes=[],
            triggering_verdicts=[],
            rationale="commit_path_clear",
            requires_uwg_handoff=True,
        )

    # ---- 6. ALLOW — X3D ----
    # Answer-only path: X1A-F PASS, X1H/I PASS or non-material WARN.
    return AggregateDecision(
        disposition=V6Disposition.ALLOW,
        failed_gate_ids=[],
        reason_codes=[],
        triggering_verdicts=[],
        rationale="answer_only_clear",
    )


__all__ = ["AggregateDecision", "aggregate_decision"]
