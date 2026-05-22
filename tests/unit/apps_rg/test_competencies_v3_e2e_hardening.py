"""E2E-style hardening: weak LLM fixtures through full v3 post-LLM pipeline + critical X2 gates."""

from __future__ import annotations

from apps_rg.runtime.sections.competencies_capability_projection import (
    finalize_competencies_v3_output,
    run_competencies_v3_post_llm_pipeline,
)
from apps_rg.runtime.sections.competencies_lane_runtime import (
    build_resume_support_blob,
    collapse_duplicate_competency_terms,
    collect_employment_bullets,
    load_base_resume,
)
from apps_rg.runtime.sections.competencies_rigor import MIN_ITEMS_PER_CATEGORY
from apps_rg.runtime.sections.competencies_v3_contract import load_executive_capability_taxonomy
from apps_rg.runtime.validators.competencies_x2 import run_competencies_x2_gates
from tests.unit.apps_rg.section_rigor.unify_ibm_lane_fixtures import assert_critical_gates_pass


def _base_context() -> tuple[list[dict], set[str], list[str], str]:
    base, _, _ = load_base_resume()
    rows, allowed, bullet_lowers = collect_employment_bullets(base)
    blob = build_resume_support_blob(rows, "")
    return rows, allowed, bullet_lowers, blob


def _brown_weak_llm_v3_payload() -> dict:
    """Mimics Brown & Brown full-run weak competencies output (fragments, credentials, sparse)."""
    return {
        "section_id": "competencies",
        "categories": [
            {
                "category_label": "Data Platforms",
                "terms": [
                    {"term": "Databricks Lakehouse Fundamentals", "source_fact_ids": ["fact_certs_001"]},
                    {"term": "unified data platform", "source_fact_ids": ["bul_unify_001"]},
                    {"term": "designed", "source_fact_ids": ["bul_unify_002"]},
                ],
            },
            {
                "category_label": "Engineering Leadership",
                "terms": [
                    {"term": "platform leads", "source_fact_ids": ["bul_unify_003"]},
                    {"term": "including senior engineers", "source_fact_ids": ["bul_unify_003"]},
                ],
            },
            {
                "category_label": "Commercial & Operating Impact",
                "terms": [
                    {"term": "enterprise sales", "source_fact_ids": ["bul_unify_004"]},
                    {"term": "data-driven decision-making", "source_fact_ids": ["bul_unify_004"]},
                ],
            },
            {
                "category_label": "Random Label",
                "terms": [{"term": "cataloging", "source_fact_ids": ["bul_ibm_001"]}],
            },
        ],
        "competencies": [],
        "selected_fact_plan": {"selected_fact_ids": []},
        "claim_ledger": [
            {
                "claim_id": "c1",
                "claim_text": "Designed governed agentic AI platform delivery.",
                "source_fact_ids": ["bul_unify_001"],
            }
        ],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "companion_context_used_as_proof": False,
        },
        "change_log": [],
    }


def _run_critical_gates(parsed: dict, *, allowed: set[str], blob: str, bullet_lowers: list[str]) -> list:
    competencies = parsed.get("competencies") or []
    return run_competencies_x2_gates(
        competencies=competencies,
        parsed_output=parsed,
        claim_ledger=parsed.get("claim_ledger") or [],
        jd_text="",
        bullet_texts_lower=bullet_lowers,
        resume_support_blob=blob,
        allowed_fact_ids=allowed,
        runtime_generation_status="REAL_LLM",
    )


def test_full_post_llm_pipeline_passes_all_competencies_critical_gates() -> None:
    rows, allowed, bullet_lowers, blob = _base_context()
    parsed = _brown_weak_llm_v3_payload()
    parsed["selected_fact_plan"] = {"selected_fact_ids": sorted(allowed)[:12]}
    out = run_competencies_v3_post_llm_pipeline(
        parsed,
        bullet_rows=rows,
        allowed_fact_ids=allowed,
        resume_support_blob=blob,
        c0_proof_blob=blob,
        bullet_texts_lower=bullet_lowers,
    )
    tax = load_executive_capability_taxonomy()
    assert len(out.get("categories") or []) >= int(tax.get("min_categories") or 6)
    for cat in out.get("categories") or []:
        terms = [t for t in (cat.get("terms") or []) if isinstance(t, dict)]
        assert len(terms) >= MIN_ITEMS_PER_CATEGORY, cat.get("category_label")
    gates = _run_critical_gates(out, allowed=allowed, blob=blob, bullet_lowers=bullet_lowers)
    assert_critical_gates_pass("competencies", gates)


