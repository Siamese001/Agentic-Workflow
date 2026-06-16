"""W1 unit tests: regen token budget gate + budgeted_regen_call."""

from __future__ import annotations

from pathlib import Path
import pytest

from apps_rg.runtime.providers import provider_contract as qwen_vllm_provider
from apps_rg.runtime.sections.executive_summary_regen_dispatch import (
    budgeted_regen_call,
    clear_regen_budget_ledger,
    regen_budget_ledger,
    resolve_regen_max_output_tokens,
    resolve_scratch_max_output_tokens,
)
from apps_rg.runtime.sections.executive_summary_token_budget import (
    estimate_regen_thread_tokens,
    regen_dispatch_allowed,
    resolve_provider_context_window,
)


def test_regen_max_output_defaults_and_cap(monkeypatch) -> None:
    """Claude-era defaults (post-Qwen-removal 2026-06-13): scratch/regen 4096."""
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_REGEN_MAX_OUTPUT_TOKENS", raising=False)
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_MAX_OUTPUT_TOKENS", raising=False)
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_QWEN_REGEN_MAX_OUTPUT_TOKENS", raising=False)
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_QWEN_MAX_OUTPUT_TOKENS", raising=False)
    assert resolve_scratch_max_output_tokens() == 4096
    assert resolve_regen_max_output_tokens() == 4096
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_REGEN_MAX_OUTPUT_TOKENS", "3000")
    assert resolve_regen_max_output_tokens() == 4096


def test_regen_dispatch_blocks_when_thread_exceeds_window(monkeypatch) -> None:
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_REGEN_CAPS", "1")
    # Force a small window via the explicit override. (Post-2026-06-15 VLLM_MAX_MODEL_LEN can no
    # longer LOWER the section ctx, so the test passes the small window directly — the SSOT way.)
    huge = "word " * 20000
    messages = [{"role": "system", "content": huge}, {"role": "user", "content": huge}]
    est = estimate_regen_thread_tokens(messages)
    check = regen_dispatch_allowed(messages, max_output_tokens=1024, provider_context_window=4096)
    assert est > check.available_input_tokens
    assert check.dispatch_allowed is False
    assert check.block_reason == "regen_input_exceeds_available_context_window"


def test_budgeted_regen_fail_closed_before_transport(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_REGEN_CAPS", "1")
    clear_regen_budget_ledger(tmp_path)
    messages = [{"role": "user", "content": "x " * 500000}]
    outcome = budgeted_regen_call(
        {"model": "test-model"},
        messages=messages,
        phase="judge_regen",
        call_site="test_over_budget",
        artifact_dir=tmp_path,
    )
    assert outcome.dispatch_allowed is False
    assert outcome.result is None
    assert outcome.block_reason == "regen_input_exceeds_available_context_window"
    ledger = regen_budget_ledger(tmp_path)
    assert len(ledger.calls) == 1
    assert ledger.calls[0]["transport_dispatched"] is False
    assert ledger.calls[0]["accepted"] is False


def test_budgeted_regen_requires_provider_response_for_accepted_parse(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("VLLM_MAX_MODEL_LEN", "16384")

    def _fake_call(*_a, **_k):
        return qwen_vllm_provider.ProviderResult(
            provider_requested="qwen_vllm",
            provider_attempted=True,
            provider_available=True,
            exact_provider_error=None,
            runtime_generation_status="REAL_LLM",
            model="test",
            raw_model_output='{"resume_display_text":"ok","claim_ledger":[]}',
            provider_response={"choices": [{"message": {"content": "{}"}}]},
        )

    monkeypatch.setattr(
        "apps_rg.runtime.sections.executive_summary_regen_dispatch.generate_section",
        _fake_call,
    )
    clear_regen_budget_ledger(tmp_path)
    messages = [{"role": "user", "content": "short prompt"}]
    outcome = budgeted_regen_call(
        {"model": "test-model"},
        messages=messages,
        phase="synthesis_regen",
        call_site="test_ok",
        artifact_dir=tmp_path,
    )
    assert outcome.dispatch_allowed is True
    assert outcome.result is not None
    assert outcome.result.runtime_generation_status == "REAL_LLM"
    resp_files = list(tmp_path.glob("provider_response_synthesis_regen_*.json"))
    assert resp_files
    from apps_rg.runtime.sections.executive_summary_regen_dispatch import (
        mark_regen_call_parse,
    )

    mark_regen_call_parse(tmp_path, outcome.call_id, parse_ok=True)
    row = regen_budget_ledger(tmp_path).calls[0]
    assert row["provider_response_present"] is True
    assert row["parse_ok"] is True
    assert row["accepted"] is True


def test_budgeted_regen_timeout_never_accepted(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("VLLM_MAX_MODEL_LEN", "16384")

    def _timeout_call(*_a, **_k):
        return qwen_vllm_provider.ProviderResult(
            provider_requested="qwen_vllm",
            provider_attempted=True,
            provider_available=False,
            exact_provider_error="chat_completion_timeout",
            runtime_generation_status="BLOCKED",
            model="test",
            raw_model_output="",
            provider_response=None,
        )

    monkeypatch.setattr(
        "apps_rg.runtime.sections.executive_summary_regen_dispatch.generate_section",
        _timeout_call,
    )
    clear_regen_budget_ledger(tmp_path)
    outcome = budgeted_regen_call(
        {"model": "test"},
        messages=[{"role": "user", "content": "hi"}],
        phase="judge_regen",
        call_site="test_timeout",
        artifact_dir=tmp_path,
    )
    from apps_rg.runtime.sections.executive_summary_regen_dispatch import (
        mark_regen_call_parse,
    )

    mark_regen_call_parse(tmp_path, outcome.call_id, parse_ok=True)
    row = regen_budget_ledger(tmp_path).calls[0]
    assert row["transport_timeout"] is True
    assert row["accepted"] is False
