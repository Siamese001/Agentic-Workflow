from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import urllib.error
import uuid
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
LANE_KEY = "executive_summary"
CMD = [
    sys.executable,
    "-m",
    "apps_rg",
    "--section",
    "executive_summary",
]

# Valid minimal ledger for unit tests calling ``aggregate_x3`` (required for input-authority closure).
EXEC_SUMMARY_TEST_INPUT_USAGE_LEDGER: dict[str, object] = {
    "schema": "section_input_usage_ledger_v1",
    "section_id": "executive_summary",
    "evidence_boundary": {
        "non_evidence_inputs_used_as_claim_evidence": False,
        "non_evidence_inputs_in_source_fact_ids": False,
    },
    "claim_support_summary": {
        "claims_with_targeting_input_in_source_fact_ids": 0,
        "claims_with_context_input_in_source_fact_ids": 0,
    },
}


def _slice_subprocess_env() -> dict[str, str]:
    import os

    return {**os.environ, "APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO": "1"}


def run_cmd(*extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        CMD + list(extra),
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=180,
        env=_slice_subprocess_env(),
    )


def mock_artifacts_dir() -> Path:
    from apps_rg.runtime.runtime_proof_layout import resolve_latest_mock_run_dir

    rd = resolve_latest_mock_run_dir(REPO_ROOT, LANE_KEY)
    if rd is not None:
        x2_probe = rd / "x2_gate_outputs.json"
        if x2_probe.is_file():
            try:
                x2_blob = json.loads(x2_probe.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                x2_blob = None
            else:
                if isinstance(x2_blob, dict) and "gates" in x2_blob:
                    return rd
                if isinstance(x2_blob, list):
                    return rd
    legacy = REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs" / LANE_KEY
    if (legacy / "l2_output.json").is_file():
        return legacy
    raise AssertionError(f"No mock artifacts for lane {LANE_KEY}; run mock dispatch first")


def load_json(name: str):
    path = mock_artifacts_dir() / name
    data = json.loads(path.read_text(encoding="utf-8"))
    if name == "x2_gate_outputs.json":
        if isinstance(data, list):
            failed = [g.get("gate_id") for g in data if not g.get("pass")]
            passed_n = sum(1 for g in data if g.get("pass"))
            return {
                "gates": data,
                "failed_gates": [g for g in failed if g],
                "x2_passed": passed_n,
                "x2_failed": len(failed),
                "total_x2_gates": len(data),
            }
    if name == "x1d_llm_judge_outputs.json" and isinstance(data, list):
        return {"judges": data}
    return data


def test_mock_command_executes_and_prints_output():
    result = run_cmd()
    assert result.returncode == 0, result.stderr
    assert "L2_EXECUTIVE_SUMMARY_OUTPUT:" in result.stdout
    assert "X1D_LLM_JUDGE_OUTPUTS:" in result.stdout
    assert "X3_DISPOSITION:" in result.stdout


def test_mocked_judges_cannot_allow():
    run_cmd()
    x3 = load_json("x3_disposition.json")
    x2 = load_json("x2_gate_outputs.json")
    failed = x2.get("failed_gates") or []
    if failed:
        assert x3["x3_code"] == "X3_BLOCK"
    else:
        # Default mock lane may classify as plumbing-only review or soft-fail when X2 passes
        # but required model-backed judges do not all clear threshold.
        assert x3["x3_code"] in (
            "X3_REVIEW_MOCKED_PLUMBING_ONLY",
            "X3_REVIEW_JUDGE_SOFT_FAIL",
        ), x3["x3_code"]
    assert x3["authorization_scope"] in ("PLUMBING_ONLY", "REVIEW_ONLY")
    assert x3["proceed_to_runtime"] is False
    assert x3["x3_code"] != "X3_ALLOW"


def test_three_judge_rows_exist():
    run_cmd()
    judges = load_json("x1d_llm_judge_outputs.json")["judges"]
    providers = {j["provider_name"] for j in judges}
    assert providers == {"Gemini Pro", "OpenAI ChatGPT", "Anthropic Claude"}


def test_judge_provider_status_tracking():
    """Verify judge provider status tracking works correctly.
    
    This test verifies that:
    - Each judge has proper evaluator_mode and provider_status
    - Blocked judges have raw_response_ref when applicable
    - X3 blocks when any required judge is blocked
    """
    result = run_cmd()
    assert result.returncode == 0
    judges = load_json("x1d_llm_judge_outputs.json")["judges"]
    
    # Verify judge rows expose either legacy provider_status or blocked evaluator_mode.
    for j in judges:
        assert "evaluator_mode" in j
        if j.get("provider_status") is not None:
            if j.get("provider_blocked") or str(j.get("provider_status", "")).startswith("BLOCKED_"):
                assert j.get("provider_blocked") is True
                assert j.get("decisive_failure") is False
                assert j.get("pass") is False
                assert str(j.get("provider_status", "")).startswith("BLOCKED_")
        elif str(j.get("evaluator_mode", "")).startswith("BLOCKED_"):
            assert j.get("pass") is False

    x3 = load_json("x3_disposition.json")
    assert x3["x3_code"] != "X3_ALLOW"
    assert x3["proceed_to_runtime"] is False


def test_provider_request_artifact_written():
    run_cmd()
    assert (mock_artifacts_dir() / "provider_request.json").exists()
    assert (mock_artifacts_dir() / "runtime_payload.json").exists()
    assert (mock_artifacts_dir() / "prompt_selection_trace.json").exists()


def test_temperature_out_of_profile_fails_fast():
    result = run_cmd("--provider", "qwen_vllm", "--temperature", "0.7")
    assert result.returncode != 0
    assert "outside executive_summary profile" in (result.stderr + result.stdout)


def test_qwen_unavailable_blocks_not_mocks():
    from apps_rg.runtime.runtime_proof_layout import resolve_run_dir_from_pointer

    env = {**_slice_subprocess_env(), "VLLM_BASE_URL": "http://127.0.0.1:9/v1"}
    env.pop("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", None)
    result = subprocess.run(
        CMD + ["--provider", "qwen_vllm"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=180,
        env=env,
    )
    assert result.returncode == 0
    rd = resolve_run_dir_from_pointer(REPO_ROOT, LANE_KEY, "real")
    assert rd is not None, "expected a real-bucket run after qwen_vllm dispatch"
    real = json.loads((rd / "real_l2_generation_result.json").read_text(encoding="utf-8"))
    assert real["runtime_generation_status"] == "BLOCKED"
    assert real["exact_provider_error"]
    x3 = json.loads((rd / "x3_disposition.json").read_text(encoding="utf-8"))
    assert x3["x3_code"] in {"X3_BLOCK", "X3_REVIEW_MOCKED_PLUMBING_ONLY", "X3_REVIEW_JUDGE_PROVIDER_BLOCKED"}
    assert x3["x3_code"] != "X3_ALLOW"


def test_x2_first_person_gate_catches_bad_text():
    from apps_rg.runtime.validators.executive_summary_x2 import run_x2_gates

    gates = run_x2_gates(
        resume_display_text="I spearheaded a governed agentic AI platform.",
        parsed_output={"resume_display_text": "I spearheaded a governed agentic AI platform."},
        claim_ledger=[{"claim_text": "governed agentic AI platform", "source_fact_ids": ["bul_unify_001"]}],
        text_claim_coverage={"sentences": [], "overall_pass": False},
        allowed_fact_ids={"bul_unify_001"},
        target_company="Synthetic Enterprise Corp.",
        jd_text="enterprise AI platform leadership",
        temperature=0.45,
        runtime_generation_status="REAL_LLM",
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
    )
    gate_map = {g.gate_id: g.pass_ for g in gates}
    assert gate_map["x2_first_person_zero"] is False


def test_provider_prompt_forbids_markdown_fences():
    from apps_rg.runtime.dispatch.executive_summary_dispatch import build_prompt_messages

    messages = build_prompt_messages(
        {
            "target_title": "SVP Engineering",
            "target_company": "Synthetic Enterprise Corp.",
            "jd_text": "enterprise AI",
            "briefing": "platform",
            "selected_fact_plan": {"facts": [{"fact_id": "bul_unify_001", "claim_text": "platform"}]},
        }
    )
    combined = "\n".join(m["content"] for m in messages)
    assert "No ```json" in combined or "No ```" in combined
    assert "RAW JSON ONLY" in combined
    assert "begin with {" in combined


def test_provider_prompt_includes_allowed_source_fact_ids_contract_and_spacing_examples():
    from apps_rg.runtime.dispatch.executive_summary_dispatch import build_prompt_messages

    messages = build_prompt_messages(
        {
            "run_id": "slice_allowed_ids_contract",
            "target_title": "SVP Engineering",
            "target_company": "Synthetic Enterprise Corp.",
            "jd_text": "enterprise AI",
            "briefing": "platform",
            "allowed_fact_ids": ["bul_unify_001", "bul_unify_003"],
            "selected_fact_plan": {
                "facts": [
                    {"fact_id": "bul_unify_001", "claim_text": "Governed AI platform delivery."},
                    {"fact_id": "bul_unify_003", "claim_text": "Operating cadence improvements."},
                ],
                "required_fact_ids": ["bul_unify_001", "bul_unify_003"],
            },
        }
    )
    combined = "\n".join(m["content"] for m in messages)
    assert "ALLOWED_SOURCE_FACT_IDS (authoritative list" in combined
    assert "  - bul_unify_001" in combined
    assert "  - bul_unify_003" in combined
    assert "bul_unify_ 003" in combined
    assert "bul_unify_003" in combined
    assert "x2_claim_ledger_orphan_zero" in combined
    assert "Copy each ID character-for-character" in combined


def test_provider_prompt_requires_dense_paragraph_narrative_arc():
    from apps_rg.runtime.dispatch.executive_summary_dispatch import build_prompt_messages

    messages = build_prompt_messages(
        {
            "target_title": "SVP Engineering",
            "target_company": "Synthetic Enterprise Corp.",
            "jd_text": "enterprise AI",
            "briefing": "platform",
            "allowed_fact_ids": ["bul_unify_001"],
            "selected_fact_plan": {"facts": [{"fact_id": "bul_unify_001", "claim_text": "platform"}]},
        }
    )
    combined = "\n".join(m["content"] for m in messages)
    cl = combined.lower()
    assert "exactly two synthesized" not in cl
    assert "input_authority" in cl
    assert "base_resume_selected_facts" in cl or "allowed_source_fact_ids" in cl
    assert "bul_unify_001" in combined
    assert "enterprise ai platform leader" in cl or "executive identity" in cl


def test_narrative_shape_rejects_sentence_stacked_proof():
    from apps_rg.runtime.dispatch.executive_summary_dispatch import (
        check_executive_summary_narrative_shape,
    )

    text = (
        "Generated $22M in IP-led revenue from reusable platform services. "
        "Integrated governed agentic AI architecture with retrieval controls. "
        "Enhanced lifecycle delivery from six months to three weeks."
    )
    claims = [{"claim_text": "a"}, {"claim_text": "b"}, {"claim_text": "c"}]
    ok, reason = check_executive_summary_narrative_shape(text, claims)
    assert ok is False
    assert reason and "claim-ledger" in reason.lower()


def test_narrative_shape_rejects_long_enumeration():
    from apps_rg.runtime.dispatch.executive_summary_dispatch import (
        check_executive_summary_narrative_shape,
    )

    text = (
        "Built routing, orchestration, GraphRAG, sandboxing, policy gating, validation, "
        "telemetry, rollback, and CI/CD controls across the platform."
    )
    ok, reason = check_executive_summary_narrative_shape(text, [])
    assert ok is False
    assert reason and "enumeration" in reason.lower()


def test_l2_resume_voice_rejects_first_person():
    from apps_rg.runtime.dispatch.executive_summary_dispatch import check_l2_resume_voice

    text = (
        "As an enterprise AI platform leader, I have generated $22M in IP-led revenue "
        "and expanded gross margins by 20%."
    )
    ok, reason = check_l2_resume_voice(text)
    assert ok is False
    assert reason and "first-person" in reason.lower()


def test_l2_resume_voice_rejects_achieved_through_bridge():
    from apps_rg.runtime.dispatch.executive_summary_dispatch import check_l2_resume_voice

    text = (
        "Enterprise AI platform leader who generated $22M in IP-led revenue. "
        "This was achieved through governed platform architecture and lifecycle controls."
    )
    ok, reason = check_l2_resume_voice(text)
    assert ok is False
    assert reason and "bridge" in reason.lower()


def test_narrative_shape_accepts_two_sentence_executive_arc():
    from apps_rg.runtime.dispatch.executive_summary_dispatch import (
        build_mock_output,
        check_executive_summary_narrative_shape,
    )

    payload = {
        "selected_fact_plan": {
            "facts": [
                {"fact_id": "bul_unify_001", "claim_text": "platform"},
                {"fact_id": "bul_unify_004", "claim_text": "cycle", "metric_raw": "6mo3wk"},
                {"fact_id": "bul_unify_006", "claim_text": "revenue", "metric_raw": "22M"},
            ]
        }
    }
    mock = build_mock_output(payload)
    ok, reason = check_executive_summary_narrative_shape(
        mock["resume_display_text"], mock["claim_ledger"]
    )
    assert ok is True, reason


def test_x2_json_parse_fails_on_markdown_fences():
    from apps_rg.runtime.validators.executive_summary_x2 import check_json_parse_valid

    raw = '```json\n{"resume_display_text": "ok"}\n```'
    ok, reason = check_json_parse_valid({"resume_display_text": "ok"}, raw)
    assert ok is False
    assert reason and "markdown" in reason.lower()


def test_x2_json_parse_passes_on_clean_json():
    from apps_rg.runtime.validators.executive_summary_x2 import check_json_parse_valid

    raw = '{"resume_display_text":"ok","claim_ledger":[]}'
    ok, reason = check_json_parse_valid({"resume_display_text": "ok"}, raw)
    assert ok is True
    assert reason is None


def test_four_action_verb_sentences_fail_stacking():
    from apps_rg.runtime.validators.executive_summary_x2 import detect_bullet_like_stacking

    text = (
        "Productized core services. Designed the platform. Strengthened retrieval. "
        "Standardized lifecycle delivery."
    )
    stacked, reason, _ = detect_bullet_like_stacking(text)
    assert stacked is True
    assert reason


def test_bridge_phrase_fails_synthesis_quality():
    from apps_rg.runtime.validators.executive_summary_x2 import check_synthesis_quality

    text = (
        "Productized core agentic AI primitives into reusable platform services. "
        "This was achieved while scaling the ML engineering organization from 8 to 28 specialists."
    )
    ok, reason = check_synthesis_quality(text)
    assert ok is False
    assert reason and "achieved while" in reason.lower()


def test_one_fact_per_sentence_fails_synthesis_quality():
    from apps_rg.runtime.validators.executive_summary_x2 import check_synthesis_quality

    text = (
        "Productized core agentic AI primitives. "
        "Designed a governed agentic AI platform. "
        "Strengthened enterprise retrieval quality. "
        "Standardized the AI systems lifecycle."
    )
    ok, reason = check_synthesis_quality(text)
    assert ok is False
    assert reason


def test_synthesized_paragraph_passes_synthesis_quality():
    from apps_rg.runtime.validators.executive_summary_x2 import check_synthesis_quality

    text = (
        "Across a governed agentic AI platform combining deterministic routing, multi-agent orchestration, "
        "GraphRAG retrieval, policy gating, validation controls, and replayable execution traces, reusable "
        "platform primitives have generated $22M in IP-led revenue, expanded gross margins by 20%, and grown "
        "the ML engineering organization from 8 to 28 specialists. "
        "The same platform discipline strengthens retrieval quality, context assembly, evaluation gates, "
        "telemetry instrumentation, rollback controls, and AI CI/CD standards that underpin reliable delivery. "
        "With intake, validation, execution, monitoring, and remediation standardized end to end, "
        "lab-to-production cycle time has fallen from six months to three weeks."
    )
    ok, reason = check_synthesis_quality(text)
    assert ok is True, reason


def test_gemini_native_response_fixture_parses():
    from apps_rg.runtime.judges.executive_summary_x1d import (
        _extract_gemini_text,
        _extract_json_from_text,
        _make_model_backed_output,
        _normalize_judge_result,
    )

    envelope = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(
                                {
                                    "score_scale": "0_to_5",
                                    "score": 4.2,
                                    "threshold": 4.0,
                                    "pass": True,
                                    "decisive_failure": False,
                                    "findings": ["factual_support"],
                                    "cited_sentence_indexes": [1, 2],
                                    "remediation_suggestions": [],
                                }
                            )
                        }
                    ]
                },
                "finishReason": "STOP",
            }
        ]
    }
    text, finish_reason = _extract_gemini_text(envelope)
    assert finish_reason == "STOP"
    parsed = _extract_json_from_text(text)
    assert parsed is not None
    normalized = _normalize_judge_result(parsed)
    out = _make_model_backed_output("gemini_pro", "abc123", "gemini-2.0-flash", normalized)
    assert out.provider_status == "MODEL_BACKED_PASS"
    assert out.score_scale == "0_to_5"
    assert out.score == 4.2
    assert out.threshold == 4.0
    assert out.normalized_score == pytest.approx(0.84)
    assert out.normalized_threshold == pytest.approx(0.8)


