"""Partner ADE C0.3 calibration — role inference + fact-link bindings."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.fact_inventory.candidate_fact_ledger import load_master_role_family_taxonomy
from apps_rg.fact_inventory.track_weighted_graph_expansion import infer_projection_role_family_key
from apps_rg.runtime.c0.c03_graph_expansion import (
    BINDING_MODE_FACT_LINKS_FIRST,
    BINDING_MODE_TAG_LABEL_ONLY,
    expand_c03_graph_bindings,
)
from apps_rg.runtime.c0.c03_role_family import resolve_c0_role_family_key
from apps_rg.runtime.proof_pool_resolver import SectionProofPool

REPO = Path(__file__).resolve().parents[3]
JD = REPO / "apps_rg/config/targeting/openai_partner_ade_jd.txt"
BRIEF = REPO / "apps_rg/config/targeting/openai_partner_ade_briefing.md"


@pytest.mark.skipif(not JD.is_file(), reason="ADE JD fixture missing")
def test_partner_ade_role_family_not_svp_default() -> None:
    jd = JD.read_text(encoding="utf-8")
    briefing = BRIEF.read_text(encoding="utf-8") if BRIEF.is_file() else ""
    taxonomy = load_master_role_family_taxonomy(repo_root=REPO)
    key = infer_projection_role_family_key(
        target_role="Partner ADE — AI Deployment Engineering",
        jd_text=jd,
        briefing_text=briefing,
        taxonomy=taxonomy,
    )
    assert key != "SVP_ENGINEERING_AI_PLATFORM"
    assert key in (
        "PARTNER_APPLIED_AI_ARCHITECTURE",
        "CONSULTING_DELIVERY_LEADERSHIP",
        "ANTHROPIC_PARTNERSHIPS_APPLIED_AI",
    )


@pytest.mark.skipif(not JD.is_file(), reason="ADE JD fixture missing")
def test_resolve_c0_role_family_from_pool_metadata() -> None:
    jd = JD.read_text(encoding="utf-8")
    pool = SectionProofPool(
        section="competencies",
        proof_source="graph",
        proof_pool_ref="x",
        proof_pool_digest="y",
        selected_fact_plan={"facts": []},
        allowed_fact_ids_ordered=[],
        allowed_fact_ids=set(),
        bullet_rows=[],
        proof_pool_metadata={
            "target_role": "Partner ADE",
            "jd_text": jd,
            "track_weighted_graph_expansion": {
                "projection_role_family_key": "PARTNER_APPLIED_AI_ARCHITECTURE",
            },
        },
        fallback_used=False,
        base_resume_fallback_used=False,
        broad_skills_ledger_present=False,
        srfs_present=False,
        base_resume_json_ref="",
        base_resume_json_hash="",
        broad_skills_ledger_ref="",
        broad_skills_ledger_digest="",
        srfs_ref="",
        base_resume_override_used=False,
    )
    assert (
        resolve_c0_role_family_key(pool=pool, repo_root=REPO)
        == "PARTNER_APPLIED_AI_ARCHITECTURE"
    )


@pytest.mark.skipif(not JD.is_file(), reason="ADE JD fixture missing")
def test_fact_links_mode_beats_tag_only_on_direct_support() -> None:
    from apps_rg.fact_inventory.competencies_graph_skills_proof_pool import (
        build_competencies_graph_skills_proof_payload,
    )
    from apps_rg.runtime.c0.c02_evidence_fetch import fetch_c02_evidence_atoms

    jd = JD.read_text(encoding="utf-8")
    briefing = BRIEF.read_text(encoding="utf-8") if BRIEF.is_file() else ""
    payload = build_competencies_graph_skills_proof_payload(
        repo_root=REPO,
        jd_text=jd,
        target_role="Partner ADE",
        briefing_text=briefing,
    )
    plan = payload.get("selected_fact_plan") or {}
    facts = list(plan.get("facts") or [])
    allowed = {str(f.get("fact_id") or "") for f in facts if f.get("fact_id")}
    pool = SectionProofPool(
        section="competencies",
        proof_source="graph",
        proof_pool_ref="p",
        proof_pool_digest="d",
        selected_fact_plan=plan,
        allowed_fact_ids_ordered=sorted(allowed),
        allowed_fact_ids=allowed,
        bullet_rows=[],
        proof_pool_metadata={},
        fallback_used=False,
        base_resume_fallback_used=False,
        broad_skills_ledger_present=False,
        srfs_present=False,
        base_resume_json_ref="",
        base_resume_json_hash="",
        broad_skills_ledger_ref="",
        broad_skills_ledger_digest="",
        srfs_ref="",
        base_resume_override_used=False,
    )
    c02 = fetch_c02_evidence_atoms(section_id="competencies", pool=pool, repo_root=REPO)
    atoms = list(c02.get("atoms") or [])
    if not atoms:
        pytest.skip("no C0.2 atoms from competencies graph pool")
    rf = infer_projection_role_family_key(
        target_role="Partner ADE",
        jd_text=jd,
        briefing_text=briefing,
        taxonomy=load_master_role_family_taxonomy(repo_root=REPO),
    )
    legacy = expand_c03_graph_bindings(
        section_id="competencies",
        atoms=atoms,
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        repo_root=REPO,
        binding_mode=BINDING_MODE_TAG_LABEL_ONLY,
    )
    hardened = expand_c03_graph_bindings(
        section_id="competencies",
        atoms=atoms,
        role_family_key=rf,
        repo_root=REPO,
        binding_mode=BINDING_MODE_FACT_LINKS_FIRST,
    )
    lm = legacy.get("binding_metrics") or {}
    hm = hardened.get("binding_metrics") or {}
    assert hm.get("direct_support_count", 0) >= lm.get("direct_support_count", 0)
    assert (
        hm.get("skill_fact_link_direct_count", 0) >= lm.get("skill_fact_link_direct_count", 0)
        or rf != "SVP_ENGINEERING_AI_PLATFORM"
    )
