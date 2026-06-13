from __future__ import annotations

import pytest

from apps_rg.fact_inventory.augmented_skills_graph import SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
from apps_rg.runtime.product_evidence_authority import (
    ProductEvidenceAuthorityError,
    finalize_product_section_proof_pool,
)
from apps_rg.runtime.proof_pool_resolver import PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH, SectionProofPool
from apps_rg.runtime.validators.graph_skills_proof_common import (
    BLOCKED_FACT_LEDGER_AUTHORITY,
    GraphSkillsProofError,
    assert_fact_ledger_not_skills_metrics_authority,
    assert_pool_not_ledger_authority,
)


def _minimal_pool(**kwargs: object) -> SectionProofPool:
    defaults: dict[str, object] = {
        "section": "headline",
        "proof_source": PROOF_SOURCE_AUGMENTED_SKILLS_GRAPH,
        "proof_pool_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        "proof_pool_digest": "graphdigest",
        "selected_fact_plan": {
            "selection_method": "augmented_skills_graph_headline",
            "facts": [{"fact_id": "fact_graph_001", "claim_text": "Graph-backed claim"}],
        },
        "allowed_fact_ids_ordered": ["fact_graph_001"],
        "allowed_fact_ids": {"fact_graph_001"},
        "bullet_rows": [],
        "proof_pool_metadata": {
            "source_authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
            "graph_only_claim_authority": True,
            "skills_authority_source_type": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
            "skills_authority_status": "PASS",
            "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
            "claim_evidence_substrate_ref": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger.json",
            "legacy_skills_ledger_role": "deprecated_reference",
        },
        "fallback_used": False,
        "base_resume_fallback_used": False,
        "broad_skills_ledger_present": False,
        "srfs_present": False,
        "base_resume_json_ref": "",
        "base_resume_json_hash": "",
        "broad_skills_ledger_ref": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger.json",
        "broad_skills_ledger_digest": "legacydigest",
        "srfs_ref": "",
        "base_resume_override_used": False,
    }
    defaults.update(kwargs)
    return SectionProofPool(**defaults)  # type: ignore[arg-type]


def test_fact_ledger_runtime_skill_read_fails_closed_after_W2() -> None:
    with pytest.raises(GraphSkillsProofError, match=BLOCKED_FACT_LEDGER_AUTHORITY):
        assert_fact_ledger_not_skills_metrics_authority(
            section_id="headline",
            proof_pool_metadata={
                "skills_authority_source_type": "fact_ledger",
                "fact_ledger_skills_authority": True,
            },
            selected_fact_plan={
                "selection_method": "fact_ledger_direct",
                "facts": [{"fact_id": "fact_legacy_001"}],
            },
        )


def test_fact_ledger_runtime_metric_read_fails_closed_after_W2() -> None:
    with pytest.raises(GraphSkillsProofError, match=BLOCKED_FACT_LEDGER_AUTHORITY):
        assert_fact_ledger_not_skills_metrics_authority(
            section_id="executive_summary",
            proof_pool_metadata={
                "metrics_authority_source_type": "candidate_fact_ledger",
                "fact_ledger_metrics_authority": True,
            },
            selected_fact_plan={
                "selection_method": "augmented_skills_graph_executive_summary",
                "facts": [{"fact_id": "fact_legacy_001", "metric_outcome_ids": ["met_001"]}],
            },
        )


def test_fact_ledger_claim_substrate_allowed_when_graphdb_authorized() -> None:
    assert_fact_ledger_not_skills_metrics_authority(
        section_id="headline",
        proof_pool_metadata={
            "source_authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
            "graph_only_claim_authority": True,
            "skills_authority_source_type": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
            "claim_evidence_source_type": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
            "claim_evidence_substrate_type": "candidate_fact_ledger",
            "claim_evidence_substrate_ref": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger.json",
            "legacy_skills_ledger_role": "deprecated_reference",
        },
        selected_fact_plan={
            "selection_method": "augmented_skills_graph_headline",
            "facts": [{"fact_id": "fact_graph_001", "candidate_fact_id": "fact_legacy_alias_001"}],
        },
    )


def test_pool_validator_rejects_fact_ledger_authority_fields() -> None:
    pool = _minimal_pool(
        proof_pool_metadata={
            "source_authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
            "graph_only_claim_authority": True,
            "skills_authority_source_type": "candidate_fact_ledger",
        }
    )
    with pytest.raises(GraphSkillsProofError, match=BLOCKED_FACT_LEDGER_AUTHORITY):
        assert_pool_not_ledger_authority(pool)


def test_product_finalize_rejects_fact_ledger_authority_before_normalization() -> None:
    pool = _minimal_pool(
        proof_pool_metadata={
            "source_authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
            "graph_only_claim_authority": True,
            "metrics_authority_source_type": "master_candidate_skills_fact_ledger",
        }
    )
    with pytest.raises(ProductEvidenceAuthorityError, match=BLOCKED_FACT_LEDGER_AUTHORITY):
        finalize_product_section_proof_pool(pool)