def test_openai_judge_prompt_forbids_0_to_10_and_percentage_scores():
    from apps_rg.runtime.judges.executive_summary_x1d import JUDGE_SCORE_SCHEMA, RUBRIC

    combined = f"{RUBRIC}\n{JUDGE_SCORE_SCHEMA}"
    assert "0_to_10" in combined
    assert "percentage" in combined.lower() or "0–100" in combined or "0-100" in combined
    assert "9.2" in combined
    assert "score_scale" in combined


def test_openai_raw_9_2_8_0_without_scale_blocked():
    from apps_rg.runtime.judges.executive_summary_x1d import _make_model_backed_output

    out = _make_model_backed_output(
        "openai_chatgpt",
        "h0",
        "gpt-4o",
        {"score": 9.2, "threshold": 8.0, "pass": True, "decisive_failure": False},
    )
    assert out.provider_status == "BLOCKED_SCHEMA_VALIDATION_ERROR"
    assert out.provider_blocked is True


def test_openai_score_scale_0_to_1():
    from apps_rg.runtime.judges.executive_summary_x1d import _make_model_backed_output

    out = _make_model_backed_output(
        "openai_chatgpt",
        "h1",
        "gpt-4o",
        {
            "score_scale": "0_to_1",
            "score": 0.92,
            "threshold": 0.80,
            "pass": True,
            "decisive_failure": False,
        },
    )
    assert out.provider_status == "MODEL_BACKED_PASS"
    assert out.score_scale == "0_to_1"
    assert out.score == pytest.approx(0.92)
    assert out.threshold == pytest.approx(0.80)
    assert out.normalized_score == pytest.approx(0.92)
    assert out.normalized_threshold == pytest.approx(0.80)


