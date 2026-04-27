"""Tests for v6 hardening primitives — Wave 2 of exit-eval-v6 deferred-scope.

Covers:
- H5: REQUIRED_ATTRIBUTES extension (13 hardening attrs)
- H6: pass^k threshold math (table + forward + inverse)
- H8: FaultInjectionReasonCode enum + disposition map
"""

from __future__ import annotations

import math

import pytest

from agentic_core.L3_orchestration.exit_eval.v6 import (
    EXIT_V6_SPAN_CATALOG,
    FAULT_INJECTION_CODES,
    FAULT_INJECTION_DISPOSITION_HINT,
    PASS_K_INSUFFICIENT_HISTORY_REASON,
    PASS_K_THRESHOLD_TABLE,
    REQUIRED_ATTRIBUTES,
    FaultInjectionReasonCode,
    is_fault_injection_code,
    pass_k_observed,
    pass_k_required_p,
)


# ============================================================
# H5 — required attribute extension
# ============================================================


@pytest.mark.parametrize(
    "attr",
    [
        "gate",
        "track",
        "trajectory_class",
        "rubric_version",
        "composition",
        "aggregate_score",
        "aggregate_threshold",
        "passed",
        "abstain",
        "disposition_hint",
        "bypass_audit_id",
        "grader_class",
        "rubric_id",
    ],
)
def test_h5_attribute_in_required_attributes(attr: str) -> None:
    """v4_hardening §H5.1: each per-gate attribute must be REQUIRED on Exit spans."""
    assert attr in REQUIRED_ATTRIBUTES, f"H5.ATTR.{attr} missing from REQUIRED_ATTRIBUTES"


def test_h5_required_attributes_count_at_least_39() -> None:
    """Wave 2 acceptance: catalog grows from 26 base to >=39 with H5 attrs.

    The matrix span_count is 40 after Wave 1's X3F addition; required-attrs is
    a separate count and grows from 26 -> 39 (26 base + 13 H5).
    """
    assert len(REQUIRED_ATTRIBUTES) >= 39


def test_h5_required_attributes_no_duplicates() -> None:
    assert len(REQUIRED_ATTRIBUTES) == len(set(REQUIRED_ATTRIBUTES))


# ============================================================
# H6 — pass^k threshold math
# ============================================================


def test_h6_threshold_table_canonical_values() -> None:
    """Spot-check the worked table from H6.1."""
    assert PASS_K_THRESHOLD_TABLE[(0.95, 5)] == 0.9898
    assert PASS_K_THRESHOLD_TABLE[(0.85, 5)] == 0.9680
    assert PASS_K_THRESHOLD_TABLE[(0.95, 10)] == 0.9949
    assert PASS_K_THRESHOLD_TABLE[(0.99, 5)] == 0.9980


@pytest.mark.parametrize(
    "theta,k,expected",
    [
        (0.95, 5, 0.9898),
        (0.85, 5, 0.9680),
        (0.95, 10, 0.9949),
        (0.99, 5, 0.9980),
    ],
)
def test_h6_pass_k_required_p_matches_table_to_4_decimals(
    theta: float, k: int, expected: float
) -> None:
    """pass_k_required_p(theta, k) must round to the H6.1 table value."""
    assert round(pass_k_required_p(theta, k), 4) == expected


def test_h6_pass_k_required_p_inverts_pass_k_observed() -> None:
    """For any (theta, k), pass_k_observed(pass_k_required_p(theta, k), k) == theta."""
    for theta, k in [(0.95, 5), (0.85, 5), (0.95, 10), (0.99, 5), (0.5, 3)]:
        p = pass_k_required_p(theta, k)
        assert math.isclose(pass_k_observed(p, k), theta, rel_tol=1e-12)


@pytest.mark.parametrize("theta", [0.0, -0.01, 1.01, 2.0])
def test_h6_pass_k_required_p_rejects_invalid_theta(theta: float) -> None:
    with pytest.raises(ValueError, match="theta"):
        pass_k_required_p(theta, 5)


@pytest.mark.parametrize("k", [0, -1, -100])
def test_h6_pass_k_required_p_rejects_invalid_k(k: int) -> None:
    with pytest.raises(ValueError, match="k must be"):
        pass_k_required_p(0.95, k)


def test_h6_pass_k_observed_at_perfect_reliability_returns_1() -> None:
    assert pass_k_observed(1.0, 100) == 1.0


def test_h6_pass_k_observed_at_zero_returns_0_for_k_ge_1() -> None:
    assert pass_k_observed(0.0, 5) == 0.0


def test_h6_pass_k_observed_falls_with_k() -> None:
    """For per_trial_p < 1, observed pass^k strictly decreases with k."""
    p = 0.95
    obs = [pass_k_observed(p, k) for k in (1, 2, 5, 10, 20)]
    for i in range(len(obs) - 1):
        assert obs[i] > obs[i + 1], f"observed[{i}]={obs[i]} not > observed[{i+1}]={obs[i+1]}"


@pytest.mark.parametrize("p", [-0.01, 1.01, 2.0])
def test_h6_pass_k_observed_rejects_invalid_p(p: float) -> None:
    with pytest.raises(ValueError, match="per_trial_p"):
        pass_k_observed(p, 5)


def test_h6_insufficient_history_reason_code_pinned() -> None:
    """H6.4: small-sample correction routes to X3B with INSUFFICIENT_HISTORY."""
    assert PASS_K_INSUFFICIENT_HISTORY_REASON == "INSUFFICIENT_HISTORY"


