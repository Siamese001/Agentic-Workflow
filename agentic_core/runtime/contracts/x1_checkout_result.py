"""X1 Checkout Result — AG-4 W5 carrier contract.

Plan: ``ag4-evidence-contract-carrier-repair-d2f9a3``.

The Exit X1 stage runs ten independent gates (X1A..X1J) over the
``ExitReviewPacket``.  Pre-AG-4 the only carrier was a boolean
``_x1_checkout(context) -> bool`` helper (see e.g.
``apps_eval.integrations.exit_adapter._x1_checkout``).  AG-4 replaces
that boolean with a structured carrier so each gate can record:

- a bounded verdict (``PASS`` / ``FAIL`` / ``WARN`` / ``UNKNOWN`` /
  ``NOT_APPLICABLE``)
- a confidence score
- evidence refs the gate used to decide
- the evaluator type (code, LLM-judge, hybrid, human-calibrated)
- a decisive reason
- a policy ref + threshold ref the gate consulted
- explicit reason fields when verdict is ``UNKNOWN`` or ``NOT_APPLICABLE``

Invariants enforced in ``__post_init__``:

1. ``UNKNOWN`` MUST NOT be treated as ``PASS``.  Helpers
   :py:meth:`X1Item.is_passing` and :py:meth:`X1CheckoutResult.is_overall_pass`
   return False for UNKNOWN.
2. ``NOT_APPLICABLE`` MUST be accompanied by a non-empty
   ``not_applicable_reason``.  ``__post_init__`` raises ``ValueError``
   otherwise.
3. Grounded answer-quality gate (``X1D``) MUST surface the evidence,
   intent, and output refs needed to compare them.  This is checked at
   the call-site in :py:meth:`X1CheckoutResult.x1d` (no constructor
   guard — gates may legitimately return ``NOT_APPLICABLE`` for
   non-grounded routes).
4. Replay eligibility (``X1G``) MUST reference a replay manifest if it
   returns ``PASS``.  Checked at call-site.
5. Observability (``X1H``) MUST reference at least one OTEL span if
   PASS.  Checked at call-site.

The ten gates X1A..X1J map to spec §X1 in
``docs/reference/05_Exit_Evaluation_and_Control/05_Live_Runtime_Exit_Control_&_Evaluation_v6.md``:

- X1A — today's rules (policy, layer, identity)
- X1B — answered it (output present, not abstain-by-omission)
- X1C — safe to leave (sandbox, mutation, write authority)
- X1D — answer good (grounded answer quality vs intent/evidence/output)
- X1E — trajectory ok (replay-determinism + retry/repair sanity)
- X1F — story adds up (consistency between exec_trace and output)
- X1G — replay eligible (replay manifest present + verifiable)
- X1H — observable (OTEL spans cover entry..exit)
- X1I — consistent across runs (pass-K consistency receipt)
- X1J — write eligibility (UWG commit pre-flight if state_diff present)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class X1Verdict(str, Enum):
    """Bounded verdict enum for X1 gates.

    Mirrors :class:`agentic_core.L3_orchestration.exit_eval.v6.types.GateResult`
    but carried at the Exit-input layer (X1) rather than the Exit-emit layer
    (GateVerdict).
    """

    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class X1EvaluatorType(str, Enum):
    """Evaluator type for an X1 gate."""

    CODE = "code"
    LLM_JUDGE = "LLM-judge"
    HYBRID = "hybrid"
    HUMAN_CALIBRATED = "human-calibrated"
    UNKNOWN = "unknown"


#: Set of verdicts that MAY be treated as PASS by downstream Exit logic.
#: AG-4 invariant: ``UNKNOWN`` is NEVER passing.
X1_PASSING_VERDICTS = frozenset({X1Verdict.PASS})


@dataclass(frozen=True, slots=True)
class X1Item:
    """Single X1 gate verdict.

    Each of the ten X1 gates emits one ``X1Item`` carried inside
    :class:`X1CheckoutResult`.

    Args:
        gate_id: One of ``X1A``..``X1J``.
        verdict: Bounded verdict enum.
        confidence: 0.0..1.0 confidence in the verdict (default 1.0 for
            deterministic code gates).
        evidence_refs: Refs to evidence the gate consulted (e.g.
            ``ExitReviewPacket.evidence_refs`` subset, OTEL span ids,
            audit row ids).
        evaluator_type: Evaluator type that produced the verdict.
        decisive_reason: Short human-readable reason for the verdict.
        policy_ref: Ref to the policy / rule the gate consulted.
        threshold_ref: Ref to the threshold profile the gate consulted.
        unknown_reason: Required when ``verdict == UNKNOWN``; explains
            why the gate could not decide.
        not_applicable_reason: Required when ``verdict == NOT_APPLICABLE``;
            explains why the gate does not apply (e.g. cache-hit route
            does not use X1D groundedness).
        score: Optional numeric score the gate computed.
        threshold: Optional threshold value the score was compared against.
        intent_ref: Optional ref to the user-intent surface (X1D groundedness
            requires intent).
        output_ref: Optional ref to the produced output (X1D groundedness
            requires output).
    """

    gate_id: str
    verdict: X1Verdict
    confidence: float = 1.0
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    evaluator_type: X1EvaluatorType = X1EvaluatorType.CODE
    decisive_reason: str = ""
    policy_ref: str = ""
    threshold_ref: str = ""
    unknown_reason: str = ""
    not_applicable_reason: str = ""
    score: float = 0.0
    threshold: float = 0.0
    intent_ref: str = ""
    output_ref: str = ""

    def __post_init__(self) -> None:
        if self.verdict == X1Verdict.NOT_APPLICABLE and not self.not_applicable_reason:
            raise ValueError(
                f"X1Item({self.gate_id}): verdict=NOT_APPLICABLE but "
                "not_applicable_reason is empty. AG-4 invariant: "
                "NOT_APPLICABLE requires a reason."
            )
        if self.gate_id not in {f"X1{c}" for c in "ABCDEFGHIJ"}:
            raise ValueError(
                f"X1Item: gate_id={self.gate_id!r} is not in X1A..X1J."
            )

    def is_passing(self) -> bool:
        """Return True iff verdict is PASS.

        AG-4 invariant: UNKNOWN/FAIL/WARN/NOT_APPLICABLE are NEVER passing.
        """
        return self.verdict in X1_PASSING_VERDICTS


@dataclass(frozen=True, slots=True)
class X1CheckoutResult:
    """Carrier for the ten X1 gate verdicts produced by Exit checkout.

    The ten ``X1Item`` slots map 1:1 to spec §X1 gates X1A..X1J.

    Default constructor produces all ten slots as
    ``UNKNOWN``-with-decisive-reason ``"not yet evaluated"``.  Callers
    populate each slot as the corresponding gate runs.

    Args:
        request_id: Identity propagation from ``ExitReviewPacket.request_id``.
        run_id: Identity propagation.
        trace_root: Identity propagation.
        x1a_todays_rules: X1A gate (policy/layer/identity).
        x1b_answered_it: X1B gate (output present).
        x1c_safe_to_leave: X1C gate (sandbox/mutation/write authority).
        x1d_answer_good: X1D gate (grounded answer quality).
        x1e_trajectory_ok: X1E gate (replay-determinism + retry sanity).
        x1f_story_adds_up: X1F gate (exec_trace ↔ output consistency).
        x1g_replay_eligible: X1G gate (replay manifest present).
        x1h_observable: X1H gate (OTEL spans cover entry..exit).
        x1i_consistent_across_runs: X1I gate (pass-K consistency).
        x1j_write_eligibility: X1J gate (UWG commit pre-flight).
        replay_manifest_ref: Required for X1G PASS.
        otel_span_refs: Required for X1H PASS.
        evidence_refs: Forwarded from ExitReviewPacket for X1D groundedness.
    """

    request_id: str = ""
    run_id: str = ""
    trace_root: str = ""

    x1a_todays_rules: X1Item = field(
        default_factory=lambda: _default_unknown("X1A"),
    )
    x1b_answered_it: X1Item = field(
        default_factory=lambda: _default_unknown("X1B"),
    )
    x1c_safe_to_leave: X1Item = field(
        default_factory=lambda: _default_unknown("X1C"),
    )
    x1d_answer_good: X1Item = field(
        default_factory=lambda: _default_unknown("X1D"),
    )
    x1e_trajectory_ok: X1Item = field(
        default_factory=lambda: _default_unknown("X1E"),
    )
    x1f_story_adds_up: X1Item = field(
        default_factory=lambda: _default_unknown("X1F"),
    )
    x1g_replay_eligible: X1Item = field(
        default_factory=lambda: _default_unknown("X1G"),
    )
    x1h_observable: X1Item = field(
        default_factory=lambda: _default_unknown("X1H"),
    )
    x1i_consistent_across_runs: X1Item = field(
        default_factory=lambda: _default_unknown("X1I"),
    )
    x1j_write_eligibility: X1Item = field(
        default_factory=lambda: _default_unknown("X1J"),
    )

    #: Forwarded refs that downstream gates depend on.  X1G PASS requires
    #: a non-empty replay_manifest_ref; X1H PASS requires non-empty
    #: otel_span_refs; X1D PASS requires non-empty evidence_refs +
    #: intent_ref + output_ref on the corresponding X1Item.
    replay_manifest_ref: str = ""
    otel_span_refs: tuple[str, ...] = field(default_factory=tuple)
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    intent_ref: str = ""
    output_ref: str = ""

    def items(self) -> tuple[X1Item, ...]:
        """Return all ten X1 items in canonical X1A..X1J order."""
        return (
            self.x1a_todays_rules,
            self.x1b_answered_it,
            self.x1c_safe_to_leave,
            self.x1d_answer_good,
            self.x1e_trajectory_ok,
            self.x1f_story_adds_up,
            self.x1g_replay_eligible,
            self.x1h_observable,
            self.x1i_consistent_across_runs,
            self.x1j_write_eligibility,
        )

    def is_overall_pass(self) -> bool:
        """Return True iff every applicable gate verdict is PASS.

        ``NOT_APPLICABLE`` (with reason) is treated as non-blocking.
        ``UNKNOWN`` / ``FAIL`` / ``WARN`` block the overall pass.
        """
        for item in self.items():
            if item.verdict == X1Verdict.NOT_APPLICABLE:
                continue
            if item.verdict != X1Verdict.PASS:
                return False
        return True

    def first_blocking_gate(self) -> Optional[X1Item]:
        """Return the first X1Item whose verdict blocks overall PASS, or None."""
        for item in self.items():
            if item.verdict == X1Verdict.NOT_APPLICABLE:
                continue
            if item.verdict != X1Verdict.PASS:
                return item
        return None

    def x1g_replay_eligibility_is_consistent(self) -> bool:
        """Return True iff X1G's PASS verdict is backed by a replay manifest.

        AG-4 invariant: replay eligibility MUST reference replay manifest.
        """
        if self.x1g_replay_eligible.verdict == X1Verdict.PASS:
            return bool(self.replay_manifest_ref)
        return True  # non-PASS verdicts don't make this claim

    def x1h_observability_is_consistent(self) -> bool:
        """Return True iff X1H PASS is backed by at least one OTEL span.

        AG-4 invariant: observability MUST reference OTEL spans where
        runtime began.
        """
        if self.x1h_observable.verdict == X1Verdict.PASS:
            return bool(self.otel_span_refs)
        return True

    def x1d_groundedness_has_required_refs(self) -> bool:
        """Return True iff X1D PASS surfaces intent + evidence + output refs.

        AG-4 invariant: grounded answer quality must compare
        intent/evidence/output.
        """
        x1d = self.x1d_answer_good
        if x1d.verdict != X1Verdict.PASS:
            return True
        return bool(
            (self.intent_ref or x1d.intent_ref)
            and (self.evidence_refs or x1d.evidence_refs)
            and (self.output_ref or x1d.output_ref)
        )


def _default_unknown(gate_id: str) -> X1Item:
    """Default UNKNOWN slot constructor — gate has not yet been evaluated."""
    return X1Item(
        gate_id=gate_id,
        verdict=X1Verdict.UNKNOWN,
        decisive_reason="not yet evaluated",
        unknown_reason="X1 evaluator has not run for this gate yet",
        evaluator_type=X1EvaluatorType.UNKNOWN,
    )


__all__ = [
    "X1Verdict",
    "X1EvaluatorType",
    "X1Item",
    "X1CheckoutResult",
    "X1_PASSING_VERDICTS",
]
