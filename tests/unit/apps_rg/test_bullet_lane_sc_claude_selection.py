"""Bullet-pool lanes: Qwen self-consistency paths + Claude per-slot selection."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from apps_rg.runtime.judges.bullet_pool_claude_selector import (
    PoolSelectionResult,
    merge_bullet_selections,
    run_claude_bullet_pool_selection,
)
from apps_rg.runtime.providers.qwen_vllm_provider import ProviderResult
from apps_rg.runtime.reasoning.bullet_lane_self_consistency import (
    SelfConsistencyPath,
    bullet_lane_sc_enabled,
    self_consistency_path_count,
    temperature_ladder,
)
from apps_rg.runtime.reasoning.employment_bullet_pool import (
    SC_PATH_COUNT_BY_LANE,
    evaluate_employment_selection_quality,
    min_selection_score_for_lane,
    build_employment_targeting_context,
)
from apps_rg.runtime.reasoning.bullet_lane_generation import generate_bullet_lane_with_sc_and_claude
from apps_rg.runtime.reasoning.section_reasoning_intensity import (
    ReasoningIntensityTier,
    section_reasoning_profile,
)
from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS


def test_bullet_pool_lanes_use_distinct_profile_from_narrative() -> None:
    assert section_reasoning_profile("unify_bullets").tier is ReasoningIntensityTier.T2_QUALITY_SECTION
    assert section_reasoning_profile("unify_narrative").tier is ReasoningIntensityTier.T3_CRITICAL_SECTION
    assert (
        section_reasoning_profile("unify_bullets").self_consistency_samples
        > section_reasoning_profile("unify_narrative").self_consistency_samples
    )


def test_narrative_lanes_declare_single_path_sc() -> None:
    assert section_reasoning_profile("executive_summary").self_consistency_samples == 5.0
    assert section_reasoning_profile("unify_narrative").self_consistency_samples == 1.0


def test_temperature_ladder_respects_bounds() -> None:
    ladder = temperature_ladder(0.38, SC_PATH_COUNT_BY_LANE["unify_bullets"], bounds=(0.35, 0.55))
    assert len(ladder) == 15
    assert all(0.35 <= t <= 0.55 for t in ladder)
    assert ladder[0] < ladder[-1]


def test_bullet_lane_sc_disable_env() -> None:
    with patch.dict("os.environ", {"APPS_RG_BULLET_SC_DISABLE": "1"}):
        assert bullet_lane_sc_enabled("unify_bullets") is False


def test_merge_bullet_selections_enforces_min_score() -> None:
    paths = [
        SelfConsistencyPath(
            0,
            0.38,
            "REAL_LLM",
            "{}",
            {"bullets": [{"bullet_id": "bul_unify_001", "bullet_text": "low"}], "claim_ledger": []},
            "",
            None,
        ),
        SelfConsistencyPath(
            1,
            0.42,
            "REAL_LLM",
            "{}",
            {"bullets": [{"bullet_id": "bul_unify_001", "bullet_text": "high"}], "claim_ledger": []},
            "",
            None,
        ),
    ]
    merged, source = merge_bullet_selections(
        paths,
        [
            {"bullet_id": "bul_unify_001", "path_index": 0, "score": 0.5, "passes": True},
            {"bullet_id": "bul_unify_001", "path_index": 1, "score": 0.88, "passes": True},
        ],
        required_bullet_ids=("bul_unify_001",),
        min_score_threshold=0.72,
    )
    assert merged["bullets"][0]["bullet_text"] == "high"
    assert source["bul_unify_001"] == 1


def test_evaluate_employment_gate_requires_score_floor() -> None:
    selections = [
        {"bullet_id": bid, "path_index": 0, "score": 0.9, "passes": True}
        for bid in UNIFY_BULLET_IDS
    ]
    merged = {
        "bullets": [{"bullet_id": bid, "bullet_text": f"text {bid}"} for bid in UNIFY_BULLET_IDS],
        "claim_ledger": [],
    }
    gate = evaluate_employment_selection_quality(
        section_lane="unify_bullets",
        required_bullet_ids=UNIFY_BULLET_IDS,
        selections=selections,
        merged_parsed=merged,
        min_score=0.72,
    )
    assert gate.ok is True

    low_sel = [{"bullet_id": UNIFY_BULLET_IDS[0], "path_index": 0, "score": 0.5, "passes": True}]
    gate_fail = evaluate_employment_selection_quality(
        section_lane="unify_bullets",
        required_bullet_ids=UNIFY_BULLET_IDS,
        selections=low_sel,
        merged_parsed={"bullets": [{"bullet_id": UNIFY_BULLET_IDS[0], "bullet_text": "x"}]},
        min_score=0.72,
    )
    assert gate_fail.ok is False
    assert UNIFY_BULLET_IDS[0] in gate_fail.slots_below_threshold or UNIFY_BULLET_IDS[0] in gate_fail.slots_missing


def test_generate_singleton_when_sc_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_BULLET_SC_DISABLE", "1")

    def _stub(payload: dict, **_: object) -> ProviderResult:
        return ProviderResult(
            provider_requested="qwen_vllm",
            provider_attempted=True,
            provider_available=True,
            exact_provider_error=None,
            runtime_generation_status="REAL_LLM",
            model="m",
            raw_model_output='{"bullets":[{"bullet_id":"bul_unify_001","bullet_text":"x"}]}',
            provider_response={},
        )

    with patch(
        "apps_rg.runtime.providers.section_qwen_slice.call_qwen_vllm",
        side_effect=_stub,
    ):
        result, raw, parsed, err, meta = generate_bullet_lane_with_sc_and_claude(
            section_lane="unify_bullets",
            slot_kind="bullets",
            provider_payload={"model": "m", "messages": []},
            parse_model_json=lambda r: (json.loads(r), ""),
            normalize_parsed=lambda p: p,
        )
    assert meta["generation_mode"] == "singleton"
    assert parsed is not None
    assert result is not None


def test_claude_selection_mocked_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    paths = [
        SelfConsistencyPath(
            0,
            0.38,
            "REAL_LLM",
            "",
            {
                "bullets": [
                    {"bullet_id": "bul_ibm_001", "bullet_text": "alpha"},
                    {"bullet_id": "bul_ibm_002", "bullet_text": "beta"},
                ],
                "claim_ledger": [],
            },
            "",
            None,
        ),
    ]
    pool: PoolSelectionResult = run_claude_bullet_pool_selection(
        section_id="ibm_bullets",
        slot_kind="bullets",
        paths=paths,
        required_bullet_ids=("bul_ibm_001", "bul_ibm_002"),
        mode="mocked",
    )
    assert pool.selection_mode == "fallback_first_complete_path"
    assert len(pool.merged_parsed.get("bullets") or []) == 2


def test_self_consistency_path_count_for_competencies() -> None:
    assert self_consistency_path_count("competencies") == 4


def test_employment_bullet_path_counts() -> None:
    assert self_consistency_path_count("unify_bullets") == 15
    assert self_consistency_path_count("ibm_bullets") == 12
    assert SC_PATH_COUNT_BY_LANE["unify_bullets"] == 15
    assert SC_PATH_COUNT_BY_LANE["ibm_bullets"] == 12


def test_employment_targeting_includes_jd_briefing_and_rewrite_contract() -> None:
    ctx = build_employment_targeting_context(
        {
            "jd_text": "SVP agentic role",
            "briefing": "emphasize platform",
            "target_title": "SVP",
            "target_company": "Acme",
            "proof_pool_metadata": {"graph_ref": "skills/graph.json"},
            "selected_fact_plan": {"selection_method": "augmented_skills_graph"},
        },
        section_lane="unify_bullets",
    )
    assert "jd_text" in ctx and "briefing" in ctx
    assert ctx["rewrite_intensity_contract"] == "2_HEAVY_3_MODERATE_1_LIGHT_PROTECTED"
    assert ctx["final_bullet_count"] == 6
    assert ctx["min_selection_score"] == pytest.approx(min_selection_score_for_lane("unify_bullets"))


def test_section_profiles_unify_15_ibm_12() -> None:
    assert section_reasoning_profile("unify_bullets").self_consistency_samples == 15.0
    assert section_reasoning_profile("ibm_bullets").self_consistency_samples == 12.0
