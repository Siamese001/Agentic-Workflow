from __future__ import annotations

from apps_rg.runtime.c0.section_authority_profile import (
    AUTHORITY_AGGREGATE_SECTION_PROOF,
    AUTHORITY_DIRECT_VECTOR_PROOF,
    AUTHORITY_INHERITED_BULLET_PROOF,
    AUTHORITY_POSITIONING_ONLY,
    c0_section_authority_profile,
    direct_vector_section_ids,
)


def test_bullet_and_competency_sections_use_direct_vector_proof() -> None:
    for section_id in (
        "competencies",
        "unify_bullets",
        "ibm_bullets",
        "insurtech_bullets",
        "ey_bullets",
    ):
        profile = c0_section_authority_profile(section_id)
        assert profile.authority_mode == AUTHORITY_DIRECT_VECTOR_PROOF
        assert profile.direct_vector_proof is True
        assert profile.product_hybrid_allowed is True
        assert section_id in direct_vector_section_ids()


def test_narrative_sections_inherit_finalized_bullet_proof() -> None:
    expected = {
        "unify_narrative": "unify_bullets",
        "ibm_narrative": "ibm_bullets",
        "insurtech_narrative": "insurtech_bullets",
        "ey_narrative": "ey_bullets",
    }
    for section_id, upstream in expected.items():
        profile = c0_section_authority_profile(section_id)
        assert profile.authority_mode == AUTHORITY_INHERITED_BULLET_PROOF
        assert profile.direct_vector_proof is False
        assert profile.inherited_bullet_proof is True
        assert profile.product_hybrid_allowed is False
        assert profile.upstream_sections == (upstream,)
        assert section_id not in direct_vector_section_ids()


def test_aggregate_sections_remain_direct_vector_authority() -> None:
    executive = c0_section_authority_profile("executive_summary")
    headline = c0_section_authority_profile("headline")

    assert executive.authority_mode == AUTHORITY_AGGREGATE_SECTION_PROOF
    assert executive.direct_vector_proof is True
    assert executive.aggregate_section_proof is True
    assert executive.product_hybrid_allowed is True

    assert headline.authority_mode == AUTHORITY_POSITIONING_ONLY
    assert headline.direct_vector_proof is True
    assert headline.aggregate_section_proof is True
    assert headline.positioning_only is True
    assert headline.product_hybrid_allowed is True
