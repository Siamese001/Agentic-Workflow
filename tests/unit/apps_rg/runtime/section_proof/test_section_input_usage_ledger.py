from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.section_proof.section_input_usage_ledger import (
    build_section_input_usage_ledger_v1,
    classify_source_fact_ids,
    sha256_hex64,
    source_fact_base_id,
    summarize_claim_ledger_proof_axes,
)


def test_source_fact_id_classification_separates_resume_facts_from_targeting_inputs() -> None:
    result = classify_source_fact_ids(
        [
            "bul_001",
            "bul_002_metric_growth",
            "jd_text",
            "target_company_acme",
            "briefing_research",
            "unknown_fact",
        ],
        allowed_fact_ids={"bul_001", "bul_002"},
    )

    assert source_fact_base_id("bul_002_metric_growth") == "bul_002"
    assert result["allowed_hits"] == ["bul_001", "bul_002_metric_growth"]
    assert result["forbidden_hits"] == [
        "jd_text",
        "target_company_acme",
        "briefing_research",
    ]
    assert result["jd_like"] == ["jd_text", "target_company_acme"]
    assert result["briefing_like"] == ["briefing_research"]
    assert result["unknown"] == ["unknown_fact"]


def test_summarize_claim_ledger_proof_axes_counts_supported_unsupported_and_non_evidence() -> None:
    summary = summarize_claim_ledger_proof_axes(
        [
            {"claim_text": "Supported claim.", "source_fact_ids": ["bul_001"]},
            {"claim_text": "Unsupported claim.", "source_fact_ids": ["unknown"]},
            {"claim_text": "Targeting claim.", "source_fact_ids": ["jd_role"]},
            {"claim_text": "Context claim.", "source_fact_ids": ["briefing_research"]},
            {"claim_text": "No ids.", "source_fact_ids": []},
            {"claim_text": "", "source_fact_ids": ["bul_001"]},
        ],
        allowed_fact_ids={"bul_001"},
    )

    assert summary == {
        "displayed_claim_count": 5,
        "claims_supported_by_selected_resume_facts": 1,
        "claims_with_targeting_input_in_source_fact_ids": 1,
        "claims_with_context_input_in_source_fact_ids": 1,
        "unsupported_claim_count": 2,
        "orphan_source_fact_id_count": 1,
    }


def test_build_section_input_usage_ledger_v1_records_hashes_and_boundary_flags(tmp_path: Path) -> None:
    base = tmp_path / "base_resume.json"
    base.write_text('{"facts":["bul_001"]}', encoding="utf-8")
    claim_ledger = [
        {"claim_text": "Supported claim.", "source_fact_ids": ["bul_001"]},
        {"claim_text": "Bad targeting claim.", "source_fact_ids": ["target_company_acme"]},
    ]

    doc = build_section_input_usage_ledger_v1(
        section_id="headline",
        run_id="run_wave2",
        request_id="req_wave2",
        trace_root="trace_wave2",
        repo_root=tmp_path,
        artifact_dir=tmp_path / "artifacts",
        runtime_payload={"base_resume_json_ref": "base_resume.json"},
        selected_fact_plan={"facts": [{"fact_id": "bul_001"}]},
        claim_ledger=claim_ledger,
        allowed_fact_ids={"bul_001"},
        jd_text="JD text",
        target_title="VP Engineering",
        target_company="Acme",
        briefing_text="Briefing text",
        jd_alignment={"jd_used_as_proof": False, "briefing_used_as_proof": False},
        extra_section_fields={"proof_source": "base_resume_fallback"},
    )

    assert doc["schema"] == "section_input_usage_ledger_v1"
    assert doc["input_refs"]["base_resume_hash"] == sha256_hex64(base.read_bytes())
    assert doc["input_refs"]["jd_text_hash"] == sha256_hex64("JD text")
    assert doc["required_input_usage"]["base_resume"]["selected_fact_ids_used"] == ["bul_001"]
    assert doc["evidence_boundary"]["non_evidence_inputs_used_as_claim_evidence"] is True
    assert doc["evidence_boundary"]["non_evidence_inputs_in_source_fact_ids"] is True
    assert doc["claim_support_summary"]["claims_supported_by_selected_resume_facts"] == 1
    assert doc["proof_source"] == "base_resume_fallback"
