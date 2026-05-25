"""Authority separation negative tests (NEG-1..NEG-6) for graph-skills quality plan."""
from __future__ import annotations

import pytest

from apps_rg.runtime.graph_selection_rationale import reject_jd_only_skill_admission
from apps_rg.runtime.legacy_proof_sources import PROOF_SOURCE_BROAD_SKILLS_LEDGER, PROOF_SOURCE_SRFS
from apps_rg.runtime.proof_pool_resolver import PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH, SectionProofPool
from apps_rg.runtime.validators.graph_skills_proof_common import (
    GraphSkillsProofError,
    assert_capsule_phrase_cannot_satisfy_unsupported_claim,
    assert_capsule_phrases_not_proof_authority,
    assert_forbidden_proof_source,
    assert_hybrid_fact_ids_in_resolver_pool,
    assert_pool_not_ledger_authority,
    assert_selected_fact_plan_not_base_resume_authority,
)


def _minimal_pool(**kwargs: object) -> SectionProofPool:
    defaults: dict[str, object] = {
        "section": "executive_summary",
        "proof_source": PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
        "proof_pool_ref": "test",
        "proof_pool_digest": "deadbeef",
        "selected_fact_plan": {"facts": [{"fact_id": "fact_a"}]},
        "allowed_fact_ids_ordered": ["fact_a"],
        "allowed_fact_ids": {"fact_a"},
        "bullet_rows": [],
        "proof_pool_metadata": {"graph_only_claim_authority": True},
        "fallback_used": False,
        "base_resume_fallback_used": False,
        "broad_skills_ledger_present": False,
        "srfs_present": False,
        "base_resume_json_ref": "",
        "base_resume_json_hash": "",
        "broad_skills_ledger_ref": "",
        "broad_skills_ledger_digest": "",
        "srfs_ref": "",
        "base_resume_override_used": False,
    }
    defaults.update(kwargs)
    return SectionProofPool(**defaults)  # type: ignore[arg-type]


def test_neg1_jd_only_skill_rejected() -> None:
    row = reject_jd_only_skill_admission(skill_id="jd_inferred", jd_text="IT strategy", fact_id_links=[])
    assert row["admitted"] is False


def test_neg2_capsule_phrase_cannot_satisfy_unsupported_claim() -> None:
    with pytest.raises(GraphSkillsProofError, match="capsule phrase"):
        assert_capsule_phrase_cannot_satisfy_unsupported_claim(
            section_id="executive_summary",
            text_claim_coverage={
                "sentences": [
                    {
                        "claim_text": "bul_unify_001 platform delivery",
                        "cited_fact_ids": [],
                        "supported": True,
                    }
                ]
            },
            allowed_fact_ids=["fact_a"],
            capsule_phrases=["bul_unify_001"],
        )


def test_neg3_hybrid_fact_outside_resolver_pool() -> None:
    with pytest.raises(GraphSkillsProofError, match="outside resolver pool"):
        assert_hybrid_fact_ids_in_resolver_pool(
            section_id="unify_bullets",
            hybrid_suggested_fact_ids=["fact_outside_pool"],
            resolver_allowed_fact_ids=["bul_unify_001", "fact_a"],
        )


def test_neg4_forbidden_proof_sources() -> None:
    with pytest.raises(GraphSkillsProofError, match="forbidden"):
        assert_forbidden_proof_source(section_id="headline", proof_source=PROOF_SOURCE_BROAD_SKILLS_LEDGER)
    with pytest.raises(GraphSkillsProofError, match="forbidden"):
        assert_forbidden_proof_source(section_id="headline", proof_source=PROOF_SOURCE_SRFS)


def test_neg5_base_resume_plan_authority_forbidden() -> None:
    with pytest.raises(GraphSkillsProofError, match="base_resume_claim_authority"):
        assert_selected_fact_plan_not_base_resume_authority(
            section_id="unify_bullets",
            proof_pool_metadata={"base_resume_claim_authority": True},
            selected_fact_plan={"facts": [{"fact_id": "bul_unify_001"}]},
        )
    with pytest.raises(GraphSkillsProofError, match="selection_method"):
        assert_selected_fact_plan_not_base_resume_authority(
            section_id="ibm_bullets",
            proof_pool_metadata={"graph_only_claim_authority": False},
            selected_fact_plan={
                "selection_method": "hydrate_ibm_bullets_from_canonical_resume",
                "facts": [{"fact_id": "bul_ibm_001"}],
            },
        )


def test_neg6_phrase_cannot_be_fact_id() -> None:
    with pytest.raises(GraphSkillsProofError, match="capsule phrase"):
        assert_capsule_phrases_not_proof_authority(
            section_id="executive_summary",
            proof_pool_metadata={
                "selected_skill_rows": [
                    {
                        "skill_id": "skill_x",
                        "allowed_phrases": ["bul_unify_001"],
                        "fact_id_links": ["fact_a"],
                    }
                ]
            },
            allowed_fact_ids=["bul_unify_001"],
            selected_fact_plan={"facts": []},
        )


def test_neg4_pool_validator_rejects_broad_ledger() -> None:
    pool = _minimal_pool(proof_source=PROOF_SOURCE_BROAD_SKILLS_LEDGER)
    with pytest.raises(GraphSkillsProofError):
        assert_pool_not_ledger_authority(pool)
