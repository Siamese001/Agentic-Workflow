"""
tests/runtime/test_l2_execution_seal.py

Spec-named test 11 of 14 (Phase 10).

Asserts the contract for the L2 execution-and-seal pipeline.

What L2 guarantees per the user spec:
  * Five-step pipeline E1 (prep) -> E2 (valid) -> E3 (exec) -> E4 (heal,
    optional) -> E5 (seal)
  * E5 emits a SealedL2Artifact contract digest
  * E3 carries token/cost telemetry
  * No StateDiff escapes E5 unless authorized -- enforced via
    reason_codes ('proposed_state_diff_only', 'no_proposed_state_diff')
"""

from __future__ import annotations

import pytest


SCENARIOS = ("A_grounded_read", "B_managed_workflow", "C_weak_evidence", "D_anti_bypass")

L2_REQUIRED_SPANS = (
    "l2.e1.prep",
    "l2.e2.valid",
    "l2.e3.exec",
    "l2.e5.seal",
)


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_l2_required_steps_present(
    spans_by_name: dict[str, dict[str, dict]],
    scenario: str,
) -> None:
    for span_name in L2_REQUIRED_SPANS:
        assert span_name in spans_by_name[scenario], (
            f"{scenario} missing L2 stage span {span_name}"
        )


def test_l2_e4_heal_is_optional(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """E4 fires only when healing is needed; current harness scenarios
    do NOT exercise E4 (no failures upstream)."""
    for scen in SCENARIOS:
        assert "l2.e4.heal" not in spans_by_name[scen], (
            f"{scen} unexpectedly invoked l2.e4.heal -- harness has no failure path"
        )


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_l2_e5_seal_emits_contract_digest(
    spans_by_name: dict[str, dict[str, dict]],
    scenario: str,
) -> None:
    """SealedL2Artifact is the spec's mandatory output of E5."""
    span = spans_by_name[scenario]["l2.e5.seal"]
    cd = span.get("contract_digest")
    assert cd is not None, f"{scenario} l2.e5.seal missing SealedL2Artifact digest"


def test_l2_e3_carries_token_telemetry_for_exec_scenarios(
    spans_by_name: dict[str, dict[str, dict]],
) -> None:
    """E3 is where the actual generation happens; tokens/cost must be set
    in scenarios that authentically execute (A and B)."""
    for scen in ("A_grounded_read", "B_managed_workflow"):
        span = spans_by_name[scen]["l2.e3.exec"]
        assert span.get("tokens_in") is not None, f"{scen} e3 missing tokens_in"
        assert span.get("tokens_out") is not None, f"{scen} e3 missing tokens_out"


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_l2_e1_prep_is_parent_of_e2_e3_e5(
    runtime_traces: dict[str, dict],
    spans_by_name: dict[str, dict[str, dict]],
    scenario: str,
) -> None:
    e1 = spans_by_name[scenario]["l2.e1.prep"]
    by_id = {s["span_id"]: s for s in runtime_traces[scenario]["spans"]}
    for child_name in ("l2.e2.valid", "l2.e3.exec", "l2.e5.seal"):
        child = spans_by_name[scenario][child_name]
        parent = by_id.get(child["parent_span_id"])
        assert parent is not None, f"{scenario}/{child_name} parent unresolvable"
        # E2/E5 are direct children of E1; E3 may chain through E2
        assert parent["span_id"] in (e1["span_id"], spans_by_name[scenario]["l2.e2.valid"]["span_id"]), (
            f"{scenario}/{child_name} unexpected parent {parent['name']!r}"
        )


def test_scenario_b_e5_marks_proposal_only(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """Managed workflow proposes a StateDiff but does not commit -- E5 must
    flag this in reason_codes."""
    span = spans_by_name["B_managed_workflow"]["l2.e5.seal"]
    rc = " ".join(span.get("reason_codes") or [])
    assert "proposed" in rc, (
        f"Scenario B l2.e5.seal reason_codes={rc!r} must mark proposal-only"
    )


def test_scenario_d_e5_marks_no_state_diff(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """Adversarial scenario: E5 must refuse to seal a StateDiff."""
    span = spans_by_name["D_anti_bypass"]["l2.e5.seal"]
    rc = " ".join(span.get("reason_codes") or [])
    assert "no_proposed_state_diff" in rc or "no_proposed" in rc, (
        f"Scenario D l2.e5.seal reason_codes={rc!r} must declare no StateDiff escaped"
    )


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_l2_e3_status_is_ok_in_clean_scenarios(
    spans_by_name: dict[str, dict[str, dict]],
    scenario: str,
) -> None:
    """E3 itself succeeds in every harness scenario -- adversarial cases
    are handled at E3 via reason_codes (e.g. instruction_injection_neutralized)
    not via status=ERROR."""
    span = spans_by_name[scenario]["l2.e3.exec"]
    assert span["status"] == "OK"


def test_scenario_d_e3_marks_injection_neutralized(spans_by_name: dict[str, dict[str, dict]]) -> None:
    span = spans_by_name["D_anti_bypass"]["l2.e3.exec"]
    rc = " ".join(span.get("reason_codes") or [])
    assert "injection" in rc.lower() or "neutralized" in rc.lower(), (
        f"Scenario D l2.e3 must signal instruction-injection neutralization; got {rc!r}"
    )
