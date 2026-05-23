"""Structured competencies min-terms expansion (x2_competencies_min_items_per_category)."""

from __future__ import annotations

from apps_rg.runtime.sections.competencies_lane_runtime import expand_structured_competencies_min_two_terms
from apps_rg.runtime.sections.competencies_rigor import MIN_ITEMS_PER_CATEGORY
from apps_rg.runtime.sections.competencies_term_phrase import term_phrase


def test_expand_structured_competencies_min_two_terms_fills_sparse_category() -> None:
    parsed: dict = {
        "competencies": [
            {
                "category_label": "Commercial & Operating Impact",
                "source_fact_ids": ["fact_revenue_ops_001"],
                "terms": [
                    {"term": "Revenue operations discipline", "source_fact_id": "fact_revenue_ops_001"},
                    {"term": "Pipeline governance", "source_fact_id": "fact_revenue_ops_001"},
                ],
            }
        ],
        "change_log": [],
    }
    bullet_rows = [
        {
            "fact_id": "fact_revenue_ops_001",
            "claim_text": "Built revenue operations cadence across enterprise GTM motions.",
            "technologies": ["forecasting", "pipeline analytics", "deal desk"],
        }
    ]
    expand_structured_competencies_min_two_terms(
        parsed,
        bullet_rows=bullet_rows,
        allowed_fact_ids={"fact_revenue_ops_001"},
        resume_support_blob_lower="revenue operations pipeline forecasting deal desk",
        bullet_texts_lower=["built revenue operations cadence across enterprise gtm motions."],
    )
    terms = parsed["competencies"][0]["terms"]
    assert len([t for t in terms if term_phrase(t)]) >= MIN_ITEMS_PER_CATEGORY
