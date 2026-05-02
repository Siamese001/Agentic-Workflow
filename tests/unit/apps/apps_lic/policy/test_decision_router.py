"""Unit tests for apps_lic.policy.decision_router.

Covers the four contractual surfaces:
  1. Schema validation at construction (PolicyLoadError on malformed YAML)
  2. First-match resolve semantics (rule order matters; later rules ignored)
  3. Default branch fallback (matched=False, rule_id="default")
  4. ROUTER_DECISION marker emission (constitutional §29)

Plus parametric coverage of the two shipped policies (`exit_policy.yaml`,
`pre_flight_policy.yaml`) against the legacy HOP4 / HOP7 behavior they
replace, so the YAML change cannot silently drift from production logic.
"""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from apps_lic.policy.decision_router import (
    DecisionRouter,
    NoMatchError,
    PolicyLoadError,
)

REPO_ROOT = Path(__file__).resolve().parents[5]
EXIT_POLICY = REPO_ROOT / "apps_lic" / "policy" / "exit_policy.yaml"
PRE_FLIGHT_POLICY = REPO_ROOT / "apps_lic" / "policy" / "pre_flight_policy.yaml"


# ---------------------------------------------------------------------- #
# Schema validation
# ---------------------------------------------------------------------- #


def test_missing_file_raises_policy_load_error(tmp_path):
    with pytest.raises(PolicyLoadError, match="not found"):
        DecisionRouter(tmp_path / "does_not_exist.yaml")


