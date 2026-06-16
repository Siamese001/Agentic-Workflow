from __future__ import annotations

from apps_rg.runtime.validators.fact_ledger_authority import (
    FACT_LEDGER_AUTHORITY_LABELS,
    fact_ledger_authority_violation_reason,
    normalize_authority_label,
)


def test_normalize_authority_label_matches_blocked_fact_ledger_labels() -> None:
    assert normalize_authority_label(" Candidate Fact-Ledger ") == "candidate_fact_ledger"
    assert normalize_authority_label("master candidate skills fact ledger") in FACT_LEDGER_AUTHORITY_LABELS


def test_fact_ledger_authority_allows_legacy_substrate_reference_only() -> None:
    assert (
        fact_ledger_authority_violation_reason(
            proof_pool_metadata={
                "source_authority": "augmented_skills_graph",
                "claim_evidence_substrate_type": "candidate_fact_ledger",
                "evidence_authority": {
                    "authority": "augmented_skills_graph",
                    "ledger_ref": "master_candidate_skills_fact_ledger.json",
                },
            },
            selected_fact_plan={
                "selection_method": "augmented_skills_graph_headline",
                "facts": [{"fact_id": "fact_graph_001"}],
            },
        )
        is None
    )


def test_fact_ledger_authority_rejects_metadata_flags_and_source_fields() -> None:
    assert (
        fact_ledger_authority_violation_reason(
            proof_pool_metadata={"fact_ledger_authority": True},
        )
        == "fact_ledger_authority=true"
    )
    assert (
        fact_ledger_authority_violation_reason(
            proof_pool_metadata={"skills_authority_source_type": "candidate_fact_ledger"},
        )
        == "skills_authority_source_type='candidate_fact_ledger'"
    )


def test_fact_ledger_authority_rejects_plan_and_nested_selection_authority() -> None:
    assert (
        fact_ledger_authority_violation_reason(
            proof_pool_metadata={},
            selected_fact_plan={"candidate_fact_ledger_skill_authority": True},
        )
        == "selected_fact_plan.candidate_fact_ledger_skill_authority=true"
    )
    assert (
        fact_ledger_authority_violation_reason(
            proof_pool_metadata={
                "selection_scope": {"selection_method": "candidate_fact_ledger_weighted"}
            },
        )
        == "selection_scope.selection_method='candidate_fact_ledger_weighted'"
    )