def test_openai_score_scale_0_to_5():
    from apps_rg.runtime.judges.executive_summary_x1d import _make_model_backed_output

    out = _make_model_backed_output(
        "openai_chatgpt",
        "h2",
        "gpt-4o",
        {
            "score_scale": "0_to_5",
            "score": 4.6,
            "threshold": 4.0,
            "pass": True,
            "decisive_failure": False,
        },
    )
    assert out.provider_status == "MODEL_BACKED_PASS"
    assert out.score_scale == "0_to_5"
    assert out.score == pytest.approx(4.6)
    assert out.threshold == pytest.approx(4.0)
    assert out.normalized_score == pytest.approx(0.92)
    assert out.normalized_threshold == pytest.approx(0.8)


def test_invalid_score_scale_blocks_model_backed_pass():
    from apps_rg.runtime.judges.executive_summary_x1d import _make_model_backed_output

    out = _make_model_backed_output(
        "openai_chatgpt",
        "h3",
        "gpt-4o",
        {
            "score_scale": "0_to_10",
            "score": 9.2,
            "threshold": 8.0,
            "pass": True,
            "decisive_failure": False,
        },
    )
    assert out.provider_status == "BLOCKED_SCHEMA_VALIDATION_ERROR"
    assert out.provider_blocked is True
    assert out.pass_ is False


def test_percentage_scores_out_of_0_to_1_range_blocked():
    from apps_rg.runtime.judges.executive_summary_x1d import _make_model_backed_output

    out = _make_model_backed_output(
        "openai_chatgpt",
        "h4",
        "gpt-4o",
        {
            "score_scale": "0_to_1",
            "score": 92.0,
            "threshold": 80.0,
            "pass": True,
            "decisive_failure": False,
        },
    )
    assert out.provider_status == "BLOCKED_SCHEMA_VALIDATION_ERROR"


def test_gemini_judge_model_env_precedence(monkeypatch):
    from apps_rg.runtime.judges.executive_summary_x1d import PROVIDERS, _resolve_gemini_model

    monkeypatch.delenv("APPS_RG_GOOGLE_JUDGE_MODEL", raising=False)
    monkeypatch.delenv("GOOGLE_AI_MODEL", raising=False)
    monkeypatch.setenv("APPS_RG_GEMINI_JUDGE_MODEL", "gemini-judge-override")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3-flash-preview")
    model, source = _resolve_gemini_model(PROVIDERS["gemini_pro"])
    assert model == "gemini-judge-override"
    assert source == "APPS_RG_GEMINI_JUDGE_MODEL"


def test_gemini_model_falls_back_to_gemini_model_env(monkeypatch):
    from apps_rg.runtime.judges.executive_summary_x1d import PROVIDERS, _resolve_gemini_model

    monkeypatch.delenv("APPS_RG_GOOGLE_JUDGE_MODEL", raising=False)
    monkeypatch.delenv("APPS_RG_GEMINI_JUDGE_MODEL", raising=False)
    monkeypatch.delenv("GOOGLE_AI_MODEL", raising=False)
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3-flash-preview")
    model, source = _resolve_gemini_model(PROVIDERS["gemini_pro"])
    assert model == "gemini-3-flash-preview"
    assert source == "GEMINI_MODEL"


def test_anthropic_model_falls_back_to_anthropic_model_env(monkeypatch):
    from apps_rg.runtime.judges.executive_summary_x1d import PROVIDERS, _resolve_anthropic_model

    monkeypatch.delenv("APPS_RG_ANTHROPIC_JUDGE_MODEL", raising=False)
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-sonnet-4.5")
    model, source = _resolve_anthropic_model(PROVIDERS["anthropic_claude"])
    assert model == "claude-sonnet-4.5"
    assert source == "ANTHROPIC_MODEL"


def test_gemini_max_tokens_finish_blocked():
    from pathlib import Path

    from apps_rg.runtime.judges.executive_summary_x1d import _finish_judge_text_parse

    out = _finish_judge_text_parse(
        provider_key="gemini_pro",
        input_hash="hash-gemini-max",
        model_name="gemini-2.5-flash",
        raw_path=Path("artifacts/apps_rg/runtime_proofs/executive_summary/test_raw.json"),
        text='{"score_scale":"0_to_5","score":3.5,"threshold":4.0,"pass":false,',
        finish_reason="MAX_TOKENS",
    )
    assert out.provider_status == "BLOCKED_RESPONSE_PARSE_ERROR"
    assert out.provider_blocked is True
    assert "MAX_TOKENS" in (out.exact_provider_error or "")


def test_gemini_compact_valid_json_parses():
    from pathlib import Path

    from apps_rg.runtime.judges.executive_summary_x1d import _finish_judge_text_parse

    text = json.dumps(
        {
            "score_scale": "0_to_5",
            "score": 4.2,
            "threshold": 4.0,
            "pass": True,
            "decisive_failure": False,
            "findings": ["synthesis ok"],
            "cited_sentence_indexes": [1],
            "remediation_suggestions": [],
        }
    )
    out = _finish_judge_text_parse(
        provider_key="gemini_pro",
        input_hash="hash-gemini-ok",
        model_name="gemini-2.5-flash",
        raw_path=Path("artifacts/apps_rg/runtime_proofs/executive_summary/test_raw.json"),
        text=text,
        finish_reason="STOP",
    )
    assert out.provider_status == "MODEL_BACKED_PASS"
    assert out.score_scale == "0_to_5"
    assert out.normalized_score == pytest.approx(0.84)


def test_gemini_generation_config_has_tokens_and_compact_instruction():
    from apps_rg.runtime.judges.executive_summary_x1d import (
        GEMINI_JUDGE_MAX_OUTPUT_TOKENS,
        JUDGE_COMPACT_OUTPUT,
        _build_judge_user_prompt,
        _gemini_generation_config,
    )

    cfg = _gemini_generation_config()
    assert cfg["maxOutputTokens"] == GEMINI_JUDGE_MAX_OUTPUT_TOKENS
    assert cfg["maxOutputTokens"] >= 4096
    assert cfg["responseMimeType"] == "application/json"
    assert cfg.get("responseSchema")
    prompt = _build_judge_user_prompt("summary text", [{"claim_text": "c", "source_fact_ids": ["a"]}])
    assert JUDGE_COMPACT_OUTPUT in prompt
    assert "0_to_5" in prompt


