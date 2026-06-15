"""Unit tests for executive_summary pre-dispatch token budget policy."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.spine.front_contracts import (
    activate_fixture_dev_bypass,
    deactivate_fixture_dev_bypass,
)
from apps_rg.runtime.dispatch.executive_summary_pa import compile_executive_summary_prompt
from apps_rg.runtime.sections.executive_summary_token_budget import (
    FAIL_CLOSED_REASON,
    FAIL_CLOSED_REASON_FIRST_PASS_95PCT,
    FAIL_SHAPE_ALTERED,
    ExecutiveSummaryTokenBudgetExceeded,
    apply_executive_summary_token_budget_policy,
    build_token_budget_operator_guidance,
    evidence_contract_digest,
    estimate_tokens_approximate,
    exceeds_first_pass_95pct_policy,
    extract_evidence_contract_snapshot,
    first_pass_95pct_limit_tokens,
    protected_fact_ids_from_payload,
    resolve_context_window_provenance,
    resolve_first_pass_input_utilization_max,
    trim_executive_summary_prompt_content,
    verify_prompt_shape_preserved,
    write_token_budget_receipt,
)


@pytest.fixture(autouse=True)
def _fec_fixture_dev_bypass() -> None:
    activate_fixture_dev_bypass(non_product_certified=True)
    yield
    deactivate_fixture_dev_bypass()


def _minimal_payload(*, briefing: str = "short briefing", run_id: str = "tb_unit_run") -> dict:
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
        "run_id": run_id,
        "target_title": "SVP Engineering",
        "target_company": "Synthetic Enterprise Corp.",
        "jd_text": "enterprise AI platform leadership",
        "briefing": briefing,
        "allowed_fact_ids": ["fact_exec_high_001", "fact_exec_high_002"],
        "selected_fact_plan": {
            "facts": [
                {
                    "fact_id": "fact_exec_high_001",
                    "claim_text": "Delivered governed agentic AI platforms at scale.",
                },
                {
                    "fact_id": "fact_exec_high_002",
                    "claim_text": "Reduced cycle time through standardized delivery patterns.",
                },
            ],
            "required_fact_ids": ["fact_exec_high_001", "fact_exec_high_002"],
        },
    }


def test_high_facts_and_allowed_ids_never_trimmed():
    payload = _minimal_payload()
    compiled = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    content = compiled.artifact.messages[0]["content"]
    protected = protected_fact_ids_from_payload(payload)
    huge_briefing = "Z" * 20000
    payload_big = {**payload, "briefing": huge_briefing}
    compiled_big = compile_executive_summary_prompt(payload_big, run_id=payload_big["run_id"])
    big_content = compiled_big.artifact.messages[0]["content"]

    trimmed, components, applied = trim_executive_summary_prompt_content(
        big_content,
        protected_ids=protected,
        available_input_tokens=estimate_tokens_approximate(content) + 500,
    )
    assert applied is True
    for fid in protected:
        assert fid in trimmed
    assert "ALLOWED_SOURCE_FACT_IDS" in trimmed
    assert "SRFS_COMPOSITION_ONESHOT_V1" in trimmed
    assert "token-budget compressed SRFS contract" not in trimmed
    trim_names = {str(c.get("component") or "") for c in components}
    assert "srfs_style_only_oneshot" not in trim_names
    assert trim_names & {"jd_briefing_prose", "e0_examples", "jd_text_prose"}


def test_evidence_contract_digest_unchanged_after_optional_trim():
    payload = _minimal_payload(briefing="B" * 24000)
    compiled = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    before = compiled.artifact.messages[0]["content"]
    protected = protected_fact_ids_from_payload(payload)
    trimmed, _, applied = trim_executive_summary_prompt_content(
        before,
        protected_ids=protected,
        available_input_tokens=6000,
    )
    assert applied
    d0 = evidence_contract_digest(extract_evidence_contract_snapshot(before, protected))
    d1 = evidence_contract_digest(extract_evidence_contract_snapshot(trimmed, protected))
    assert d0 == d1
    assert not verify_prompt_shape_preserved(before, trimmed, srfs_mode=True)


def test_srfs_shape_block_never_replaced_by_stub():
    payload = _minimal_payload()
    pool_ids = ["fact_exec_high_001", "fact_exec_high_002"]
    compiled = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    content = compiled.artifact.messages[0]["content"]
    assert "<srfs_style_only_oneshot" in content
    protected = protected_fact_ids_from_payload(payload)
    trimmed, components, _ = trim_executive_summary_prompt_content(
        content,
        protected_ids=protected,
        available_input_tokens=5000,
    )
    assert "token-budget compressed SRFS contract" not in trimmed
    assert "<srfs_style_only_oneshot" in trimmed
    assert not any(c.get("component") == "srfs_style_only_oneshot" for c in components)


def test_blocks_instead_of_shape_altering_when_optional_trim_insufficient():
    """Brown-scale prompts must block — not compress I0/SRFS and limp to Qwen."""
    payload = _minimal_payload(briefing="B" * 18000)
    payload["jd_text"] = "J" * 12000
    compiled = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    with pytest.raises(ExecutiveSummaryTokenBudgetExceeded) as excinfo:
        apply_executive_summary_token_budget_policy(
            compiled,
            runtime_payload=payload,
            provider="qwen_vllm",
            model="Qwen/Qwen2.5-32B-Instruct-AWQ",
            requested_max_output_tokens=1024,
            provider_context_window=4096,
        )
    receipt = excinfo.value.receipt
    assert receipt["status"] == "FAIL"
    assert receipt["fail_closed_reason"] in (
        FAIL_CLOSED_REASON,
        FAIL_CLOSED_REASON_FIRST_PASS_95PCT,
    )
    assert receipt["dispatch_allowed"] is False
    assert receipt["first_pass_95pct_policy_enabled"] is True
    assert receipt["shape_altering_trim_forbidden"] is True
    assert receipt["evidence_contract_preserved"] is True
    assert receipt["evidence_contract_digest_before"] == receipt["evidence_contract_digest_after"]
    assert "I0 compressed for token budget" not in compiled.artifact.messages[0]["content"]


def test_fail_closed_when_required_content_still_exceeds_budget():
    payload = _minimal_payload(briefing="X" * 5000)
    compiled = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    with pytest.raises(ExecutiveSummaryTokenBudgetExceeded) as excinfo:
        apply_executive_summary_token_budget_policy(
            compiled,
            runtime_payload=payload,
            provider="qwen_vllm",
            model="Qwen/Qwen2.5-32B-Instruct-AWQ",
            requested_max_output_tokens=1024,
            provider_context_window=4096,
        )
    receipt = excinfo.value.receipt
    assert receipt["status"] == "FAIL"
    assert receipt["fail_closed_reason"] in (
        FAIL_CLOSED_REASON,
        FAIL_CLOSED_REASON_FIRST_PASS_95PCT,
    )
    assert receipt["dispatch_allowed"] is False


def test_apply_policy_writes_pass_receipt_when_optional_trim_fits(tmp_path: Path):
    payload = _minimal_payload()
    compiled = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    before_tokens = estimate_tokens_approximate(compiled.artifact.messages[0]["content"])
    # SRFS compile is ~19k est. input tokens; window must clear W2.2 85% utilization after optional trim.
    ctx_window = int(before_tokens / 0.85) + 1024 + 512 + 512
    out, receipt = apply_executive_summary_token_budget_policy(
        compiled,
        runtime_payload=payload,
        provider="qwen_vllm",
        model="Qwen/Qwen2.5-32B-Instruct-AWQ",
        requested_max_output_tokens=1024,
        provider_context_window=ctx_window,
    )
    assert receipt["status"] == "PASS"
    assert receipt["dispatch_allowed"] is True
    assert receipt["evidence_contract_digest_before"] == receipt["evidence_contract_digest_after"]
    assert receipt["prompt_shape_preserved"] is True
    write_token_budget_receipt(tmp_path, receipt)
    saved = json.loads((tmp_path / "token_budget_receipt.json").read_text(encoding="utf-8"))
    assert saved["status"] == "PASS"
    assert saved["provider_context_window_source"] == "ENV_VLLM_MAX_MODEL_LEN"
    assert saved["server_context_window_verified"] is False
    assert saved.get("server_context_window_warning")
    assert saved["first_pass_95pct_policy_enabled"] is True
    assert out.artifact.messages[0]["content"]


def test_context_window_provenance_floors_legacy_vllm_to_section_default(monkeypatch) -> None:
    """Post-Qwen (2026-06-15): VLLM_MAX_MODEL_LEN can only RAISE the section ctx, never lower it.

    A legacy Qwen-era VLLM value (e.g. 16384/24576) below the Claude-era section default must NOT
    cap the section budget — that silent cap was the executive_summary token-block class. When
    APPS_RG_SECTION_MAX_MODEL_LEN is absent, the section default applies and the lower VLLM value is
    floored away; provenance still reports env-sourced / server-unverified.
    """
    import importlib

    from apps_rg.runtime import section_model_limits

    monkeypatch.delenv("APPS_RG_SECTION_MAX_MODEL_LEN", raising=False)
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_VERIFY_VLLM_CONTEXT_WINDOW", raising=False)
    monkeypatch.setenv("VLLM_MAX_MODEL_LEN", "16384")  # legacy Qwen value, below the Claude default
    importlib.reload(section_model_limits)
    try:
        prov = resolve_context_window_provenance()
        # 16384 < section default (131072) → floored to the default, never lowered to the Qwen value.
        assert prov.provider_context_window == section_model_limits.SECTION_MODEL_MAX_MODEL_LEN
        assert prov.provider_context_window == 131072
        assert prov.provider_context_window_source == "ENV_VLLM_MAX_MODEL_LEN"
        assert prov.server_context_window_verified is False
        assert prov.server_context_window_warning
    finally:
        importlib.reload(section_model_limits)


def test_first_pass_95pct_policy_blocks_between_cap_and_100_percent() -> None:
    available = 8464
    util_max = resolve_first_pass_input_utilization_max()
    limit = first_pass_95pct_limit_tokens(available)
    assert limit == int(8464 * util_max)
    assert exceeds_first_pass_95pct_policy(limit + 1, available)
    assert not exceeds_first_pass_95pct_policy(limit, available)


def test_brown_scale_first_pass_fits_default_utilization_at_16k_window() -> None:
    """Regression: trimmed Brown blockers ~12034 est.; p50 PASS dispatch ~12625 @ 13824."""
    available = 16384 - 2048 - 512
    assert available == 13824
    limit = first_pass_95pct_limit_tokens(available)
    assert limit >= 12625
    assert not exceeds_first_pass_95pct_policy(12034, available)
    assert not exceeds_first_pass_95pct_policy(12625, available)


def test_apply_policy_fail_closed_on_first_pass_95pct_after_optional_trim() -> None:
    # Optional trim must not drop below 95% first-pass gate; tight window forces block.
    payload = _minimal_payload(briefing="B" * 24000)
    payload["jd_text"] = "J" * 12000
    compiled = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    with pytest.raises(ExecutiveSummaryTokenBudgetExceeded) as excinfo:
        apply_executive_summary_token_budget_policy(
            compiled,
            runtime_payload=payload,
            provider="qwen_vllm",
            model="Qwen/Qwen2.5-32B-Instruct-AWQ",
            requested_max_output_tokens=1024,
            provider_context_window=8000,
        )
    receipt = excinfo.value.receipt
    assert receipt["fail_closed_reason"] == FAIL_CLOSED_REASON_FIRST_PASS_95PCT
    assert receipt["first_pass_95pct_exceeded"] is True
    assert receipt["dispatch_allowed"] is False
    guidance = receipt.get("operator_guidance")
    assert isinstance(guidance, dict)
    assert "briefing" in str(guidance.get("operator_message") or "").lower()
    assert "jd" in str(guidance.get("operator_message") or "").lower()
    assert int(guidance.get("tokens_to_remove_estimate") or 0) > 0
    assert any(s.get("target") == "do_not_cut" for s in guidance.get("suggestions") or [])


def test_token_budget_guidance_suggests_shorten_briefing_ssot() -> None:
    root = Path(__file__).resolve().parents[5]
    full = root / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md"
    if not full.is_file():
        import pytest

        pytest.skip("Brown briefing fixture missing")
    receipt = {
        "compiled_prompt_tokens_after_trim": 22000,
        "available_input_tokens": 22016,
        "first_pass_95pct_limit_tokens": 20915,
        "first_pass_utilization_pct": 96.0,
        "first_pass_input_utilization_max": 0.95,
        "fail_closed_reason": FAIL_CLOSED_REASON_FIRST_PASS_95PCT,
        "trim_applied": False,
        "trimmed_components": [],
    }
    guidance = build_token_budget_operator_guidance(
        receipt,
        runtime_payload={"manual_brief": str(full), "briefing": "x" * 1000, "jd_text": "y" * 100},
    )
    briefing_sugs = [s for s in guidance.get("suggestions") or [] if s.get("target") == "briefing"]
    assert briefing_sugs
    assert "briefing" in str(briefing_sugs[0].get("action") or "").lower()
    assert "exec_briefing_sibling_path" not in briefing_sugs[0]
    assert "briefing_exec" not in str(briefing_sugs[0].get("action") or "")
