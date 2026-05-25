"""Executive summary prompt dedup v2 — smaller static slots, single proof_law, E0 retained at L2."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.sections.executive_summary_evidence_capsule import (
    _capsule_enabled,
    compile_executive_summary_evidence_capsule,
)
from apps_rg.runtime.sections.executive_summary_pa import (
    build_executive_summary_assembly_input,
    compile_executive_summary_prompt,
    load_executive_summary_template_slots,
)
from apps_rg.runtime.sections.executive_summary_token_budget import estimate_tokens_approximate

REPO = Path(__file__).resolve().parents[3]
TEMPLATE = (
    REPO / "apps_rg" / "prompt_assembly" / "templates" / "executive_summary.generate_scratch_v1.yaml"
)


def _minimal_payload(*, product_visible: bool = False) -> dict:
    pp = {
        "proof_pool_type": "augmented_skills_graph",
        "evidence_authority": {
            "authority": "augmented_skills_graph",
            "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
            "ledger_ref": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger.json",
        },
    }
    return {
        "product_visible": product_visible,
        "proof_pool_metadata": pp,
        "run_id": "dedup_v2_run",
        "target_title": "SVP Engineering",
        "target_company": "Acme Corp",
        "jd_text": "enterprise AI platform",
        "briefing": "regulated enterprise",
        "allowed_fact_ids": ["fact_exec_001", "fact_exec_002"],
        "selected_fact_plan": {
            "facts": [
                {"fact_id": "fact_exec_001", "claim_text": "Built governed AI platforms."},
                {"fact_id": "fact_exec_002", "claim_text": "Reduced delivery cycle time."},
            ],
        },
    }


def test_template_has_dedup_marker_and_single_proof_law():
    raw = TEMPLATE.read_text(encoding="utf-8")
    assert "EXEC_SUMMARY_PROMPT_JUDGE_ALIGNED_V5" in raw or "EXEC_SUMMARY_PROMPT_JUDGE_ALIGNED_V4" in raw
    assert "pa_core_law_v1" in raw
    assert raw.count("<proof_law_v1>") == 1
    assert "<pre_output_checklist>" not in raw
    assert "EXEC_SUMMARY_PROMPT_JUDGE_ALIGNED_V5" in raw or "EXEC_SUMMARY_PROMPT_JUDGE_ALIGNED_V4" in raw or "pa_core_law_v1" in raw
    assert "many-shot" in raw.lower() or "E0" in raw


def test_static_yaml_slots_smaller_than_prior_baseline():
    slots = load_executive_summary_template_slots()
    static_est = sum(estimate_tokens_approximate(slots[k]) for k in ("S0", "D0", "I0", "E0", "Y0", "R0"))
    assert static_est < 7500, f"static slots still heavy: {static_est}"


def test_compiled_prompt_smaller_without_duplicate_allowed_id_json():
    payload = _minimal_payload()
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    content = out.artifact.messages[0]["content"]
    assert "EXEC_SUMMARY_PROMPT_CORE_LAW_V3" in content or "proof_law_v1" in content
    assert "PRODUCT_SHAPE" in content
    assert content.count("ALLOWED_SOURCE_FACT_IDS (JSON array)") == 0
    assert "proof_law_v1" in content
    assert "proof_law_v1" in content
    est = estimate_tokens_approximate(content)
    assert est < 12000, f"compiled prompt still large for minimal fixture: {est}"


def test_capsule_enabled_for_augmented_skills_graph_authority():
    payload = _minimal_payload()
    assert _capsule_enabled(payload) is True


def test_graph_path_capsule_compiles_without_srfs_integration():
    payload = _minimal_payload()
    assert "srfs_integration" not in payload
    capsule, receipt = compile_executive_summary_evidence_capsule(payload)
    assert receipt["status"] == "PASS"
    assert payload.get("evidence_capsule_active") is True
    assert capsule["facts"]