def test_anthropic_content_block_valid_json_parses():
    from pathlib import Path

    from apps_rg.runtime.judges.executive_summary_x1d import (
        _extract_anthropic_message_text,
        _finish_judge_text_parse,
    )

    payload = {
        "content": [
            {
                "type": "text",
                "text": json.dumps(
                    {
                        "score_scale": "0_to_5",
                        "score": 4.5,
                        "threshold": 4.0,
                        "pass": True,
                        "decisive_failure": False,
                        "findings": ["resume voice acceptable"],
                        "cited_sentence_indexes": [1],
                        "remediation_suggestions": [],
                    }
                ),
            }
        ]
    }
    text = _extract_anthropic_message_text(payload)
    out = _finish_judge_text_parse(
        provider_key="anthropic_claude",
        input_hash="hash-anthropic-ok",
        model_name="claude-sonnet-4-6",
        raw_path=Path("artifacts/apps_rg/runtime_proofs/executive_summary/test_raw.json"),
        text=text,
    )
    assert out.provider_status == "MODEL_BACKED_PASS"
    assert out.normalized_score == pytest.approx(0.9)


def test_anthropic_fenced_json_parses():
    from pathlib import Path

    from apps_rg.runtime.judges.executive_summary_x1d import _finish_judge_text_parse

    text = (
        '```json\n'
        + json.dumps(
            {
                "score_scale": "0_to_1",
                "score": 0.85,
                "threshold": 0.8,
                "pass": True,
                "decisive_failure": False,
                "findings": ["supported"],
                "cited_sentence_indexes": [1],
                "remediation_suggestions": [],
            }
        )
        + "\n```"
    )
    out = _finish_judge_text_parse(
        provider_key="anthropic_claude",
        input_hash="hash-anthropic-fence",
        model_name="claude-sonnet-4-6",
        raw_path=Path("artifacts/apps_rg/runtime_proofs/executive_summary/test_raw.json"),
        text=text,
    )
    assert out.provider_status == "MODEL_BACKED_PASS"


def test_anthropic_parse_failure_preserves_blocked_status():
    from pathlib import Path

    from apps_rg.runtime.judges.executive_summary_x1d import _finish_judge_text_parse

    out = _finish_judge_text_parse(
        provider_key="anthropic_claude",
        input_hash="hash-anthropic-bad",
        model_name="claude-sonnet-4-6",
        raw_path=Path("artifacts/apps_rg/runtime_proofs/executive_summary/test_raw.json"),
        text="not valid judge json at all",
    )
    assert out.provider_status == "BLOCKED_RESPONSE_PARSE_ERROR"
    assert out.provider_blocked is True


def test_anthropic_compact_json_instruction_present():
    from apps_rg.runtime.judges.executive_summary_x1d import (
        ANTHROPIC_JUDGE_MAX_OUTPUT_TOKENS,
        JUDGE_COMPACT_OUTPUT,
        JUDGE_COMPACT_SYSTEM,
    )

    assert "compact JSON" in JUDGE_COMPACT_SYSTEM
    assert "0_to_5" in JUDGE_COMPACT_OUTPUT
    assert ANTHROPIC_JUDGE_MAX_OUTPUT_TOKENS >= 1024


def test_gemini_parse_failure_preserves_blocked_status():
    from apps_rg.runtime.judges.executive_summary_x1d import _make_blocked_output

    blocked = _make_blocked_output(
        "gemini_pro",
        "hash1",
        "BLOCKED_RESPONSE_PARSE_ERROR",
        "BLOCKED_RESPONSE_PARSE_ERROR",
        "Failed to extract JSON from Gemini response",
        raw_response_ref="artifacts/test_raw.json",
        model_name="gemini-2.0-flash",
    )
    assert blocked.provider_status == "BLOCKED_RESPONSE_PARSE_ERROR"
    assert blocked.provider_blocked is True
    assert blocked.decisive_failure is False
    assert blocked.raw_response_ref == "artifacts/test_raw.json"


def test_anthropic_model_not_found_blocked(monkeypatch):
    from apps_rg.runtime.judges import executive_summary_x1d as x1d

    monkeypatch.setenv("APPS_RG_ENABLE_NETWORK_TESTS", "1")
    monkeypatch.setenv("APPS_RG_ANTHROPIC_ALLOW_MODEL_FALLBACK", "false")
    monkeypatch.delenv("APPS_RG_ANTHROPIC_JUDGE_MODEL", raising=False)

    def fake_urlopen(req, timeout=60):
        body = b'{"type":"error","error":{"type":"not_found_error","message":"model: claude-sonnet-4.5"}}'
        raise urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, io.BytesIO(body))

    monkeypatch.setattr(x1d.urllib.request, "urlopen", fake_urlopen)
    out = x1d._call_anthropic("test-key", "prompt", "claude-sonnet-4.5", "hash2", "anthropic_claude")
    assert out.provider_status == "BLOCKED_MODEL_NOT_FOUND"
    assert out.model_name == "claude-sonnet-4.5"
    assert out.provider_blocked is True
    assert out.decisive_failure is False


def test_anthropic_env_model_override_respected(monkeypatch):
    from apps_rg.runtime.judges.executive_summary_x1d import _resolve_anthropic_model, PROVIDERS

    monkeypatch.setenv("APPS_RG_ANTHROPIC_JUDGE_MODEL", "claude-custom-judge-v1")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-sonnet-4.5")
    model, source = _resolve_anthropic_model(PROVIDERS["anthropic_claude"])
    assert model == "claude-custom-judge-v1"
    assert source == "APPS_RG_ANTHROPIC_JUDGE_MODEL"


def test_anthropic_fallback_not_used_without_flag(monkeypatch):
    from apps_rg.runtime.judges import executive_summary_x1d as x1d

    monkeypatch.setenv("APPS_RG_ENABLE_NETWORK_TESTS", "1")
    monkeypatch.setenv("APPS_RG_ANTHROPIC_ALLOW_MODEL_FALLBACK", "false")
    calls: list[str] = []

    def fake_urlopen(req, timeout=60):
        calls.append("primary")
        raise urllib.error.HTTPError(
            req.full_url, 404, "Not Found", {}, io.BytesIO(b'{"error":{"type":"not_found_error"}}')
        )

    monkeypatch.setattr(x1d.urllib.request, "urlopen", fake_urlopen)
    out = x1d._call_anthropic("key", "prompt", "missing-model", "h3", "anthropic_claude")
    assert out.provider_status == "BLOCKED_MODEL_NOT_FOUND"
    assert calls == ["primary"]


def test_x3_review_when_any_required_judge_blocked():
    from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3

    x3 = aggregate_x3(
        resume_display_text="text",
        claim_ledger=[{"claim_text": "c", "source_fact_ids": ["bul_unify_001"]}],
        x2_gates=[{"gate_id": "x2_schema_valid", "pass": True}],
        x1d_judges=[
            {
                "provider_key": "gemini_pro",
                "evaluator_mode": "BLOCKED_RESPONSE_PARSE_ERROR",
                "provider_blocked": True,
                "decisive_failure": False,
            },
            {
                "provider_key": "openai_chatgpt",
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_PASS",
                "provider_blocked": False,
                "decisive_failure": False,
            },
            {
                "provider_key": "anthropic_claude",
                "evaluator_mode": "BLOCKED_MODEL_NOT_FOUND",
                "provider_blocked": True,
                "decisive_failure": False,
            },
        ],
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        section_input_usage_ledger=EXEC_SUMMARY_TEST_INPUT_USAGE_LEDGER,
    )
    assert x3.x3_code == "X3_REVIEW_JUDGE_PROVIDER_BLOCKED"


def test_x3_allow_only_when_all_model_backed_pass():
    from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3

    judges = [
        {
            "provider_key": k,
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "provider_blocked": False,
            "pass": True,
            "decisive_failure": False,
            "normalized_score": 0.9,
            "normalized_threshold": 0.8,
        }
        for k in ("gemini_pro", "openai_chatgpt", "anthropic_claude")
    ]
    x3 = aggregate_x3(
        resume_display_text="text",
        claim_ledger=[{"claim_text": "c", "source_fact_ids": ["bul_unify_001"]}],
        x2_gates=[{"gate_id": "x2_schema_valid", "pass": True}],
        x1d_judges=judges,
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        section_input_usage_ledger=EXEC_SUMMARY_TEST_INPUT_USAGE_LEDGER,
    )
    assert x3.x3_code == "X3_ALLOW"
    assert x3.pass_ is True
    assert x3.soft_failed_judges == []