def test_finalize_recovers_after_collapse_leaves_sparse_categories() -> None:
    rows, allowed, bullet_lowers, blob = _base_context()
    parsed = _brown_weak_llm_v3_payload()
    collapse_duplicate_competency_terms(parsed, rows, blob)
    out = finalize_competencies_v3_output(
        parsed,
        allowed_fact_ids=allowed,
        allowed_skill_ids=set(),
        skill_rows_by_id={},
        resume_support_blob_lower=blob,
    )
    for cat in out.get("categories") or []:
        terms = [t for t in (cat.get("terms") or []) if isinstance(t, dict)]
        assert len(terms) >= MIN_ITEMS_PER_CATEGORY
    phrases = []
    for cat in out.get("categories") or []:
        for t in cat.get("terms") or []:
            if isinstance(t, dict):
                phrases.append(str(t.get("term") or "").lower())
    assert "databricks lakehouse fundamentals" not in phrases
    assert "including senior engineers" not in phrases
    gates = _run_critical_gates(out, allowed=allowed, blob=blob, bullet_lowers=bullet_lowers)
    assert_critical_gates_pass("competencies", gates)


def test_finalize_collapses_cross_category_near_duplicate_terms() -> None:
    """Shorter near-duplicate is dropped when a longer variant exists (full-run graphrag pattern)."""
    rows, allowed, _, blob = _base_context()
    parsed = {
        "categories": [
            {
                "category_id": "tech_strategy_innovation",
                "category_label": "Technology Strategy & Innovation",
                "terms": [
                    {"term": "GraphRAG retrieval", "source_fact_ids": ["bul_unify_001"]},
                    {"term": "Deterministic routing", "source_fact_ids": ["bul_unify_002"]},
                    {"term": "Multi-agent orchestration", "source_fact_ids": ["bul_unify_003"]},
                ],
            },
            {
                "category_id": "ai_platform_leadership",
                "category_label": "AI Platform Leadership",
                "terms": [
                    {"term": "GraphRAG retrieval engineering", "source_fact_ids": ["bul_unify_001"]},
                    {"term": "Policy-aware routing controls", "source_fact_ids": ["bul_unify_002"]},
                    {"term": "Governed agentic AI platform architecture", "source_fact_ids": ["bul_unify_003"]},
                ],
            },
        ],
        "competencies": [],
        "claim_ledger": [],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "companion_context_used_as_proof": False,
        },
    }
    out = finalize_competencies_v3_output(
        parsed,
        allowed_fact_ids=allowed,
        resume_support_blob_lower=blob,
    )
    phrases = []
    for cat in out.get("competencies") or []:
        for t in cat.get("terms") or []:
            if isinstance(t, dict):
                phrases.append(str(t.get("term") or t.get("text") or "").lower())
    assert "graphrag retrieval" not in phrases or "graphrag retrieval engineering" not in phrases
    assert any("graphrag" in p for p in phrases)


def test_finalize_repairs_out_of_slice_fact_id_typo() -> None:
    """Model typo fact_engineering_platform_1 is mapped to allowlisted fact_engineering_platform_001."""
    rows, allowed, bullet_lowers, blob = _base_context()
    allowed = set(allowed) | {"fact_engineering_platform_001", "fact_engineering_platform_004"}
    parsed = {
        "categories": [
            {
                "category_id": "tech_strategy_innovation",
                "category_label": "Technology Strategy & Innovation",
                "terms": [
                    {
                        "term": "Multi-Agent Orchestration",
                        "source_fact_ids": ["fact_engineering_platform_001", "fact_engineering_platform_1"],
                    }
                ],
            }
        ],
        "competencies": [],
        "claim_ledger": [],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "companion_context_used_as_proof": False,
        },
    }
    out = finalize_competencies_v3_output(
        parsed,
        allowed_fact_ids=allowed,
        resume_support_blob_lower=blob,
    )
    for cat in out.get("competencies") or []:
        for t in cat.get("terms") or []:
            if not isinstance(t, dict):
                continue
            sids = t.get("source_fact_ids") or []
            assert "fact_engineering_platform_1" not in sids
            assert all(s in allowed for s in sids)


def test_post_projection_keyword_reduce_still_meets_min_items_per_category() -> None:
    rows, allowed, bullet_lowers, blob = _base_context()
    out = finalize_competencies_v3_output(
        _brown_weak_llm_v3_payload(),
        allowed_fact_ids=allowed,
        resume_support_blob_lower=blob,
    )
    for cat in out.get("competencies") or []:
        terms = [t for t in (cat.get("terms") or []) if isinstance(t, dict)]
        assert len(terms) >= MIN_ITEMS_PER_CATEGORY, cat.get("category_label")
    gates = _run_critical_gates(out, allowed=allowed, blob=blob, bullet_lowers=bullet_lowers)
    assert _gate_pass(gates, "x2_competencies_min_items_per_category")
    assert _gate_pass(gates, "x2_duplicate_variants_collapsed")


def _gate_pass(results: list, gate_id: str) -> bool:
    for g in results:
        if g.gate_id == gate_id:
            return g.pass_
    raise AssertionError(f"missing gate {gate_id}")
