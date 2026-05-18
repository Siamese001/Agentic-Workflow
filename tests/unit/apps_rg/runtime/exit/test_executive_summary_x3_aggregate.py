"""Unit tests for apps_rg executive_summary_x3.aggregate_x3 (headline and shared lanes).

Policy encoded here matches runtime: proof-eligible ``X3_ALLOW`` requires every configured
X1D judge row to be MODEL_BACKED + MODEL_BACKED_PASS with no provider_blocked / blocked modes.
There is no quorum branch — a rate-limited external judge remains ``X3_REVIEW_JUDGE_PROVIDER_BLOCKED``.
"""
from __future__ import annotations

from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3


def _judge_model_backed_pass(
    provider_key: str,
    *,
    score: float = 0.9,
    threshold: float = 0.8,
) -> dict:
    return {
        "provider_key": provider_key,
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_PASS",
        "pass": True,
        "decisive_failure": False,
        "provider_blocked": False,
        "normalized_score": score,
        "normalized_threshold": threshold,
    }


def _judge_blocked_rate_limit(provider_key: str) -> dict:
    return {
        "provider_key": provider_key,
        "evaluator_mode": "BLOCKED_RATE_LIMIT",
        "provider_status": "BLOCKED_RATE_LIMIT",
        "pass": False,
        "decisive_failure": False,
        "provider_blocked": True,
        "exact_provider_error": "Gemini quota or rate limited (HTTP 429).",
    }


def _judge_mocked_plumbing(provider_key: str) -> dict:
    return {
        "provider_key": provider_key,
        "evaluator_mode": "MOCKED",
        "provider_status": "MOCKED",
        "pass": True,
        "decisive_failure": False,
        "provider_blocked": False,
    }


def _minimal_usage_ledger() -> dict:
    return {
        "schema": "section_input_usage_ledger_v1",
        "evidence_boundary": {
            "non_evidence_inputs_used_as_claim_evidence": False,
            "non_evidence_inputs_in_source_fact_ids": False,
        },
        "claim_support_summary": {
            "claims_with_targeting_input_in_source_fact_ids": 0,
            "claims_with_context_input_in_source_fact_ids": 0,
        },
    }


def _base_kwargs(judges: list[dict]) -> dict:
    return {
        "resume_display_text": "SVP Engineering | A | B | C",
        "claim_ledger": [],
        "x2_gates": [{"gate_id": "x2_example", "pass": True}],
        "x1d_judges": judges,
        "runtime_generation_status": "REAL_LLM",
        "product_quality_status": "PASS",
        "section_input_usage_ledger": _minimal_usage_ledger(),
    }


def test_all_three_model_backed_pass_x3_allow() -> None:
    judges = [
        _judge_model_backed_pass("gemini_pro"),
        _judge_model_backed_pass("openai_chatgpt"),
        _judge_model_backed_pass("anthropic_claude"),
    ]
    x3 = aggregate_x3(**_base_kwargs(judges))
    assert x3.x3_code == "X3_ALLOW"
    assert x3.pass_ is True
    assert x3.blocked_judges == []
    assert x3.blocked_judge_detail_rows == []
    assert set(x3.model_backed_pass_provider_keys) == {
        "gemini_pro",
        "openai_chatgpt",
        "anthropic_claude",
    }
    assert x3.proof_eligible_allow_requires == "every_configured_x1d_judge_model_backed_pass"
    assert "ALLOW_BY_QUORUM" not in x3.x3_code


def test_one_judge_blocked_rate_limit_x3_review_provider_blocked() -> None:
    judges = [
        _judge_blocked_rate_limit("gemini_pro"),
        _judge_model_backed_pass("openai_chatgpt"),
        _judge_model_backed_pass("anthropic_claude"),
    ]
    x3 = aggregate_x3(**_base_kwargs(judges))
    assert x3.x3_code == "X3_REVIEW_JUDGE_PROVIDER_BLOCKED"
    assert x3.pass_ is False
    assert x3.blocked_judges == ["gemini_pro"]
    assert len(x3.blocked_judge_detail_rows) == 1
    row = x3.blocked_judge_detail_rows[0]
    assert row["provider_key"] == "gemini_pro"
    assert row["evaluator_mode"] == "BLOCKED_RATE_LIMIT"
    assert row["provider_blocked"] is True
    assert "429" in row["exact_provider_error"]
    assert set(x3.model_backed_pass_provider_keys) == {"openai_chatgpt", "anthropic_claude"}


def test_mock_judge_with_real_llm_not_proof_allow() -> None:
    judges = [
        _judge_mocked_plumbing("gemini_pro"),
        _judge_model_backed_pass("openai_chatgpt"),
        _judge_model_backed_pass("anthropic_claude"),
    ]
    x3 = aggregate_x3(**_base_kwargs(judges))
    assert x3.x3_code == "X3_REVIEW_MOCKED_PLUMBING_ONLY"
    assert x3.pass_ is False
    assert x3.mocked_judges == ["gemini_pro"]
    assert x3.x3_code != "X3_ALLOW"


def test_blocked_mode_schema_without_quorum_still_review_blocked() -> None:
    """BLOCKED_* parse/schema modes count as blocked; no partial-quorum ALLOW."""
    judges = [
        {
            "provider_key": "gemini_pro",
            "evaluator_mode": "BLOCKED_RESPONSE_PARSE_ERROR",
            "provider_status": "BLOCKED_RESPONSE_PARSE_ERROR",
            "pass": False,
            "decisive_failure": False,
            "provider_blocked": True,
            "exact_provider_error": "Failed to extract JSON",
        },
        _judge_model_backed_pass("openai_chatgpt"),
        _judge_model_backed_pass("anthropic_claude"),
    ]
    x3 = aggregate_x3(**_base_kwargs(judges))
    assert x3.x3_code == "X3_REVIEW_JUDGE_PROVIDER_BLOCKED"
    assert x3.pass_ is False
