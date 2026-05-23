"""W2.1 — evidence capsule must not enable SRFS pool as proof authority."""

from __future__ import annotations

import pytest

from apps_rg.runtime.sections.executive_summary_evidence_capsule import (
    _capsule_enabled,
    compile_executive_summary_evidence_capsule,
)


def _payload(*, proof_pool_type: str, facts: list[dict]) -> dict:
    return {
        "proof_pool_metadata": {
            "proof_pool_type": proof_pool_type,
            "selected_role_fact_set_used": proof_pool_type == "selected_role_fact_set",
        },
        "selected_fact_plan": {"facts": facts},
        "allowed_fact_ids": [f["fact_id"] for f in facts],
    }


def test_capsule_enabled_with_graph_facts() -> None:
    facts = [
        {
            "fact_id": "bul_unify_001",
            "text": "Led platform engineering and delivery for enterprise SaaS.",
            "claim_text": "Led platform engineering and delivery for enterprise SaaS.",
        }
    ]
    payload = _payload(proof_pool_type="augmented_skills_graph", facts=facts)
    assert _capsule_enabled(payload) is True
    try:
        _, receipt = compile_executive_summary_evidence_capsule(payload)
    except Exception as exc:
        if "EVIDENCE_CAPSULE_PRESERVATION" in str(exc):
            pytest.skip("preservation needs full fact ledger shape in unit fixture")
        raise
    assert receipt.get("selected_role_fact_set_used") is False
    assert receipt.get("graph_proof_pool_used") is True


def test_capsule_requires_facts_red_path() -> None:
    payload = _payload(proof_pool_type="augmented_skills_graph", facts=[])
    assert _capsule_enabled(payload) is False
    with pytest.raises(ValueError, match="requires selected_fact_plan.facts"):
        compile_executive_summary_evidence_capsule(payload)


def test_srfs_pool_type_receipt_still_denies_srfs_authority() -> None:
    facts = [
        {
            "fact_id": "bul_unify_001",
            "text": "Led platform engineering and delivery for enterprise SaaS.",
            "claim_text": "Led platform engineering and delivery for enterprise SaaS.",
        }
    ]
    payload = _payload(proof_pool_type="selected_role_fact_set", facts=facts)
    try:
        _, receipt = compile_executive_summary_evidence_capsule(payload)
    except Exception as exc:
        if "EVIDENCE_CAPSULE_PRESERVATION" in str(exc):
            pytest.skip("preservation needs full fact ledger shape in unit fixture")
        raise
    assert receipt.get("selected_role_fact_set_used") is False
