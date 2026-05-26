"""ibm_bullets: Phase 2 career-track-only graph proof pool + X2 gate."""
from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.fact_inventory.candidate_fact_ledger import (
    default_ledger_path,
    default_taxonomy_path,
    load_master_candidate_fact_ledger,
    load_master_role_family_taxonomy,
)
from apps_rg.runtime.section_graph_skills_proof_pool import allocate_section_facts_from_graph_substrate
from apps_rg.runtime.sections.ibm_bullets_graph_evidence import (
    IBM_EMPLOYMENT_WINDOW_LABEL,
    IBM_PHASE2_CAREER_TRACK,
    IBM_TRACK_RANKED_SELECTION_METHOD,
    check_ibm_bullets_phase2_career_track_scope,
)
from apps_rg.runtime.validators.ibm_bullets_x2 import run_ibm_bullets_x2_gates

REPO = Path(__file__).resolve().parents[3]


def test_allocate_ibm_bullets_phase2_track_ranked_only() -> None:
    ledger_path = default_ledger_path(REPO)
    ledger = load_master_candidate_fact_ledger(path=ledger_path)
    taxonomy = load_master_role_family_taxonomy(repo_root=REPO)
    plan, _ordered, _allowed = allocate_section_facts_from_graph_substrate(
        ledger=ledger,
        taxonomy=taxonomy,
        section_id="ibm_bullets",
        target_company="Brown & Brown",
        target_role="SVP IT Strategy & Innovation",
        jd_text="cloud data platform enterprise architecture",
        briefing_text="",
        ledger_path=ledger_path,
        taxonomy_path=default_taxonomy_path(REPO),
    )
    assert plan["selection_method"] == IBM_TRACK_RANKED_SELECTION_METHOD
    assert plan["career_track_scope_allowed"] == [IBM_PHASE2_CAREER_TRACK]
    assert plan["employment_window"] == IBM_EMPLOYMENT_WINDOW_LABEL
    facts = plan.get("facts") or []
    assert len(facts) >= 5
    assert all(str(f.get("career_track") or "") == IBM_PHASE2_CAREER_TRACK for f in facts)
    assert all(str(f.get("fact_id") or "").startswith("bul_ibm_") for f in facts[:5])


def test_phase2_scope_gate_passes_on_ranked_plan() -> None:
    ledger_path = default_ledger_path(REPO)
    ledger = load_master_candidate_fact_ledger(path=ledger_path)
    taxonomy = load_master_role_family_taxonomy(repo_root=REPO)
    plan, _o, _a = allocate_section_facts_from_graph_substrate(
        ledger=ledger,
        taxonomy=taxonomy,
        section_id="ibm_bullets",
        target_company="IBM",
        target_role="Lead Client Partner",
        jd_text="",
        briefing_text="",
        ledger_path=ledger_path,
        taxonomy_path=default_taxonomy_path(REPO),
    )
    meta = {
        "selection_method": plan["selection_method"],
        "career_track_scope_allowed": plan["career_track_scope_allowed"],
        "employment_window": plan["employment_window"],
        "selected_tracks": plan["career_track_scope_allowed"],
    }
    ok, obs = check_ibm_bullets_phase2_career_track_scope(
        proof_pool_metadata=meta,
        selected_fact_plan=plan,
    )
    assert ok is True
    assert obs["selection_method"] == IBM_TRACK_RANKED_SELECTION_METHOD


def test_phase2_scope_gate_rejects_genai_track_fact() -> None:
    ok, obs = check_ibm_bullets_phase2_career_track_scope(
        proof_pool_metadata={
            "selection_method": IBM_TRACK_RANKED_SELECTION_METHOD,
            "career_track_scope_allowed": [IBM_PHASE2_CAREER_TRACK],
            "employment_window": IBM_EMPLOYMENT_WINDOW_LABEL,
            "selected_tracks": ["track_genai_agentic"],
        },
        selected_fact_plan={
            "selection_method": IBM_TRACK_RANKED_SELECTION_METHOD,
            "career_track_scope_allowed": [IBM_PHASE2_CAREER_TRACK],
            "employment_window": IBM_EMPLOYMENT_WINDOW_LABEL,
            "facts": [
                {
                    "fact_id": "bul_ibm_001",
                    "career_track": "track_genai_agentic",
                    "claim_text": "x",
                }
            ],
        },
    )
    assert ok is False
    assert obs.get("reason") in (
        "forbidden_career_tracks_in_pool",
        "plan_fact_wrong_career_track",
    )


def test_x2_gate_ibm_phase2_career_track_scope_registered() -> None:
    ledger_path = default_ledger_path(REPO)
    ledger = load_master_candidate_fact_ledger(path=ledger_path)
    taxonomy = load_master_role_family_taxonomy(repo_root=REPO)
    plan, _o, allowed = allocate_section_facts_from_graph_substrate(
        ledger=ledger,
        taxonomy=taxonomy,
        section_id="ibm_bullets",
        target_company="IBM",
        target_role="SVP",
        jd_text="cloud",
        briefing_text="",
        ledger_path=ledger_path,
        taxonomy_path=default_taxonomy_path(REPO),
    )
    meta = {
        "selection_method": plan["selection_method"],
        "career_track_scope_allowed": plan["career_track_scope_allowed"],
        "employment_window": plan["employment_window"],
        "proof_pool_type": "augmented_skills_graph",
        "graph_skills_proof_pool": True,
    }
    bullets = [
        {
            "bullet_id": f"bul_ibm_{i:03d}",
            "bullet_text": f"Delivered enterprise outcomes {i}.",
            "source_fact_ids": [f"bul_ibm_{i:03d}"],
        }
        for i in range(1, 6)
    ]
    gates = run_ibm_bullets_x2_gates(
        bullets=bullets,
        parsed_output={"selected_fact_plan": plan, "bullets": bullets},
        claim_ledger=[{"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]} for b in bullets],
        allowed_fact_ids=allowed,
        jd_text="",
        runtime_generation_status="REAL_LLM",
        proof_pool_metadata=meta,
        runtime_payload={"selected_fact_plan": plan, "allowed_fact_ids": sorted(allowed)},
    )
    gate = next(g for g in gates if g.gate_id == "x2_ibm_phase2_career_track_scope")
    assert gate.pass_ is True
