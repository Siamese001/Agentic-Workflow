"""Unit tests for executive_summary evidence capsule compiler."""
from __future__ import annotations

import json

import pytest

from apps_rg.runtime.section_front_spine_bridge import (
    activate_fixture_dev_bypass,
    deactivate_fixture_dev_bypass,
)
from apps_rg.runtime.dispatch.executive_summary_pa import compile_executive_summary_prompt
from apps_rg.runtime.sections.executive_summary_evidence_capsule import (
    CAPSULE_VERSION,
    compile_executive_summary_evidence_capsule,
    format_evidence_capsule_c0_block,
)
from apps_rg.runtime.sections.executive_summary_token_budget import estimate_tokens_approximate
from apps_rg.runtime.sections.selected_role_fact_set import metric_derivative_fact_id


@pytest.fixture(autouse=True)
def _fec_fixture_dev_bypass() -> None:
    activate_fixture_dev_bypass(non_product_certified=True)
    yield
    deactivate_fixture_dev_bypass()


def _minimal_payload() -> dict:
    return {
        "product_visible": False,
        "proof_pool_metadata": {"proof_pool_type": "selected_role_fact_set"},
        "run_id": "cap_unit_run",
        "target_title": "SVP Engineering",
        "target_company": "Acme Corp",
        "jd_text": "enterprise AI",
        "briefing": "regulated enterprise",
        "allowed_fact_ids": ["fact_exec_high_001", "fact_exec_high_002"],
        "selected_fact_plan": {
            "facts": [
                {
                    "fact_id": "fact_exec_high_001",
                    "claim_text": "Delivered governed agentic AI platforms at scale.",
                    "confidence": "HIGH",
                    "metric_raw": "40% error reduction",
                },
                {
                    "fact_id": "fact_exec_high_002",
                    "claim_text": "Reduced cycle time through standardized delivery patterns.",
                    "confidence": "HIGH",
                },
            ],
            "required_fact_ids": ["fact_exec_high_001", "fact_exec_high_002"],
        },
        "srfs_integration": {
            "artifact_path_resolved": "artifacts/apps_rg/fact_inventory/selected_role_fact_set_active.json",
            "selection_id": "sel_capsule_test",
            "executive_summary_selected_fact_ids": [
                "fact_exec_high_001",
                "fact_exec_high_002",
            ],
            "blocked_facts_count": 1,
            "facts_requiring_human_confirmation_count": 2,
            "unsupported_jd_needs_count": 3,
        },
    }


def test_high_facts_preserved_in_capsule():
    payload = _minimal_payload()
    capsule, receipt = compile_executive_summary_evidence_capsule(payload)
    ids = {r["source_fact_id"] for r in capsule["facts"]}
    assert "fact_exec_high_001" in ids
    assert "fact_exec_high_002" in ids
    assert receipt["preserved_high_fact_ids"] == [
        "fact_exec_high_001",
        "fact_exec_high_002",
    ]
    assert receipt["dropped_high_fact_ids"] == []
    assert receipt["source_fact_id_preservation_status"] == "PASS"


def test_allowed_fact_ids_preserved_exactly_no_normalization():
    payload = _minimal_payload()
    mid = metric_derivative_fact_id("fact_exec_high_001", "40% error reduction")
    payload["allowed_fact_ids"] = [
        "fact_exec_high_001",
        mid,
        "fact_exec_high_002",
    ]
    capsule, receipt = compile_executive_summary_evidence_capsule(payload)
    assert capsule["allowed_fact_ids"] == payload["allowed_fact_ids"]
    c0 = format_evidence_capsule_c0_block(capsule, payload["allowed_fact_ids"])
    assert mid in c0
    assert "fact_exec_high_ 001" not in c0
    assert receipt["metric_anchor_preservation_status"] == "PASS"


def test_style_only_srfs_prose_excluded_from_compiled_prompt():
    payload = _minimal_payload()
    baseline = dict(payload)
    baseline["evidence_capsule_disabled"] = True
    before = compile_executive_summary_prompt(baseline, run_id=payload["run_id"])
    before_text = before.artifact.messages[0]["content"]
    assert "<srfs_style_only_oneshot" in before_text

    compile_executive_summary_evidence_capsule(payload)
    after = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    after_text = after.artifact.messages[0]["content"]
    assert "<srfs_style_only_oneshot" not in after_text
    assert "EVIDENCE_CAPSULE_" in after_text
    assert "SELECTED_ROLE_FACT_SET_APPENDIX_CAPSULE" in after_text


def test_capsule_digest_is_deterministic():
    p1 = _minimal_payload()
    p2 = _minimal_payload()
    _, r1 = compile_executive_summary_evidence_capsule(p1)
    _, r2 = compile_executive_summary_evidence_capsule(p2)
    assert r1["output_capsule_digest"] == r2["output_capsule_digest"]
    assert r1["input_srfs_digest"] == r2["input_srfs_digest"]
    assert r1["capsule_version"] == CAPSULE_VERSION


def test_capsule_reduces_prompt_estimate_vs_verbose_srfs():
    payload = _minimal_payload()
    baseline = dict(payload)
    baseline["evidence_capsule_disabled"] = True
    before = compile_executive_summary_prompt(baseline, run_id=payload["run_id"])
    before_est = estimate_tokens_approximate(before.artifact.messages[0]["content"])
    compile_executive_summary_evidence_capsule(payload)
    after = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    after_est = estimate_tokens_approximate(after.artifact.messages[0]["content"])
    assert after_est < before_est
