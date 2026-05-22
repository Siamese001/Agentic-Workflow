"""Contract tests: competencies deterministic source_fact_id mapping (no X2 weakening)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.sections.competencies_lane_runtime import (
    build_mock_output,
    build_resume_support_blob,
    build_selected_fact_plan,
    collect_employment_bullets,
    dedupe_structured_competency_terms,
    expand_structured_competencies_min_two_terms,
    load_base_resume,
    prune_claim_ledger_bullet_paste,
    rebuild_claim_ledger_from_competencies,
    repair_structured_competencies_source_facts,
    term_phrase,
)
from apps_rg.runtime.validators.competencies_x2 import run_competencies_x2_gates


def _base_context() -> tuple:
    base, _, _ = load_base_resume()
    rows, allowed, bullet_lowers = collect_employment_bullets(base)
    blob = build_resume_support_blob(rows, "")
    return rows, allowed, bullet_lowers, blob


def test_repair_binds_invalid_structured_source_fact_to_valid_category_id() -> None:
    """Invalid model source_fact_id is rebound to a category-declared bul_* (no invented ids)."""
    _, allowed, _, blob = _base_context()
    parsed: dict = {
        "competencies": [
            {
                "category_label": "Grounded Test",
                "terms": [{"text": "GraphRAG", "source_fact_id": "not_a_real_bullet_id"}],
                "source_fact_ids": ["bul_unify_001"],
            }
        ],
        "change_log": [],
    }
    repair_structured_competencies_source_facts(
        parsed,
        allowed_fact_ids=allowed,
        resume_support_blob_lower=blob,
    )
    assert parsed["competencies"][0]["terms"][0]["source_fact_id"] == "bul_unify_001"


def test_rebuild_ledger_maps_every_structured_term() -> None:
    _, allowed, _, blob = _base_context()
    parsed = {
        "competencies": [
            {
                "category_label": "Grounded Test",
                "terms": [{"text": "GraphRAG", "source_fact_id": "bul_unify_001"}],
                "source_fact_ids": ["bul_unify_001"],
            }
        ],
        "selected_fact_plan": {"section_id": "competencies", "selection_method": "x", "required_fact_ids": []},
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
        "excluded_jd_skills": [],
        "removed_or_rewritten_terms": [],
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    rebuild_claim_ledger_from_competencies(parsed, allowed)
    flat = [term_phrase(t) for c in parsed["competencies"] for t in c["terms"]]
    ledger_l = {e["claim_text"].strip().lower() for e in parsed["claim_ledger"]}
    assert all(t.lower() in ledger_l for t in flat)


def test_prune_keeps_long_competency_row_when_term_matches() -> None:
    long_phrase = "enterprise " + "reliability " * 12  # > 72 chars, still a competency row
    parsed = {
        "competencies": [
            {
                "category_label": "Long Phrase Cat",
                "terms": [long_phrase],
                "source_fact_ids": ["bul_unify_001"],
            }
        ],
        "claim_ledger": [{"claim_text": long_phrase, "source_fact_ids": ["bul_unify_001"]}],
    }
    prune_claim_ledger_bullet_paste(parsed)
    assert len(parsed["claim_ledger"]) == 1


def test_prune_drops_employment_bullet_paste_not_in_terms() -> None:
    paste = ("Designed and operationalized governed agentic AI platform for regulated enterprise workflows. " * 3).strip()
    assert len(paste) > 220
    parsed = {
        "competencies": [
            {
                "category_label": "Short",
                "terms": ["GraphRAG"],
                "source_fact_ids": ["bul_unify_001"],
            }
        ],
        "claim_ledger": [{"claim_text": paste, "source_fact_ids": ["bul_unify_001"]}],
    }
    prune_claim_ledger_bullet_paste(parsed)
    assert parsed["claim_ledger"] == []


def test_x2_all_terms_source_fact_ids_fails_when_ledger_missing_term() -> None:
    base, _, _ = load_base_resume()
    rows, allowed, bullet_lowers = collect_employment_bullets(base)
    blob = build_resume_support_blob(rows, "")
    plan = build_selected_fact_plan(rows, sorted(allowed))
    mo = build_mock_output({"selected_fact_plan": plan})
    competencies = mo["competencies"]
    gates = run_competencies_x2_gates(
        competencies=competencies,
        parsed_output=dict(mo),
        claim_ledger=[],
        jd_text="",
        bullet_texts_lower=bullet_lowers,
        resume_support_blob=blob,
        allowed_fact_ids=allowed,
        runtime_generation_status="REAL_LLM",
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        x1d_judges=_three_pass_judges(),
    )
    gate = next(g for g in gates if g.gate_id == "x2_all_terms_source_fact_ids")
    assert gate.pass_ is False


def test_x2_structured_term_primary_facts_fails_without_source_fact_id() -> None:
    base, _, _ = load_base_resume()
    rows, allowed, bullet_lowers = collect_employment_bullets(base)
    blob = build_resume_support_blob(rows, "")
    plan = build_selected_fact_plan(rows, sorted(allowed))
    mo = build_mock_output({"selected_fact_plan": plan})
    competencies = json.loads(json.dumps(mo["competencies"]))  # deep copy-ish
    competencies[0] = {
        "category_label": "Broken structured cat",
        "terms": [
            {"text": "GraphRAG", "source_fact_id": "bul_unify_001"},
            {"text": "needs object form"},
        ],
        "source_fact_ids": ["bul_unify_001"],
    }
    ledger = json.loads(json.dumps(mo["claim_ledger"]))
    gates = run_competencies_x2_gates(
        competencies=competencies,
        parsed_output={**mo, "competencies": competencies},
        claim_ledger=ledger,
        jd_text="",
        bullet_texts_lower=bullet_lowers,
        resume_support_blob=blob,
        allowed_fact_ids=allowed,
        runtime_generation_status="REAL_LLM",
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        x1d_judges=_three_pass_judges(),
    )
    gate = next(g for g in gates if g.gate_id == "x2_structured_term_primary_facts")
    assert gate.pass_ is False


def test_repair_and_rebuild_restores_source_fact_x2_mapping() -> None:
    """Regression: bogus structured source_fact_id is repaired from category proofs before X2."""
    rows, allowed, bullet_lowers, blob = _base_context()
    plan = build_selected_fact_plan(rows, sorted(allowed))
    parsed = dict(build_mock_output({"selected_fact_plan": plan}))
    parsed["competencies"][0]["terms"][0]["source_fact_id"] = "bogus_bullet_xyz"
    repair_structured_competencies_source_facts(
        parsed,
        allowed_fact_ids=allowed,
        resume_support_blob_lower=blob,
    )
    rebuild_claim_ledger_from_competencies(parsed, allowed)
    prune_claim_ledger_bullet_paste(parsed)
    gates = run_competencies_x2_gates(
        competencies=parsed["competencies"],
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="",
        bullet_texts_lower=bullet_lowers,
        resume_support_blob=blob,
        allowed_fact_ids=allowed,
        runtime_generation_status="REAL_LLM",
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        x1d_judges=_three_pass_judges(),
    )
    by_id = {g.gate_id: g.pass_ for g in gates}
    assert by_id.get("x2_all_terms_source_fact_ids") is True
    assert by_id.get("x2_structured_term_primary_facts") is True


def test_competencies_diagnostics_reports_final_resume_snapshot_parity() -> None:
    from apps_rg.runtime.competencies_x2_diagnostics import build_competencies_x2_diagnostics

    rows, allowed, _, _ = _base_context()
    plan = build_selected_fact_plan(rows, sorted(allowed))
    parsed = dict(build_mock_output({"selected_fact_plan": plan}))
    rebuild_claim_ledger_from_competencies(parsed, allowed)
    fr = {"sections": [{"section_id": "competencies", "l2_output_snapshot": parsed}]}
    d = build_competencies_x2_diagnostics(
        l2_output=parsed,
        final_resume_blob=fr,
        x2_failed_checks=[],
        fec_evidence_refs_available=["fv_c0_smoke:comp:001"],
        compiled_prompt_fact_refs_available=["bul_unify_001"],
    )
    assert d["competencies_json_parity_final_vs_lane_l2"] is True
    assert d["fec_evidence_refs_available"][0].startswith("fv_")
    assert d["structured_terms_count"] >= 1
    assert d["structured_terms_count"] == d["terms_with_source_fact_ids"]
    assert d["terms_missing_source_fact_ids"] == []


def test_fixture_single_structured_term_fails_format_gate_then_expand_goes_green() -> None:
    """Reproduce x2_competency_format_category_colon_terms idx=single-term collapse; deterministic expand repairs."""
    rows, allowed, bullet_lowers, blob = _base_context()
    plan = build_selected_fact_plan(rows, sorted(allowed))
    parsed = dict(build_mock_output({"selected_fact_plan": plan}))
    parsed["competencies"][0]["terms"] = [
        {"text": "governed agentic systems", "source_fact_id": "bul_unify_001"},
    ]
    rebuild_claim_ledger_from_competencies(parsed, allowed)
    prune_claim_ledger_bullet_paste(parsed)
    bad = run_competencies_x2_gates(
        competencies=parsed["competencies"],
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="",
        bullet_texts_lower=bullet_lowers,
        resume_support_blob=blob,
        allowed_fact_ids=allowed,
        runtime_generation_status="REAL_LLM",
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        x1d_judges=_three_pass_judges(),
    )
    fm_bad = next(g for g in bad if g.gate_id == "x2_competency_format_category_colon_terms")
    assert fm_bad.pass_ is False

    expand_structured_competencies_min_two_terms(
        parsed,
        bullet_rows=rows,
        allowed_fact_ids=allowed,
        resume_support_blob_lower=blob,
        bullet_texts_lower=bullet_lowers,
    )
    dedupe_structured_competency_terms(parsed)
    rebuild_claim_ledger_from_competencies(parsed, allowed)
    prune_claim_ledger_bullet_paste(parsed)
    good = run_competencies_x2_gates(
        competencies=parsed["competencies"],
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="",
        bullet_texts_lower=bullet_lowers,
        resume_support_blob=blob,
        allowed_fact_ids=allowed,
        runtime_generation_status="REAL_LLM",
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        x1d_judges=_three_pass_judges(),
    )
    fm_ok = next(g for g in good if g.gate_id == "x2_competency_format_category_colon_terms")
    assert fm_ok.pass_ is True
    assert len(parsed["competencies"][0]["terms"]) >= 2
    rst = next(g for g in good if g.gate_id == "x2_no_bullet_outcome_restatement")
    assert rst.pass_ is True


def test_expand_preserves_claim_ledger_per_structured_term() -> None:
    rows, allowed, bullet_lowers, blob = _base_context()
    plan = build_selected_fact_plan(rows, sorted(allowed))
    parsed = dict(build_mock_output({"selected_fact_plan": plan}))
    parsed["competencies"][0]["terms"] = [
        {"text": "governed agentic systems", "source_fact_id": "bul_unify_001"},
    ]
    expand_structured_competencies_min_two_terms(
        parsed,
        bullet_rows=rows,
        allowed_fact_ids=allowed,
        resume_support_blob_lower=blob,
        bullet_texts_lower=bullet_lowers,
    )
    rebuild_claim_ledger_from_competencies(parsed, allowed)
    phrases = []
    for t in parsed["competencies"][0]["terms"]:
        if isinstance(t, dict) and term_phrase(t):
            phrases.append(term_phrase(t))
    lowered = [e["claim_text"].strip().lower() for e in parsed["claim_ledger"]]
    assert all(p.lower() in lowered for p in phrases)
    for t in parsed["competencies"][0]["terms"]:
        if isinstance(t, dict):
            fid = str(t.get("source_fact_id", "")).split("_metric_")[0]
            assert fid in allowed


def test_final_resume_snapshot_structured_ids_parity_with_lane() -> None:
    """Assembly embeds verbatim l2_output_snapshot — structured source_fact_id keys survive."""
    rows, allowed, _, _ = _base_context()
    plan = build_selected_fact_plan(rows, sorted(allowed))
    parsed = dict(build_mock_output({"selected_fact_plan": plan}))
    lane_terms = parsed["competencies"][0]["terms"]
    fr = {"sections": [{"section_id": "competencies", "l2_output_snapshot": parsed}]}
    snap = None
    for sec in fr["sections"]:
        if isinstance(sec, dict) and sec.get("section_id") == "competencies":
            snap = sec.get("l2_output_snapshot")
            break
    assert isinstance(snap, dict)
    assert snap["competencies"][0]["terms"] == lane_terms


def test_x1d_judges_all_pass_do_not_bypass_category_count_rigor() -> None:
    rows, allowed, bullet_lowers, blob = _base_context()
    plan = build_selected_fact_plan(rows, sorted(allowed))
    mo = dict(build_mock_output({"selected_fact_plan": plan}))
    comps = list(mo["competencies"][:5])
    mo["competencies"] = comps
    rebuild_claim_ledger_from_competencies(mo, allowed)
    gates = run_competencies_x2_gates(
        competencies=comps,
        parsed_output=mo,
        claim_ledger=mo["claim_ledger"],
        jd_text="",
        bullet_texts_lower=bullet_lowers,
        resume_support_blob=blob,
        allowed_fact_ids=allowed,
        runtime_generation_status="REAL_LLM",
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        x1d_judges=_three_pass_judges(),
    )
    g_cat = next(g for g in gates if g.gate_id == "x2_competencies_min_category_count")
    assert g_cat.pass_ is False


def test_v3_post_llm_pipeline_weak_fixture_passes_critical_x2_gates() -> None:
    """Brown-style weak LLM output through v3 finalize seam must pass lane-critical gates."""
    from apps_rg.runtime.sections.competencies_capability_projection import (
        run_competencies_v3_post_llm_pipeline,
    )
    from tests.unit.apps_rg.section_rigor.unify_ibm_lane_fixtures import assert_critical_gates_pass

    rows, allowed, bullet_lowers, blob = _base_context()
    weak: dict = {
        "categories": [
            {
                "category_label": "Data Platforms",
                "terms": [
                    {"term": "Databricks Lakehouse Fundamentals", "source_fact_ids": ["fact_certs_001"]},
                    {"term": "designed", "source_fact_ids": ["bul_unify_001"]},
                ],
            }
        ],
        "competencies": [],
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
    out = run_competencies_v3_post_llm_pipeline(
        weak,
        bullet_rows=rows,
        allowed_fact_ids=allowed,
        resume_support_blob=blob,
        c0_proof_blob=blob,
        bullet_texts_lower=bullet_lowers,
    )
    gates = run_competencies_x2_gates(
        competencies=out.get("competencies") or [],
        parsed_output=out,
        claim_ledger=out.get("claim_ledger") or [],
        jd_text="",
        bullet_texts_lower=bullet_lowers,
        resume_support_blob=blob,
        allowed_fact_ids=allowed,
        runtime_generation_status="REAL_LLM",
    )
    assert_critical_gates_pass("competencies", gates)


def test_near_duplicate_structured_terms_then_expand_minimum_two_terms() -> None:
    rows, allowed, bullet_lowers, blob = _base_context()
    plan = build_selected_fact_plan(rows, sorted(allowed))
    parsed = dict(build_mock_output({"selected_fact_plan": plan}))
    t0 = parsed["competencies"][0]["terms"][0]
    assert isinstance(t0, dict)
    parsed["competencies"][0]["terms"] = [dict(t0), dict(t0)]
    dedupe_structured_competency_terms(parsed)
    assert sum(1 for t in parsed["competencies"][0]["terms"] if isinstance(t, dict)) == 1
    expand_structured_competencies_min_two_terms(
        parsed,
        bullet_rows=rows,
        allowed_fact_ids=allowed,
        resume_support_blob_lower=blob,
        bullet_texts_lower=bullet_lowers,
    )
    assert sum(
        1 for t in parsed["competencies"][0]["terms"] if isinstance(t, dict) and term_phrase(t)
    ) >= 2


def test_mock_slice_still_passes_x2_source_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")
    from apps_rg.runtime.sections import competencies_lane as lane

    args = lane.build_competencies_lane_args(
        provider="qwen_vllm",
        temperature=lane.COMPETENCIES_TEMP_DEFAULT,
        x1d_judges="gemini_pro,openai_chatgpt,anthropic_claude",
        mock_judges=True,
        allow_test_mock_judges=True,
        target_title="SVP Engineering",
        target_company="Synthetic Enterprise Corp.",
        jd_text="",
        briefing="",
    )
    ctx = lane.run_competencies_lane_execution(args)
    rd = Path(ctx["artifact_dir"])
    x2 = json.loads((rd / "x2_gate_outputs.json").read_text(encoding="utf-8"))
    ids = {g["gate_id"]: g["pass"] for g in x2.get("gates", [])}
    assert ids.get("x2_all_terms_source_fact_ids") is True
    assert ids.get("x2_structured_term_primary_facts") is True


def _three_pass_judges() -> list[dict]:
    return [
        {
            "provider_key": "gemini_pro",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "decisive_failure": False,
            "normalized_score": 0.9,
            "normalized_threshold": 0.8,
        },
        {
            "provider_key": "openai_chatgpt",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "decisive_failure": False,
            "normalized_score": 0.9,
            "normalized_threshold": 0.8,
        },
        {
            "provider_key": "anthropic_claude",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "decisive_failure": False,
            "normalized_score": 0.9,
            "normalized_threshold": 0.8,
        },
    ]
