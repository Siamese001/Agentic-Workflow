"""Hardening ratchet: unify_bullets graph-compose must not leak legacy six-bullet template."""
from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import patch

import pytest

from apps_rg.fact_inventory.candidate_fact_ledger import (
    default_ledger_path,
    default_taxonomy_path,
    load_master_candidate_fact_ledger,
    load_master_role_family_taxonomy,
)
from apps_rg.runtime.section_graph_skills_proof_pool import (
    _graph_substrate_company_hint_plan,
    allocate_section_facts_from_graph_substrate,
)
from apps_rg.runtime.sections.unify_bullets_graph_evidence import (
    FORBIDDEN_C0_PROMPT_SUBSTRINGS,
    LEGACY_SIX_PACK_LEDGER_ORDER,
    TRACK_RANKED_SELECTION_METHOD,
    append_unify_path_framing_to_messages,
    assert_c0_pack_has_no_forbidden_template_leaks,
    format_unify_graph_bullet_evidence_pack,
    is_allowed_unify_selection_method,
    is_legacy_six_pack_ledger_order,
    max_consecutive_word_overlap,
)
from apps_rg.runtime.spine.front_contracts import (
    activate_fixture_dev_bypass,
    deactivate_fixture_dev_bypass,
)
from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS, run_unify_bullets_x2_gates

