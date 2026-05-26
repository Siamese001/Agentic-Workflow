"""All seven sections: dual-source semantics (claim evidence vs skills authority)."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.fact_inventory.augmented_skills_graph import (
    CLAIM_EVIDENCE_SOURCE_TYPE_AUGMENTED_SKILLS_GRAPH,
    CLAIM_EVIDENCE_SOURCE_TYPE_CANDIDATE_FACT_LEDGER,
    SKILLS_AUTHORITY_SOURCE_TYPE,
    assert_skills_not_broad_ledger_authority,
    build_verified_skill_inventory_projection,
    default_augmented_skills_graph_path,
)
from apps_rg.runtime.proof_pool_resolver import PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH
from apps_rg.fact_inventory.candidate_fact_ledger import default_ledger_path
from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool

REPO = Path(__file__).resolve().parents[2]
GRAPH_PATH = default_augmented_skills_graph_path(REPO)
CANDIDATE_LEDGER_PATH = default_ledger_path(REPO)

SECTION_IDS = (
    "headline",
    "executive_summary",
    "competencies",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
)


def _assert_dual_source(meta: dict, *, pool) -> None:  # noqa: ANN001
    assert_skills_not_broad_ledger_authority(meta)
    assert meta.get("skills_authority_source_type") == SKILLS_AUTHORITY_SOURCE_TYPE
    assert meta.get("claim_evidence_source_type") in (
        CLAIM_EVIDENCE_SOURCE_TYPE_AUGMENTED_SKILLS_GRAPH,
        CLAIM_EVIDENCE_SOURCE_TYPE_CANDIDATE_FACT_LEDGER,
        "selected_role_fact_set",
        "base_resume_fallback",
    )
    assert meta.get("skills_authority_status") == "PASS"
    assert meta.get("legacy_broad_skills_ledger_skills_authority") is False
    assert meta.get("broad_skills_ledger_skills_authority") is not True
    if pool.proof_source == "broad_skills_ledger":
        assert meta.get("claim_evidence_source_type") == CLAIM_EVIDENCE_SOURCE_TYPE_CANDIDATE_FACT_LEDGER
        assert meta.get("broad_skills_ledger_claim_evidence_only") is True
    assert meta.get("skills_authority_graph_ref")
    assert meta.get("skills_authority_graph_digest")


@pytest.mark.parametrize("section_id", SECTION_IDS)
def test_dual_source_metadata_per_section(section_id: str) -> None:
    if not CANDIDATE_LEDGER_PATH.is_file():
        pytest.skip(f"candidate ledger missing: {CANDIDATE_LEDGER_PATH}")
    if not GRAPH_PATH.is_file():
        pytest.skip(f"graph missing: {GRAPH_PATH}")
    pool = resolve_section_proof_pool(section=section_id, repo_root=REPO)
    _assert_dual_source(pool.proof_pool_metadata, pool=pool)


def test_competencies_graph_projection_authoritative() -> None:
    if not GRAPH_PATH.is_file():
        pytest.skip("graph missing")
    proj = build_verified_skill_inventory_projection(section_id="competencies")
    assert proj.get("projection_from_graph") is True
    assert proj.get("source_authority") == "augmented_skills_graph"
    assert "verified_skill_inventory_projection" in proj
    assert proj.get("verified_skill_inventory_deprecated", {}).get("authority") == "deprecated_non_authority"


def test_unify_bullets_resolves_graph_skills_not_base_fallback_only() -> None:
    if not CANDIDATE_LEDGER_PATH.is_file():
        pytest.skip("candidate ledger missing")
    pool = resolve_section_proof_pool(section="unify_bullets", repo_root=REPO)
    assert pool.proof_source == PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH
    assert pool.base_resume_fallback_used is False
    meta = pool.proof_pool_metadata
    assert meta.get("skills_authority_status") == "PASS"
    assert meta.get("claim_evidence_source_type") == CLAIM_EVIDENCE_SOURCE_TYPE_AUGMENTED_SKILLS_GRAPH


def test_no_section_uses_broad_skills_ledger_as_skills_authority() -> None:
    if not CANDIDATE_LEDGER_PATH.is_file():
        pytest.skip("candidate ledger missing")
    for section_id in SECTION_IDS:
        pool = resolve_section_proof_pool(section=section_id, repo_root=REPO)
        assert_skills_not_broad_ledger_authority(pool.proof_pool_metadata)
