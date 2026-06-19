"""Unit tests: competencies X2 proof-quality gates (mock-marker hygiene, row consistency)."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.sections.competencies_lane_runtime import (
    build_mock_output,
    build_resume_support_blob,
    build_selected_fact_plan,
    canonicalize_competency_terms_for_proof,
    collect_employment_bullets,
    load_base_resume,
    rebuild_claim_ledger_from_competencies,
)
from apps_rg.runtime.validators.competencies_x2 import (
    X2GateResult,
    competencies_x2_gate_rows_internally_consistent,
    run_competencies_x2_gates,
)


def _three_pass_judges() -> list[dict]:
    def _j(pk: str) -> dict:
        return {
            "provider_key": pk,
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "decisive_failure": False,
            "normalized_score": 1.0,
            "normalized_threshold": 0.8,
        }

    return [_j("gemini_pro"), _j("openai_chatgpt"), _j("anthropic_claude")]


def test_real_llm_payload_with_mock_fixture_language_fails_marker_gate() -> None:
    base, _, _ = load_base_resume()
    rows, allowed, bullet_lowers = collect_employment_bullets(base)
    blob = build_resume_support_blob(rows, "")
    plan = build_selected_fact_plan(rows, sorted(allowed))
    mo = build_mock_output({"selected_fact_plan": plan})
    parsed = dict(mo)
    canonicalize_competency_terms_for_proof(parsed)
    rebuild_claim_ledger_from_competencies(parsed, allowed)
    parsed["change_log"] = [{"operation": "mocked_runtime_slice", "reason": "provider not requested"}]
    raw_out = json.dumps(parsed, sort_keys=True)
    gates = run_competencies_x2_gates(
        competencies=parsed["competencies"],
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="",
        briefing_text="",
        bullet_texts_lower=bullet_lowers,
        resume_support_blob=blob,
        allowed_fact_ids=allowed,
        runtime_generation_status="REAL_LLM",
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        raw_output=raw_out,
        x1d_judges=_three_pass_judges(),
    )
    gate = next(g for g in gates if g.gate_id == "x2_no_mock_fixture_markers_in_real_llm_output")
    assert gate.pass_ is False


def test_x2_pass_rows_have_null_failure_reason_for_style_gates() -> None:
    base, _, _ = load_base_resume()
    rows, allowed, bullet_lowers = collect_employment_bullets(base)
    blob = build_resume_support_blob(rows, "")
    plan = build_selected_fact_plan(rows, sorted(allowed))
    mo = build_mock_output({"selected_fact_plan": plan})
    parsed = dict(mo)
    canonicalize_competency_terms_for_proof(parsed)
    rebuild_claim_ledger_from_competencies(parsed, allowed)
    gates = run_competencies_x2_gates(
        competencies=parsed["competencies"],
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="",
        briefing_text="",
        bullet_texts_lower=bullet_lowers,
        resume_support_blob=blob,
        allowed_fact_ids=allowed,
        runtime_generation_status="REAL_LLM",
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        raw_output=json.dumps(parsed, sort_keys=True),
        x1d_judges=_three_pass_judges(),
    )
    for gid in ("x2_no_inline_source_tags", "x2_no_first_person", "x2_no_em_dash"):
        g = next(x for x in gates if x.gate_id == gid)
        assert g.pass_ is True, gid
        assert g.failure_reason is None, gid
    consistency = next(g for g in gates if g.gate_id == "x2_gate_rows_are_internally_consistent")
    assert consistency.pass_ is True


def test_canonicalize_terms_coerces_plain_strings() -> None:
    parsed = {
        "competencies": [
            {
                "category_label": "Mixed Shape Cat",
                "terms": [
                    {"text": "structured term", "source_fact_id": "bul_unify_001"},
                    "plain string term",
                ],
                "source_fact_ids": ["bul_unify_001"],
            }
        ]
    }
    canonicalize_competency_terms_for_proof(parsed)
    terms = parsed["competencies"][0]["terms"]
    assert all(isinstance(t, dict) for t in terms)
    plain = next(t for t in terms if t["text"] == "plain string term")
    assert plain["source_fact_id"] == "bul_unify_001"
    assert "bul_unify_001" in plain["source_fact_ids"]


def test_gate_row_consistency_rejects_pass_with_failure_like_observed_em_dash():
    gates = [
        X2GateResult(
            "x2_no_em_dash",
            "deterministic",
            True,
            "em dash found",
            "absent",
            None,
            "x2_no_em_dash",
        ),
    ]
    ok, bad = competencies_x2_gate_rows_internally_consistent(gates)
    assert ok is False
    assert "x2_no_em_dash" in bad


def test_gate_row_consistency_rejects_pass_row_with_failure_reason():
    gates = [
        X2GateResult(
            "x2_no_first_person",
            "deterministic",
            True,
            "ok",
            "absent",
            "should not be set",
            "ref",
        ),
    ]
    ok, bad = competencies_x2_gate_rows_internally_consistent(gates)
    assert ok is False


def test_gate_row_consistency_rejects_fail_row_without_failure_reason():
    gates = [
        X2GateResult(
            "x2_no_bullet_format",
            "deterministic",
            False,
            "dash item",
            "no leading bullet chars",
            None,
            "ref",
        ),
    ]
    ok, bad = competencies_x2_gate_rows_internally_consistent(gates)
    assert ok is False


def test_single_token_acronym_passes_compact_gate_when_structured():
    base, _, _ = load_base_resume()
    rows, allowed, bullet_lowers = collect_employment_bullets(base)
    blob = build_resume_support_blob(rows, "")
    plan = build_selected_fact_plan(rows, sorted(allowed))
    mo = build_mock_output({"selected_fact_plan": plan})
    parsed = dict(mo)
    parsed["competencies"][0]["terms"][0] = {
        "text": "AWS",
        "source_fact_id": "bul_unify_001",
        "source_fact_ids": ["bul_unify_001"],
    }
    canonicalize_competency_terms_for_proof(parsed)
    rebuild_claim_ledger_from_competencies(parsed, allowed)
    gates = run_competencies_x2_gates(
        competencies=parsed["competencies"],
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="",
        briefing_text="",
        bullet_texts_lower=bullet_lowers,
        resume_support_blob=blob,
        allowed_fact_ids=allowed,
        runtime_generation_status="REAL_LLM",
        cli_provider="qwen_vllm",
        raw_output=json.dumps(parsed, sort_keys=True),
        x1d_judges=_three_pass_judges(),
    )
    g = next(x for x in gates if x.gate_id == "x2_competency_term_compact_word_count")
    assert g.pass_ is True


def test_single_token_unsupported_generic_fails_compact_gate():
    base, _, _ = load_base_resume()
    rows, allowed, bullet_lowers = collect_employment_bullets(base)
    blob = build_resume_support_blob(rows, "")
    plan = build_selected_fact_plan(rows, sorted(allowed))
    mo = build_mock_output({"selected_fact_plan": plan})
    parsed = dict(mo)
    parsed["competencies"][0]["terms"][0] = {
        "text": "zzzqvx",
        "source_fact_id": "bul_unify_001",
        "source_fact_ids": ["bul_unify_001"],
    }
    canonicalize_competency_terms_for_proof(parsed)
    rebuild_claim_ledger_from_competencies(parsed, allowed)
    gates = run_competencies_x2_gates(
        competencies=parsed["competencies"],
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="",
        briefing_text="",
        bullet_texts_lower=bullet_lowers,
        resume_support_blob=blob,
        allowed_fact_ids=allowed,
        runtime_generation_status="REAL_LLM",
        cli_provider="qwen_vllm",
        raw_output=json.dumps(parsed, sort_keys=True),
        x1d_judges=_three_pass_judges(),
    )
    g = next(x for x in gates if x.gate_id == "x2_competency_term_compact_word_count")
    assert g.pass_ is False


def test_seven_word_term_fails_compact_gate():
    base, _, _ = load_base_resume()
    rows, allowed, bullet_lowers = collect_employment_bullets(base)
    blob = build_resume_support_blob(rows, "")
    plan = build_selected_fact_plan(rows, sorted(allowed))
    mo = build_mock_output({"selected_fact_plan": plan})
    parsed = dict(mo)
    parsed["competencies"][0]["terms"][0] = {
        "text": "one two three four five six seven",
        "source_fact_id": "bul_unify_001",
        "source_fact_ids": ["bul_unify_001"],
    }
    canonicalize_competency_terms_for_proof(parsed)
    rebuild_claim_ledger_from_competencies(parsed, allowed)
    gates = run_competencies_x2_gates(
        competencies=parsed["competencies"],
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="",
        briefing_text="",
        bullet_texts_lower=bullet_lowers,
        resume_support_blob=blob,
        allowed_fact_ids=allowed,
        runtime_generation_status="REAL_LLM",
        cli_provider="qwen_vllm",
        raw_output=json.dumps(parsed, sort_keys=True),
        x1d_judges=_three_pass_judges(),
    )
    g = next(x for x in gates if x.gate_id == "x2_competency_term_compact_word_count")
    assert g.pass_ is False


def test_sentence_like_term_fails_full_sentence_gate():
    base, _, _ = load_base_resume()
    rows, allowed, bullet_lowers = collect_employment_bullets(base)
    blob = build_resume_support_blob(rows, "")
    plan = build_selected_fact_plan(rows, sorted(allowed))
    mo = build_mock_output({"selected_fact_plan": plan})
    parsed = dict(mo)
    parsed["competencies"][0]["terms"][0] = {
        "text": "First word starts here.",
        "source_fact_id": "bul_unify_001",
        "source_fact_ids": ["bul_unify_001"],
    }
    canonicalize_competency_terms_for_proof(parsed)
    rebuild_claim_ledger_from_competencies(parsed, allowed)
    gates = run_competencies_x2_gates(
        competencies=parsed["competencies"],
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="",
        briefing_text="",
        bullet_texts_lower=bullet_lowers,
        resume_support_blob=blob,
        allowed_fact_ids=allowed,
        runtime_generation_status="REAL_LLM",
        cli_provider="qwen_vllm",
        raw_output=json.dumps(parsed, sort_keys=True),
        x1d_judges=_three_pass_judges(),
    )
    g = next(x for x in gates if x.gate_id == "x2_no_full_sentences")
    assert g.pass_ is False


def test_run_competencies_x2_fails_on_thin_selected_graph_evidence_depth():
    from apps_rg.runtime.validators.competencies_x2 import run_competencies_x2_gates
    from apps_rg.runtime.sections.competency_capability_evidence import (
        attach_competency_bundles_to_proof_pool_metadata,
    )
    from apps_rg.runtime.sections.graph_role_episode_selector import (
        build_selected_graph_evidence_plan_for_section,
    )

    base, _, bullet_lowers = load_base_resume()
    rows, allowed, _ = collect_employment_bullets(base)
    blob = build_resume_support_blob(rows, "")
    plan = build_selected_fact_plan(rows, sorted(allowed))
    mo = build_mock_output({"selected_fact_plan": plan})
    parsed = dict(mo)
    canonicalize_competency_terms_for_proof(parsed)
    rebuild_claim_ledger_from_competencies(parsed, allowed)
    thin_report = {
        "status": "insufficient_depth",
        "summary": "competencies: 7/8 rich items, 26 unique skills, 13 unique metrics, 88% semantic coverage, 100% axis coverage",
        "thin_item_ids": ["reb_ey_insurance_core_modernization"],
        "weakest_link": {"item_id": "reb_ey_insurance_core_modernization"},
    }
    selected_graph_plan, _, _ = build_selected_graph_evidence_plan_for_section(
        repo_root=Path(__file__).resolve().parents[3],
        section_id="competencies",
        target_role="SVP Engineering",
        jd_text="agentic multi-agent GraphRAG runtime platform control plane",
        briefing_text="regulated enterprise",
    )
    meta = {
        "proof_pool_type": "augmented_skills_graph",
        "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        "skills_authority_status": "PASS",
        "selected_graph_evidence_plan": selected_graph_plan,
        "graph_skills_proof_pool": True,
    }
    meta = attach_competency_bundles_to_proof_pool_metadata(meta, section_id="competencies")
    meta["graph_evidence_depth_report"] = thin_report
    gates = run_competencies_x2_gates(
        competencies=parsed["competencies"],
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="unrelated",
        bullet_texts_lower=bullet_lowers,
        resume_support_blob=blob,
        allowed_fact_ids=allowed,
        runtime_generation_status="REAL_LLM",
        proof_pool_metadata=meta,
    )
    gate = next(g for g in gates if g.gate_id == "x2_competencies_selected_graph_evidence_depth_sufficient")
    assert gate.pass_ is False
    assert "thin" in str(gate.failure_reason or "").lower()
