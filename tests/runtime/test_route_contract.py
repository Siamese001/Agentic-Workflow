"""
tests/runtime/test_route_contract.py

Spec-named test 9 of 14 (Phase 10).

Asserts the contract for the ``l0.route_decision`` runtime stage.

What L0 route_decision guarantees per the user spec:
  * Emits a RouteContract artifact carrying route_id, blueprint_hash,
    replay_key, contract_digest, reason_codes
  * Is the routing primitive that downstream C0/L3/L2 reference
  * Reason codes explain WHY this route was chosen (e.g.
    "grounding_required=true", "L3_required=true")
  * Always carries a route_id from the closed vocabulary R1..R6 family
"""

from __future__ import annotations

import pytest


SCENARIOS = ("A_grounded_read", "B_managed_workflow", "C_weak_evidence", "D_anti_bypass")

# Closed vocabulary the harness uses today. The user spec lists R1..R6
# variants (R1A/R1B, R3, R4, R5, R6); harness exercises R3 and R5.
ADMISSIBLE_ROUTE_IDS = frozenset({"R3_SIMPLE_GROUNDED_READ", "R5_MANAGED_WORKFLOW"})


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_route_decision_span_present(spans_by_name: dict[str, dict[str, dict]], scenario: str) -> None:
    assert "l0.route_decision" in spans_by_name[scenario]


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_route_id_is_admissible(spans_by_name: dict[str, dict[str, dict]], scenario: str) -> None:
    span = spans_by_name[scenario]["l0.route_decision"]
    rid = span.get("route_id")
    assert rid in ADMISSIBLE_ROUTE_IDS, (
        f"{scenario} l0.route_decision route_id={rid!r} not in admissible set "
        f"{sorted(ADMISSIBLE_ROUTE_IDS)}"
    )


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_route_decision_carries_replay_key(spans_by_name: dict[str, dict[str, dict]], scenario: str) -> None:
    """replay_key is the deterministic anchor for Phase-6 replay verification."""
    span = spans_by_name[scenario]["l0.route_decision"]
    assert span.get("replay_key") is not None, (
        f"{scenario} l0.route_decision missing replay_key"
    )


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_route_decision_carries_blueprint_hash(spans_by_name: dict[str, dict[str, dict]], scenario: str) -> None:
    span = spans_by_name[scenario]["l0.route_decision"]
    assert span.get("blueprint_hash") is not None, (
        f"{scenario} l0.route_decision missing blueprint_hash"
    )


@pytest.mark.parametrize("scenario", ("A_grounded_read", "B_managed_workflow", "C_weak_evidence"))
def test_route_decision_declares_route_contract_digest(
    spans_by_name: dict[str, dict[str, dict]],
    scenario: str,
) -> None:
    """RouteContract artifact is the spec-required output of L0."""
    span = spans_by_name[scenario]["l0.route_decision"]
    cd = span.get("contract_digest")
    assert cd is not None, f"{scenario} l0.route_decision missing RouteContract digest"


def test_scenario_a_route_is_grounded_read(spans_by_name: dict[str, dict[str, dict]]) -> None:
    span = spans_by_name["A_grounded_read"]["l0.route_decision"]
    assert span["route_id"] == "R3_SIMPLE_GROUNDED_READ"


def test_scenario_b_route_is_managed_workflow(spans_by_name: dict[str, dict[str, dict]]) -> None:
    span = spans_by_name["B_managed_workflow"]["l0.route_decision"]
    assert span["route_id"] == "R5_MANAGED_WORKFLOW"


def test_scenario_a_reason_codes_explain_route(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """Reason codes must explain why this route was chosen."""
    span = spans_by_name["A_grounded_read"]["l0.route_decision"]
    codes = " ".join(span.get("reason_codes") or [])
    assert "grounding_required" in codes, (
        f"Scenario A reason_codes={span.get('reason_codes')!r} should mention grounding_required"
    )


def test_scenario_b_reason_codes_indicate_l3_required(spans_by_name: dict[str, dict[str, dict]]) -> None:
    span = spans_by_name["B_managed_workflow"]["l0.route_decision"]
    codes = " ".join(span.get("reason_codes") or [])
    assert "L3_required" in codes


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_route_decision_status_is_ok(spans_by_name: dict[str, dict[str, dict]], scenario: str) -> None:
    """L0 itself must succeed even when the chosen route ultimately blocks
    (Scenario D's BLOCK happens at exit.x3, not at L0)."""
    span = spans_by_name[scenario]["l0.route_decision"]
    assert span["status"] == "OK"


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_route_decision_parented_correctly(
    spans_by_name: dict[str, dict[str, dict]],
    runtime_traces: dict[str, dict],
    scenario: str,
) -> None:
    """L0 must be a sibling of u0.intake under runtime.request."""
    span = spans_by_name[scenario]["l0.route_decision"]
    by_id = {s["span_id"]: s for s in runtime_traces[scenario]["spans"]}
    parent = by_id.get(span["parent_span_id"])
    assert parent is not None and parent["name"] == "runtime.request", (
        f"{scenario} l0.route_decision parent is {parent['name'] if parent else None!r}, "
        f"expected runtime.request"
    )
