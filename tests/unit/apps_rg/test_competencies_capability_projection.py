"""Competencies v3 executive capability projection regressions."""

from __future__ import annotations

from apps_rg.runtime.sections.competencies_capability_projection import (
    apply_executive_capability_projection,
    is_raw_fragment_term,
    map_to_capability_synonym,
)
from apps_rg.runtime.validators.competencies_x2 import (
    run_competencies_x2_gates,
    term_supports_resume_or_graph,
)


def _parsed(categories: list[dict]) -> dict:
    return {
        "section_id": "competencies",
        "categories": categories,
        "selected_fact_plan": {"selected_fact_ids": ["bul_unify_001"]},
        "claim_ledger": [
            {
                "claim_id": "c1",
                "claim_text": "Governed agentic AI platform delivery.",
                "source_fact_ids": ["bul_unify_001"],
            }
        ],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "companion_context_used_as_proof": False,
        },
    }


def test_unified_data_platform_not_repaired_to_databricks_fundamentals():
    mapped = map_to_capability_synonym("unified data platform")
    assert mapped
    assert "fundamentals" not in mapped.lower()
    assert "databricks lakehouse fundamentals" not in (mapped or "").lower()


def test_multi_cloud_deployment_not_repaired_to_designed():
    mapped = map_to_capability_synonym("multi-cloud deployment")
    assert mapped
    assert mapped.lower() != "designed"
    assert is_raw_fragment_term("Designed")


def test_career_development_not_repaired_to_platform_leads():
    mapped = map_to_capability_synonym("career development")
    assert mapped
    assert "platform leads" not in mapped.lower()


def test_min_term_expansion_does_not_add_including_senior_engineers():
    parsed = _parsed(
        [
            {
                "category_id": "engineering_delivery_leadership",
                "category_label": "Engineering & Delivery Leadership",
                "terms": [
                    {
                        "term": "including senior engineers",
                        "source_fact_ids": ["bul_unify_001"],
                        "source_skill_ids": [],
                        "support_class": "FACT_ONLY",
                    }
                ],
            }
        ]
    )
    out = apply_executive_capability_projection(
        parsed,
        allowed_fact_ids={"bul_unify_001", "bul_unify_002", "bul_unify_003"},
        allowed_skill_ids=set(),
        resume_support_blob_lower="agentic platform orchestration governance engineering",
    )
    phrases = []
    for cat in out.get("categories") or []:
        for t in cat.get("terms") or []:
            phrases.append(str(t.get("term") or "").lower())
    assert "including senior engineers" not in phrases


def test_graph_backed_abstract_term_passes_without_exact_raw_overlap():
    term = {
        "term": "Agentic orchestration fabric",
        "source_fact_ids": [],
        "source_skill_ids": ["skill_agentic_orchestration_001"],
        "support_class": "SKILL_GRAPH_ONLY",
    }
    assert term_supports_resume_or_graph(
        term,
        allowed_fact_ids=set(),
        allowed_skill_ids={"skill_agentic_orchestration_001"},
        resume_support_blob_lower="unrelated jd briefing text only",
    )


def test_every_emitted_term_has_support_ids_after_projection():
    parsed = _parsed(
        [
            {
                "category_id": "ai_platform_leadership",
                "category_label": "AI Platform Leadership",
                "terms": [
                    {"term": "enterprise sales", "source_fact_ids": ["bul_unify_001"]},
                    {"term": "data-driven decision-making", "source_fact_ids": ["bul_unify_002"]},
                ],
            }
        ]
    )
    out = apply_executive_capability_projection(
        parsed,
        allowed_fact_ids={"bul_unify_001", "bul_unify_002", "bul_unify_003"},
        allowed_skill_ids=set(),
        resume_support_blob_lower="agentic platform governance orchestration",
    )
    comps = out.get("competencies") or []
    for cat in comps:
        for t in cat.get("terms") or []:
            sids = t.get("source_fact_ids") or []
            skills = t.get("source_skill_ids") or []
            assert sids or skills


def test_jd_and_briefing_not_proof_sources_in_schema_gate():
    parsed = _parsed([])
    parsed["jd_alignment"]["jd_used_as_proof"] = True
    results = run_competencies_x2_gates(
        competencies=[],
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="",
        bullet_texts_lower=[],
        resume_support_blob="agentic",
        allowed_fact_ids={"bul_unify_001"},
        runtime_generation_status="REAL_LLM",
    )
    schema = next(g for g in results if g.gate_id == "x2_competency_schema_valid")
    assert not schema.pass_
