"""Contract/runtime tests: executive_summary token budget receipt + provider request proof."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from apps_rg.runtime.dispatch.executive_summary_pa import compile_executive_summary_prompt
from apps_rg.runtime.sections.executive_summary_token_budget import (
    apply_executive_summary_token_budget_policy,
    estimate_tokens_approximate,
    write_token_budget_receipt,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CMD = [sys.executable, "-m", "apps_rg", "--section", "executive_summary"]


def _minimal_payload() -> dict:
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
        "run_id": "tb_contract_run",
        "target_title": "SVP Engineering",
        "target_company": "Brown & Brown",
        "jd_text": "enterprise AI platform leadership",
        "briefing": "regulated enterprise environment",
        "allowed_fact_ids": ["fact_exec_high_001"],
        "selected_fact_plan": {
            "facts": [
                {
                    "fact_id": "fact_exec_high_001",
                    "claim_text": "Delivered governed agentic AI platforms at scale.",
                }
            ],
            "required_fact_ids": ["fact_exec_high_001"],
        },
    }


def test_token_budget_policy_on_compiled_prompt_produces_receipt(tmp_path: Path):
    payload = _minimal_payload()
    compiled = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    before_tokens = estimate_tokens_approximate(compiled.artifact.messages[0]["content"])
    ctx_window = int(before_tokens / 0.85) + 1024 + 512 + 512
    _, receipt = apply_executive_summary_token_budget_policy(
        compiled,
        runtime_payload=payload,
        provider="qwen_vllm",
        model="Qwen/Qwen2.5-32B-Instruct-AWQ",
        requested_max_output_tokens=1024,
        provider_context_window=ctx_window,
    )
    write_token_budget_receipt(tmp_path, receipt)
    path = tmp_path / "token_budget_receipt.json"
    assert path.is_file()
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert doc["section"] == "executive_summary"
    assert doc["provider_context_window"] == ctx_window
    assert doc["provider_context_window_source"] == "ENV_VLLM_MAX_MODEL_LEN"
    assert doc["server_context_window_verified"] is False
    assert doc.get("first_pass_95pct_policy_enabled") is True
    assert doc["requested_max_output_tokens"] == 1024
    assert "available_input_tokens" in doc
    assert "compiled_prompt_tokens_before_trim" in doc
    assert "protected_components_preserved" in doc


def test_provider_request_mock_fallback_not_introduced_by_token_budget():
    """Regression: token budget block path must not enable mock fallback."""
    payload = _minimal_payload()
    compiled = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    before_tokens = estimate_tokens_approximate(compiled.artifact.messages[0]["content"])
    ctx_window = int(before_tokens / 0.85) + 1024 + 512 + 512
    _, receipt = apply_executive_summary_token_budget_policy(
        compiled,
        runtime_payload=payload,
        provider="qwen_vllm",
        model="Qwen/Qwen2.5-32B-Instruct-AWQ",
        requested_max_output_tokens=1024,
        provider_context_window=ctx_window,
    )
    assert receipt.get("status") == "PASS"
    assert receipt.get("first_pass_95pct_exceeded") is False
    assert receipt.get("evidence_contract_digest_before") == receipt.get("evidence_contract_digest_after")
    assert receipt.get("prompt_shape_preserved") is True
    assert receipt.get("shape_altering_trim_forbidden") is True
    from apps_rg.runtime.providers.qwen_vllm_provider import build_qwen_request

    messages = compiled.artifact.messages
    req, _payload = build_qwen_request(
        messages=messages,
        prompt_hash="abc",
        input_payload_hash="def",
        max_tokens=1024,
    )
    assert req.mock_fallback_allowed is False
    after_tokens = receipt["compiled_prompt_tokens_after_trim"]
    available = receipt["available_input_tokens"]
    assert after_tokens <= available


@pytest.mark.skipif(
    os.environ.get("APPS_RG_EXEC_SUMMARY_LIVE_TOKEN_BUDGET") != "1",
    reason="Set APPS_RG_EXEC_SUMMARY_LIVE_TOKEN_BUDGET=1 for live Brown & Brown runtime proof",
)
def test_live_run_writes_token_budget_receipt():
    env = {
        **os.environ,
        "APPS_RG_EXEC_SUMMARY_QWEN_MAX_OUTPUT_TOKENS": "1024",
        "APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO": "1",
    }
    result = subprocess.run(
        CMD
        + [
            "--target-company",
            "Brown & Brown",
            "--target-role",
            "Senior Vice President, IT Strategy & Innovation",
            "--jd",
            "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt",
            "--manual-brief",
            "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=600,
        env=env,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    from apps_rg.runtime.runtime_proof_layout import resolve_latest_real_run_dir

    run_dir = resolve_latest_real_run_dir(REPO_ROOT, "executive_summary")
    assert run_dir is not None
    receipt_path = run_dir / "token_budget_receipt.json"
    assert receipt_path.is_file(), f"missing {receipt_path}"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["status"] in ("PASS", "FAIL")
    prov_req = json.loads((run_dir / "provider_request.json").read_text(encoding="utf-8"))
    assert prov_req.get("mock_fallback_allowed") is False
    if receipt["status"] == "PASS":
        assert receipt["compiled_prompt_tokens_after_trim"] <= receipt["available_input_tokens"]
        assert prov_req.get("max_tokens") == 1024