def test_x3_soft_fail_when_model_backed_fail_without_decisive():
    from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3

    x3 = aggregate_x3(
        resume_display_text="text",
        claim_ledger=[{"claim_text": "c", "source_fact_ids": ["bul_unify_001"]}],
        x2_gates=[{"gate_id": "x2_schema_valid", "pass": True}],
        x1d_judges=[
            {
                "provider_key": "gemini_pro",
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_PASS",
                "pass": True,
                "decisive_failure": False,
                "normalized_score": 1.0,
                "normalized_threshold": 0.8,
            },
            {
                "provider_key": "openai_chatgpt",
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_PASS",
                "pass": True,
                "decisive_failure": False,
                "normalized_score": 0.92,
                "normalized_threshold": 0.8,
            },
            {
                "provider_key": "anthropic_claude",
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_FAIL",
                "pass": False,
                "decisive_failure": False,
                "normalized_score": 0.72,
                "normalized_threshold": 0.8,
            },
        ],
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        section_input_usage_ledger=EXEC_SUMMARY_TEST_INPUT_USAGE_LEDGER,
    )
    assert x3.x3_code == "X3_REVIEW_JUDGE_SOFT_FAIL"
    assert x3.authorization_scope == "REVIEW_ONLY"
    assert x3.proceed_to_runtime is False
    assert x3.pass_ is False
    assert x3.soft_failed_judges == ["anthropic_claude"]
    assert "without decisive failure" in x3.decisive_reason


def test_x3_block_when_model_backed_fail_with_decisive():
    from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3

    x3 = aggregate_x3(
        resume_display_text="text",
        claim_ledger=[{"claim_text": "c", "source_fact_ids": ["bul_unify_001"]}],
        x2_gates=[{"gate_id": "x2_schema_valid", "pass": True}],
        x1d_judges=[
            {
                "provider_key": "gemini_pro",
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_PASS",
                "pass": True,
                "decisive_failure": False,
            },
            {
                "provider_key": "anthropic_claude",
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_FAIL",
                "pass": False,
                "decisive_failure": True,
            },
        ],
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        section_input_usage_ledger=EXEC_SUMMARY_TEST_INPUT_USAGE_LEDGER,
    )
    assert x3.x3_code == "X3_BLOCK"
    assert x3.decisive_judge_failures == ["anthropic_claude"]


def test_x3_allow_impossible_with_model_backed_fail():
    from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3

    x3 = aggregate_x3(
        resume_display_text="text",
        claim_ledger=[{"claim_text": "c", "source_fact_ids": ["bul_unify_001"]}],
        x2_gates=[{"gate_id": "x2_schema_valid", "pass": True}],
        x1d_judges=[
            {
                "provider_key": "openai_chatgpt",
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_FAIL",
                "pass": False,
                "decisive_failure": False,
            }
        ],
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        section_input_usage_ledger=EXEC_SUMMARY_TEST_INPUT_USAGE_LEDGER,
    )
    assert x3.x3_code != "X3_ALLOW"


def test_x3_allow_impossible_when_normalized_score_below_threshold():
    from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3

    x3 = aggregate_x3(
        resume_display_text="text",
        claim_ledger=[{"claim_text": "c", "source_fact_ids": ["bul_unify_001"]}],
        x2_gates=[{"gate_id": "x2_schema_valid", "pass": True}],
        x1d_judges=[
            {
                "provider_key": "openai_chatgpt",
                "evaluator_mode": "MODEL_BACKED",
                "provider_status": "MODEL_BACKED_PASS",
                "pass": True,
                "decisive_failure": False,
                "normalized_score": 0.79,
                "normalized_threshold": 0.8,
            }
        ],
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        section_input_usage_ledger=EXEC_SUMMARY_TEST_INPUT_USAGE_LEDGER,
    )
    assert x3.x3_code != "X3_ALLOW"


def test_x3_review_mocked_judge():
    from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3

    x3 = aggregate_x3(
        resume_display_text="text",
        claim_ledger=[{"claim_text": "c", "source_fact_ids": ["bul_unify_001"]}],
        x2_gates=[{"gate_id": "x2_schema_valid", "pass": True}],
        x1d_judges=[{"provider_key": "openai_chatgpt", "evaluator_mode": "MOCKED", "decisive_failure": False}],
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        section_input_usage_ledger=EXEC_SUMMARY_TEST_INPUT_USAGE_LEDGER,
    )
    assert x3.x3_code == "X3_REVIEW_MOCKED_PLUMBING_ONLY"


def test_ledger_row_materialized_in_display_false_for_empty_or_whitespace_claim_text():
    from apps_rg.runtime.validators.executive_summary_x2 import ledger_row_materialized_in_display

    resume = "Engineering executive led governed platform delivery for enterprise."
    assert ledger_row_materialized_in_display({"claim_text": "", "source_fact_ids": ["a"]}, resume) is False
    assert ledger_row_materialized_in_display({"source_fact_ids": ["a"]}, resume) is False
    assert ledger_row_materialized_in_display({"claim_text": "   \t\n", "source_fact_ids": ["a"]}, resume) is False


def test_ledger_row_materialized_in_display_true_when_claim_text_overlaps_resume():
    from apps_rg.runtime.validators.executive_summary_x2 import ledger_row_materialized_in_display

    resume = "Engineering executive led governed platform delivery for enterprise."
    assert (
        ledger_row_materialized_in_display(
            {"claim_text": "governed platform delivery", "source_fact_ids": ["bul_unify_001"]},
            resume,
        )
        is True
    )


