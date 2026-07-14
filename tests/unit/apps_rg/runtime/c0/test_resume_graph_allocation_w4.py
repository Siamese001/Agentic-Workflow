from __future__ import annotations

import copy
import random
from pathlib import Path

import pytest

from apps_rg.runtime.c0.resume_graph_allocation import (
    ALL_CLAIM_BEARING_SECTIONS,
    ResumeGraphAllocationError,
    allocate_candidate_sets,
    build_resume_graph_usage_ledger,
    build_whole_resume_graph_allocation,
    normalize_metric_signature,
    slice_section_plan_for_allocation,
    validate_resume_graph_allocation_plan,
)
from apps_rg.runtime.c0.constants import C0_SECTIONS_ENABLED


def _candidate(
    slot_id: str,
    skill_id: str,
    *,
    score: float,
    fact_id: str | None = None,
    metric_id: str = "",
    metric_text: str = "",
    authority_pass: bool = True,
    employer_lane: str = "unify",
) -> dict[str, object]:
    fact = fact_id or f"fact_{skill_id}"
    return {
        "candidate_id": f"cand:{slot_id}:{skill_id}:{metric_id or 'no_metric'}",
        "section_id": slot_id.split(":", 1)[0],
        "claim_unit_id": slot_id,
        "skill_id": skill_id,
        "fact_id": fact,
        "metric_outcome_id": metric_id,
        "metric_text": metric_text,
        "authority_pass": authority_pass,
        "proof_strength_raw": score,
        "target_alignment_score": score / 2,
        "path_confidence_raw": 1.0,
        "source_independence_score": 1.0,
        "employer_lane": employer_lane,
        "source_family": employer_lane,
        "graph_path_ids": [f"root:{fact}", f"root:{fact}/skill:{skill_id}"],
        "edge_ids": [f"edge:{fact}:{skill_id}"],
        "citation_refs": [fact],
        "metric_value": "22" if metric_id else "",
        "metric_unit": "USD_M" if metric_id else "",
    }


def _matrix() -> tuple[dict[str, list[dict[str, object]]], list[dict[str, object]]]:
    slots = [
        {"slot_id": "headline:001", "section_id": "headline", "metric_required": False},
        {
            "slot_id": "executive_summary:001",
            "section_id": "executive_summary",
            "metric_required": True,
        },
        {
            "slot_id": "unify_bullets:001",
            "section_id": "unify_bullets",
            "metric_required": False,
            "employer_lane": "unify",
        },
    ]
    candidates = {
        "headline:001": [
            _candidate("headline:001", "skill_a", score=0.91),
            _candidate("headline:001", "skill_b", score=0.88),
        ],
        "executive_summary:001": [
            _candidate(
                "executive_summary:001",
                "skill_a",
                score=0.99,
                metric_id="metric_revenue",
                metric_text="$22M revenue",
            ),
            _candidate(
                "executive_summary:001",
                "skill_c",
                score=0.87,
                metric_id="metric_margin",
                metric_text="35 percent margin",
            ),
        ],
        "unify_bullets:001": [
            _candidate("unify_bullets:001", "skill_b", score=0.95),
            _candidate("unify_bullets:001", "skill_d", score=0.84),
        ],
    }
    return candidates, slots


def test_allocation_is_permutation_invariant_and_has_zero_reuse() -> None:
    candidates, slots = _matrix()
    expected = allocate_candidate_sets(
        candidate_sets=candidates,
        slot_specs=slots,
        graph_digest="g" * 64,
        policy_digest="p" * 64,
    )

    shuffled_candidates = copy.deepcopy(candidates)
    rng = random.Random(13)
    for rows in shuffled_candidates.values():
        rng.shuffle(rows)
    shuffled_slots = list(reversed(copy.deepcopy(slots)))
    actual = allocate_candidate_sets(
        candidate_sets=dict(reversed(list(shuffled_candidates.items()))),
        slot_specs=shuffled_slots,
        graph_digest="g" * 64,
        policy_digest="p" * 64,
    )

    assert actual["allocation_plan_digest"] == expected["allocation_plan_digest"]
    assert actual["assignments"] == expected["assignments"]
    assert actual["uniqueness_receipt"]["pass"] is True
    assert not actual["uniqueness_receipt"]["repeated_skill_ids"]
    assert not actual["uniqueness_receipt"]["repeated_metric_outcome_ids"]


def test_blocked_highest_score_never_wins() -> None:
    candidates, slots = _matrix()
    candidates["headline:001"].append(
        _candidate("headline:001", "skill_blocked", score=100.0, authority_pass=False)
    )
    plan = allocate_candidate_sets(
        candidate_sets=candidates,
        slot_specs=slots,
        graph_digest="g" * 64,
        policy_digest="p" * 64,
    )
    assert "skill_blocked" not in {row["skill_id"] for row in plan["assignments"]}
    blocked = [
        row
        for row in plan["candidate_decisions"]
        if row["candidate_id"].endswith(":skill_blocked:no_metric")
    ]
    assert blocked and blocked[0]["reason_codes"] == ["authority_gate_failed"]


