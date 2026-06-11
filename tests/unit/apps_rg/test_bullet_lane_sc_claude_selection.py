"""Bullet-pool lanes: Qwen self-consistency paths + Claude per-slot selection."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from apps_rg.runtime.judges.bullet_pool_claude_selector import (
    POOL_SELECTOR_SYSTEM_PROMPT,
    PoolSelectionResult,
    _call_anthropic_pool_selector,
    _parse_selections,
    merge_bullet_selections,
    run_claude_bullet_pool_selection,
)
from apps_rg.runtime.providers.provider_contract import ProviderResult
from apps_rg.runtime.reasoning.bullet_lane_self_consistency import (
    BULLET_POOL_LANES,
    SelfConsistencyPath,
    bullet_lane_sc_enabled,
    self_consistency_path_count,
    temperature_ladder,
)
from apps_rg.runtime.reasoning.employment_bullet_pool import (
    EMPLOYMENT_BULLET_JUDGE_PROVIDERS,
    SC_PATH_COUNT_BY_LANE,
    build_employment_targeting_context,
    employment_pool_x1d_judge_rows,
    evaluate_employment_selection_quality,
    is_employment_pool_generation,
    min_selection_score_for_lane,
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
    # Variance-class redesign: bullet lanes use the Claude pool selector (generation
    # variance handled by selection, not sampling) while narratives are single-path HTTP
    # with SC=4 as a floor. Distinctness is now tier + pool-vs-singleton path, not SC>SC.
    assert (
        section_reasoning_profile("unify_bullets").self_consistency_samples
        >= section_reasoning_profile("unify_narrative").self_consistency_samples
    )


def test_narrative_lanes_declare_single_path_sc() -> None:
    # Variance-class redesign: exec summary SC=5 stays dominant; narrative SC floored at 4.0
    # (was 1.0) so single-path narratives still get minimal self-consistency headroom.
    assert section_reasoning_profile("executive_summary").self_consistency_samples == 5.0
    assert section_reasoning_profile("unify_narrative").self_consistency_samples == 4.0


def test_temperature_ladder_respects_bounds() -> None:
    n_paths = SC_PATH_COUNT_BY_LANE["unify_bullets"]
    ladder = temperature_ladder(0.38, n_paths, bounds=(0.35, 0.55))
    # Variance-class alignment (2026-06): ladder length tracks the (reduced) SC path count.
    assert len(ladder) == n_paths
    assert all(0.35 <= t <= 0.55 for t in ladder)
    assert ladder[0] < ladder[-1]


def test_bullet_lane_sc_disable_env() -> None:
    with patch.dict("os.environ", {"APPS_RG_BULLET_SC_DISABLE": "1"}):
        assert bullet_lane_sc_enabled("unify_bullets") is False


def test_bullet_lane_sc_enabled_for_registered_role_bullet_lanes() -> None:
    assert {"unify_bullets", "ibm_bullets"} <= set(BULLET_POOL_LANES)
    for lane in ("unify_bullets", "ibm_bullets"):
        assert bullet_lane_sc_enabled(lane) is True


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

    def _stub(*_a: object, **_: object) -> ProviderResult:
        return ProviderResult(
            provider_requested="external_claude",
            provider_attempted=True,
            provider_available=True,
            exact_provider_error=None,
            runtime_generation_status="REAL_LLM",
            model="m",
            raw_model_output='{"bullets":[{"bullet_id":"bul_unify_001","bullet_text":"x"}]}',
            provider_response={},
        )

    with patch(
        "apps_rg.runtime.providers.section_provider_call.call_section_model_provider",
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
    # Variance-class alignment (2026-06): candidate-category pool 10 -> 8 (>= final 6).
    assert self_consistency_path_count("competencies") == 8


def test_employment_bullet_path_counts() -> None:
    # Variance-class alignment (2026-06): generation SC 15/12 -> 4 over FIXED slot count
    # (unify=6, ibm=5). Selection rigor (Claude pool selector + min_score + X2) unchanged.
    assert self_consistency_path_count("unify_bullets") == 4
    assert self_consistency_path_count("ibm_bullets") == 4
    assert SC_PATH_COUNT_BY_LANE["unify_bullets"] == 4
    assert SC_PATH_COUNT_BY_LANE["ibm_bullets"] == 4


def test_employment_targeting_includes_jd_briefing_and_pool_contract() -> None:
    ctx = build_employment_targeting_context(
        {
            "jd_text": "SVP agentic role",
            "briefing": "emphasize platform",
            "target_title": "SVP",
            "target_company": "Acme",
            "proof_pool_metadata": {"graph_ref": "skills/graph.json"},
            "selected_fact_plan": {"selection_method": "augmented_skills_graph"},
            "allowed_fact_ids": ["fact_alpha"],
        },
        section_lane="unify_bullets",
    )
    assert "jd_text" in ctx and "briefing" in ctx
    assert "rewrite_intensity" not in ctx
    # Variance-class alignment (2026-06): pool path count 15 -> 4 over fixed 6 slots.
    assert ctx["pool_path_count"] == 4
    assert ctx["final_bullet_count"] == 6
    assert ctx["min_selection_score"] == pytest.approx(min_selection_score_for_lane("unify_bullets"))
    assert ctx["allowed_fact_ids"] == ["fact_alpha"]
    assert ctx["selector_requires_valid_candidates"] is True


def test_selector_filters_candidates_outside_allowed_fact_set(tmp_path) -> None:
    paths = [
        SelfConsistencyPath(
            0,
            0.38,
            "REAL_LLM",
            "",
            {
                "bullets": [
                    {
                        "bullet_id": "bul_unify_001",
                        "bullet_text": "Source-backed good candidate.",
                        "source_fact_ids": ["fact_good"],
                    },
                    {
                        "bullet_id": "bul_unify_002",
                        "bullet_text": "Unsupported candidate.",
                        "source_fact_ids": ["fact_bad"],
                    },
                ],
                "claim_ledger": [
                    {"claim_text": "good", "source_fact_ids": ["fact_good"]},
                    {"claim_text": "bad", "source_fact_ids": ["fact_bad"]},
                ],
            },
            "",
            None,
        )
    ]
    pool = run_claude_bullet_pool_selection(
        section_id="unify_bullets",
        slot_kind="bullets",
        paths=paths,
        required_bullet_ids=("bul_unify_001", "bul_unify_002"),
        targeting_context={
            "allowed_fact_ids": ["fact_good"],
            "selector_requires_valid_candidates": True,
        },
        artifact_dir=tmp_path,
        mode="mocked",
    )
    assert pool.selection_mode == "fallback_empty"
    bullets = pool.merged_parsed.get("bullets") or []
    assert [b["bullet_id"] for b in bullets] == ["bul_unify_001"]
    receipt = json.loads((tmp_path / "bullet_pool_candidate_validity.json").read_text(encoding="utf-8"))
    assert receipt["strict"] is True
    assert receipt["paths"][0]["eligible_bullet_count"] == 1
    assert any(r["reason"] == "source_fact_id_not_allowed" for r in receipt["paths"][0]["rejections"])


def _entailment_path(idx: int, temperature: float, bullets: list[dict]) -> SelfConsistencyPath:
    return SelfConsistencyPath(
        idx,
        temperature,
        "REAL_LLM",
        "",
        {"bullets": bullets, "claim_ledger": []},
        "",
        None,
    )


_ENTAILMENT_CTX = {
    "allowed_fact_ids": ["bul_unify_001"],
    "selector_requires_valid_candidates": True,
    "slot_entailment_corpus": {
        "bul_unify_001": "Cut bespoke delivery from six months to three weeks via platform reuse."
    },
}


def test_selector_excludes_non_entailed_candidate_and_entailed_alternate_wins(tmp_path) -> None:
    """W4.3: a candidate citing the right fact_id but claiming a magnitude absent from the
    slot corpus is excluded BEFORE pool formatting; the entailed alternate wins the slot."""
    paths = [
        _entailment_path(
            0,
            0.38,
            [
                {
                    "bullet_id": "bul_unify_001",
                    "bullet_text": "Drove $25M platform revenue.",
                    "source_fact_ids": ["bul_unify_001"],
                }
            ],
        ),
        _entailment_path(
            1,
            0.42,
            [
                {
                    "bullet_id": "bul_unify_001",
                    "bullet_text": "Cut delivery time from six months to three weeks.",
                    "source_fact_ids": ["bul_unify_001"],
                }
            ],
        ),
    ]
    pool = run_claude_bullet_pool_selection(
        section_id="unify_bullets",
        slot_kind="bullets",
        paths=paths,
        required_bullet_ids=("bul_unify_001",),
        targeting_context=dict(_ENTAILMENT_CTX),
        artifact_dir=tmp_path,
        mode="mocked",
    )
    bullets = pool.merged_parsed.get("bullets") or []
    assert [b["bullet_text"] for b in bullets] == ["Cut delivery time from six months to three weeks."]
    assert pool.source_path_by_slot == {"bul_unify_001": 1}

    receipt = json.loads((tmp_path / "bullet_pool_fact_entailment.json").read_text(encoding="utf-8"))
    rounds = receipt["rounds"]
    assert len(rounds) == 1
    assert rounds[0]["operation"] == "selector_fact_entailment_exclusion"
    assert rounds[0]["bypass"] is False
    assert rounds[0]["corpus_present"] is True
    assert rounds[0]["excluded_total"] == 1
    rejection = rounds[0]["paths"][0]["rejections"][0]
    assert rejection["bullet_id"] == "bul_unify_001"
    assert rejection["reason"] == "numeric_token_not_entailed"
    assert rejection["missing_tokens"] == ["$25M"]
    assert rejection["bullet_sha16"]


def test_selector_entailment_emptied_pool_hits_strict_emptiness_return(tmp_path) -> None:
    """W4.3 required change: when exclusion empties every path's bullets, parsed=None makes
    the existing strict-emptiness return fire — no Claude call against a zero-candidate pool."""
    paths = [
        _entailment_path(
            0,
            0.38,
            [
                {
                    "bullet_id": "bul_unify_001",
                    "bullet_text": "Drove $25M platform revenue.",
                    "source_fact_ids": ["bul_unify_001"],
                }
            ],
        ),
    ]
    pool = run_claude_bullet_pool_selection(
        section_id="unify_bullets",
        slot_kind="bullets",
        paths=paths,
        required_bullet_ids=("bul_unify_001",),
        targeting_context=dict(_ENTAILMENT_CTX),
        artifact_dir=tmp_path,
        mode="mocked",
    )
    assert pool.selection_mode == "blocked_no_selector_eligible_candidates"
    assert pool.merged_parsed == {}
    assert pool.selections == []


def test_selector_entailment_emptied_slot_lands_in_selection_gate_slots_missing(tmp_path) -> None:
    ctx = {
        "allowed_fact_ids": ["bul_unify_001", "bul_unify_002"],
        "selector_requires_valid_candidates": True,
        "slot_entailment_corpus": {
            "bul_unify_001": "Platform spine delivery across enterprise programs.",
            "bul_unify_002": "Dependency graph accelerator adoption.",
        },
    }
    paths = [
        _entailment_path(
            0,
            0.38,
            [
                {
                    "bullet_id": "bul_unify_001",
                    "bullet_text": "Delivered the platform spine.",
                    "source_fact_ids": ["bul_unify_001"],
                },
                {
                    "bullet_id": "bul_unify_002",
                    "bullet_text": "Drove $99M accelerator revenue.",
                    "source_fact_ids": ["bul_unify_002"],
                },
            ],
        ),
    ]
    pool = run_claude_bullet_pool_selection(
        section_id="unify_bullets",
        slot_kind="bullets",
        paths=paths,
        required_bullet_ids=("bul_unify_001", "bul_unify_002"),
        targeting_context=ctx,
        artifact_dir=tmp_path,
        mode="mocked",
    )
    merged_ids = [b["bullet_id"] for b in (pool.merged_parsed.get("bullets") or [])]
    assert merged_ids == ["bul_unify_001"]
    gate = evaluate_employment_selection_quality(
        section_lane="unify_bullets",
        required_bullet_ids=("bul_unify_001", "bul_unify_002"),
        selections=[
            {"bullet_id": "bul_unify_001", "path_index": 0, "score": 0.9, "passes": True},
            {"bullet_id": "bul_unify_002", "path_index": 0, "score": 0.9, "passes": True},
        ],
        merged_parsed=pool.merged_parsed,
        min_score=0.72,
    )
    assert "bul_unify_002" in gate.slots_missing


def test_selector_entailment_bypass_env_restores_pass_through(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APPS_RG_SELECTOR_FACT_ENTAILMENT_BYPASS", "1")
    paths = [
        _entailment_path(
            0,
            0.38,
            [
                {
                    "bullet_id": "bul_unify_001",
                    "bullet_text": "Drove $25M platform revenue.",
                    "source_fact_ids": ["bul_unify_001"],
                }
            ],
        ),
    ]
    pool = run_claude_bullet_pool_selection(
        section_id="unify_bullets",
        slot_kind="bullets",
        paths=paths,
        required_bullet_ids=("bul_unify_001",),
        targeting_context=dict(_ENTAILMENT_CTX),
        artifact_dir=tmp_path,
        mode="mocked",
    )
    bullets = pool.merged_parsed.get("bullets") or []
    assert [b["bullet_text"] for b in bullets] == ["Drove $25M platform revenue."]
    receipt = json.loads((tmp_path / "bullet_pool_fact_entailment.json").read_text(encoding="utf-8"))
    assert receipt["rounds"][0]["bypass"] is True
    assert receipt["rounds"][0]["excluded_total"] == 0


def test_selector_entailment_fail_open_when_corpus_missing(tmp_path) -> None:
    paths = [
        _entailment_path(
            0,
            0.38,
            [
                {
                    "bullet_id": "bul_unify_001",
                    "bullet_text": "Drove $25M platform revenue.",
                    "source_fact_ids": ["bul_unify_001"],
                }
            ],
        ),
    ]
    pool = run_claude_bullet_pool_selection(
        section_id="unify_bullets",
        slot_kind="bullets",
        paths=paths,
        required_bullet_ids=("bul_unify_001",),
        targeting_context={
            "allowed_fact_ids": ["bul_unify_001"],
            "selector_requires_valid_candidates": True,
        },
        artifact_dir=tmp_path,
        mode="mocked",
    )
    bullets = pool.merged_parsed.get("bullets") or []
    assert [b["bullet_text"] for b in bullets] == ["Drove $25M platform revenue."]
    receipt = json.loads((tmp_path / "bullet_pool_fact_entailment.json").read_text(encoding="utf-8"))
    assert receipt["rounds"][0]["corpus_present"] is False
    assert receipt["rounds"][0]["excluded_total"] == 0


def test_targeting_context_carries_slot_entailment_corpus() -> None:
    ctx = build_employment_targeting_context(
        {
            "jd_text": "SVP agentic role",
            "briefing": "emphasize platform",
            "allowed_fact_ids": ["bul_unify_001"],
            "selected_fact_plan": {
                "selection_method": "augmented_skills_graph",
                "facts": [
                    {
                        "fact_id": "bul_unify_001",
                        "claim_text": "Cut bespoke delivery from six months to three weeks.",
                        "metric_raw": "",
                    }
                ],
            },
        },
        section_lane="unify_bullets",
    )
    corpus = ctx["slot_entailment_corpus"]
    assert "bul_unify_001" in corpus
    assert "Cut bespoke delivery from six months to three weeks." in corpus["bul_unify_001"]


def test_section_profiles_unify_15_ibm_12() -> None:
    # Variance-class alignment (2026-06): profile SC for bullet lanes is 4.0 (was 15/12);
    # generation variance is handled by the Claude pool selector + X2 gates, not sampling.
    assert section_reasoning_profile("unify_bullets").self_consistency_samples == 4.0
    assert section_reasoning_profile("ibm_bullets").self_consistency_samples == 4.0


def test_employment_pool_generation_mode_detected() -> None:
    assert is_employment_pool_generation({"generation_mode": "qwen_employment_pool_claude_top_n_regen"})
    assert not is_employment_pool_generation({"generation_mode": "singleton"})


def test_employment_bullet_rubric_not_exec_summary_dimensions() -> None:
    from apps_rg.runtime.judges.employment_bullet_judge_rubric import (
        FORBIDDEN_EXEC_SUMMARY_DIMENSION_IDS,
        assert_no_exec_summary_dimensions,
        employment_bullet_dimensions,
        pool_selector_dimension_ids,
    )
    from apps_rg.runtime.judges.ibm_bullets_x1d import IBM_RUBRIC
    from apps_rg.runtime.judges.unify_bullets_x1d import UNIFY_RUBRIC

    assert_no_exec_summary_dimensions("unify_bullets")
    assert_no_exec_summary_dimensions("ibm_bullets")
    unify_ids = {d.dimension_id for d in employment_bullet_dimensions("unify_bullets")}
    ibm_ids = {d.dimension_id for d in employment_bullet_dimensions("ibm_bullets")}
    assert not unify_ids & FORBIDDEN_EXEC_SUMMARY_DIMENSION_IDS
    assert not ibm_ids & FORBIDDEN_EXEC_SUMMARY_DIMENSION_IDS
    assert "bullet_line_discipline" in unify_ids
    assert "foundation_enterprise_credibility" in ibm_ids
    assert "executive_signal" not in UNIFY_RUBRIC
    assert "synthesis_quality" not in IBM_RUBRIC
    assert "claim_ledger_grounding" in pool_selector_dimension_ids("unify_bullets")


def test_employment_pool_x1d_is_single_claude_judge(tmp_path) -> None:
    gen_meta = {
        "generation_mode": "qwen_employment_pool_claude_top_n_regen",
        "selection_gate": {"ok": True},
        "selection_mode": "claude_employment_top_n_pass",
    }
    (tmp_path / "bullet_pool_selection.json").write_text(
        json.dumps(
            {
                "selections": [
                    {"bullet_id": bid, "score": 0.85, "passes": True, "path_index": i}
                    for i, bid in enumerate(UNIFY_BULLET_IDS)
                ]
            }
        ),
        encoding="utf-8",
    )
    rows = employment_pool_x1d_judge_rows(
        artifact_dir=tmp_path,
        section_id="unify_bullets",
        gen_meta=gen_meta,
    )
    assert len(rows) == 1
    assert rows[0]["provider_key"] == "anthropic_claude"
    assert rows[0]["pass"] is True
    assert rows[0]["judge_role"] == "employment_bullet_pool_selector"
    assert list(EMPLOYMENT_BULLET_JUDGE_PROVIDERS) == ["anthropic_claude"]


# ---------------------------------------------------------------------------
# Bug:BulletPoolSelectorDualJsonObjects — regression coverage (2026-06-11)
#
# Live failure (reproduced twice: AIG full-run attempt4 + patch-run 2, ibm_bullets):
# claude-sonnet-4-6 obeyed the old X1D rubric system prompt IN ADDITION to the pool-selection
# user prompt and returned TWO top-level JSON objects (rubric verdict, blank line, selections).
# _extract_json_from_text raised "Extra data" on every strategy -> _parse_selections returned
# None -> BLOCKED_RESPONSE_PARSE_ERROR "Pool selector JSON missing selections array" ->
# selection_mode=fallback_first_complete_path -> selections=0 -> selection gate
# all-slots-missing -> synthetic decisive judge fail -> X3_BLOCK.
# ---------------------------------------------------------------------------

# EXACT live assistant text from
# artifacts/apps_rg/e2e_aig_verify/attempt4_20260610_2329/modular_r4/sections/ibm_bullets/real/
#   ibm_bullets_20260611_125552/x1d_anthropic_claude_provider_response_raw_20260611_130358_394.json
# (content[0].text verbatim; stop_reason=end_turn, output_tokens=1360 — NOT truncation).
_LIVE_DUAL_OBJECT_SELECTOR_RESPONSE = """{"score_scale":"0_to_5","score":0.0,"threshold":4.0,"pass":true,"decisive_failure":false,"findings":["bul_ibm_001 best variant is PATH 2/4/5 (Salesforce pipeline analytics, $10M ARR, no unify/runtime vocab, clean outcome)","bul_ibm_002 best variant is PATH 4 (budget dashboards, microservices, cost optimization, no stuffing, clean discipline)","bul_ibm_003 best variant is PATH 4/5 (M&A due diligence, synergy models, CFO-level, integration costs/revenue, grounded)","bul_ibm_004 best variant is PATH 4 (Fortune 500, monolithic to containerized microservices, AWS/Kubernetes, risk/compliance/data, cloud-native governed analytics)","bul_ibm_005 best variant is PATH 4 (IBM-AWS alliance P&L, AI co-sell frameworks, 20% joint revenue, concise, no stuffing)"],"cited_sentence_indexes":[],"remediation_suggestions":[],"dimension_verdicts":{"claim_ledger_grounding":{"pass":true,"severity":"none","codes":["all five bullets grounded in skills-graph facts: Salesforce GTM, budget dashboards, M&A due diligence, legacy modernization, IBM-AWS alliance"]},"bullet_line_discipline":{"pass":true,"severity":"none","codes":["all selected variants are single-line, action-verb-led, outcome-terminated, no run-on constructions"]},"jd_briefing_targeting_discipline":{"pass":true,"severity":"none","codes":["JD phrases not copied verbatim; bullets emphasize financial-services transformation, cloud-native, AI co-sell, M&A — aligned to AIG targeting"]},"keyword_discipline_without_stuffing":{"pass":true,"severity":"none","codes":["Salesforce, microservices, Kubernetes, AWS, containerized, ARR, P&L — relevant and not over-stacked"]},"cross_bullet_outcome_diversity":{"pass":true,"severity":"none","codes":["GTM revenue, cost optimization, M&A investment thesis, cloud modernization, alliance P&L — five distinct outcome types"]},"foundation_enterprise_credibility":{"pass":true,"severity":"none","codes":["Fortune 500 financial institutions, CFO-level buyers, IBM-AWS alliance, enterprise-scope M&A — credible enterprise signals"]},"no_unify_runtime_vocabulary":{"pass":true,"severity":"none","codes":["no unify, runtime, agentic, or disallowed vocabulary present in any selected variant"]}}}

