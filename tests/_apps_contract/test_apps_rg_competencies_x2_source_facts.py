"""Contract tests: competencies deterministic source_fact_id mapping (no X2 weakening)."""

from __future__ import annotations

import json

import pytest

from apps_rg.runtime.dispatch.competencies_dispatch import (
    build_mock_output,
    build_resume_support_blob,
    build_selected_fact_plan,
    collect_employment_bullets,
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


def test_mock_slice_still_passes_x2_source_mapping() -> None:
    import subprocess
    import sys
    from pathlib import Path

    repo = Path(__file__).resolve().parents[2]
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "apps_rg.runtime.dispatch.competencies_dispatch",
            "--provider",
            "mock",
            "--mock-judges",
            "--allow-non-allow-exit-zero",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, r.stderr
    from apps_rg.runtime.runtime_proof_layout import resolve_latest_mock_run_dir

    rd = resolve_latest_mock_run_dir(repo, "competencies")
    if rd is None:
        pytest.skip("mock competencies run dir missing")
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
