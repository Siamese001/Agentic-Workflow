"""Unit tests for apps_lic LIC X1D LLM judge packet, guards, and scoring."""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import pytest

from apps_lic.engines.judges.lic_x1d_llm_judge import (
    JUDGE_RUBRIC_VERSION,
    LicX1DJudgeOutput,
    build_lic_x1d_judge_packet,
    render_lic_x1d_judge_prompt,
    run_lic_x1d_llm_judge,
)
from apps_lic.policy.reasoning_intensity import (
    JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
    default_reasoning_policy,
)

pytestmark = pytest.mark.unit

_GOOD_MESSAGE = (
    "Hi Scott, AIG's Agentic AI role reads like an operating-model rewrite "
    "across underwriting and claims. I have built governed agent workflows "
    "with evals and telemetry baked in. Worth a brief call?"
)
_GENERIC_MESSAGE = "Hi Scott, I noticed your role and see potential synergies."


def _base_kwargs(
    *,
    message_text: str = _GOOD_MESSAGE,
    x2_gates_passed: bool = True,
    support_status: str = "PASS",
    validation_passed: bool = True,
    issues: list[str] | None = None,
) -> dict[str, Any]:
    policy = default_reasoning_policy()
    x2_gate_summary = {
        "deterministic_schema_policy_no_send_judge": {
            "score": 1.0,
            "threshold": 0.8,
            "pass": True,
            "evidence_refs": ["schema_policy_no_send_clean"],
            "authority": "x2_deterministic_gate",
        },
        "linkedin_tone_channel_quality_judge": {
            "score": 0.9,
            "threshold": 0.65,
            "pass": True,
            "evidence_refs": ["linkedin_tone_channel_clean"],
            "authority": "x2_deterministic_gate",
        },
    }
    return {
        "draft": {
            "message_text": message_text,
            "channel": "linkedin",
            "recipient_class": "executive",
            "target_contact_name": "Scott Hallworth",
            "target_contact_title": "EVP and Chief Digital Officer",
            "target_contact_company": "AIG",
            "unsupported_claims": [],
            "candidate_count": 1,
        },
        "report": {
            "passed": validation_passed,
            "issues": issues or [],
        },
        "evidence": {"count": 4, "support_status": support_status},
        "policy": policy,
        "x2_gate_summary": x2_gate_summary,
        "x2_gates_passed": x2_gates_passed,
    }


def test_build_packet_uses_body_fallback_and_counts_sentences() -> None:
    packet = build_lic_x1d_judge_packet(
        draft={
            "body": "First sentence. Second sentence!",
            "channel": "linkedin",
            "recipient_category": "executive",
        },
        report={"issues": ["tone_warning"]},
        evidence={"support_status": "PASS", "count": 2},
        policy=default_reasoning_policy(),
        x2_gate_summary={"gate_a": {"pass": True}},
        x2_gates_passed=True,
    )

    assert packet["judge_packet_version"] == "lic_x1d_message_quality_packet_v1"
    assert packet["judge_task"] == "GRADE_ONLY"
    assert packet["channel"] == "linkedin"
    assert packet["candidate_output"]["message_text"] == "First sentence. Second sentence!"
    assert packet["candidate_output"]["sentence_count"] == 2
    assert packet["target_contact"]["recipient_class"] == "executive"
    assert packet["x2_gates_passed"] is True
    assert packet["validation_issues"] == ["tone_warning"]
    assert packet["rubric_ref"].endswith("LIC_X1D_RUBRIC")


def test_render_prompt_embeds_sorted_packet_json() -> None:
    packet = build_lic_x1d_judge_packet(**_base_kwargs())
    prompt = render_lic_x1d_judge_prompt(packet)

    assert "LIC_X1D_RUBRIC" in prompt
    assert "JUDGE_PACKET:" in prompt
    assert json.dumps(packet, sort_keys=True, separators=(",", ":")) in prompt


def test_run_skips_when_x2_gates_fail() -> None:
    output = run_lic_x1d_llm_judge(**_base_kwargs(x2_gates_passed=False))

    assert output.provider_status == "SKIPPED_X2_FAILED"
    assert output.evaluator_mode == "SKIPPED_X2_FAILED"
    assert output.pass_ is False
    assert output.score is None
    assert output.packet_hash


@pytest.mark.parametrize("support_status", ["WEAK", "EMPTY"])
def test_run_skips_when_c0_evidence_weak_or_empty(support_status: str) -> None:
    output = run_lic_x1d_llm_judge(**_base_kwargs(support_status=support_status))

    assert output.provider_status == "SKIPPED_C0_EVIDENCE_WEAK"
    assert output.evaluator_mode == "SKIPPED_C0_EVIDENCE_WEAK"
    assert output.pass_ is False
    assert "weak or empty" in (output.exact_provider_error or "").lower()


def test_run_test_stub_passes_specific_quality_message(monkeypatch) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_X1D_JUDGE_STUB", "1")
    output = run_lic_x1d_llm_judge(**_base_kwargs())

    assert output.evaluator_mode == "TEST_STUB"
    assert output.provider_status == "TEST_STUB_PASS"
    assert output.pass_ is True
    assert output.score is not None
    assert output.score >= 4.0
    assert output.normalized_score == pytest.approx(output.score / 5.0, rel=1e-3)
    assert output.rubric_version == JUDGE_RUBRIC_VERSION


def test_run_test_stub_fails_generic_message(monkeypatch) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_X1D_JUDGE_STUB", "1")
    output = run_lic_x1d_llm_judge(**_base_kwargs(message_text=_GENERIC_MESSAGE))

    assert output.provider_status == "TEST_STUB_FAIL"
    assert output.pass_ is False
    assert "generic_phrase_detected" in output.findings


