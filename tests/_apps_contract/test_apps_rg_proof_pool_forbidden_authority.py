"""W4.1 — proof pool resolver fail-closed forbidden authority branches."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.fact_inventory.candidate_fact_ledger import default_ledger_path
from apps_rg.runtime.product_evidence_authority import (
    ProductEvidenceAuthorityError,
    build_evidence_authority,
    validate_evidence_authority_block,
    validate_proof_pool_metadata_product_law,
)
from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool

REPO = Path(__file__).resolve().parents[2]


def test_legacy_broad_skills_ledger_rejected() -> None:
    with pytest.raises(ValueError, match="legacy_broad_skills_ledger is not permitted"):
        resolve_section_proof_pool(section="headline", repo_root=REPO, legacy_broad_skills_ledger=True)


@pytest.mark.parametrize(
    "authority",
    [
        "base_resume_fallback",
        "selected_role_fact_set",
        "broad_skills_ledger",
    ],
)
def test_forbidden_evidence_authority_metadata(authority: str) -> None:
    ea = build_evidence_authority(graph_ref="g.json", ledger_ref="l.json", skills_authority_status="PASS")
    ea = {**ea, "authority": authority}
    with pytest.raises(ProductEvidenceAuthorityError, match="forbidden evidence_authority"):
        validate_evidence_authority_block(ea, section_id="headline")


def test_unknown_authority_metadata_red_path() -> None:
    ea = build_evidence_authority(graph_ref="g.json", ledger_ref="l.json", skills_authority_status="PASS")
    ea = {**ea, "authority": "unknown"}
    with pytest.raises(ProductEvidenceAuthorityError, match="unknown"):
        validate_evidence_authority_block(ea, section_id="headline")


def test_missing_graph_ref_fail_closed() -> None:
    with pytest.raises(ProductEvidenceAuthorityError, match="graph_ref required"):
        validate_evidence_authority_block(
            build_evidence_authority(graph_ref="", ledger_ref="ledger.json", skills_authority_status="PASS"),
            section_id="headline",
        )


def test_missing_ledger_ref_fail_closed() -> None:
    with pytest.raises(ProductEvidenceAuthorityError, match="ledger_ref required"):
        validate_evidence_authority_block(
            build_evidence_authority(graph_ref="graph.json", ledger_ref="", skills_authority_status="PASS"),
            section_id="headline",
        )


def test_empty_metadata_fail_closed() -> None:
    with pytest.raises(ProductEvidenceAuthorityError, match="empty proof_pool_metadata"):
        validate_proof_pool_metadata_product_law({}, section_id="headline")


def test_srfs_used_flag_forbidden_on_product_metadata() -> None:
    meta = {
        "proof_pool_type": "augmented_skills_graph",
        "selected_role_fact_set_used": True,
        "evidence_authority": build_evidence_authority(
            graph_ref="g.json",
            ledger_ref="l.json",
            skills_authority_status="PASS",
        ),
        "selection_scope": {
            "section_id": "headline",
            "selection_method": "graph",
            "is_proof_authority": False,
        },
        "layout_context": {
            "base_resume_json_ref": "base.json",
            "story_claim_authority": False,
            "generated_story_claims_from_base_resume": False,
        },
    }
    with pytest.raises(ProductEvidenceAuthorityError, match="selected_role_fact_set_used must be false"):
        validate_proof_pool_metadata_product_law(meta, section_id="headline", proof_source="augmented_skills_graph")


def test_base_resume_fallback_used_forbidden() -> None:
    meta = {
        "proof_pool_type": "augmented_skills_graph",
        "base_resume_fallback_used": True,
        "evidence_authority": build_evidence_authority(
            graph_ref="g.json",
            ledger_ref="l.json",
            skills_authority_status="PASS",
        ),
        "selection_scope": {"section_id": "headline", "is_proof_authority": False},
        "layout_context": {
            "base_resume_json_ref": "base.json",
            "story_claim_authority": False,
            "generated_story_claims_from_base_resume": False,
        },
    }
    with pytest.raises(ProductEvidenceAuthorityError, match="base_resume_fallback forbidden"):
        validate_proof_pool_metadata_product_law(meta, section_id="headline", proof_source="augmented_skills_graph")


def test_graph_authority_required_when_ledger_present() -> None:
    if not default_ledger_path(REPO).is_file():
        pytest.skip("ledger missing")
    pool = resolve_section_proof_pool(section="competencies", repo_root=REPO, product_visible=False)
    assert pool.proof_source == "augmented_skills_graph"
    assert pool.base_resume_fallback_used is False
