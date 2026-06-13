"""Unit tests for W2.2 graph-bundle min-term backfill (typed-edge-role-facet-guardrails-a6f3d2)."""
from __future__ import annotations

from apps_rg.runtime.sections.competencies_lane_runtime import backfill_graph_bundle_min_terms
from apps_rg.runtime.sections.competencies_rigor import MIN_ITEMS_PER_CATEGORY


def _term_count(cat: dict) -> int:
    return len(cat.get("terms") or [])


def test_backfill_fills_graph_bundle_category_to_floor() -> None:
    """A graph-bundle category below the floor is filled from the bundle's vocabulary_anchors."""
    parsed = {
        "competencies": [
            {
                "category_label": "Commercial & Operating Impact",
                "competency_bundle_id": "ccb_platform_productization",
                "source_fact_ids": ["fact_engineering_platform_001"],
                "graph_skill_node_ids": ["skill_agentic_platform_productization"],
                "terms": [
                    {"term": "IP-led platform commercialization", "source_fact_ids": ["fact_engineering_platform_001"]},
                    {"term": "Operating model optimization", "source_fact_ids": ["fact_engineering_platform_001"]},
                ],
            }
        ]
    }
    backfill_graph_bundle_min_terms(parsed)
    cat = parsed["competencies"][0]
    assert _term_count(cat) >= MIN_ITEMS_PER_CATEGORY
    # The appended term is graph-backed (carries graph_skill_node_ids).
    appended = cat["terms"][-1]
    assert appended.get("graph_skill_node_ids")
    assert appended.get("support_class") == "GRAPH_BACKED_BUNDLE"
    assert appended.get("term")  # non-empty phrase from the bundle anchors


def test_backfill_noop_when_already_at_floor() -> None:
    """A category already at/above the floor is left untouched."""
    terms = [
        {"term": f"term {i}", "source_fact_ids": ["fact_x"]} for i in range(MIN_ITEMS_PER_CATEGORY)
    ]
    parsed = {
        "competencies": [
            {
                "category_label": "X",
                "competency_bundle_id": "ccb_platform_productization",
                "terms": list(terms),
            }
        ]
    }
    backfill_graph_bundle_min_terms(parsed)
    assert _term_count(parsed["competencies"][0]) == MIN_ITEMS_PER_CATEGORY


def test_backfill_noop_without_bundle_id() -> None:
    """A fact-only category (no competency_bundle_id) is NOT touched by this pass."""
    parsed = {
        "competencies": [
            {
                "category_label": "Fact Only",
                "terms": [{"term": "single term", "source_fact_ids": ["fact_x"]}],
            }
        ]
    }
    backfill_graph_bundle_min_terms(parsed)
    # Untouched — no bundle to source anchors from.
    assert _term_count(parsed["competencies"][0]) == 1


def test_backfill_does_not_duplicate_existing_anchor_terms() -> None:
    """Anchors already present as terms are not re-appended."""
    parsed = {
        "competencies": [
            {
                "category_label": "LLMOps & Reliability",
                "competency_bundle_id": "ccb_llmops_reliability",
                "source_fact_ids": ["fact_engineering_platform_003"],
                "graph_skill_node_ids": ["skill_audit_grade_observability"],
                "terms": [
                    {"term": "audit-grade observability", "source_fact_ids": ["fact_engineering_platform_003"]},
                ],
            }
        ]
    }
    backfill_graph_bundle_min_terms(parsed)
    cat = parsed["competencies"][0]
    phrases = [str(t.get("term")).lower().strip().rstrip(".") for t in cat["terms"]]
    # No duplicate of the pre-existing anchor.
    assert phrases.count("audit-grade observability") == 1
    assert _term_count(cat) >= MIN_ITEMS_PER_CATEGORY


def test_backfill_handles_categories_key_variant() -> None:
    """Works whether the data lives under 'competencies' or 'categories'."""
    parsed = {
        "categories": [
            {
                "category_label": "LLMOps & Reliability",
                "competency_bundle_id": "ccb_llmops_reliability",
                "source_fact_ids": ["fact_engineering_platform_003"],
                "graph_skill_node_ids": ["skill_audit_grade_observability"],
                "terms": [{"term": "audit-grade observability", "source_fact_ids": ["fact_engineering_platform_003"]}],
            }
        ]
    }
    backfill_graph_bundle_min_terms(parsed)
    assert _term_count(parsed["categories"][0]) >= MIN_ITEMS_PER_CATEGORY