# ============================================================
# H8 — fault-injection reason codes
# ============================================================


def test_h8_all_nine_codes_present() -> None:
    """H8 fault matrix has exactly 9 fail-modes."""
    expected = {
        "JUDGE_TIMEOUT",
        "JUDGE_ERROR",
        "GRADER_EXCEPTION",
        "RUBRIC_UNAVAILABLE",
        "AUDIT_UNAVAILABLE",
        "CONSISTENCY_HISTORY_UNAVAILABLE",
        "COMMIT_UNAVAILABLE",
        "L5_RECLEARANCE_UNAVAILABLE",
        "GRADER_BYPASS_DETECTED",
    }
    actual = {code.value for code in FaultInjectionReasonCode}
    assert actual == expected


def test_h8_codes_frozen_set_matches_enum() -> None:
    assert FAULT_INJECTION_CODES == frozenset(c.value for c in FaultInjectionReasonCode)


@pytest.mark.parametrize("code", [c.value for c in FaultInjectionReasonCode])
def test_h8_is_fault_injection_code_recognises_each(code: str) -> None:
    assert is_fault_injection_code(code) is True


def test_h8_is_fault_injection_code_rejects_unknown() -> None:
    assert is_fault_injection_code("UNRELATED_CODE") is False
    assert is_fault_injection_code("") is False


def test_h8_disposition_hint_covers_all_codes() -> None:
    """Every H8 code must have a disposition hint mapped — fail-closed by design."""
    mapped = set(FAULT_INJECTION_DISPOSITION_HINT)
    all_codes = set(FaultInjectionReasonCode)
    assert mapped == all_codes, f"missing dispositions for: {all_codes - mapped}"


def test_h8_disposition_hints_only_x3a_or_x3b() -> None:
    """No fault-injection mode may fail-forward to X3D or X3C."""
    for code, disp in FAULT_INJECTION_DISPOSITION_HINT.items():
        assert disp in {"X3A", "X3B"}, (
            f"{code.value} -> {disp} violates H8 fail-closed rule"
        )


def test_h8_grader_exception_routes_to_x3a() -> None:
    """H8: code-based grader exception routes to X3A (deny), not X3B."""
    assert (
        FAULT_INJECTION_DISPOSITION_HINT[FaultInjectionReasonCode.GRADER_EXCEPTION]
        == "X3A"
    )


def test_h8_rubric_unavailable_routes_to_x3a() -> None:
    """H8: rubric corrupt/missing -> X3A (deny). FORBIDDEN: silent default."""
    assert (
        FAULT_INJECTION_DISPOSITION_HINT[FaultInjectionReasonCode.RUBRIC_UNAVAILABLE]
        == "X3A"
    )


def test_h8_judge_failures_route_to_x3b() -> None:
    """H8: judge timeout/error -> X3B (escalate). HITL adjudicates."""
    assert (
        FAULT_INJECTION_DISPOSITION_HINT[FaultInjectionReasonCode.JUDGE_TIMEOUT] == "X3B"
    )
    assert (
        FAULT_INJECTION_DISPOSITION_HINT[FaultInjectionReasonCode.JUDGE_ERROR] == "X3B"
    )


def test_h8_uwg_failure_routes_to_x3b() -> None:
    """H8: UWG unavailable on commit-path -> X3B (escalate, freeze)."""
    assert (
        FAULT_INJECTION_DISPOSITION_HINT[FaultInjectionReasonCode.COMMIT_UNAVAILABLE]
        == "X3B"
    )


def test_h8_l5_reclearance_failure_routes_to_x3b_with_freeze() -> None:
    """H8: L5 re-clearance failure -> X3B but FROZEN-hold per addendum."""
    assert (
        FAULT_INJECTION_DISPOSITION_HINT[FaultInjectionReasonCode.L5_RECLEARANCE_UNAVAILABLE]
        == "X3B"
    )


def test_h8_grader_bypass_detected_routes_to_x3b() -> None:
    """H8 + G9: detected bypass -> retire judge + X3B."""
    assert (
        FAULT_INJECTION_DISPOSITION_HINT[FaultInjectionReasonCode.GRADER_BYPASS_DETECTED]
        == "X3B"
    )


# ============================================================
# Integration sanity: hardening symbols cleanly importable
# ============================================================


def test_v6_package_exports_all_hardening_symbols() -> None:
    """All Wave-2 symbols importable from the v6 package surface."""
    from agentic_core.L3_orchestration.exit_eval import v6

    for name in [
        "FAULT_INJECTION_CODES",
        "FAULT_INJECTION_DISPOSITION_HINT",
        "PASS_K_INSUFFICIENT_HISTORY_REASON",
        "PASS_K_THRESHOLD_TABLE",
        "FaultInjectionReasonCode",
        "is_fault_injection_code",
        "pass_k_observed",
        "pass_k_required_p",
    ]:
        assert hasattr(v6, name), f"v6.{name} not exported"
        assert name in v6.__all__, f"{name} missing from v6.__all__"


def test_span_catalog_unchanged_after_h5_attr_addition() -> None:
    """Sanity: extending REQUIRED_ATTRIBUTES doesn't change the span catalog count."""
    # Catalog is 40 after Wave 1 X3F addition; should remain 40 in Wave 2.
    assert len(EXIT_V6_SPAN_CATALOG) == 40