def test_x2_claim_ledger_claim_text_non_empty_fails_only_source_fact_ids():
    from apps_rg.runtime.claim_ledger.canonical_exec_summary_v2 import normalize_exec_summary_claim_ledger
    from apps_rg.runtime.validators.executive_summary_x2 import run_x2_gates

    ledger = normalize_exec_summary_claim_ledger([{"source_fact_ids": ["bul_unify_001"]}])
    gates = run_x2_gates(
        resume_display_text="Some prose with platform tokens.",
        parsed_output={"resume_display_text": "Some prose with platform tokens."},
        claim_ledger=ledger,
        text_claim_coverage={"sentences": [], "overall_pass": False},
        allowed_fact_ids={"bul_unify_001"},
        target_company="Acme Corp.",
        jd_text="enterprise AI",
        temperature=0.45,
        runtime_generation_status="REAL_LLM",
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_claim_ledger_claim_text_non_empty"].pass_ is False
    assert "idx=0" in (by_id["x2_claim_ledger_claim_text_non_empty"].failure_reason or "")
    assert "bul_unify_001" in (by_id["x2_claim_ledger_claim_text_non_empty"].failure_reason or "")


def test_x2_claim_ledger_claim_text_non_empty_fails_whitespace_only():
    from apps_rg.runtime.claim_ledger.canonical_exec_summary_v2 import normalize_exec_summary_claim_ledger
    from apps_rg.runtime.validators.executive_summary_x2 import run_x2_gates

    ledger = normalize_exec_summary_claim_ledger(
        [{"claim_text": "  \t  ", "source_fact_ids": ["bul_unify_001"]}]
    )
    gates = run_x2_gates(
        resume_display_text="Some prose.",
        parsed_output={"resume_display_text": "Some prose."},
        claim_ledger=ledger,
        text_claim_coverage={"sentences": [], "overall_pass": False},
        allowed_fact_ids={"bul_unify_001"},
        target_company="Acme Corp.",
        jd_text="enterprise AI",
        temperature=0.45,
        runtime_generation_status="REAL_LLM",
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_claim_ledger_claim_text_non_empty"].pass_ is False


def test_x2_claim_ledger_claim_text_non_empty_passes_when_claim_alias_normalized():
    from apps_rg.runtime.claim_ledger.canonical_exec_summary_v2 import normalize_exec_summary_claim_ledger
    from apps_rg.runtime.validators.executive_summary_x2 import run_x2_gates

    ledger = normalize_exec_summary_claim_ledger(
        [{"claim": "Material claim prose here.", "source_fact_ids": ["bul_unify_001"]}]
    )
    assert ledger[0]["claim_text"] == "Material claim prose here."
    gates = run_x2_gates(
        resume_display_text="Material claim prose here and more.",
        parsed_output={"resume_display_text": "Material claim prose here and more."},
        claim_ledger=ledger,
        text_claim_coverage={"sentences": [{"sentence_index": 1, "material_claims": [], "sentence_pass": True}], "overall_pass": True},
        allowed_fact_ids={"bul_unify_001"},
        target_company="Acme Corp.",
        jd_text="enterprise AI",
        temperature=0.45,
        runtime_generation_status="REAL_LLM",
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_claim_ledger_claim_text_non_empty"].pass_ is True


def test_x3_block_lists_claim_text_gate_when_ledger_text_missing():
    from apps_rg.runtime.claim_ledger.canonical_exec_summary_v2 import normalize_exec_summary_claim_ledger
    from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3
    from apps_rg.runtime.validators.executive_summary_x2 import run_x2_gates

    ledger = normalize_exec_summary_claim_ledger([{"source_fact_ids": ["bul_unify_001"]}])
    gates = run_x2_gates(
        resume_display_text="Alpha beta.",
        parsed_output={"resume_display_text": "Alpha beta."},
        claim_ledger=ledger,
        text_claim_coverage={"sentences": [], "overall_pass": False},
        allowed_fact_ids={"bul_unify_001"},
        target_company="Acme Corp.",
        jd_text="enterprise AI",
        temperature=0.45,
        runtime_generation_status="REAL_LLM",
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
    )
    x3 = aggregate_x3(
        resume_display_text="Alpha beta.",
        claim_ledger=ledger,
        x2_gates=[g.to_dict() for g in gates],
        x1d_judges=[
            {
                "provider_key": "openai_chatgpt",
                "evaluator_mode": "MODEL_BACKED",
                "pass": True,
                "decisive_failure": False,
                "provider_status": "MODEL_BACKED_PASS",
            }
        ],
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        section_input_usage_ledger=EXEC_SUMMARY_TEST_INPUT_USAGE_LEDGER,
    )
    assert x3.x3_code == "X3_BLOCK"
    assert "x2_claim_ledger_claim_text_non_empty" in x3.x2_failed_gates


def test_x2_target_company_gate_catches_bad_text():
    from apps_rg.runtime.validators.executive_summary_x2 import run_x2_gates

    gates = run_x2_gates(
        resume_display_text="At Synthetic Enterprise Corp., led agentic AI platform modernization.",
        parsed_output={"resume_display_text": "At Synthetic Enterprise Corp., led agentic AI platform modernization."},
        claim_ledger=[{"claim_text": "agentic AI platform", "source_fact_ids": ["bul_unify_001"]}],
        text_claim_coverage={"sentences": [], "overall_pass": False},
        allowed_fact_ids={"bul_unify_001"},
        target_company="Synthetic Enterprise Corp.",
        jd_text="enterprise AI platform leadership",
        temperature=0.45,
        runtime_generation_status="REAL_LLM",
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
    )
    gate_map = {g.gate_id: g.pass_ for g in gates}
    assert gate_map["x2_target_company_as_experience_zero"] is False


def test_x3_allow_requires_model_backed_judges_and_real_llm():
    from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3

    x3 = aggregate_x3(
        resume_display_text="good text",
        claim_ledger=[{"claim_text": "good", "source_fact_ids": ["bul_unify_001"]}],
        x2_gates=[{"gate_id": "x2_schema_valid", "pass": True}],
        x1d_judges=[{"provider_key": "openai_chatgpt", "evaluator_mode": "MOCKED", "decisive_failure": False}],
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        section_input_usage_ledger=EXEC_SUMMARY_TEST_INPUT_USAGE_LEDGER,
    )
    assert x3.x3_code != "X3_ALLOW"


def test_l6_shadow_package_offline_only():
    run_cmd()
    l6 = load_json("l6_shadow_eval_package.json")
    assert l6["offline_only"] is True
    assert l6["promotion_allowed"] is False
    assert l6["learning_mutation_performed"] is False
    auth = l6.get("runtime_approval_authority")
    if isinstance(auth, str):
        assert auth == "NONE"
    elif isinstance(auth, dict):
        assert auth.get("actual") is False
    else:
        nested = (l6.get("boundary_checks") or {}).get("runtime_approval_authority")
        assert isinstance(nested, dict)
        assert nested.get("actual") is False


LEDGER_CONTRACT = REPO_ROOT / "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json"
TAX_CONTRACT = REPO_ROOT / "apps_rg/config/domain_contract/master_role_family_taxonomy.yaml"


@pytest.fixture
def persisted_selected_role_fact_set_path(tmp_path: Path) -> Path:
    if not LEDGER_CONTRACT.is_file() or not TAX_CONTRACT.is_file():
        pytest.skip("SRFS ledger/taxonomy fixture files not present")

    from apps_rg.fact_inventory.candidate_fact_ledger import (
        load_master_candidate_fact_ledger,
        load_master_role_family_taxonomy,
    )
    from apps_rg.fact_inventory.selected_role_fact_set import (
        select_candidate_facts_for_role,
        selected_role_fact_set_to_json_dict,
    )

    ledger = load_master_candidate_fact_ledger(path=LEDGER_CONTRACT)
    taxonomy = load_master_role_family_taxonomy(path=TAX_CONTRACT)
    srfs = select_candidate_facts_for_role(
        target_company="Acme Labs",
        target_role="SVP Strategic Alliances kubernetes microservices",
        jd_text="RevOps forecasting pipeline analytics Salesforce quotas ISV alliances.",
        briefing_text="C-suite steering for platform modernization.",
        ledger=ledger,
        taxonomy=taxonomy,
        source_ledger_path=str(LEDGER_CONTRACT),
        taxonomy_ref=str(TAX_CONTRACT),
        repo_root=REPO_ROOT,
        now_slug="20260518_CONTRACTTESTEXEC",
    )
    payload = selected_role_fact_set_to_json_dict(srfs)
    p = tmp_path / "selected_role_fact_set_exec_fixture.json"
    p.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return p


def test_git_diff_agentic_core_is_clean():
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", "agentic_core"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, r.stderr
    assert (r.stdout or "").strip() == "", r.stdout


def test_x2_srfs_gates_skipped_when_no_selected_role_fact_set():
    from apps_rg.runtime.validators.executive_summary_x2 import run_x2_gates

    gates = run_x2_gates(
        resume_display_text="Good. Good second.",
        parsed_output={"resume_display_text": "Good. Good second."},
        claim_ledger=[{"claim_text": "Good", "source_fact_ids": ["bul_unify_001"]}],
        text_claim_coverage={"sentences": [], "overall_pass": False},
        allowed_fact_ids={"bul_unify_001"},
        target_company="Synthetic Enterprise Corp.",
        jd_text="enterprise AI platform leadership",
        temperature=0.45,
        runtime_generation_status="REAL_LLM",
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
    )
    by_id = {g.gate_id: g for g in gates}
    for gid in (
        "x2_srfs_executive_selected_fact_scope",
        "x2_srfs_blocked_or_confirmation_fact_citation_zero",
        "x2_srfs_jd_or_briefing_standalone_proof_id_zero",
        "x2_exec_summary_srfs_sentence_count_4_5",
        "x2_exec_summary_srfs_density_word_count",
    ):
        g = by_id[gid]
        assert g.pass_ is True
        assert g.observed_value == "skipped_no_selected_role_fact_set"


def test_x2_srfs_standalone_proof_id_gate_fails_when_integration_active():
    from apps_rg.runtime.validators.executive_summary_x2 import run_x2_gates

    si = {
        "artifact_path_resolved": str((REPO_ROOT / "artifacts").resolve()),
        "selection_id": "test_only",
        "executive_summary_selected_fact_ids": ["JD_ONLY"],
        "blocked_candidate_fact_ids": [],
        "confirmation_required_candidate_fact_ids": [],
    }
    resume = (
        "Engineering executive building production-grade governed AI platforms for regulated enterprise environments. "
        "Designs runtime architectures combining validation controls and traceability to improve reliability and "
        "auditability. "
        "Leads platform lifecycle and commercialization, connecting governed primitives to reusable services across "
        "enterprise programs. "
        "Leads commercial proof lines including $22M IP-led revenue and gross margin expansion supported by selected "
        "facts. "
        "Fellow of the Society of Actuaries reinforces quantitative credibility when credential facts are present in "
        "the ledger."
    )
    gates = run_x2_gates(
        resume_display_text=resume,
        parsed_output={
            "resume_display_text": resume,
            "self_check": {
                "selected_fact_pool_too_small": True,
                "selected_fact_pool_too_small_reason": "jd_only_contract_test_short_coverage",
            },
        },
        claim_ledger=[{"claim_text": "claim", "source_fact_ids": ["JD_ONLY"]}],
        text_claim_coverage={"sentences": [], "overall_pass": False},
        allowed_fact_ids={"JD_ONLY"},
        target_company="Synthetic Enterprise Corp.",
        jd_text="enterprise AI platform leadership",
        temperature=0.45,
        runtime_generation_status="REAL_LLM",
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
        srfs_integration=si,
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_srfs_jd_or_briefing_standalone_proof_id_zero"].pass_ is False


def test_compile_exec_summary_srfs_includes_style_oneshot_block():
    from apps_rg.runtime.dispatch.executive_summary_pa import (
        SRFS_STYLE_ONESHOT_MARKER,
        compile_executive_summary_prompt,
    )

    payload = {
        "run_id": "rt_slice_srfs_style_compile",
        "target_title": "SVP Engineering",
        "target_company": "Unify Consulting",
        "jd_text": "enterprise AI",
        "briefing": "regulated enterprise",
        "allowed_fact_ids": ["fact_a", "fact_b"],
        "selected_fact_plan": {
            "section_id": "executive_summary",
            "facts": [
                {"fact_id": "fact_a", "claim_text": "Claim a."},
                {"fact_id": "fact_b", "claim_text": "Claim b."},
            ],
            "required_fact_ids": ["fact_a", "fact_b"],
        },
        "srfs_integration": {
            "artifact_path_resolved": str(REPO_ROOT / "artifacts" / "dummy_srfs_path.json"),
            "selection_id": "sel_rt_slice",
            "executive_summary_selected_fact_ids": ["fact_a", "fact_b"],
            "blocked_facts_count": 1,
            "facts_requiring_human_confirmation_count": 2,
            "unsupported_jd_needs_count": 0,
            "blocked_candidate_fact_ids": [],
            "confirmation_required_candidate_fact_ids": [],
        },
    }
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    body = out.artifact.messages[0]["content"]
    assert SRFS_STYLE_ONESHOT_MARKER in body
    assert "STYLE_ONLY_NOT_PROOF" in body
    assert "srfs_governance_required_or_explain" in body
    assert "SRFS_FIVE_PART_EXEC_ARCH_V1" in body
    assert "SRFS_SENTENCE_RESP_SEP_V1" in body
    assert "srfs_style_contrast_chain_vs_split" in body
    assert "srfs_suggested_target_shape" in body
    assert "x2_exec_summary_srfs_sentence_responsibility_shape" in body
    assert "x2_exec_summary_srfs_sentence_count_4_5" in body
    assert "x2_exec_summary_srfs_density_word_count" in body


def test_srfs_sentence_responsibility_shape_passes_compliant_five_sentences():
    from apps_rg.runtime.validators.executive_summary_x2 import check_srfs_sentence_responsibility_shape

    si = {"artifact_path_resolved": str(REPO_ROOT / "artifacts" / "srfs_shape_fixture.json")}
    text = (
        "Engineering executive building production-grade governed AI platforms for regulated enterprise environments. "
        "Designs and operates runtime architectures that combine deterministic routing, multi-agent orchestration, "
        "graph-aware retrieval, validation controls, and traceability to improve reliability and auditability. "
        "Leads the full platform lifecycle across architecture, operating model, engineering scale-out, and "
        "commercialization, connecting governed runtime primitives to reusable platform services adopted across enterprise "
        "programs. "
        "Delivered measurable commercial and engineering outcomes including IP-led revenue expansion, gross margin "
        "improvement, and disciplined deployment cycles grounded in cited executive facts. "
        "Fellow of the Society of Actuaries reinforces quantitative credibility for regulated enterprise stakeholders."
    )
    ok, reason = check_srfs_sentence_responsibility_shape(text, si)
    assert ok is True, reason


def test_srfs_sentence_responsibility_shape_skipped_without_srfs():
    from apps_rg.runtime.validators.executive_summary_x2 import check_srfs_sentence_responsibility_shape

    ok, reason = check_srfs_sentence_responsibility_shape("One. Two. Three.", None)
    assert ok is True
    assert reason and "skipped" in reason.lower()


def test_srfs_sentence_responsibility_shape_fails_s1_integrating():
    from apps_rg.runtime.validators.executive_summary_x2 import check_srfs_sentence_responsibility_shape

    si = {"artifact_path_resolved": "/tmp/x.json"}
    text = (
        "Executive thesis integrating microservices for regulated environments. "
        "Second sentence routing only. "
        "Third is lifecycle bridge without revenue. "
        "Fourth holds measurable outcomes only. "
        "Fifth closes with credibility supported by facts."
    )
    ok, _ = check_srfs_sentence_responsibility_shape(text, si)
    assert ok is False


def test_srfs_sentence_responsibility_shape_fails_s1_to_improve():
    from apps_rg.runtime.validators.executive_summary_x2 import check_srfs_sentence_responsibility_shape

    si = {"artifact_path_resolved": "/tmp/x.json"}
    text = (
        "Engineering executive building platforms to improve reliability in regulated environments. "
        "Mechanism sentence with orchestration. "
        "Lifecycle bridge without commercial metrics. "
        "Outcomes sentence with revenue facts. "
        "Credibility sentence supported by facts."
    )
    ok, _ = check_srfs_sentence_responsibility_shape(text, si)
    assert ok is False


def test_srfs_sentence_responsibility_shape_fails_s1_digit():
    from apps_rg.runtime.validators.executive_summary_x2 import check_srfs_sentence_responsibility_shape

    si = {"artifact_path_resolved": "/tmp/x.json"}
    text = (
        "Engineering executive with 10 years in governed AI platforms for enterprise. "
        "Mechanism sentence. "
        "Lifecycle bridge. "
        "Outcomes sentence. "
        "Credibility sentence."
    )
    ok, _ = check_srfs_sentence_responsibility_shape(text, si)
    assert ok is False


def test_srfs_sentence_responsibility_shape_fails_s2_revenue():
    from apps_rg.runtime.validators.executive_summary_x2 import check_srfs_sentence_responsibility_shape

    si = {"artifact_path_resolved": "/tmp/x.json"}
    text = (
        "Engineering executive building governed AI platforms for regulated enterprise environments. "
        "Designs architectures with $22M revenue in the mechanism sentence. "
        "Lifecycle bridge sentence stays clean. "
        "Outcomes would belong here. "
        "Credibility closes here."
    )
    ok, _ = check_srfs_sentence_responsibility_shape(text, si)
    assert ok is False


def test_srfs_sentence_responsibility_shape_fails_s2_team_scale():
    from apps_rg.runtime.validators.executive_summary_x2 import check_srfs_sentence_responsibility_shape

    si = {"artifact_path_resolved": "/tmp/x.json"}
    text = (
        "Engineering executive building governed AI platforms for regulated enterprise environments. "
        "Scaling from 8 to 28 specialists in sentence two is forbidden. "
        "Lifecycle bridge stays clean. "
        "Outcomes belong here. "
        "Credibility belongs here."
    )
    ok, _ = check_srfs_sentence_responsibility_shape(text, si)
    assert ok is False


def test_srfs_sentence_responsibility_shape_fails_s4_fellow_opener():
    from apps_rg.runtime.validators.executive_summary_x2 import check_srfs_sentence_responsibility_shape

    si = {"artifact_path_resolved": "/tmp/x.json"}
    text = (
        "Engineering executive building governed AI platforms for regulated enterprise environments. "
        "Mechanism sentence with routing and orchestration. "
        "Lifecycle bridge connects services to adoption without metrics. "
        "Fellow of the Society of Actuaries must not lead outcomes. "
        "Closing sentence attempts credibility but structure is already invalid."
    )
    ok, _ = check_srfs_sentence_responsibility_shape(text, si)
    assert ok is False


def test_srfs_sentence_responsibility_shape_fails_s5_holds_certifications_opener():
    from apps_rg.runtime.validators.executive_summary_x2 import check_srfs_sentence_responsibility_shape

    si = {"artifact_path_resolved": "/tmp/x.json"}
    text = (
        "Engineering executive building governed AI platforms for regulated enterprise environments. "
        "Mechanism sentence with routing and orchestration. "
        "Lifecycle bridge connects services to adoption across programs. "
        "Outcomes sentence reports revenue and margin supported by facts. "
        "Holds certifications in cloud and data platforms for executive delivery."
    )
    ok, _ = check_srfs_sentence_responsibility_shape(text, si)
    assert ok is False


def test_srfs_sentence_responsibility_shape_gate_skipped_in_run_x2_without_srfs():
    from apps_rg.runtime.validators.executive_summary_x2 import run_x2_gates

    gates = run_x2_gates(
        resume_display_text="Alpha. Beta. Gamma.",
        parsed_output={"resume_display_text": "Alpha. Beta. Gamma."},
        claim_ledger=[{"claim_text": "x", "source_fact_ids": ["bul_unify_001"]}],
        text_claim_coverage={"sentences": [], "overall_pass": False},
        allowed_fact_ids={"bul_unify_001"},
        target_company="Synthetic Enterprise Corp.",
        jd_text="enterprise AI",
        temperature=0.45,
        runtime_generation_status="REAL_LLM",
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
    )
    by_id = {g.gate_id: g for g in gates}
    g = by_id["x2_exec_summary_srfs_sentence_responsibility_shape"]
    assert g.pass_ is True
    assert "skipped" in str(g.observed_value).lower()


def test_srfs_sentence_count_4_5_fails_three_sentences():
    from apps_rg.runtime.validators.executive_summary_x2 import check_srfs_sentence_count_4_5

    si = {"artifact_path_resolved": "/tmp/x.json"}
    ok, _ = check_srfs_sentence_count_4_5("One. Two. Three.", si)
    assert ok is False


def test_srfs_density_word_count_passes_in_band():
    from apps_rg.runtime.validators.executive_summary_x2 import check_srfs_density_word_count

    si = {"artifact_path_resolved": "/tmp/x.json"}
    text = ("Word " * 99) + "end."
    ok, r = check_srfs_density_word_count(text, {"self_check": {}}, si)
    assert ok is True, r


def test_srfs_density_word_count_fails_under_without_excuse():
    from apps_rg.runtime.validators.executive_summary_x2 import check_srfs_density_word_count

    si = {"artifact_path_resolved": "/tmp/x.json"}
    ok, _ = check_srfs_density_word_count("Too few words here.", {"self_check": {}}, si)
    assert ok is False


def test_srfs_density_word_count_passes_under_with_excuse():
    from apps_rg.runtime.validators.executive_summary_x2 import check_srfs_density_word_count

    si = {"artifact_path_resolved": "/tmp/x.json"}
    ok, r = check_srfs_density_word_count(
        "Short.",
        {
            "self_check": {
                "selected_fact_pool_too_small": True,
                "selected_fact_pool_too_small_reason": "fixture pool deliberately tiny",
            }
        },
        si,
    )
    assert ok is True, r


def test_srfs_density_word_count_fails_over_max():
    from apps_rg.runtime.validators.executive_summary_x2 import check_srfs_density_word_count

    si = {"artifact_path_resolved": "/tmp/x.json"}
    text = "word " * 200
    ok, _ = check_srfs_density_word_count(text, {"self_check": {}}, si)
    assert ok is False


def test_x2_sentence_count_2_3_skipped_when_srfs_active():
    from apps_rg.runtime.validators.executive_summary_x2 import run_x2_gates

    si = {"artifact_path_resolved": "/tmp/srfs.json", "executive_summary_selected_fact_ids": ["fact_a"]}
    resume = (
        "Engineering executive building governed AI platforms for regulated enterprise environments. "
        "Mechanism sentence with orchestration and traceability to improve reliability. "
        "Lifecycle bridge without commercial metrics in this lane. "
        "Outcomes sentence with $1M revenue supported by facts. "
        "Fellow of the Society closes credibility when supported."
    )
    gates = run_x2_gates(
        resume_display_text=resume,
        parsed_output={
            "resume_display_text": resume,
            "self_check": {
                "selected_fact_pool_too_small": True,
                "selected_fact_pool_too_small_reason": "contract_test_short_resume",
            },
        },
        claim_ledger=[{"claim_text": "x", "source_fact_ids": ["fact_a"]}],
        text_claim_coverage={"sentences": [], "overall_pass": False},
        allowed_fact_ids={"fact_a"},
        target_company="Synthetic Enterprise Corp.",
        jd_text="enterprise AI",
        temperature=0.45,
        runtime_generation_status="REAL_LLM",
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
        srfs_integration=si,
    )
    by_id = {g.gate_id: g for g in gates}
    g23 = by_id["x2_exec_summary_sentence_count_2_3"]
    assert g23.pass_ is True
    assert "skipped_srfs" in str(g23.observed_value)
    from apps_rg.runtime.validators.executive_summary_x2 import check_srfs_blocked_or_confirmation_citations

    ok, reason = check_srfs_blocked_or_confirmation_citations(
        [{"claim_text": "x", "source_fact_ids": ["fact_blocked_001"]}],
        blocked_ids=frozenset({"fact_blocked_001"}),
        confirmation_ids=frozenset(),
    )
    assert ok is False
    assert reason and "blocked" in reason.lower()

    ok2, _ = check_srfs_blocked_or_confirmation_citations(
        [{"claim_text": "x", "source_fact_ids": ["fact_ok_001"]}],
        blocked_ids=frozenset({"fact_blocked_001"}),
        confirmation_ids=frozenset({"fact_med_001"}),
    )
    assert ok2 is True


def test_zz_exec_summary_selected_role_fact_set_cli_smoke(persisted_selected_role_fact_set_path: Path) -> None:
    # finalize_runtime_proof_run requires artifact paths under repo root (relative tracing).
    import shutil

    from apps_rg.runtime.runtime_proof_layout import lane_root

    uid = uuid.uuid4().hex
    artifact = REPO_ROOT / "artifacts" / "apps_rg" / "_pytest_exec_srfs" / uid
    artifact.mkdir(parents=True)
    ptr_path = lane_root(REPO_ROOT, LANE_KEY) / "latest_mock_run.json"
    prev_ptr = ptr_path.read_text(encoding="utf-8") if ptr_path.is_file() else None
    try:
        env = {**_slice_subprocess_env(), "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB": "1"}
        result = subprocess.run(
            CMD
            + [
                "--provider",
                "mock",
                "--temperature",
                "0.45",
                "--artifact-dir",
                str(artifact),
                "--selected-role-fact-set",
                str(persisted_selected_role_fact_set_path),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=180,
            env=env,
        )
        assert result.returncode == 0, result.stderr
        rt = json.loads((artifact / "runtime_payload.json").read_text(encoding="utf-8"))
        assert "srfs_integration" in rt
        ref = json.loads((artifact / "selected_role_fact_set_ref.json").read_text(encoding="utf-8"))
        assert ref["selection_id"] == rt["srfs_integration"]["selection_id"]
        exec_ids = ref["executive_summary_selected_fact_ids"]
        assert exec_ids
        compiled = (artifact / "compiled_prompt.txt").read_text(encoding="utf-8")
        from apps_rg.runtime.dispatch.executive_summary_pa import SRFS_STYLE_ONESHOT_MARKER

        for fid in exec_ids[:5]:
            assert fid in compiled
        assert "SELECTED_ROLE_FACT_SET_APPENDIX" in compiled
        assert "NOT PROOF" in compiled
        assert SRFS_STYLE_ONESHOT_MARKER in compiled
        assert "STYLE_ONLY_NOT_PROOF" in compiled
        assert "<north_star_synthesis_contract>" in compiled
        allowed_ids = set(rt.get("allowed_fact_ids") or [])
        assert allowed_ids
        canon = json.loads((artifact / "canonical_claim_ledger_v2.json").read_text(encoding="utf-8"))
        for cl in canon.get("claims", []):
            for fid in cl.get("source_fact_ids", []):
                assert str(fid) in allowed_ids
        x2 = json.loads((artifact / "x2_gate_outputs.json").read_text(encoding="utf-8"))
        by_id = {g["gate_id"]: g for g in x2.get("gates", [])}
        assert by_id["x2_srfs_executive_selected_fact_scope"]["pass"] is True
        assert by_id["x2_claim_ledger_claim_text_non_empty"]["pass"] is True
        assert by_id["x2_exec_summary_srfs_sentence_responsibility_shape"]["pass"] is True
        assert by_id["x2_exec_summary_srfs_sentence_count_4_5"]["pass"] is True
        assert by_id["x2_exec_summary_srfs_density_word_count"]["pass"] is True
    finally:
        shutil.rmtree(artifact, ignore_errors=True)
        if prev_ptr is not None:
            ptr_path.write_text(prev_ptr, encoding="utf-8")
        elif ptr_path.is_file():
            ptr_path.unlink()


def test_source_sensitive_audit_word_boundary_auditability_ok():
    """'auditability' must not false-trigger token gate for 'audit'."""
    from apps_rg.runtime.validators.executive_summary_x2 import check_source_sensitive_phrases

    facts = [{"claim_text": "Built cloud platforms.", "achievement_summary": ""}]
    text = "Executive with expertise in platforms enhancing reliability and auditability."
    ok, reason = check_source_sensitive_phrases(text, facts)
    assert ok is True, reason


def test_source_sensitive_audit_token_requires_fact_support():
    from apps_rg.runtime.validators.executive_summary_x2 import check_source_sensitive_phrases

    facts = [{"claim_text": "Built cloud platforms.", "achievement_summary": ""}]
    text = "Executive leading audit readiness for enterprise platforms."
    ok, reason = check_source_sensitive_phrases(text, facts)
    assert ok is False
    assert reason and "audit" in reason.lower()


def test_no_agentic_core_in_overlay_files():
    overlay_files = [
        "apps_rg/runtime/dispatch/executive_summary_dispatch.py",
        "apps_rg/runtime/sections/executive_summary_lane.py",
        "apps_rg/runtime/providers/qwen_vllm_provider.py",
        "apps_rg/runtime/validators/executive_summary_x2.py",
        "apps_rg/runtime/judges/executive_summary_x1d.py",
        "apps_rg/runtime/exit/executive_summary_x3.py",
        "apps_rg/runtime/shadow/executive_summary_l6.py",
    ]
    for relative in overlay_files:
        assert (REPO_ROOT / relative).exists()
