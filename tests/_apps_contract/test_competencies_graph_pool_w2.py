"""W2/W3 — competencies graph pool (adaptive paths -> 6-8 merge) + selector receipt wiring.

The selector receipt is OpenAI-backed; the formal competencies X1D judge is wired separately.
"""
from __future__ import annotations

import json

from apps_rg.runtime.reasoning.bullet_lane_self_consistency import SelfConsistencyPath
from apps_rg.runtime.reasoning.competencies_graph_pool import (
    COMPETENCIES_FINAL_CATEGORY_COUNT,
    COMPETENCIES_MIN_CATEGORY_COUNT,
    COMPETENCIES_SC_PATH_COUNT,
    DEFAULT_COMPETENCIES_MIN_SELECTION_SCORE,
    merge_competencies_graph_pool_top_eight,
)
from apps_rg.runtime.reasoning.employment_bullet_pool import COMPETENCIES_SC_PATH_COUNT as POOL_SC
from apps_rg.runtime.reasoning.section_reasoning_intensity import section_reasoning_profile


def _cat(label: str, terms: list[str]) -> dict:
    return {
        "category_label": label,
        "terms": [
            {
                "text": t,
                "source_fact_id": "bul_001",
                "source_fact_ids": ["bul_001"],
                "support_class": "FACT_ONLY",
            }
            for t in terms
        ],
        "source_fact_ids": ["bul_001"],
    }


def test_resolve_cli_x1d_judges_competencies_defaults_openai_chatgpt() -> None:
    from apps_rg.runtime.section_cli_defaults import resolve_cli_x1d_judges

    assert resolve_cli_x1d_judges(None, section_id="competencies") == "openai_chatgpt"


def test_competencies_sc_path_count_and_profile() -> None:
    # Two distinct knobs:
    #  * COMPETENCIES_SC_PATH_COUNT / POOL_SC — the initial deterministic selection-grouping
    #    generator. It starts at 4 and can expand toward 8 when coverage/score gates need it.
    #  * section_reasoning_profile(...).self_consistency_samples — the CREATIVE self-consistency
    #    sampling knob. Per the variance-class redesign (competencies dominant risk = "missing
    #    required anchored terms", solved by deterministic inclusion rules), this is "very low".
    assert COMPETENCIES_SC_PATH_COUNT == 4
    assert POOL_SC == 4
    prof = section_reasoning_profile("competencies")
    assert prof.self_consistency_samples == 2.0


def test_competencies_pool_x1d_judge_rows_selector_receipt_is_openai(tmp_path) -> None:
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
            "generation_mode": "model_competencies_graph_pool_adaptive_6_8_regen",
            "selection_gate": {"ok": True},
            "selection_mode": "claude_competencies_adaptive_6_8_pass",
        },
    )
    assert len(rows) == 1
    assert rows[0]["provider_key"] == "openai_chatgpt"
    assert rows[0]["judge_role"] == "competencies_graph_pool_selector"
    assert rows[0]["advisory_only"] is True
    assert rows[0]["proof_eligible_judge"] is False


def test_merge_competencies_graph_pool_top_eight_from_selections() -> None:
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
                    _cat("Platform", ["i"]),
                    _cat("Governance", ["j"]),
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
        {"category_label": "Platform", "path_index": 0, "score": 0.84, "passes": True},
        {"category_label": "Governance", "path_index": 0, "score": 0.83, "passes": True},
        {"category_label": "Extra", "path_index": 0, "score": 0.50, "passes": True},
    ]
    merged, _src = merge_competencies_graph_pool_top_eight(
        paths,
        selections,
        allowed_fact_ids={"bul_001"},
        min_score_threshold=DEFAULT_COMPETENCIES_MIN_SELECTION_SCORE,
    )
    comps = merged.get("competencies") or []
    # Seven categories are high-signal (>=0.84), so adaptive emit keeps seven and drops
    # lower-signal overflow rather than padding to the max.
    assert len(comps) == 7
    assert COMPETENCIES_MIN_CATEGORY_COUNT <= len(comps) <= COMPETENCIES_FINAL_CATEGORY_COUNT
    labels = {str(c.get("category_label")) for c in comps}
    assert "Extra" not in labels
