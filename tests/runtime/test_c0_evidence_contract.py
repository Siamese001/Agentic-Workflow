"""
tests/runtime/test_c0_evidence_contract.py

Spec-named test 10 of 14 (Phase 10).

Asserts the contract for the C0 retrieval pipeline runtime stage.

What C0 guarantees per the user spec:
  * c0.0.preflight gate (only invoked when grounding_required=true)
  * c0.1.retrieval_plan -> c0.2.fetch -> c0.4.shape_rerank_stratify ->
    c0.5.final_evidence_contract chain (with c0.2a.hydrate and
    c0.3.graph_traverse as children of c0.2.fetch)
  * c0.6.weak_support_refinement is conditional -- only when c0.5
    declares the evidence is WEAK_WITH_CAVEATS
  * c0.5 emits a FinalEvidenceContract artifact that downstream
    prompt_assembly + L2 must reference
"""

from __future__ import annotations

import pytest


SCENARIOS = ("A_grounded_read", "B_managed_workflow", "C_weak_evidence", "D_anti_bypass")

C0_REQUIRED_SPANS = (
    "c0.0.preflight",
    "c0.1.retrieval_plan",
    "c0.2.fetch",
    "c0.2a.hydrate",
    "c0.3.graph_traverse",
    "c0.4.shape_rerank_stratify",
    "c0.5.final_evidence_contract",
)


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_c0_pipeline_complete(spans_by_name: dict[str, dict[str, dict]], scenario: str) -> None:
    """Every scenario in the harness exercises grounding, so the full
    C0.0 -> C0.5 chain must be present."""
    for span_name in C0_REQUIRED_SPANS:
        assert span_name in spans_by_name[scenario], (
            f"{scenario} missing C0 stage span {span_name}"
        )


def test_c0_5_emits_final_evidence_contract_digest(spans_by_name: dict[str, dict[str, dict]]) -> None:
    for scenario in SCENARIOS:
        span = spans_by_name[scenario]["c0.5.final_evidence_contract"]
        cd = span.get("contract_digest")
        assert cd is not None, (
            f"{scenario} c0.5.final_evidence_contract missing contract_digest"
        )


def test_c0_6_only_in_weak_evidence_scenario(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """c0.6.weak_support_refinement is conditional -- the spec says it
    fires only when c0.5 outputs WEAK_WITH_CAVEATS."""
    assert "c0.6.weak_support_refinement" in spans_by_name["C_weak_evidence"], (
        "Scenario C must invoke c0.6 (weak evidence is its purpose)"
    )
    for scen in ("A_grounded_read", "B_managed_workflow", "D_anti_bypass"):
        assert "c0.6.weak_support_refinement" not in spans_by_name[scen], (
            f"{scen} must NOT invoke c0.6 -- evidence is not weak"
        )


def test_scenario_c_c0_5_declares_weak_reason(spans_by_name: dict[str, dict[str, dict]]) -> None:
    span = spans_by_name["C_weak_evidence"]["c0.5.final_evidence_contract"]
    rc = span.get("reason_codes") or []
    assert any("WEAK" in code for code in rc), (
        f"Scenario C c0.5 reason_codes={rc!r} must contain a WEAK marker"
    )


def test_c0_2_fetch_is_parent_of_hydrate_and_traverse(
    runtime_traces: dict[str, dict],
    spans_by_name: dict[str, dict[str, dict]],
) -> None:
    """Per the spec, hydrate and graph_traverse are sub-stages OF fetch."""
    for scen in SCENARIOS:
        fetch = spans_by_name[scen]["c0.2.fetch"]
        by_id = {s["span_id"]: s for s in runtime_traces[scen]["spans"]}
        for child_name in ("c0.2a.hydrate", "c0.3.graph_traverse", "c0.4.shape_rerank_stratify"):
            child = spans_by_name[scen][child_name]
            parent = by_id.get(child["parent_span_id"])
            assert parent is not None, f"{scen}/{child_name} parent unresolvable"
            assert parent["span_id"] == fetch["span_id"], (
                f"{scen}/{child_name} parent is {parent['name']!r}, expected c0.2.fetch"
            )


def test_c0_5_is_sibling_under_preflight(
    spans_by_name: dict[str, dict[str, dict]],
) -> None:
    """c0.5 is a sibling of c0.2.fetch under c0.0.preflight -- the spec's
    pipeline puts c0.5 OUTSIDE the fetch lifespan because it consumes
    fetch's output, not nests inside it."""
    for scen in SCENARIOS:
        c5 = spans_by_name[scen]["c0.5.final_evidence_contract"]
        c0 = spans_by_name[scen]["c0.0.preflight"]
        assert c5["parent_span_id"] == c0["span_id"], (
            f"{scen} c0.5 parent_span_id != c0.0.preflight span_id"
        )
        # And c0.5 must START after c0.4 ends (ordering by clock).
        c4 = spans_by_name[scen]["c0.4.shape_rerank_stratify"]
        assert c5["start_unix_ns"] >= c4["end_unix_ns"], (
            f"{scen} c0.5 started before c0.4 ended (ordering violation)"
        )


def test_c0_6_is_child_of_c0_5(
    runtime_traces: dict[str, dict],
    spans_by_name: dict[str, dict[str, dict]],
) -> None:
    """c0.6 weak refinement happens INSIDE c0.5's lifespan."""
    c6 = spans_by_name["C_weak_evidence"]["c0.6.weak_support_refinement"]
    c5 = spans_by_name["C_weak_evidence"]["c0.5.final_evidence_contract"]
    assert c6["parent_span_id"] == c5["span_id"]


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_c0_status_is_ok_in_all_clean_scenarios(
    spans_by_name: dict[str, dict[str, dict]],
    scenario: str,
) -> None:
    """C0 itself does not fail in any harness scenario; weakness/adversarial
    handling is signaled via reason_codes, not status=ERROR."""
    for span_name in C0_REQUIRED_SPANS:
        assert spans_by_name[scenario][span_name]["status"] == "OK", (
            f"{scenario}/{span_name} status not OK"
        )


def test_scenario_d_c0_4_marks_airlock(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """Scenario D's adversarial content must be quoted/data-only at c0.4."""
    span = spans_by_name["D_anti_bypass"]["c0.4.shape_rerank_stratify"]
    rc = " ".join(span.get("reason_codes") or [])
    assert "airlock" in rc.lower() or "data" in rc.lower(), (
        f"Scenario D c0.4 reason_codes must indicate airlock/data treatment; got {rc!r}"
    )
