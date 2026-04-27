"""v6 hardening primitives — Wave 2 of exit-eval-v6 deferred-scope completion.

This module codifies the *constants* and *reason codes* mandated by
``docs/reference/05_Exit_Evaluation_and_Control/v4_hardening_addendum.md``
sections H6 (pass^k threshold math) and H8 (fault-injection matrix).

It does **not** implement the full hardening control planes (H1 reward-hack
detection, H2 agentic-judge controls, H3 break-glass control plane, H4
jailbreak probe set, H7 rubric-diff review process, H9 operator runbook).
Those are separate subsystems each requiring a dedicated implementation
plan; this module gives the runtime types they will all reference.

Wave-2 acceptance rows in the matrix:
- H5.ATTR.* (13 OTEL attributes added to ``REQUIRED_ATTRIBUTES``)
- H6.MATH.threshold_table (this module — ``PASS_K_THRESHOLD_TABLE``)
- H8.FM.* (9 fault-injection reason codes — ``FaultInjectionReasonCode``)
"""

from __future__ import annotations

from enum import Enum
from typing import Final


# =====================================================================
# H6 — pass^k threshold math
# =====================================================================
#
# Per addendum §H6.1, when per-trial success is an independent Bernoulli with
# probability p, then ``pass^k = p^k``. The table below pins the worked
# implication of common (theta, k) policies on the per-trial reliability the
# agent must achieve.
#
# Operators read this as: "to gate at theta=0.95 with k=5 trials, the agent
# needs ~0.9898 per-trial success" — which is high enough that most
# commit-path trajectory classes will route to X3B (HITL) early in deployment.
# That is the spec-required behavior, not a tuning failure.

# Hard cap (theta, k) -> required per-trial p, for convenience to operators.
# Reproduce by pass_k_required_p(theta, k).
PASS_K_THRESHOLD_TABLE: Final[dict[tuple[float, int], float]] = {
    (0.95, 5): 0.9898,
    (0.85, 5): 0.9680,
    (0.95, 10): 0.9949,
    (0.99, 5): 0.9980,
}


def pass_k_required_p(theta: float, k: int) -> float:
    """Return the per-trial reliability needed to achieve pass^k >= theta.

    Solves theta = p^k for p, i.e. p = theta ** (1/k).

    Args:
        theta: target pass^k threshold in (0, 1]
        k: number of trials, k >= 1

    Returns:
        required per-trial Bernoulli success probability in (0, 1]

    Raises:
        ValueError: if theta not in (0, 1] or k < 1
    """
    if not 0.0 < theta <= 1.0:
        raise ValueError(f"theta must be in (0, 1]; got {theta!r}")
    if k < 1:
        raise ValueError(f"k must be >= 1; got {k!r}")
    return float(theta ** (1.0 / k))


def pass_k_observed(per_trial_p: float, k: int) -> float:
    """Forward direction: given per-trial success p over k trials, compute pass^k.

    Args:
        per_trial_p: per-trial Bernoulli success probability in [0, 1]
        k: number of trials, k >= 1

    Returns:
        observed pass^k in [0, 1]

    Raises:
        ValueError: if per_trial_p not in [0, 1] or k < 1
    """
    if not 0.0 <= per_trial_p <= 1.0:
        raise ValueError(f"per_trial_p must be in [0, 1]; got {per_trial_p!r}")
    if k < 1:
        raise ValueError(f"k must be >= 1; got {k!r}")
    return float(per_trial_p**k)


# H6.4 — Small-sample correction. When fewer than k trials are available
# in a (trajectory_class, rubric_version, agent_version, policy_version)
# bucket, X1G/X1I MUST NOT extrapolate to a smaller-k pass^k estimate. It
# routes to X3B with INSUFFICIENT_HISTORY. This constant exposes the
# minimum-sample policy for callers.
PASS_K_INSUFFICIENT_HISTORY_REASON: Final[str] = "INSUFFICIENT_HISTORY"


# =====================================================================
# H8 — fault-injection reason codes
# =====================================================================
#
# Per addendum §H8 every gate must have a defined behavior when its own
# machinery fails. The taxonomy below pins the 9 fail-modes and their
# fail-closed routing. ``FaultInjectionReasonCode`` is the canonical enum;
# tests and gate code reference it directly so a typo at a call site
# becomes a static-analysis error rather than a silent miss.