{"selections":[{"bullet_id":"bul_ibm_001","path_index":4,"score":0.84,"passes":true,"rationale":"PATH 4 is clean and concise: 'Architected Salesforce-driven pipeline analytics to systematically prioritize high-potential enterprise deals, refining GTM strategies across the financial-services portfolio and generating $10M in new annual recurring revenue.' Strong claim_ledger_grounding ($10M ARR, Salesforce), no stuffing, no unify/runtime vocab, single tight line, outcome-terminated. Scores PATH 2 and 5 equally but PATH 4 hyphenates financial-services consistently and avoids the slightly weaker 'refining GTM strategies' placement of PATH 5."},{"bullet_id":"bul_ibm_002","path_index":4,"score":0.83,"passes":true,"rationale":"PATH 4: 'Deployed transparent budget dashboards and microservices architecture for senior finance teams to surface underused resource pools, enabling data-driven reallocation decisions and measurable cost optimization across enterprise cloud investments.' Best balance of claim grounding (dashboards, microservices, cost optimization), no keyword stuffing, clean line discipline, CFO/finance stakeholder credibility, and no disallowed vocabulary."},{"bullet_id":"bul_ibm_003","path_index":4,"score":0.85,"passes":true,"rationale":"PATH 4: 'Led enterprise-scope M&A technology due diligence and built synergy models quantifying integration costs and revenue opportunities, equipping CFO-level buyers with executive value propositions to support go-to-market investment decisions.' Tightest construction across paths — dual outcomes (costs + revenue), CFO-level credibility, no JD phrase copying, no stuffing, grounded in skills-graph M&A due diligence fact."},{"bullet_id":"bul_ibm_004","path_index":4,"score":0.86,"passes":true,"rationale":"PATH 4: 'Directed large-scale legacy modernization programs for Fortune 500 financial institutions, replacing monolithic risk calculation engines with containerized microservices on AWS and Kubernetes to enable cloud-native governed analytics across risk, compliance, and data domains.' Strongest variant — Fortune 500 credibility, specific technical transformation (monolithic→containerized), named platforms (AWS, Kubernetes), governed analytics outcome, no unify/runtime vocab, no stuffing."},{"bullet_id":"bul_ibm_005","path_index":4,"score":0.84,"passes":true,"rationale":"PATH 4: 'Owned P&L accountability for the IBM-AWS financial services alliance and designed AI-driven co-sell frameworks that expanded joint revenue by 20% across cloud transformation pursuits.' Most concise variant — P&L accountability, named alliance (IBM-AWS), quantified outcome (20%), AI co-sell grounded in skills graph, no disallowed vocabulary, no stuffing, clean line discipline."}],"pool_summary":{"paths_scored":7,"final_bullet_count":5,"min_score_threshold":0.72,"selector":"anthropic_claude"}}"""


def test_parse_selections_recovers_selections_from_live_dual_object_response() -> None:
    """The exact live raw response (rubric object + selections object) must parse."""
    doc = _parse_selections(_LIVE_DUAL_OBJECT_SELECTOR_RESPONSE)
    assert isinstance(doc, dict)
    selections = doc.get("selections")
    assert isinstance(selections, list) and len(selections) == 5
    assert [s["bullet_id"] for s in selections] == [
        "bul_ibm_001",
        "bul_ibm_002",
        "bul_ibm_003",
        "bul_ibm_004",
        "bul_ibm_005",
    ]
    # Every live selection met the 0.72 floor — the block was purely a parse failure.
    assert all(float(s["score"]) >= 0.72 and s["passes"] is True for s in selections)
    assert doc["pool_summary"]["selector"] == "anthropic_claude"
    assert doc["pool_summary"]["min_score_threshold"] == pytest.approx(0.72)
    # The rubric verdict object must NOT be the doc the selector consumes.
    assert "dimension_verdicts" not in doc


def test_parse_selections_single_object_and_brace_bearing_rationales_still_parse() -> None:
    single = (
        '{"selections":[{"bullet_id":"bul_ibm_001","path_index":1,"score":0.8,"passes":true,'
        '"rationale":"keeps {braces} and \\"quotes\\" inside strings"}],'
        '"pool_summary":{"selector":"anthropic_claude"}}'
    )
    doc = _parse_selections(single)
    assert isinstance(doc, dict)
    assert doc["selections"][0]["bullet_id"] == "bul_ibm_001"
    # Dual-object variant with braces/escapes inside string values exercises the
    # balanced-span scanner directly (direct json.loads fails with Extra data).
    dual = '{"score_scale":"0_to_5","pass":true}\n\n' + single
    doc2 = _parse_selections(dual)
    assert isinstance(doc2, dict)
    assert doc2["selections"][0]["rationale"] == 'keeps {braces} and "quotes" inside strings'


def test_parse_selections_recovers_from_fenced_dual_objects() -> None:
    fenced = "```json\n" + _LIVE_DUAL_OBJECT_SELECTOR_RESPONSE + "\n```"
    doc = _parse_selections(fenced)
    assert isinstance(doc, dict)
    assert isinstance(doc.get("selections"), list) and len(doc["selections"]) == 5


def test_parse_selections_rubric_only_object_keeps_legacy_dict_result() -> None:
    """Shape A (rubric-only, zero selections — 034411 both rounds): legacy behavior is to
    return the parsed dict; upstream then sees selections=[] and the selection gate stays
    the honest arbiter. This test pins that we did not silently change Shape A semantics."""
    rubric_only = _LIVE_DUAL_OBJECT_SELECTOR_RESPONSE.split("\n\n", 1)[0]
    doc = _parse_selections(rubric_only)
    assert isinstance(doc, dict)
    assert "selections" not in doc
    assert doc["score_scale"] == "0_to_5"


def test_parse_selections_fails_closed_on_unusable_text() -> None:
    assert _parse_selections("") is None
    assert _parse_selections("I cannot evaluate this pool.") is None
    assert _parse_selections("{not json at all") is None


def test_pool_selector_system_prompt_is_selection_schema_not_rubric() -> None:
    """Root-cause guard: the selector call must never re-anchor on the X1D rubric schema."""
    import inspect

    assert '"selections"' in POOL_SELECTOR_SYSTEM_PROMPT
    assert '"pool_summary"' in POOL_SELECTOR_SYSTEM_PROMPT
    for rubric_token in ("score_scale", "dimension_verdicts"):
        # Named only as forbidden output, never as the mandated shape.
        assert f"no {rubric_token}" in POOL_SELECTOR_SYSTEM_PROMPT
    src = inspect.getsource(_call_anthropic_pool_selector)
    assert "POOL_SELECTOR_SYSTEM_PROMPT" in src
    assert "build_x1d_judge_system_prompt" not in src