def test_selection_margin_records_global_constraint_tradeoff() -> None:
    candidates, slots = _matrix()
    plan = allocate_candidate_sets(
        candidate_sets=candidates,
        slot_specs=slots,
        graph_digest="g" * 64,
        policy_digest="p" * 64,
    )
    assignments = {row["claim_unit_id"]: row for row in plan["assignments"]}

    # The globally unique solution reserves skill_a for executive summary, so
    # headline selects skill_b even though skill_a is its stronger local peer.
    headline = assignments["headline:001"]
    assert headline["skill_id"] == "skill_b"
    assert headline["selection_margin"] == -0.03
    assert headline["selection_margin_available"] is True
    assert headline["selection_margin_basis"] == "proof_strength_raw"
    assert headline["best_eligible_rejected_candidate_id"].endswith(
        ":skill_a:no_metric"
    )
    assert (
        plan["solver_metadata"]["selection_margin_policy"]
        == "signed_first_differing_lexicographic_component_vs_best_locally_eligible_rejected_v1"
    )


def test_equivalent_metric_signatures_cannot_be_reused() -> None:
    slots = [
        {"slot_id": "executive_summary:001", "section_id": "executive_summary", "metric_required": True},
        {"slot_id": "unify_bullets:001", "section_id": "unify_bullets", "metric_required": True},
    ]
    candidates = {
        "executive_summary:001": [
            _candidate(
                "executive_summary:001",
                "skill_a",
                score=1.0,
                metric_id="metric_a",
                metric_text="35% operating margin",
            )
        ],
        "unify_bullets:001": [
            _candidate(
                "unify_bullets:001",
                "skill_b",
                score=1.0,
                metric_id="metric_b",
                metric_text="35 percent operating margin",
            )
        ],
    }
    with pytest.raises(ResumeGraphAllocationError, match="normalized_metric_signature") as exc:
        allocate_candidate_sets(
            candidate_sets=candidates,
            slot_specs=slots,
            graph_digest="g" * 64,
            policy_digest="p" * 64,
        )
    assert "unsatisfied_constraints" in exc.value.receipt


def test_usage_ledger_is_plan_bound_and_section_only_does_not_claim_global_uniqueness() -> None:
    candidates, slots = _matrix()
    plan = allocate_candidate_sets(
        candidate_sets=candidates,
        slot_specs=slots,
        graph_digest="g" * 64,
        policy_digest="p" * 64,
        allocation_scope="SECTION_ONLY",
    )
    ledger = build_resume_graph_usage_ledger(plan)
    assert plan["global_uniqueness_claimed"] is False
    assert ledger["allocation_plan_digest"] == plan["allocation_plan_digest"]
    assert ledger["durable_graph_state_mutated"] is False
    assert ledger["current_run_only"] is True
    assert validate_resume_graph_allocation_plan(plan) == []


@pytest.mark.parametrize(
    ("left", "right"),
    [
        ("35% operating margin", "35 percent operating margin"),
        ("$22M IP-led revenue", "USD 22 million IP led revenue"),
    ],
)
def test_metric_signature_normalization_collapses_equivalent_surfaces(
    left: str, right: str
) -> None:
    assert normalize_metric_signature(left) == normalize_metric_signature(right)


def test_real_graph_whole_resume_allocation_covers_all_lanes_and_is_order_invariant() -> None:
    repo = Path(__file__).resolve().parents[5]
    forward = build_whole_resume_graph_allocation(
        repo_root=repo,
        target_role="SVP Agentic Engineering and Platform",
    )
    section_order = list(reversed(list(forward["section_plans"])))
    reverse = build_whole_resume_graph_allocation(
        repo_root=repo,
        target_role="SVP Agentic Engineering and Platform",
        section_order=section_order,
    )
    plan = forward["allocation_plan"]
    assert reverse["allocation_plan"]["allocation_plan_digest"] == plan[
        "allocation_plan_digest"
    ]
    assert plan["uniqueness_receipt"]["pass"] is True
    assert plan["global_uniqueness_claimed"] is True
    assert len(plan["assignments"]) == 47
    assert set(forward["section_final_evidence_contracts"]) == set(
        forward["section_plans"]
    )
    assert all(
        row["pass"] is True
        for row in forward["section_final_evidence_contracts"].values()
    )
    headline_slice = slice_section_plan_for_allocation(
        section_plan=forward["section_plans"]["headline"],
        allocation_plan=plan,
        final_evidence_contract=forward["section_final_evidence_contracts"]["headline"],
        section_id="headline",
    )
    allocated_headline_skills = {
        row["skill_id"]
        for row in plan["assignments"]
        if row["section_id"] == "headline"
    }
    assert set(headline_slice["selected_skill_ids"]) == allocated_headline_skills
    assert headline_slice["allocation_plan_digest"] == plan["allocation_plan_digest"]


def test_c0_authority_lane_set_matches_whole_resume_allocator() -> None:
    assert C0_SECTIONS_ENABLED == frozenset(ALL_CLAIM_BEARING_SECTIONS)