class FaultInjectionReasonCode(str, Enum):
    """v4_hardening §H8 fault-injection reason codes.

    Every value is a reason-code string emitted on a ``GateVerdict`` when
    the gate's machinery itself fails. Each value's docstring records the
    affected gate(s) and the correct behavior per H8.
    """

    JUDGE_TIMEOUT = "JUDGE_TIMEOUT"
    """Judge LLM timeout. Affects X1D, X1E, X1F. Behavior: abstain=True,
    route to X3B. FORBIDDEN: silent retry forever, default-to-pass."""

    JUDGE_ERROR = "JUDGE_ERROR"
    """Judge LLM 4xx/5xx. Affects X1D, X1E, X1F. Behavior: abstain=True,
    route to X3B. FORBIDDEN: silent retry that bypasses gate's time budget."""

    GRADER_EXCEPTION = "GRADER_EXCEPTION"
    """Code-based grader raised an unhandled exception. Affects any gate.
    Behavior: route to X3A (deny). Log full traceback. FORBIDDEN:
    catch-and-pass; never treat as grader success."""

    RUBRIC_UNAVAILABLE = "RUBRIC_UNAVAILABLE"
    """Rubric file missing or corrupt. Affects any gate. Behavior: route
    to X3A (deny). Page on-call. FORBIDDEN: fall back to a hardcoded
    default rubric."""

    AUDIT_UNAVAILABLE = "AUDIT_UNAVAILABLE"
    """BUS P or BUS T write failure. Affects any gate. Behavior: route
    to X3B (escalate). Rationale: an ungraded run without audit trail is
    worse than no run. FORBIDDEN: proceed without writing the bus."""

    CONSISTENCY_HISTORY_UNAVAILABLE = "CONSISTENCY_HISTORY_UNAVAILABLE"
    """X1G/X1I history-store read failure. Affects X1G consistency gate.
    Behavior: route to X3B with this code. FORBIDDEN: assume pass^k=1.0."""

    COMMIT_UNAVAILABLE = "COMMIT_UNAVAILABLE"
    """UWG unavailable on a commit-path run (X3C). Behavior: freeze the
    run, do NOT ACK the commit, route back to X3B. FORBIDDEN: buffer
    locally and replay later (creates silent re-ordering)."""

    L5_RECLEARANCE_UNAVAILABLE = "L5_RECLEARANCE_UNAVAILABLE"
    """L5 re-clearance call failed on the X3B->L5 path. Behavior: hold
    in FROZEN state. Page on-call. FORBIDDEN: resume without re-clear."""

    GRADER_BYPASS_DETECTED = "GRADER_BYPASS_DETECTED"
    """Per addendum §H8 + §G9 — a grader was found to be flippable by a
    known bypass pattern (e.g., judge directives in agent output). Affects
    X1D, X1E, X1F. Behavior: retire the judge, route current run to X3B.
    FORBIDDEN: keep using the same judge."""


#: All 9 fault-injection codes for fast set-membership tests.
FAULT_INJECTION_CODES: Final[frozenset[str]] = frozenset(
    code.value for code in FaultInjectionReasonCode
)


def is_fault_injection_code(code: str) -> bool:
    """Return True if ``code`` is one of the H8 fault-injection codes.

    Useful in dispatch logic that wants to fail-close on any H8 fault
    regardless of which specific mode fired.
    """
    return code in FAULT_INJECTION_CODES


# =====================================================================
# H8 disposition routing — fail-closed map
# =====================================================================
#
# Per addendum §H8: every fault-injection code routes to a specific X3
# disposition (X3A or X3B). This map is the canonical lookup. The only
# failure mode that fails-forward is "code-based grader agrees with its
# previous version on a shadow deploy" — which is handled in H7 rubric
# review, not at this layer.

FAULT_INJECTION_DISPOSITION_HINT: Final[dict[FaultInjectionReasonCode, str]] = {
    FaultInjectionReasonCode.JUDGE_TIMEOUT: "X3B",
    FaultInjectionReasonCode.JUDGE_ERROR: "X3B",
    FaultInjectionReasonCode.GRADER_EXCEPTION: "X3A",
    FaultInjectionReasonCode.RUBRIC_UNAVAILABLE: "X3A",
    FaultInjectionReasonCode.AUDIT_UNAVAILABLE: "X3B",
    FaultInjectionReasonCode.CONSISTENCY_HISTORY_UNAVAILABLE: "X3B",
    FaultInjectionReasonCode.COMMIT_UNAVAILABLE: "X3B",
    FaultInjectionReasonCode.L5_RECLEARANCE_UNAVAILABLE: "X3B",  # but FROZEN-hold
    FaultInjectionReasonCode.GRADER_BYPASS_DETECTED: "X3B",
}


__all__ = [
    "PASS_K_THRESHOLD_TABLE",
    "PASS_K_INSUFFICIENT_HISTORY_REASON",
    "FaultInjectionReasonCode",
    "FAULT_INJECTION_CODES",
    "FAULT_INJECTION_DISPOSITION_HINT",
    "pass_k_required_p",
    "pass_k_observed",
    "is_fault_injection_code",
]
