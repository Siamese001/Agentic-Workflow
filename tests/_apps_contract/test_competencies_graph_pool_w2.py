"""W2/W3 — competencies graph pool (10 paths → top 6 merge) + gemini_pro pool judge row."""
from __future__ import annotations

import json

from apps_rg.runtime.reasoning.bullet_lane_self_consistency import SelfConsistencyPath
from apps_rg.runtime.reasoning.competencies_graph_pool import (
    COMPETENCIES_FINAL_CATEGORY_COUNT,
    COMPETENCIES_SC_PATH_COUNT,
    merge_competencies_graph_pool_top_six,
)
from apps_rg.runtime.reasoning.employment_bullet_pool import COMPETENCIES_SC_PATH_COUNT as POOL_SC
from apps_rg.runtime.reasoning.section_reasoning_intensity import section_reasoning_profile


def _cat(label: str, terms: list[str]) -> dict:
    return {
        "category_label": label,
        "terms": [{"text": t, "source_fact_ids": ["bul_001"]} for t in terms],
        "source_fact_ids": ["bul_001"],
    }


def test_resolve_cli_x1d_judges_competencies_defaults_gemini_pro() -> None:
    from apps_rg.runtime.section_cli_defaults import resolve_cli_x1d_judges

    assert resolve_cli_x1d_judges(None, section_id="competencies") == "gemini_pro"


def test_competencies_sc_path_count_and_profile() -> None:
    assert COMPETENCIES_SC_PATH_COUNT == 10
    assert POOL_SC == 10
    prof = section_reasoning_profile("competencies")
    assert prof.self_consistency_samples == 10.0


def test_competencies_pool_x1d_judge_rows_gemini_pro_single_row(tmp_path) -> None:
    from apps_rg.runtime.reasoning.employment_bullet_pool import competencies_pool_x1d_judge_rows

    sel_path = tmp_path / "bullet_pool_selection.json"
    selections = [
        {"category_label": f"Category_{i}", "path_index": 0, "score": 0.9, "passes": True}
        for i in range(6)
    ]
    sel_path.write_text(json.dumps({"selections": selections}), encoding="utf-8")
    rows = competencies_pool_x1d_judge_rows(
        artifact_dir=tmp_path,
        section_id="competencies",
        gen_meta={
            "generation_mode": "qwen_competencies_graph_pool_claude_top_6_regen",
            "selection_gate": {"ok": True},
            "selection_mode": "claude_competencies_top_6_pass",
        },
    )
    assert len(rows) == 1
    assert rows[0]["provider_key"] == "gemini_pro"
    assert rows[0]["judge_role"] == "competencies_graph_pool_selector"


def test_merge_competencies_graph_pool_top_six_from_selections() -> None:
    paths = [
        SelfConsistencyPath(
            path_index=0,
            temperature=0.35,
            runtime_generation_status="REAL_LLM",
            raw_output="",
            parsed={
                "competencies": [
                    _cat("Leadership", ["a", "b"]),
                    _cat("Data", ["c"]),
                    _cat("Cloud", ["d"]),
                    _cat("AI", ["e"]),
                    _cat("Product", ["f"]),
                    _cat("Security", ["g"]),
                    _cat("Extra", ["h"]),
                ]
            },
            parse_error="",
            provider_result=None,
        ),
    ]
    selections = [
        {"category_label": "Leadership", "path_index": 0, "score": 0.95, "passes": True},
        {"category_label": "Data", "path_index": 0, "score": 0.90, "passes": True},
        {"category_label": "Cloud", "path_index": 0, "score": 0.88, "passes": True},
        {"category_label": "AI", "path_index": 0, "score": 0.87, "passes": True},
        {"category_label": "Product", "path_index": 0, "score": 0.86, "passes": True},
        {"category_label": "Security", "path_index": 0, "score": 0.85, "passes": True},
        {"category_label": "Extra", "path_index": 0, "score": 0.50, "passes": True},
    ]
    merged, _src = merge_competencies_graph_pool_top_six(
        paths,
        selections,
        allowed_fact_ids={"bul_001"},
        min_score_threshold=0.72,
    )
    comps = merged.get("competencies") or []
    assert len(comps) == COMPETENCIES_FINAL_CATEGORY_COUNT
    labels = {str(c.get("category_label")) for c in comps}
    assert "Extra" not in labels
