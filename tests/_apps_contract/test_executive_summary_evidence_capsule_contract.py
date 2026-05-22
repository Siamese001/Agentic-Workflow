"""Contract tests: PA consumes evidence capsule with evidence law and allowed IDs."""
from __future__ import annotations

import pytest

from apps_rg.runtime.section_front_spine_bridge import (
    activate_fixture_dev_bypass,
    deactivate_fixture_dev_bypass,
)
from apps_rg.runtime.dispatch.executive_summary_pa import compile_executive_summary_prompt
from apps_rg.runtime.sections.executive_summary_evidence_capsule import (
    compile_executive_summary_evidence_capsule,
    write_evidence_capsule_receipt,
)


@pytest.fixture(autouse=True)
def _fec_fixture_dev_bypass() -> None:
    activate_fixture_dev_bypass(non_product_certified=True)
    yield
    deactivate_fixture_dev_bypass()


def _payload() -> dict:
    return {
        "product_visible": False,
        "proof_pool_metadata": {
            "proof_pool_type": "augmented_skills_graph",
            "graph_skills_proof_pool": True,
            "evidence_authority": {
                "authority": "augmented_skills_graph",
                "skills_authority_status": "PASS",
            },
        },
        "run_id": "cap_contract_run",
        "target_title": "SVP",
        "target_company": "Brown & Brown",
        "jd_text": "AI strategy",
        "briefing": "insurance brokerage",
        "allowed_fact_ids": ["fact_governance_003"],
        "selected_fact_plan": {
            "facts": [
                {
                    "fact_id": "fact_governance_003",
                    "claim_text": "Implemented Basel III frameworks.",
                    "confidence": "HIGH",
                }
            ],
        },
    }


def test_pa_includes_evidence_law_allowed_ids_and_jd_not_proof(tmp_path):
    payload = _payload()
    _, receipt = compile_executive_summary_evidence_capsule(payload)
    write_evidence_capsule_receipt(tmp_path, receipt)
    compiled = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    text = compiled.artifact.messages[0]["content"]
    assert "ALLOWED_SOURCE_FACT_IDS" in text
    assert "NO FABRICATION" in text.upper() or "no fabrication" in text.lower()
    assert "jd_used_as_proof=false" in text or "jd_used_as_proof must be false" in text
    assert "claim_ledger" in text
    assert "NOT PROOF" in text or "targeting only" in text
    assert "fact_governance_003" in text
    assert (tmp_path / "evidence_capsule_receipt.json").is_file()