REPO = Path(__file__).resolve().parents[3]
JD = (REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt").read_text(encoding="utf-8")
BRIEF = (REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md").read_text(
    encoding="utf-8"
)


@pytest.fixture(autouse=True)
def _fixture_bypass():
    activate_fixture_dev_bypass(non_product_certified=True)
    yield
    deactivate_fixture_dev_bypass()


def _brown_allocate() -> dict:
    ledger = load_master_candidate_fact_ledger(repo_root=REPO)
    taxonomy = load_master_role_family_taxonomy(repo_root=REPO)
    plan, _, _ = allocate_section_facts_from_graph_substrate(
        ledger=ledger,
        taxonomy=taxonomy,
        section_id="unify_bullets",
        target_company="Brown & Brown",
        target_role="SVP IT Strategy & Innovation",
        jd_text=JD,
        briefing_text=BRIEF,
        ledger_path=default_ledger_path(repo_root=REPO),
        taxonomy_path=default_taxonomy_path(repo_root=REPO),
    )
    return plan


def test_legacy_six_pack_detector() -> None:
    assert is_legacy_six_pack_ledger_order(list(LEGACY_SIX_PACK_LEDGER_ORDER))
    assert not is_legacy_six_pack_ledger_order(
        [
            "fact_engineering_platform_004",
            "fact_engineering_platform_006",
            "fact_engineering_platform_003",
            "fact_engineering_platform_001",
            "fact_exec_002",
            "fact_engineering_platform_002",
        ]
    )


def test_selection_method_guard_rejects_company_hint() -> None:
    assert is_allowed_unify_selection_method(TRACK_RANKED_SELECTION_METHOD)
    assert not is_allowed_unify_selection_method("augmented_skills_graph_unify_bullets_company_hint")
    assert not is_allowed_unify_selection_method("hydrate_unify_bullets_from_canonical_resume")


def test_company_hint_plan_raises_for_unify_bullets() -> None:
    ledger = load_master_candidate_fact_ledger(repo_root=REPO)
    with pytest.raises(ValueError, match="forbidden for unify_bullets"):
        _graph_substrate_company_hint_plan(ledger, section_id="unify_bullets", hints=("unify",), limit=6)


def test_brown_allocation_not_legacy_six_pack() -> None:
    plan = _brown_allocate()
    assert plan["selection_method"] == TRACK_RANKED_SELECTION_METHOD
    ledger_ids = [
        str(f.get("ledger_candidate_fact_id") or f.get("candidate_fact_id") or "")
        for f in plan.get("facts") or []
    ]
    assert not is_legacy_six_pack_ledger_order(ledger_ids)
    assert ledger_ids == [
        "fact_engineering_platform_002",
        "fact_engineering_platform_001",
        "fact_engineering_platform_003",
        "fact_engineering_platform_004",
        "fact_engineering_platform_005",
        "fact_engineering_platform_006",
    ]


def test_c0_pack_forbidden_substrings_blocked() -> None:
    with pytest.raises(ValueError, match="forbidden template leakage"):
        assert_c0_pack_has_no_forbidden_template_leaks(
            "CANONICAL UNIFY FACTS\nbul_unify_001 | theme: Agentic AI"
        )


def test_c0_pack_format_has_compose_slots_and_skills() -> None:
    plan = _brown_allocate()
    body = format_unify_graph_bullet_evidence_pack(
        {
            "selected_fact_plan": plan,
            "proof_pool_metadata": {
                "selected_skill_rows": [
                    {
                        "skill_id": "skill_agentic_platform_productization",
                        "allowed_phrases": ["agentic platform productization"],
                        "fact_id_links": ["fact_engineering_platform_006"],
                    }
                ]
            },
        },
        allowed_block="ALLOWED_SOURCE_FACT_IDS: [bul_unify_001]\n",
        unify_id_hygiene="",
    )
    for forbidden in FORBIDDEN_C0_PROMPT_SUBSTRINGS:
        assert forbidden not in body
    assert "compose_one_bullet_from" in body
    assert TRACK_RANKED_SELECTION_METHOD in body or "track_ranked" in body


def test_path_framing_has_no_legacy_theme_angles() -> None:
    msgs = append_unify_path_framing_to_messages(
        [{"role": "user", "content": "base"}],
        path_index=2,
        temperature=0.4,
        runtime_payload={"jd_text": JD, "briefing": BRIEF},
    )
    text = msgs[-1]["content"]
    assert "PATH_FRAMING" in text
    assert "Dependency graph intelligence" not in text
    assert "legacy resume themes" in text.lower()


def test_max_consecutive_word_overlap_detects_archive_copy() -> None:
    archive = (
        "Designed and operationalized governed agentic AI platform capabilities for regulated "
        "enterprise workflows, including deterministic routing."
    )
    bullet = (
        "Designed and operationalized governed agentic AI platform capabilities for regulated "
        "enterprises, enhancing compliance."
    )
    assert max_consecutive_word_overlap(archive, bullet) >= 8


def test_x2_fails_on_company_hint_selection_method() -> None:
    bullets = [
        {"bullet_id": bid, "bullet_text": f"Outcome for {bid}.", "source_fact_ids": [bid]}
        for bid in UNIFY_BULLET_IDS
    ]
    ledger = [{"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]} for b in bullets]
    po = {
        "bullets": bullets,
        "selected_fact_plan": {
            "selection_method": "augmented_skills_graph_unify_bullets_company_hint",
            "facts": [{"fact_id": bid, "claim_text": "archive prose " * 5} for bid in UNIFY_BULLET_IDS],
        },
        "claim_ledger": ledger,
        "jd_alignment": {},
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=po,
        claim_ledger=ledger,
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text=JD,
        runtime_generation_status="MOCKED",
    )
    gate = next(g for g in gates if g.gate_id == "x2_unify_track_ranked_selection_method")
    assert gate.pass_ is False


def test_x2_fails_on_legacy_six_pack_allocation() -> None:
    bullets = [
        {"bullet_id": bid, "bullet_text": f"Outcome for {bid}.", "source_fact_ids": [bid]}
        for bid in UNIFY_BULLET_IDS
    ]
    ledger = [{"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]} for b in bullets]
    facts = [
        {
            "fact_id": bid,
            "ledger_candidate_fact_id": lid,
            "claim_text": f"Ledger claim for {lid}.",
        }
        for bid, lid in zip(UNIFY_BULLET_IDS, LEGACY_SIX_PACK_LEDGER_ORDER, strict=True)
    ]
    po = {
        "bullets": bullets,
        "selected_fact_plan": {
            "selection_method": TRACK_RANKED_SELECTION_METHOD,
            "facts": facts,
        },
        "claim_ledger": ledger,
        "jd_alignment": {},
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=po,
        claim_ledger=ledger,
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text=JD,
        runtime_generation_status="MOCKED",
    )
    gate = next(g for g in gates if g.gate_id == "x2_unify_not_legacy_six_pack_allocation")
    assert gate.pass_ is False


def test_x2_fails_on_archive_verbatim_bullet() -> None:
    archive = (
        "Designed and operationalized governed agentic AI platform capabilities for regulated "
        "enterprise workflows with deterministic routing and orchestration."
    )
    bullets = [
        {
            "bullet_id": "bul_unify_001",
            "bullet_text": (
                "Designed and operationalized governed agentic AI platform capabilities for regulated "
                "enterprises, enhancing compliance."
            ),
            "source_fact_ids": ["bul_unify_001"],
        },
        *[
            {"bullet_id": bid, "bullet_text": f"Distinct outcome {bid}.", "source_fact_ids": [bid]}
            for bid in UNIFY_BULLET_IDS[1:]
        ],
    ]
    ledger = [{"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]} for b in bullets]
    po = {
        "bullets": bullets,
        "selected_fact_plan": {
            "selection_method": TRACK_RANKED_SELECTION_METHOD,
            "facts": [
                {"fact_id": "bul_unify_001", "claim_text": archive},
                *[{"fact_id": bid, "claim_text": "other"} for bid in UNIFY_BULLET_IDS[1:]],
            ],
        },
        "claim_ledger": ledger,
        "jd_alignment": {},
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=po,
        claim_ledger=ledger,
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text=JD,
        runtime_generation_status="MOCKED",
    )
    gate = next(g for g in gates if g.gate_id == "x2_unify_no_archive_claim_verbatim")
    assert gate.pass_ is False


def test_graph_ranked_empty_expansion_not_legacy_six_pack() -> None:
    """Zero graph scores must not yield sorted engineering_platform_001..006 only."""
    from apps_rg.runtime.section_graph_skills_proof_pool import _graph_ranked_unify_bullets_plan

    ledger = load_master_candidate_fact_ledger(repo_root=REPO)

    def _empty_expansion(**_kwargs: object) -> dict:
        return {"selected_facts": [], "selected_skills": []}

    with patch(
        "apps_rg.fact_inventory.track_weighted_graph_expansion.build_track_weighted_expansion",
        side_effect=_empty_expansion,
    ):
        result = _graph_ranked_unify_bullets_plan(
            ledger,
            section_id="unify_bullets",
            target_role="SVP IT Strategy & Innovation",
            jd_text=JD,
            briefing_text=BRIEF,
            limit=6,
            repo_root=REPO,
        )
    assert result is not None
    plan, _, _ = result
    ledger_ids = list(plan.get("ledger_pick_order") or [])
    assert ledger_ids
    assert not is_legacy_six_pack_ledger_order(ledger_ids)


def test_graph_ranked_fail_closed_when_only_legacy_pack() -> None:
    from apps_rg.runtime.section_graph_skills_proof_pool import _graph_ranked_unify_bullets_plan

    ledger = load_master_candidate_fact_ledger(repo_root=REPO)
    with patch(
        "apps_rg.runtime.sections.unify_bullets_graph_evidence.is_legacy_six_pack_ledger_order",
        return_value=True,
    ):
        result = _graph_ranked_unify_bullets_plan(
            ledger,
            section_id="unify_bullets",
            target_role="SVP IT Strategy & Innovation",
            jd_text=JD,
            briefing_text=BRIEF,
            limit=6,
            repo_root=REPO,
        )
    assert result is None
