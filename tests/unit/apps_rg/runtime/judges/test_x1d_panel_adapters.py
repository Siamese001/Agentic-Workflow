from __future__ import annotations

import pytest

from apps_rg.runtime.judges.executive_summary_x1d import JudgeOutput
from apps_rg.runtime.judges.x1d_panel_adapters import AppsRgX1dPanelAdapter, build_panel_adapter
from apps_rg.runtime.judges.x1d_panel_context import X1dPanelProviderContext
from apps_rg.runtime.judges.x1d_panel_harness import AdapterInvokeError, CanonicalJudgeContract


def _contract() -> CanonicalJudgeContract:
    return CanonicalJudgeContract(
        section_id="executive_summary",
        user_prompt="Grade only.",
        deterministic_gate_summary={"x2": {"pass": True}},
        proof_boundary={"judges_must_not_rewrite": True},
    )


def _judge_output(*, blocked: bool = False) -> JudgeOutput:
    return JudgeOutput(
        judge_id="j1",
        provider_name="OpenAI",
        provider_key="openai_chatgpt",
        evaluator_mode="BLOCKED_PROVIDER" if blocked else "MODEL_BACKED",
        provider_status="BLOCKED_AUTH" if blocked else "MODEL_BACKED_PASS",
        model_name="model",
        provider_available=not blocked,
        provider_blocked=blocked,
        exact_provider_error="auth failed" if blocked else None,
        input_hash="input",
        score=4.5,
        score_scale="0_to_5",
        threshold=4.0,
        pass_=not blocked,
        decisive_failure=False,
        findings=["ok"],
        cited_sentence_indexes=[1],
        remediation_suggestions=[],
    )


def _ctx(provider_key: str = "openai_chatgpt", *, section_id: str = "executive_summary") -> X1dPanelProviderContext:
    return X1dPanelProviderContext(
        provider_key=provider_key,
        api_key="test-key",
        model="model",
        input_hash="input-hash",
        model_source="env",
        model_requested="model",
        section_id=section_id,
    )


def test_panel_adapter_declared_policy_uses_provider_json_lock() -> None:
    openai_policy = AppsRgX1dPanelAdapter(_ctx("openai_chatgpt")).declared_policy(attempt=2)
    gemini_policy = AppsRgX1dPanelAdapter(_ctx("gemini_pro")).declared_policy(attempt=1)

    assert openai_policy.max_output_tokens >= gemini_policy.max_output_tokens
    assert openai_policy.json_output_lock == "json_object"
    assert gemini_policy.json_output_lock == "responseSchema"
    assert gemini_policy.temperature == 0.1


def test_panel_adapter_declared_policy_scales_by_section_profile() -> None:
    low = AppsRgX1dPanelAdapter(_ctx(section_id="competencies")).declared_policy(attempt=1)
    medium = AppsRgX1dPanelAdapter(_ctx(section_id="unify_bullets")).declared_policy(attempt=1)
    high = AppsRgX1dPanelAdapter(_ctx(section_id="executive_summary")).declared_policy(attempt=1)

    assert low.max_output_tokens == 4096
    assert medium.max_output_tokens == 4096
    assert high.max_output_tokens == 8192
    assert low.max_output_tokens <= medium.max_output_tokens <= high.max_output_tokens

    medium_retry = AppsRgX1dPanelAdapter(_ctx(section_id="unify_bullets")).declared_policy(attempt=2)
    high_retry = AppsRgX1dPanelAdapter(_ctx(section_id="executive_summary")).declared_policy(attempt=2)
    assert medium_retry.max_output_tokens == 8192
    assert high_retry.max_output_tokens == 8192
    low_retry = AppsRgX1dPanelAdapter(_ctx(section_id="competencies")).declared_policy(attempt=2)
    assert low_retry.max_output_tokens == 8192


def test_panel_adapter_converts_judge_output_to_panel_outcome(monkeypatch) -> None:
    from apps_rg.runtime.judges import x1d_panel_adapters as adapters

    monkeypatch.setattr(
        adapters,
        "_invoke_judge_with_bounded_retries",
        lambda dispatch, *, provider_key, section_id=None: _judge_output(),
    )
    ctx = _ctx()

    outcome, receipt = AppsRgX1dPanelAdapter(ctx).invoke(_contract(), attempt=1)

    assert ctx.last_judge_output is not None
    assert outcome.provider_key == "openai_chatgpt"
    assert outcome.pass_ is True
    assert outcome.raw_body["judge_output"]["pass"] is True
    assert receipt.contract_hash == _contract().contract_hash()
    assert receipt.parse_status == "ok"


def test_panel_adapter_blocks_hard_provider_failures(monkeypatch) -> None:
    from apps_rg.runtime.judges import x1d_panel_adapters as adapters

    monkeypatch.setattr(
        adapters,
        "_invoke_judge_with_bounded_retries",
        lambda dispatch, *, provider_key, section_id=None: _judge_output(blocked=True),
    )

    with pytest.raises(AdapterInvokeError, match="auth failed"):
        AppsRgX1dPanelAdapter(_ctx()).invoke(_contract(), attempt=1)


def test_build_panel_adapter_validates_provider_key() -> None:
    assert build_panel_adapter(_ctx("openai_chatgpt")).provider_key == "openai_chatgpt"
    with pytest.raises(KeyError, match="unknown provider key"):
        build_panel_adapter(_ctx("missing_provider"))
