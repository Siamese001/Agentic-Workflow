"""W4 — competencies graph_8x8 pool (8 paths -> 8 categories -> single gemini_pro X1D)."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from apps_rg.runtime.judges.bullet_pool_claude_selector import (
    PoolSelectionResult,
    run_claude_bullet_pool_selection,
)
from apps_rg.runtime.providers.provider_contract import ProviderResult
from apps_rg.runtime.reasoning.bullet_lane_self_consistency import SelfConsistencyPath
from apps_rg.runtime.reasoning.bullet_lane_generation import generate_bullet_lane_with_sc_and_claude
from apps_rg.runtime.reasoning.competencies_graph_pool import (
    COMPETENCIES_CANDIDATE_CATEGORY_COUNT,
    COMPETENCIES_FINAL_CATEGORY_COUNT,
    COMPETENCIES_SC_PATH_COUNT,
    build_competencies_targeting_context,
    evaluate_competencies_selection_quality,
    is_competencies_pool_generation,
    min_competencies_selection_score,
)
from apps_rg.runtime.reasoning.employment_bullet_pool import (
    competencies_pool_x1d_judge_rows,
    sc_path_count_for_lane,
)
from apps_rg.runtime.sections.section_product_shape_ssot import section_product_shape


def _cat(label: str, terms: list[str]) -> dict:
    return {
        "category_label": label,
        "terms": [{"text": t, "source_fact_ids": ["bul_001"]} for t in terms],
        "source_fact_ids": ["bul_001"],
    }


def _path_with_categories(
    path_index: int,
    n_categories: int = COMPETENCIES_FINAL_CATEGORY_COUNT,
) -> SelfConsistencyPath:
    return SelfConsistencyPath(
        path_index=path_index,
        temperature=0.35 + path_index * 0.01,
        runtime_generation_status="REAL_LLM",
        raw_output="",
        parsed={
            "competencies": [
                _cat(f"Category_{path_index}_{i}", [f"t{i}a", f"t{i}b"])
                for i in range(n_categories)
            ],
            "claim_ledger": [],
        },
        parse_error="",
        provider_result=None,
    )


def test_competencies_pool_generation_mode_detected() -> None:
    assert is_competencies_pool_generation(
        {"generation_mode": "qwen_competencies_graph_pool_claude_top_8_regen"}
    )
    assert not is_competencies_pool_generation({"generation_mode": "singleton"})


def test_sc_path_count_and_targeting_context_graph_8x8() -> None:
    # Variance-class alignment (2026-06): candidate-category pool is the final exact 8.
    assert sc_path_count_for_lane("competencies") == COMPETENCIES_SC_PATH_COUNT == 8
    ctx = build_competencies_targeting_context(
        {
            "target_title": "SVP",
            "target_company": "Acme",
            "jd_text": "agentic AI",
            "briefing": "platform",
            "proof_pool_metadata": {
                "graph_ref": "artifacts/skills/graph.json",
                "proof_pool_type": "augmented_skills_graph",
                "selected_skill_rows": [{"skill_id": "sk_graph_001"}],
            },
            "selected_fact_plan": {"selection_method": "augmented_skills_graph"},
        },
        allowed_fact_ids={"bul_001"},
        allowed_skill_ids={"sk_graph_001"},
    )
    assert ctx["candidate_category_count"] == COMPETENCIES_CANDIDATE_CATEGORY_COUNT
    assert ctx["final_category_count"] == COMPETENCIES_FINAL_CATEGORY_COUNT
    assert ctx["pool_path_count"] == 8
    assert ctx["proof_pool_type"] == "augmented_skills_graph"
    assert ctx["selection_model"] == "graph_8x8_v1"


def test_section_product_shape_competencies_exactly_eight() -> None:
    shape = section_product_shape("competencies")
    assert "x2_competencies_min_category_count" in shape.required_gate_ids
    assert "graph_8x8" in shape.shape_summary


def test_evaluate_competencies_gate_requires_eight_passing_categories() -> None:
    labels = [f"Cat_{i}" for i in range(COMPETENCIES_FINAL_CATEGORY_COUNT)]
    selections = [
        {"category_label": lab, "path_index": 0, "score": 0.9, "passes": True} for lab in labels
    ]
    merged = {"competencies": [_cat(lab, ["a", "b"]) for lab in labels]}
    gate = evaluate_competencies_selection_quality(
        selections=selections,
        merged_parsed=merged,
        min_score=min_competencies_selection_score(),
    )
    assert gate.ok is True
    assert gate.categories_in_merged == COMPETENCIES_FINAL_CATEGORY_COUNT


def test_claude_competencies_selection_mocked_emits_eight_categories() -> None:
    paths = [_path_with_categories(0)]
    pool: PoolSelectionResult = run_claude_bullet_pool_selection(
        section_id="competencies",
        slot_kind="competencies",
        paths=paths,
        targeting_context={
            "allowed_fact_ids": ["bul_001"],
            "allowed_skill_ids": [],
            "resume_support_blob_lower": "bul_001 alpha beta",
        },
        mode="mocked",
    )
    assert pool.selection_mode == "competencies_graph_top_8_heuristic"
    comps = pool.merged_parsed.get("competencies") or []
    assert len(comps) == COMPETENCIES_FINAL_CATEGORY_COUNT


def test_generate_competencies_graph_pool_lane_mocked(monkeypatch: pytest.MonkeyPatch) -> None:
    paths = [_path_with_categories(i, n_categories=COMPETENCIES_FINAL_CATEGORY_COUNT) for i in range(8)]

    def _fake_paths(**_: object) -> tuple[list[SelfConsistencyPath], ProviderResult]:
        return paths, ProviderResult(
            provider_requested="qwen_vllm",
            provider_attempted=True,
            provider_available=True,
            exact_provider_error=None,
            runtime_generation_status="REAL_LLM",
            model="stub",
            raw_model_output="{}",
            provider_response={},
        )

    monkeypatch.setattr(
        "apps_rg.runtime.reasoning.bullet_lane_generation.run_qwen_self_consistency_paths",
        _fake_paths,
    )

    result, raw, parsed, err, meta = generate_bullet_lane_with_sc_and_claude(
        section_lane="competencies",
        slot_kind="competencies",
        provider_payload={"model": "stub", "messages": []},
        parse_model_json=lambda r: (json.loads(r) if r.strip().startswith("{") else None, ""),
        normalize_parsed=lambda p: p,
        targeting_context={"allowed_fact_ids": ["bul_001"], "resume_support_blob_lower": ""},
        judge_mode="mocked",
    )
    assert err == ""
    assert is_competencies_pool_generation(meta)
    assert meta["initial_path_count"] == 8
    assert meta["final_category_count"] == COMPETENCIES_FINAL_CATEGORY_COUNT
    assert parsed is not None
    assert len(parsed.get("competencies") or []) == COMPETENCIES_FINAL_CATEGORY_COUNT
    assert result is not None


def test_competencies_pool_x1d_row_from_generation_meta(tmp_path) -> None:
    selections = [
        {"category_label": f"C{i}", "path_index": 0, "score": 0.88, "passes": True}
        for i in range(COMPETENCIES_FINAL_CATEGORY_COUNT)
    ]
    (tmp_path / "bullet_pool_selection.json").write_text(
        json.dumps({"selections": selections}),
        encoding="utf-8",
    )
    gen_meta = {
        "generation_mode": "qwen_competencies_graph_pool_claude_top_8_regen",
        "selection_gate": {"ok": True, "categories_in_merged": COMPETENCIES_FINAL_CATEGORY_COUNT},
        "selection_mode": "claude_competencies_top_8_pass",
    }
    rows = competencies_pool_x1d_judge_rows(
        artifact_dir=tmp_path,
        section_id="competencies",
        gen_meta=gen_meta,
    )
    assert len(rows) == 1
    assert rows[0]["provider_key"] == "gemini_pro"
    assert rows[0]["judge_role"] == "competencies_graph_pool_selector"


def test_apply_executive_capability_projection_trims_to_eight_emit() -> None:
    from apps_rg.runtime.sections.competencies_capability_projection import (
        apply_executive_capability_projection,
    )
    from apps_rg.runtime.sections.competencies_rigor import MAX_CATEGORY_COUNT

    parsed = {
        "competencies": [
            _cat("Technology Strategy & Innovation", ["roadmap", "portfolio"]),
            _cat("AI Platform Leadership", ["graphrag", "orchestration"]),
            _cat("Data & Analytics Modernization", ["lakehouse", "catalog"]),
            _cat("Governance, Risk & Compliance", ["lineage", "policy"]),
            _cat("Engineering & Delivery Leadership", ["scale-out", "sre"]),
            _cat("Commercial & Operating Impact", ["gtm", "revenue"]),
            _cat("LLMOps & Reliability", ["evaluation", "telemetry"]),
            _cat("Distributed Infrastructure", ["lakehouse", "streaming"]),
        ],
        "change_log": [],
    }
    out = apply_executive_capability_projection(
        parsed,
        allowed_fact_ids={"bul_001"},
        allowed_skill_ids={"sk_graph_001"},
        skill_rows_by_id={
            "sk_graph_001": {"skill_id": "sk_graph_001", "canonical_name": "GraphRAG"}
        },
        resume_support_blob_lower="bul_001 graphrag orchestration",
    )
    comps = out.get("competencies") or []
    assert len(comps) == MAX_CATEGORY_COUNT
    assert len(out.get("categories") or []) == MAX_CATEGORY_COUNT


def test_canonical_competencies_cli_uses_gemini_pro_only() -> None:
    from apps_rg.runtime.internal.generated_lane_rollup import canonical_lane_command

    cmd = canonical_lane_command("competencies")
    assert "--x1d-judges gemini_pro" in cmd
    assert "openai_chatgpt" not in cmd
    assert "anthropic_claude" not in cmd