def test_to_dict_maps_pass_field() -> None:
    output = LicX1DJudgeOutput(
        judge_id=JUDGE_LINKEDIN_ORIGINALITY_THOUGHTFULNESS_X1D,
        evaluator_mode="TEST_STUB",
        provider_status="TEST_STUB_PASS",
        provider_profile="qwen_vllm_x1d",
        model_name="test-model",
        provider_available=True,
        provider_blocked=False,
        score=4.5,
        score_scale="0_to_5",
        normalized_score=0.9,
        threshold=4.0,
        normalized_threshold=0.8,
        pass_=True,
        decisive_failure=False,
    )

    data = output.to_dict()

    assert data["pass"] is True
    assert "pass_" not in data


def test_run_blocks_network_under_pytest_without_stub() -> None:
    output = run_lic_x1d_llm_judge(**_base_kwargs())

    assert output.provider_status == "NETWORK_TESTS_NOT_ENABLED"
    assert output.evaluator_mode == "BLOCKED_PROVIDER_UNAVAILABLE"
    assert output.pass_ is False


def test_run_model_backed_pass_with_mocked_provider(monkeypatch) -> None:
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setenv("APPS_LIC_X1D_JUDGE_HEALTHCHECK_ENABLED", "0")

    payload = {
        "score_scale": "0_to_5",
        "score": 4.6,
        "threshold": 4.0,
        "pass": True,
        "decisive_failure": False,
        "findings": ["specific_and_thoughtful"],
        "quality_flags": [],
        "cited_message_spans": ["operating-model rewrite"],
        "remediation_suggestions": [],
    }

    fake_client = _fake_openai_client(json.dumps(payload))
    monkeypatch.setitem(
        __import__("sys").modules,
        "apps_lic.integrations.llm_client",
        SimpleNamespace(OpenAI=lambda **kwargs: fake_client),
    )

    output = run_lic_x1d_llm_judge(**_base_kwargs())

    assert output.evaluator_mode == "MODEL_BACKED"
    assert output.provider_status == "MODEL_BACKED_PASS"
    assert output.pass_ is True
    assert output.normalized_score == pytest.approx(4.6 / 5.0, rel=1e-3)
    assert output.findings == ["specific_and_thoughtful"]
    assert output.output_hash


def test_run_model_backed_honors_decisive_failure(monkeypatch) -> None:
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setenv("APPS_LIC_X1D_JUDGE_HEALTHCHECK_ENABLED", "0")

    payload = {
        "score_scale": "0_to_5",
        "score": 4.8,
        "threshold": 4.0,
        "pass": True,
        "decisive_failure": True,
        "findings": ["fabricated_metric"],
    }
    fake_client = _fake_openai_client(json.dumps(payload))
    monkeypatch.setitem(
        __import__("sys").modules,
        "apps_lic.integrations.llm_client",
        SimpleNamespace(OpenAI=lambda **kwargs: fake_client),
    )

    output = run_lic_x1d_llm_judge(**_base_kwargs())

    assert output.provider_status == "MODEL_BACKED_FAIL"
    assert output.decisive_failure is True
    assert output.pass_ is False


def test_run_model_backed_normalizes_zero_to_one_scale(monkeypatch) -> None:
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setenv("APPS_LIC_X1D_JUDGE_HEALTHCHECK_ENABLED", "0")

    payload = {
        "score_scale": "0_to_1",
        "score": 0.82,
        "threshold": 0.8,
        "pass": True,
        "decisive_failure": False,
        "findings": ["passes_on_unit_scale"],
    }
    fake_client = _fake_openai_client(json.dumps(payload))
    monkeypatch.setitem(
        __import__("sys").modules,
        "apps_lic.integrations.llm_client",
        SimpleNamespace(OpenAI=lambda **kwargs: fake_client),
    )

    output = run_lic_x1d_llm_judge(**_base_kwargs())

    assert output.normalized_score == pytest.approx(0.82, rel=1e-3)
    assert output.normalized_threshold == pytest.approx(0.8, rel=1e-3)
    assert output.pass_ is True


@pytest.mark.parametrize(
    "response_text,expected_status",
    [
        ("not json at all", "BLOCKED_RESPONSE_PARSE_ERROR"),
        (
            '{"score_scale":"0_to_7","score":4.0,"threshold":4.0}',
            "BLOCKED_SCHEMA_VALIDATION_ERROR",
        ),
        ('```json\n{"score_scale":"0_to_5","score":"bad","threshold":4.0}\n```', "BLOCKED_SCHEMA_VALIDATION_ERROR"),
    ],
)
def test_run_model_backed_blocks_on_invalid_response(
    monkeypatch,
    response_text: str,
    expected_status: str,
) -> None:
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setenv("APPS_LIC_X1D_JUDGE_HEALTHCHECK_ENABLED", "0")

    fake_client = _fake_openai_client(response_text)
    monkeypatch.setitem(
        __import__("sys").modules,
        "apps_lic.integrations.llm_client",
        SimpleNamespace(OpenAI=lambda **kwargs: fake_client),
    )

    output = run_lic_x1d_llm_judge(**_base_kwargs())

    assert output.provider_status == expected_status
    assert output.pass_ is False


def _fake_openai_client(content: str) -> SimpleNamespace:
    message = SimpleNamespace(content=content)
    choice = SimpleNamespace(message=message)
    response = SimpleNamespace(choices=[choice])
    completions = SimpleNamespace(create=lambda **kwargs: response)
    chat = SimpleNamespace(completions=completions)
    return SimpleNamespace(chat=chat)
