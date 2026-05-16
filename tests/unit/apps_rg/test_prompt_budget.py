"""Unit tests for apps_rg prompt budget packing and guards."""
from __future__ import annotations

import pytest

from apps_rg.l2_recipe.pa_context_bridge import build_prompt_assembly_input_from_l2_context
from apps_rg.l2_recipe.prompt_budget import (
    PromptBudgetError,
    R0_SLOT_MARKER,
    pack_prompt_keep_schema_suffix,
    prepare_prompt_for_local_vllm,
)


def test_pack_keeps_r0_suffix_when_prefix_huge() -> None:
    tail = f"{R0_SLOT_MARKER}\n# R0 schema tail preserved\n"
    prefix = "E" * 80_000
    prompt = prefix + tail
    out, meta = pack_prompt_keep_schema_suffix(prompt, max_total_chars=len(tail) + 2500)
    assert tail in out
    assert meta["prompt_packed"] is True
    assert meta["removed_prefix_chars"] > 0


def test_prepare_prompt_raises_when_small_max_tokens_starves_completion() -> None:
    tail = f"{R0_SLOT_MARKER}\n# R0\n"
    prompt = ("p" * 8000) + tail
    with pytest.raises(PromptBudgetError) as exc:
        prepare_prompt_for_local_vllm(prompt, requested_max_tokens=512)
    assert exc.value.code == "E3_OUTPUT_BUDGET_TOO_SMALL"


def test_diagnostic_min_context_env_slims_resume(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_DIAGNOSTIC_MIN_CONTEXT", "1")
    try:
        blob = (
            '{"schema_version":"base_resume_v1.0","candidate_name":"Amit Ayer",'
            '"facts":{"employment":[{"employer":"Unify Consulting","title":"SVP"}'
            ',{"employer":"IBM","title":"Lead"}],"education":[{"degree":"BS"}]}}'
        )
        inp = build_prompt_assembly_input_from_l2_context(
            {
                "target_company": "Unify Consulting",
                "target_role": "SVP Eng",
                "master_resume_data": blob,
                "jd_data": "{}",
            }
        )
        assert "DIAGNOSTIC_MIN_CONTEXT" in inp.i0_instructions
        assert inp.e0_examples is None
        assert "Unify Consulting" in inp.c0_jd_requirements.content
        assert '"employment":[{' in inp.c0_candidate_facts.content
        assert '"IBM"' not in inp.c0_candidate_facts.content
    finally:
        monkeypatch.delenv("APPS_RG_DIAGNOSTIC_MIN_CONTEXT", raising=False)


def test_redact_endpoint_helper() -> None:
    from apps_rg.l2_recipe.provider_run_diagnostics import redact_endpoint

    assert "127.0.0.1" not in redact_endpoint("http://127.0.0.1:8000/v1")
