"""Declarative reasoning intensity + HTTP slice receipt hygiene for apps_rg."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from apps_rg.runtime.providers import section_qwen_slice
from apps_rg.runtime.providers.qwen_vllm_provider import ProviderResult
from apps_rg.runtime.sections.prompt_trace_reasoning import attach_reasoning_to_prompt_trace
from apps_rg.runtime.reasoning.apps_rg_http_reasoning_plan import build_apps_rg_http_reasoning_plan
from apps_rg.runtime.reasoning.section_reasoning_intensity import (
    ReasoningIntensityTier,
    executive_summary_must_dominate_lesser_sections,
    profile_to_requested_kw,
    section_reasoning_profile,
)
from agentic_core.runtime.reasoning.reasoning_control_requirement import ReceiptState
from agentic_core.runtime.reasoning.reasoning_control_resolver import resolve_gateway_receipt
from agentic_core.runtime.reasoning.transport_capabilities import TransportCapabilities


def test_executive_summary_dominates_t0_and_t2_knobs() -> None:
    executive_summary_must_dominate_lesser_sections()


def test_locked_sections_are_t0() -> None:
    assert section_reasoning_profile("education").tier is ReasoningIntensityTier.T0_LOCKED_FACT
    assert section_reasoning_profile("certifications").tier is ReasoningIntensityTier.T0_LOCKED_FACT


def test_narrative_critical_sections_map_to_t3() -> None:
    for lane in ("unify_narrative", "ibm_narrative"):
        assert section_reasoning_profile(lane).tier is ReasoningIntensityTier.T3_CRITICAL_SECTION


def test_bullet_pool_sections_map_to_t2_with_sc() -> None:
    for lane in ("competencies", "unify_bullets", "ibm_bullets"):
        prof = section_reasoning_profile(lane)
        assert prof.tier is ReasoningIntensityTier.T2_QUALITY_SECTION
    assert section_reasoning_profile("competencies").self_consistency_samples == 4.0
    assert section_reasoning_profile("unify_bullets").self_consistency_samples == 15.0
    assert section_reasoning_profile("ibm_bullets").self_consistency_samples == 12.0


def test_headline_singleton_lane_is_t0_locked_fact() -> None:
    assert section_reasoning_profile("headline").tier is ReasoningIntensityTier.T0_LOCKED_FACT


def test_ibm_narrative_single_path_and_bullets_pool() -> None:
    assert section_reasoning_profile("ibm_narrative").tier is ReasoningIntensityTier.T3_CRITICAL_SECTION
    assert section_reasoning_profile("ibm_bullets").tier is ReasoningIntensityTier.T2_QUALITY_SECTION


def test_unknown_lane_falls_through_t2_quality_not_t1_reserved() -> None:
    fake = section_reasoning_profile("nonexistent_future_lane_xyz")
    assert fake.tier is ReasoningIntensityTier.T2_QUALITY_SECTION


def test_attach_reasoning_prompt_trace_skips_when_not_qwen() -> None:
    base = {"runtime_path": "x", "provider": "mock"}
    merged = attach_reasoning_to_prompt_trace(base, provider="mock", lane_key="headline", provider_result_data={"reasoning_execution_receipt": {"ledger": []}})
    assert "reasoning_section_lane" not in merged


def test_attach_reasoning_prompt_trace_merges_for_qwen() -> None:
    base = {"a": 1}
    rec = {"quality_certification_denied": False, "ledger": []}
    out = attach_reasoning_to_prompt_trace(
        base,
        provider="qwen_vllm",
        lane_key="headline",
        provider_result_data={"reasoning_execution_receipt": rec, "model": "m"},
    )
    assert out["reasoning_section_lane"] == "headline"
    assert out["reasoning_execution_receipt"] == rec


def test_scratchpad_raises_before_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VLLM_BASE_URL", raising=False)
    orch = dict(profile_to_requested_kw(section_reasoning_profile("education")))
    bad = dict(orch)
    bad["model"] = "m"
    bad["messages"] = []
    bad["scratchpad"] = "leak"

    exc = "^scratchpad_keys_forbidden"
    with pytest.raises(ValueError, match=exc):
        section_qwen_slice.call_qwen_vllm(section_qwen_slice.tag_reasoning_lane(bad, "education"))


def test_orchestration_not_forwarded_snapshot_on_http_body() -> None:
    captured: dict = {}

    def _stub(payload: dict, **_: object) -> ProviderResult:
        captured.clear()
        captured.update(payload)
        return ProviderResult(
            provider_requested="qwen_vllm",
            provider_attempted=False,
            provider_available=False,
            exact_provider_error="stub",
            runtime_generation_status="BLOCKED",
            model=str(payload.get("model", "")),
            raw_model_output="",
            provider_response=None,
            reasoning_execution_receipt=None,
        )

    orch = dict(profile_to_requested_kw(section_reasoning_profile("ibm_bullets")))
    orch.update(
        {
            "model": "m",
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 10,
            "timeout_seconds": 1,
            "response_format": {"type": "json_object"},
            "tot_branches": float(orch["tot_branches"]),
            "tot_depth": float(orch["tot_depth"]),
            "reflexion_loops": orch["reflexion_loops"],
            "self_consistency_samples": orch["self_consistency_samples"],
        }
    )
    merged = orch  # forwarded keys stripped by slice

    with patch.object(section_qwen_slice.qwen_vllm_provider, "call_qwen_vllm", side_effect=_stub):
        res = section_qwen_slice.call_qwen_vllm(section_qwen_slice.tag_reasoning_lane(merged, "ibm_bullets"))

    assert captured.get("_reasoning_section_lane") is None
    forbidden = {"tot_branches", "tot_depth", "reflexion_loops", "self_consistency_samples", "cot_paths"}
    assert not forbidden.intersection(captured.keys())
    assert captured["temperature"] == pytest.approx(float(profile_to_requested_kw(section_reasoning_profile("ibm_bullets"))["temperature"]))
    prim = getattr(res, "reasoning_execution_receipt", None)
    assert isinstance(prim, dict)
    rows = prim.get("ledger") or []
    by_name = {r["control_name"]: r for r in rows}
    branches = by_name["tot_branches"]
    assert branches["receipt_state"] == ReceiptState.IGNORED.value
    assert ReceiptState.APPLIED.value != branches["receipt_state"]

    samples = by_name["self_consistency_samples"]
    assert samples["receipt_state"] == ReceiptState.IGNORED.value
    ref_blob = json.loads(samples["proved_reference"])
    assert ref_blob["samples_requested"] >= 3
    assert ref_blob["samples_completed"] == 1

    loops = by_name.get("reflexion_loops")
    if loops and loops.get("requested"):
        ref_loop = json.loads(loops["proved_reference"])
        assert ref_loop["loops_requested"] >= 1
        assert ref_loop["loops_completed"] == 0


def test_softened_t0_headline_allows_quality_cert_path_like_http_singleton() -> None:
    orch = dict(profile_to_requested_kw(section_reasoning_profile("headline")))
    plan = build_apps_rg_http_reasoning_plan(merged_requested_kw=orch, profile=section_reasoning_profile("headline"))
    rec = resolve_gateway_receipt(
        plan,
        TransportCapabilities(frozenset({"temperature", "max_tokens"})),
        {"temperature": float(orch["temperature"]), "max_tokens": 900},
    )
    assert rec.aggregate_blocked is False
    assert rec.quality_certification_denied is False


def test_softened_t2_allows_positive_quality_cert_aggregate_path() -> None:
    orch = dict(profile_to_requested_kw(section_reasoning_profile("ibm_bullets")))
    merged = orch
    plan = build_apps_rg_http_reasoning_plan(merged_requested_kw=merged, profile=section_reasoning_profile("ibm_bullets"))
    rec = resolve_gateway_receipt(
        plan,
        TransportCapabilities(frozenset({"temperature"})),
        {"temperature": float(merged["temperature"])},
    )
    assert rec.aggregate_blocked is False
