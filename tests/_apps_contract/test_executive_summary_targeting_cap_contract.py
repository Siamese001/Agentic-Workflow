"""Contract: capsule + targeting cap + token budget on Brown-scale inputs."""
from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.spine.front_contracts import (
    activate_fixture_dev_bypass,
    deactivate_fixture_dev_bypass,
)
from apps_rg.runtime.dispatch.executive_summary_pa import compile_executive_summary_prompt
from apps_rg.runtime.sections.executive_summary_evidence_capsule import (
    compile_executive_summary_evidence_capsule,
)
from apps_rg.runtime.sections.executive_summary_token_budget import (
    ExecutiveSummaryTokenBudgetExceeded,
    apply_executive_summary_token_budget_policy,
)

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _fec_fixture_dev_bypass() -> None:
    activate_fixture_dev_bypass(non_product_certified=True)
    yield
    deactivate_fixture_dev_bypass()


def _brown_payload() -> dict:
    jd = (REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt").read_text(
        encoding="utf-8"
    )
    brief = (
        REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md"
    ).read_text(encoding="utf-8")
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
        "run_id": "targeting_cap_contract",
        "target_title": "Senior Vice President, IT Strategy & Innovation",
        "target_company": "Brown & Brown",
        "jd_text": jd,
        "briefing": brief,
        "allowed_fact_ids": ["fact_governance_003"],
        "selected_fact_plan": {
            "facts": [
                {
                    "fact_id": "fact_governance_003",
                    "claim_text": "Implemented Basel III / CCAR frameworks.",
                    "confidence": "HIGH",
                }
            ],
        },
    }


def test_brown_scale_token_budget_receipt_includes_targeting_cap_fields():
    payload = _brown_payload()
    baseline = dict(payload)
    baseline["evidence_capsule_disabled"] = True
    baseline_compiled = compile_executive_summary_prompt(baseline, run_id=payload["run_id"])
    from apps_rg.runtime.sections.executive_summary_token_budget import estimate_tokens_approximate

    before_capsule = estimate_tokens_approximate(
        baseline_compiled.artifact.messages[0]["content"]
    )
    compile_executive_summary_evidence_capsule(payload)
    compiled = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    payload["prompt_token_estimates"] = {"before_capsule_prompt_estimate": before_capsule}
    try:
        _, receipt = apply_executive_summary_token_budget_policy(
            compiled,
            runtime_payload=payload,
            provider="retired_provider_profile",
            model="Retired/Provider-Model",
            requested_max_output_tokens=1024,
            provider_context_window=16384,
        )
    except ExecutiveSummaryTokenBudgetExceeded as exc:
        receipt = exc.receipt
    assert receipt.get("capsule_applied") is True
    assert receipt.get("targeting_cap_applied") is True
    assert receipt.get("forbidden_trim_violations") == []
    assert receipt.get("evidence_contract_preserved") is True
    t_before = receipt.get("targeting_tokens_before_cap")
    t_after = receipt.get("targeting_tokens_after_cap")
    assert isinstance(t_before, int) and isinstance(t_after, int)
    assert t_after < t_before
    if receipt.get("status") == "PASS":
        assert receipt["compiled_prompt_tokens_after_trim"] <= receipt["available_input_tokens"]
