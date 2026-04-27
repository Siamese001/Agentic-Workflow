"""
tests/runtime/test_exit_eval_control.py

Spec-named test 12 of 14 (Phase 10).

Asserts the contract for the Exit evaluation-and-control stage.

What Exit guarantees per the user spec:
  * Four-stage pipeline: preflight -> x1.gates -> x2.aggregate -> x3.disposition
  * x1 carries gate_id (the X-series gate identifiers run on this request)
  * x3 emits the final disposition with reason_codes documenting the
    decision (ALLOW_FINISH, BLOCK_WRITE, ALLOW_FINISH_WITH_CAVEAT, etc.)
  * x3 status=BLOCKED on adversarial bypass attempts
"""

from __future__ import annotations

import pytest


SCENARIOS = ("A_grounded_read", "B_managed_workflow", "C_weak_evidence", "D_anti_bypass")

EXIT_REQUIRED_SPANS = (
    "exit.preflight",
    "exit.x1.gates",
    "exit.x2.aggregate",
    "exit.x3.disposition",
)


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_exit_pipeline_complete(
    spans_by_name: dict[str, dict[str, dict]],
    scenario: str,
) -> None:
    for span_name in EXIT_REQUIRED_SPANS:
        assert span_name in spans_by_name[scenario], (
            f"{scenario} missing exit stage span {span_name}"
        )


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_exit_x1_gates_carries_gate_id(
    spans_by_name: dict[str, dict[str, dict]],
    scenario: str,
) -> None:
    """x1.gates is the sole stage that declares which X-series gates ran."""
    span = spans_by_name[scenario]["exit.x1.gates"]
    gid = span.get("gate_id")
    assert gid is not None, f"{scenario} exit.x1.gates missing gate_id"
    assert isinstance(gid, str) and len(gid) > 0


def test_scenarios_a_and_c_x1_gate_id_format(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """Read-only flows reference the X1 family of gates."""
    for scen in ("A_grounded_read", "C_weak_evidence"):
        gid = spans_by_name[scen]["exit.x1.gates"]["gate_id"]
        assert gid.startswith("X1"), (
            f"{scen} gate_id={gid!r}, expected X1-family for read-only flow"
        )


def test_scenario_b_x1_includes_x3_for_write_eligibility(
    spans_by_name: dict[str, dict[str, dict]],
) -> None:
    """Managed workflow proposing a StateDiff must run X3 write-eligibility gates."""
    gid = spans_by_name["B_managed_workflow"]["exit.x1.gates"]["gate_id"]
    assert "X3" in gid, f"Scenario B gate_id={gid!r} must include X3 family"


def test_scenario_d_x1_includes_x3_blocked(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """Adversarial bypass must run X3 family AND block."""
    span = spans_by_name["D_anti_bypass"]["exit.x1.gates"]
    gid = span["gate_id"]
    assert "X3" in gid, f"Scenario D gate_id={gid!r} must include X3 family"
    rc = " ".join(span.get("reason_codes") or [])
    assert "blocked" in rc.lower() or "block" in rc.lower(), (
        f"Scenario D x1 reason_codes={rc!r} must declare write-eligibility blocked"
    )


def test_scenario_a_x3_disposition_is_allow_finish(
    spans_by_name: dict[str, dict[str, dict]],
) -> None:
    span = spans_by_name["A_grounded_read"]["exit.x3.disposition"]
    rc = " ".join(span.get("reason_codes") or [])
    assert "ALLOW_FINISH" in rc, (
        f"Scenario A x3 reason_codes={rc!r} must declare ALLOW_FINISH"
    )
    assert span["status"] == "OK"


def test_scenario_b_x3_disposition_is_proposal_only(
    spans_by_name: dict[str, dict[str, dict]],
) -> None:
    span = spans_by_name["B_managed_workflow"]["exit.x3.disposition"]
    rc = " ".join(span.get("reason_codes") or [])
    assert "PROPOSAL" in rc.upper() or "proposal" in rc, (
        f"Scenario B x3 reason_codes={rc!r} must declare proposal-only"
    )


def test_scenario_c_x3_disposition_is_caveated(
    spans_by_name: dict[str, dict[str, dict]],
) -> None:
    span = spans_by_name["C_weak_evidence"]["exit.x3.disposition"]
    rc = " ".join(span.get("reason_codes") or [])
    assert "CAVEAT" in rc.upper(), (
        f"Scenario C x3 reason_codes={rc!r} must declare a caveat"
    )


def test_scenario_d_x3_status_is_blocked(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """The crown jewel of the bypass scenario: exit must report BLOCKED."""
    span = spans_by_name["D_anti_bypass"]["exit.x3.disposition"]
    assert span["status"] == "BLOCKED", (
        f"Scenario D x3 status={span['status']!r}, must be BLOCKED"
    )
    rc = " ".join(span.get("reason_codes") or [])
    assert "BLOCK_WRITE" in rc, (
        f"Scenario D x3 reason_codes={rc!r} must contain BLOCK_WRITE"
    )


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_exit_x3_carries_replay_key(
    spans_by_name: dict[str, dict[str, dict]],
    scenario: str,
) -> None:
    """replay_key on x3 lets Phase-6 replay verification anchor on the
    final disposition."""
    span = spans_by_name[scenario]["exit.x3.disposition"]
    assert span.get("replay_key") is not None, (
        f"{scenario} exit.x3.disposition missing replay_key"
    )


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_exit_pipeline_ordering(
    spans_by_name: dict[str, dict[str, dict]],
    scenario: str,
) -> None:
    """Strict order: preflight -> x1 -> x2 -> x3."""
    pre = spans_by_name[scenario]["exit.preflight"]
    x1 = spans_by_name[scenario]["exit.x1.gates"]
    x2 = spans_by_name[scenario]["exit.x2.aggregate"]
    x3 = spans_by_name[scenario]["exit.x3.disposition"]
    assert x1["parent_span_id"] == pre["span_id"], f"{scenario} x1 parent != preflight"
    assert x2["parent_span_id"] == pre["span_id"], f"{scenario} x2 parent != preflight"
    assert x3["parent_span_id"] == pre["span_id"], f"{scenario} x3 parent != preflight"
    # Time-order: x1 starts before x2 starts before x3 starts
    assert x1["start_unix_ns"] <= x2["start_unix_ns"] <= x3["start_unix_ns"], (
        f"{scenario} exit pipeline starts out of order"
    )
