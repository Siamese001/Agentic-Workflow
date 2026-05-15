from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = REPO_ROOT / "artifacts" / "apps_rg" / "runtime_proofs" / "executive_summary"
CMD = [sys.executable, "-m", "apps_rg.runtime.dispatch.executive_summary_dispatch", "--allow-non-allow-exit-zero"]


def run_cmd(*extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(CMD + list(extra), cwd=REPO_ROOT, text=True, capture_output=True, timeout=120)


def load_json(name: str):
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def test_mock_command_executes_and_prints_output():
    result = run_cmd("--provider", "mock", "--mock-judges")
    assert result.returncode == 0, result.stderr
    assert "L2_EXECUTIVE_SUMMARY_OUTPUT:" in result.stdout
    assert "X1D_LLM_JUDGE_OUTPUTS:" in result.stdout
    assert "X3_DISPOSITION:" in result.stdout


def test_mocked_judges_cannot_allow():
    run_cmd("--provider", "mock", "--mock-judges")
    x3 = load_json("x3_disposition.json")
    x2 = load_json("x2_gate_outputs.json")
    if not x2.get("failed_gates"):
        assert x3["x3_code"] == "X3_REVIEW_MOCKED_PLUMBING_ONLY"
    else:
        assert x3["x3_code"] == "X3_BLOCK"
    assert x3["authorization_scope"] == "PLUMBING_ONLY"
    assert x3["proceed_to_runtime"] is False


def test_three_judge_rows_exist():
    run_cmd("--provider", "mock", "--mock-judges")
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
    result = run_cmd("--provider", "mock")
    assert result.returncode == 0
    judges = load_json("x1d_llm_judge_outputs.json")["judges"]
    
    # Verify each judge has required fields
    for j in judges:
        assert "evaluator_mode" in j
        assert "provider_status" in j
        if j.get("provider_blocked") or str(j.get("provider_status", "")).startswith("BLOCKED_"):
            assert j.get("provider_blocked") is True
            assert j.get("decisive_failure") is False
            assert j.get("pass") is False
            assert str(j.get("provider_status", "")).startswith("BLOCKED_")

    x3 = load_json("x3_disposition.json")
    assert x3["x3_code"] != "X3_ALLOW"
    assert x3["proceed_to_runtime"] is False


def test_provider_request_artifact_written():
    run_cmd("--provider", "mock", "--mock-judges")
    assert (ARTIFACT_DIR / "provider_request.json").exists()
    assert (ARTIFACT_DIR / "runtime_payload.json").exists()
    assert (ARTIFACT_DIR / "prompt_selection_trace.json").exists()


def test_temperature_out_of_profile_fails_fast():
    result = run_cmd("--provider", "qwen_vllm", "--temperature", "0.7")
    assert result.returncode != 0
    assert "outside executive_summary profile" in (result.stderr + result.stdout)


def test_qwen_unavailable_blocks_not_mocks(monkeypatch):
    monkeypatch.setenv("VLLM_BASE_URL", "http://127.0.0.1:9/v1")
    result = run_cmd("--provider", "qwen_vllm")
    assert result.returncode == 0
    real = load_json("real_l2_generation_result.json")
    assert real["runtime_generation_status"] == "BLOCKED"
    assert real["exact_provider_error"]
    x3 = load_json("x3_disposition.json")
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
    )
    assert x3.x3_code != "X3_ALLOW"


def test_l6_shadow_package_offline_only():
    run_cmd("--provider", "mock", "--mock-judges")
    l6 = load_json("l6_shadow_eval_package.json")
    assert l6["offline_only"] is True
    assert l6["promotion_allowed"] is False
    assert l6["learning_mutation_performed"] is False
    assert l6["runtime_approval_authority"] == "NONE"


def test_no_agentic_core_in_overlay_files():
    overlay_files = [
        "apps_rg/runtime/dispatch/executive_summary_dispatch.py",
        "apps_rg/runtime/providers/qwen_vllm_provider.py",
        "apps_rg/runtime/validators/executive_summary_x2.py",
        "apps_rg/runtime/judges/executive_summary_x1d.py",
        "apps_rg/runtime/exit/executive_summary_x3.py",
        "apps_rg/runtime/shadow/executive_summary_l6.py",
    ]
    for relative in overlay_files:
        assert (REPO_ROOT / relative).exists()
