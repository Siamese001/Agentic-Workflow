"""Competencies lane nuance: categories, proof flags, term support ids, gate consistency."""

from __future__ import annotations

from apps_rg.runtime.sections.competencies_rigor import check_competencies_term_support_ids_present
from apps_rg.runtime.validators.competencies_x2 import run_competencies_x2_gates

COMPETENCIES_CRITICAL_GATES = frozenset(
    {
        "x2_competency_companion_context_not_proof",
        "x2_competencies_min_category_count",
        "x2_competencies_min_items_per_category",
        "x2_competencies_approved_category_labels",
        "x2_competencies_term_support_ids_present",
        "x2_competencies_no_fragment_or_one_word_terms",
        "x2_competencies_no_low_rigor_two_word_items",
        "x2_competencies_no_credential_relisting",
        "x2_competencies_no_reserved_certification_category",
        "x2_competencies_no_metrics_as_skills_without_capability_context",
        "x2_competencies_role_alignment_terms",
        "x2_competencies_no_all_generic_skill_phrase",
        "x2_competencies_keyword_repetition_limit",
        "x2_claim_ledger_claim_text_non_empty",
        "x2_gate_rows_are_internally_consistent",
    }
)


def _term(text: str, fid: str = "bul_unify_001") -> dict:
    return {"text": text, "source_fact_id": fid, "source_fact_ids": [fid]}


def _six_categories() -> list[dict]:
    cats = []
    for i in range(6):
        cats.append(
            {
                "category_label": f"Platform Area {i}",
                "terms": [
                    _term("agentic platform orchestration"),
                    _term("governed runtime delivery"),
                    _term("policy-gated execution"),
                ],
                "source_fact_ids": ["bul_unify_001"],
            }
        )
    return cats


def test_companion_context_used_as_proof_fails_gate() -> None:
    competencies = _six_categories()
    parsed = {
        "competencies": competencies,
        "selected_fact_plan": {"selected_fact_ids": ["bul_unify_001"]},
        "claim_ledger": [
            {
                "claim_id": "c1",
                "claim_text": "Built agentic AI platforms with runtime governance.",
                "source_fact_ids": ["bul_unify_001"],
            }
        ],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "companion_context_used_as_proof": True,
        },
    }
    gates = run_competencies_x2_gates(
        competencies=competencies,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="",
        bullet_texts_lower=[],
        resume_support_blob="agentic platform orchestration governance aws databricks",
        allowed_fact_ids={"bul_unify_001"},
        runtime_generation_status="REAL_LLM",
    )
    assert any(g.gate_id == "x2_competency_companion_context_not_proof" and not g.pass_ for g in gates)


def test_term_missing_source_fact_ids_fails_support_ids_gate() -> None:
    competencies = _six_categories()
    competencies[0]["terms"] = [{"text": "agentic orchestration"}]
    ok, _ = check_competencies_term_support_ids_present(competencies)
    assert ok is False


def test_duplicate_gate_ids_fail_internal_consistency_gate() -> None:
    competencies = _six_categories()
    parsed = {
        "competencies": competencies,
        "selected_fact_plan": {"selected_fact_ids": ["bul_unify_001"]},
        "claim_ledger": [{"claim_text": "", "source_fact_ids": ["bul_unify_001"]}],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "companion_context_used_as_proof": False,
        },
    }
    gates = run_competencies_x2_gates(
        competencies=competencies,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="",
        bullet_texts_lower=[],
        resume_support_blob="agentic platform orchestration governance",
        allowed_fact_ids={"bul_unify_001"},
        runtime_generation_status="REAL_LLM",
    )
    ids = [g.gate_id for g in gates]
    assert len(ids) == len(set(ids))
    assert any(g.gate_id == "x2_claim_ledger_claim_text_non_empty" and not g.pass_ for g in gates)
    assert any(g.gate_id == "x2_gate_rows_are_internally_consistent" for g in gates)
