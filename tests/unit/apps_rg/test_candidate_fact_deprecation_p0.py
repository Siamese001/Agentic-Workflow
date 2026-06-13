from __future__ import annotations

import pytest

from apps_rg.fact_inventory.augmented_skills_graph import SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
from apps_rg.runtime.validators.graph_skills_proof_common import (
    BLOCKED_CANDIDATE_FACT_AUTHORITY,
    GraphSkillsProofError,
    assert_candidate_fact_authority_deprecated,
)


def test_candidate_fact_runtime_authority_read_fails_closed_before_W1() -> None:
    with pytest.raises(GraphSkillsProofError, match=BLOCKED_CANDIDATE_FACT_AUTHORITY):
        assert_candidate_fact_authority_deprecated(
            section_id="headline",
            proof_pool_metadata={
                "candidate_fact_ledger_used_as_authority": True,
                "source_authority": "candidate_fact_ledger",
                "graph_only_claim_authority": False,
            },
            selected_fact_plan={
                "selection_method": "candidate_fact_ledger_direct",
                "facts": [{"candidate_fact_id": "fact_legacy_only_001"}],
            },
        )


def test_candidate_fact_id_lineage_alias_allowed_when_graphdb_authorized() -> None:
    assert_candidate_fact_authority_deprecated(
        section_id="headline",
        proof_pool_metadata={
            "source_authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
            "graph_only_claim_authority": True,
            "claim_evidence_source_type": "candidate_fact_ledger",
            "legacy_skills_ledger_role": "deprecated_reference",
        },
        selected_fact_plan={
            "selection_method": "augmented_skills_graph_headline",
            "facts": [
                {
                    "fact_id": "graph_fact_001",
                    "candidate_fact_id": "fact_legacy_alias_001",
                }
            ],
        },
    )


def test_candidate_fact_claim_substrate_without_graphdb_authority_fails_closed() -> None:
    with pytest.raises(GraphSkillsProofError, match=BLOCKED_CANDIDATE_FACT_AUTHORITY):
        assert_candidate_fact_authority_deprecated(
            section_id="executive_summary",
            proof_pool_metadata={
                "claim_evidence_source_type": "candidate_fact_ledger",
                "graph_only_claim_authority": False,
            },
            selected_fact_plan={
                "selection_method": "augmented_skills_graph_executive_summary",
                "facts": [{"fact_id": "fact_legacy_only_001"}],
            },
        )