def test_missing_required_keys_raises(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("policy_name: foo\n")  # missing layer/router/rules
    with pytest.raises(PolicyLoadError, match="missing required"):
        DecisionRouter(bad)


def test_empty_rules_raises(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        dedent(
            """
            policy_name: x
            layer: L0
            router: r
            rules: []
            """
        )
    )
    with pytest.raises(PolicyLoadError, match="non-empty list"):
        DecisionRouter(bad)


def test_rule_missing_when_or_then_raises(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        dedent(
            """
            policy_name: x
            layer: L0
            router: r
            rules:
              - rule_id: r1
                when: {a: 1}
            """
        )
    )
    with pytest.raises(PolicyLoadError, match="missing 'then'"):
        DecisionRouter(bad)


# ---------------------------------------------------------------------- #
# First-match semantics
# ---------------------------------------------------------------------- #


@pytest.fixture
def trivial_router(tmp_path) -> DecisionRouter:
    p = tmp_path / "trivial.yaml"
    p.write_text(
        dedent(
            """
            policy_name: trivial
            layer: L0
            router: trivial_router
            inputs: [a, b]
            rules:
              - rule_id: r_specific
                when: {a: 1, b: 2}
                then: {verdict: specific}
              - rule_id: r_a_only
                when: {a: 1}
                then: {verdict: a_only}
              - rule_id: r_any_b
                when: {b: "*"}
                then: {verdict: any_b}
              - rule_id: r_in_list
                when: {a: [9, 10, 11]}
                then: {verdict: in_list}
            default:
              verdict: fallback
            """
        )
    )
    return DecisionRouter(p)


def test_first_match_wins_specific(trivial_router):
    m = trivial_router.resolve({"a": 1, "b": 2}, emit_marker=False)
    assert m.matched and m.rule_id == "r_specific"
    assert m.verdict == {"verdict": "specific"}


def test_first_match_falls_through_to_a_only(trivial_router):
    m = trivial_router.resolve({"a": 1, "b": 99}, emit_marker=False)
    assert m.matched and m.rule_id == "r_a_only"


def test_star_matches_any_value_when_key_present(trivial_router):
    m = trivial_router.resolve({"b": "anything"}, emit_marker=False)
    assert m.matched and m.rule_id == "r_any_b"


def test_star_does_not_match_when_key_absent(trivial_router):
    # No 'b' key → r_any_b cannot match; no 'a' either → falls to default
    m = trivial_router.resolve({"c": 5}, emit_marker=False)
    assert not m.matched and m.rule_id == "default"


def test_list_membership_matches(trivial_router):
    m = trivial_router.resolve({"a": 10}, emit_marker=False)
    assert m.matched and m.rule_id == "r_in_list"


def test_list_membership_misses(trivial_router):
    m = trivial_router.resolve({"a": 99}, emit_marker=False)
    assert not m.matched  # falls to default


# ---------------------------------------------------------------------- #
# Default branch
# ---------------------------------------------------------------------- #


def test_default_branch_when_no_match(trivial_router):
    m = trivial_router.resolve({}, emit_marker=False)
    assert not m.matched
    assert m.rule_id == "default"
    assert m.verdict == {"verdict": "fallback"}


def test_no_match_no_default_raises(tmp_path):
    p = tmp_path / "no_default.yaml"
    p.write_text(
        dedent(
            """
            policy_name: nodef
            layer: L0
            router: r
            rules:
              - rule_id: only
                when: {x: 1}
                then: {y: 2}
            """
        )
    )
    router = DecisionRouter(p)
    with pytest.raises(NoMatchError, match="no matching rule"):
        router.resolve({"x": 99}, emit_marker=False)


def test_resolve_rejects_non_dict_state(trivial_router):
    with pytest.raises(TypeError, match="state must be dict"):
        trivial_router.resolve("not a dict", emit_marker=False)  # type: ignore[arg-type]


# ---------------------------------------------------------------------- #
# ROUTER_DECISION marker emission (constitutional §29)
# ---------------------------------------------------------------------- #


def test_router_decision_marker_emitted_on_match(trivial_router, capsys):
    trivial_router.resolve({"a": 1, "b": 2}, emit_marker=True)
    captured = capsys.readouterr().out
    assert "ROUTER_DECISION:" in captured
    assert "layer=L0" in captured
    assert "router=trivial_router" in captured
    assert "rule_id=r_specific" in captured
    assert "matched=True" in captured


def test_router_decision_marker_suppressed_via_arg(trivial_router, capsys):
    trivial_router.resolve({"a": 1, "b": 2}, emit_marker=False)
    captured = capsys.readouterr().out
    assert "ROUTER_DECISION:" not in captured


def test_router_decision_marker_suppressed_via_env(monkeypatch, trivial_router, capsys):
    monkeypatch.setenv("ROUTER_ENFORCEMENT_BYPASS", "1")
    trivial_router.resolve({"a": 1, "b": 2})  # no override; relies on env
    captured = capsys.readouterr().out
    assert "ROUTER_DECISION:" not in captured


# ---------------------------------------------------------------------- #
# Shipped policy: exit_policy.yaml — HOP7 parity
# ---------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def exit_router() -> DecisionRouter:
    return DecisionRouter(EXIT_POLICY)


@pytest.mark.parametrize(
    "state, expected_disposition, expected_action",
    [
        # passed=True dominates regardless of severity
        ({"passed": True, "severity": "HIGH", "rule_id": "anything"}, "ALLOW", "PROCEED"),
        # CRITICAL severity → DENY
        (
            {"passed": False, "severity": "CRITICAL", "rule_id": "placeholder_check"},
            "DENY",
            "FAIL",
        ),
        # HIGH + strategic_alignment_check → REVISE → RETRY_HOP2 (factual back-hop)
        (
            {
                "passed": False,
                "severity": "HIGH",
                "rule_id": "strategic_alignment_check",
            },
            "REVISE",
            "RETRY_HOP2",
        ),
        # HIGH + factual_grounding_check → also factual back-hop
        (
            {"passed": False, "severity": "HIGH", "rule_id": "factual_grounding_check"},
            "REVISE",
            "RETRY_HOP2",
        ),
        # HIGH + any other rule → REVISE → RETRY_HOP5 (creative back-hop)
        (
            {"passed": False, "severity": "HIGH", "rule_id": "length_constraint_check"},
            "REVISE",
            "RETRY_HOP5",
        ),
        # MEDIUM → HITL
        (
            {"passed": False, "severity": "MEDIUM", "rule_id": "spam_trigger_check"},
            "HITL",
            "MANUAL_REVIEW",
        ),
        # LOW → ABSTAIN
        (
            {"passed": False, "severity": "LOW", "rule_id": "tone_check"},
            "ABSTAIN",
            "PROCEED_WITH_WARNING",
        ),
    ],
)
def test_exit_policy_parity_with_legacy_hop7(
    exit_router, state, expected_disposition, expected_action
):
    m = exit_router.resolve(state, emit_marker=False)
    assert m.matched, f"expected match for state={state}, got default branch"
    assert m.verdict["x3_disposition"] == expected_disposition
    assert m.verdict["gate_action"] == expected_action


def test_exit_policy_default_for_unrecognized_state(exit_router):
    # passed=False with no severity → all rules miss; falls to default HITL
    m = exit_router.resolve({"passed": False}, emit_marker=False)
    assert not m.matched
    assert m.verdict["x3_disposition"] == "HITL"


# ---------------------------------------------------------------------- #
# Shipped policy: pre_flight_policy.yaml — HOP4 + HOP5 archetype-switch parity
# ---------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def pre_flight_router() -> DecisionRouter:
    return DecisionRouter(PRE_FLIGHT_POLICY)


@pytest.mark.parametrize(
    "state, expected_route, expected_n_candidates",
    [
        # CONNECTED + C_LEVEL → FOLLOW_UP, n=2 (multi-candidate per legacy HOP5)
        (
            {
                "archetype": "C_LEVEL",
                "connection_status": "CONNECTED",
                "premium_available": False,
            },
            "FOLLOW_UP",
            2,
        ),
        # CONNECTED + DIRECTOR → FOLLOW_UP, n=1
        (
            {
                "archetype": "DIRECTOR",
                "connection_status": "CONNECTED",
                "premium_available": False,
            },
            "FOLLOW_UP",
            1,
        ),
        # NOT_CONNECTED + premium + C_LEVEL → INMAIL, n=2
        (
            {
                "archetype": "C_LEVEL",
                "connection_status": "NOT_CONNECTED",
                "premium_available": True,
            },
            "INMAIL",
            2,
        ),
        # NOT_CONNECTED + premium + IC → INMAIL, n=1
        (
            {
                "archetype": "IC",
                "connection_status": "NOT_CONNECTED",
                "premium_available": True,
            },
            "INMAIL",
            1,
        ),
        # NOT_CONNECTED + no premium + C_LEVEL → CONNECTION_REQ, n=2
        (
            {
                "archetype": "C_LEVEL",
                "connection_status": "NOT_CONNECTED",
                "premium_available": False,
            },
            "CONNECTION_REQ",
            2,
        ),
        # NOT_CONNECTED + no premium + VP → CONNECTION_REQ, n=1
        (
            {
                "archetype": "VP",
                "connection_status": "NOT_CONNECTED",
                "premium_available": False,
            },
            "CONNECTION_REQ",
            1,
        ),
    ],
)
def test_pre_flight_policy_envelope_resolution(
    pre_flight_router, state, expected_route, expected_n_candidates
):
    m = pre_flight_router.resolve(state, emit_marker=False)
    assert m.matched, f"expected match for state={state}, got default"
    assert m.verdict["route"] == expected_route
    assert m.verdict["n_candidates"] == expected_n_candidates


def test_pre_flight_explicit_override_wins(pre_flight_router):
    state = {
        "archetype": "IC",
        "connection_status": "NOT_CONNECTED",
        "premium_available": False,
        "route_override": "INMAIL",
    }
    m = pre_flight_router.resolve(state, emit_marker=False)
    assert m.matched and m.rule_id == "explicit_override"
    assert m.verdict["route"] == "OVERRIDE"


def test_pre_flight_default_envelope_is_safe(pre_flight_router):
    # Empty state → should fall to default (CONNECTION_REQ, n=1)
    m = pre_flight_router.resolve({}, emit_marker=False)
    assert not m.matched
    assert m.verdict["route"] == "CONNECTION_REQ"
    assert m.verdict["n_candidates"] == 1
