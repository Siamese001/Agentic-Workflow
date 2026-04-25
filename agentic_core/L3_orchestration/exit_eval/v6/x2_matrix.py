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
