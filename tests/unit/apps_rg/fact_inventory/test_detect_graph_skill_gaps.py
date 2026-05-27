"""Unit tests for detect_graph_skill_gaps.py gap detector."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.fact_inventory.detect_graph_skill_gaps import (
    build_gap_report,
    detect_draft_skills_matching_jd,
    detect_jd_rejected_skills,
    detect_uncited_fact_ids,
)

# ---------------------------------------------------------------------------
# Fixtures — minimal JSON payloads (no disk I/O for core logic tests)
# ---------------------------------------------------------------------------

CLEAN_GSR: dict = {
    "schema": "graph_selection_rationale_v1",
    "section_id": "executive_summary",
    "selected_skill_count": 5,
    "allowed_fact_count": 3,
    "jd_keyword_hits": ["agentic AI", "IT strategy", "insurance"],
    "jd_only_admission_checks": [
        {
            "skill_id": "skill_agentic_ai_platforms",
            "admitted": True,
            "reason_code": "ok_graph_fact_links",
            "fact_id_links_count": 2,
            "jd_text_present": True,
        },
        {
            "skill_id": "skill_it_governance",
            "admitted": True,
            "reason_code": "ok_graph_fact_links",
            "fact_id_links_count": 1,
            "jd_text_present": True,
        },
    ],
}

REJECTED_GSR: dict = {
    "schema": "graph_selection_rationale_v1",
    "section_id": "executive_summary",
    "selected_skill_count": 10,
    "allowed_fact_count": 4,
    "jd_keyword_hits": ["agentic AI", "insurance brokerage", "strategy"],
    "jd_only_admission_checks": [
        {
            "skill_id": "skill_agentic_ai_platforms",
            "admitted": True,
            "reason_code": "ok_graph_fact_links",
            "fact_id_links_count": 2,
            "jd_text_present": True,
        },
        {
            "skill_id": "skill_jd_only_inferred",
            "admitted": False,
            "reason_code": "jd_only_or_empty_fact_id_links",
            "fact_id_links_count": 0,
            "jd_text_present": True,
        },
        {
            "skill_id": "skill_no_facts_no_jd",
            "admitted": False,
            "reason_code": "empty_fact_id_links",
            "fact_id_links_count": 0,
            "jd_text_present": False,
        },
    ],
}

CLEAN_C03: dict = {
    "section_id": "executive_summary",
    "selected_source_fact_ids": ["fact_exec_001", "fact_exec_002", "fact_platform_001"],
}

MINIMAL_LEDGER: dict = {
    "metadata": {"schema_version": "test"},
    "skill_rows": [
        {
            "skill_id": "skill_agentic_ai_platforms",
            "activation_status": "ACTIVE_CONFIRMED",
            "fact_id_links": ["fact_platform_001"],
            "allowed_phrases": ["agentic AI", "governed AI platform"],
            "forbidden_phrases": [],
            "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
            "pillar": "pillar_agentic_ai_platforms",
        },
        {
            "skill_id": "skill_draft_no_facts",
            "activation_status": "DRAFT",
            "fact_id_links": [],
            "allowed_phrases": ["agentic AI strategy", "insurance brokerage"],
            "forbidden_phrases": [],
            "support_level": "DERIVED_SUPPORTED",
            "pillar": "pillar_insurer_it_strategy_ai_enablement",
        },
        {
            "skill_id": "skill_draft_with_facts",
            "activation_status": "DRAFT",
            "fact_id_links": ["fact_exec_001"],
            "allowed_phrases": ["enterprise governance"],
            "forbidden_phrases": [],
            "support_level": "DERIVED_SUPPORTED",
            "pillar": "pillar_enterprise_portfolio_governance",
        },
    ],
}


# ---------------------------------------------------------------------------
# detect_jd_rejected_skills
# ---------------------------------------------------------------------------

class TestDetectJdRejectedSkills:
    def test_clean_gsr_returns_empty(self) -> None:
        result = detect_jd_rejected_skills(CLEAN_GSR)
        assert result == []

    def test_rejected_skills_extracted(self) -> None:
        result = detect_jd_rejected_skills(REJECTED_GSR)
        assert len(result) == 2
        skill_ids = {r["skill_id"] for r in result}
        assert "skill_jd_only_inferred" in skill_ids
        assert "skill_no_facts_no_jd" in skill_ids

    def test_admitted_skills_excluded(self) -> None:
        result = detect_jd_rejected_skills(REJECTED_GSR)
        skill_ids = {r["skill_id"] for r in result}
        assert "skill_agentic_ai_platforms" not in skill_ids

    def test_reason_code_preserved(self) -> None:
        result = detect_jd_rejected_skills(REJECTED_GSR)
        by_id = {r["skill_id"]: r for r in result}
        assert by_id["skill_jd_only_inferred"]["reason_code"] == "jd_only_or_empty_fact_id_links"

    def test_empty_checks_list(self) -> None:
        gsr = {**CLEAN_GSR, "jd_only_admission_checks": []}
        assert detect_jd_rejected_skills(gsr) == []

    def test_missing_checks_key(self) -> None:
        gsr = {"section_id": "executive_summary"}
        assert detect_jd_rejected_skills(gsr) == []


# ---------------------------------------------------------------------------
# detect_draft_skills_matching_jd
# ---------------------------------------------------------------------------

class TestDetectDraftSkillsMatchingJd:
    def test_draft_no_facts_always_included(self) -> None:
        result = detect_draft_skills_matching_jd(CLEAN_GSR, MINIMAL_LEDGER)
        ids = {r["skill_id"] for r in result}
        assert "skill_draft_no_facts" in ids

    def test_active_skills_not_included(self) -> None:
        result = detect_draft_skills_matching_jd(CLEAN_GSR, MINIMAL_LEDGER)
        ids = {r["skill_id"] for r in result}
        assert "skill_agentic_ai_platforms" not in ids

    def test_jd_phrase_overlap_detected(self) -> None:
        result = detect_draft_skills_matching_jd(REJECTED_GSR, MINIMAL_LEDGER)
        draft_no_facts = next(
            (r for r in result if r["skill_id"] == "skill_draft_no_facts"), None
        )
        assert draft_no_facts is not None
        # "agentic AI strategy" and "insurance brokerage" both overlap JD hits
        # "insurance brokerage" overlaps "insurance brokerage" in REJECTED_GSR jd_keyword_hits
        assert draft_no_facts["missing_fact_links"] is True

    def test_missing_fact_links_flag(self) -> None:
        # skill_draft_no_facts: has no fact_id_links → always included, flag=True
        result = detect_draft_skills_matching_jd(CLEAN_GSR, MINIMAL_LEDGER)
        by_id = {r["skill_id"]: r for r in result}
        assert by_id["skill_draft_no_facts"]["missing_fact_links"] is True
        # skill_draft_with_facts: has fact_id_links BUT no JD phrase overlap with CLEAN_GSR
        # → correctly NOT included (has facts and no relevance signal)
        assert "skill_draft_with_facts" not in by_id


# ---------------------------------------------------------------------------
# detect_uncited_fact_ids
# ---------------------------------------------------------------------------

class TestDetectUncitedFactIds:
    def test_no_resume_text_returns_empty(self) -> None:
        result = detect_uncited_fact_ids(CLEAN_C03, "")
        assert result == []

    def test_cited_facts_not_in_result(self) -> None:
        resume_text = "fact_exec_001 and fact_exec_002 are referenced here."
        result = detect_uncited_fact_ids(CLEAN_C03, resume_text)
        assert "fact_exec_001" not in result
        assert "fact_exec_002" not in result

    def test_uncited_fact_detected(self) -> None:
        resume_text = "fact_exec_001 and fact_exec_002 only."
        result = detect_uncited_fact_ids(CLEAN_C03, resume_text)
        assert "fact_platform_001" in result

    def test_all_uncited(self) -> None:
        resume_text = "No facts mentioned here."
        result = detect_uncited_fact_ids(CLEAN_C03, resume_text)
        assert set(result) == {"fact_exec_001", "fact_exec_002", "fact_platform_001"}

    def test_empty_selected_ids(self) -> None:
        c03 = {**CLEAN_C03, "selected_source_fact_ids": []}
        result = detect_uncited_fact_ids(c03, "any text")
        assert result == []


# ---------------------------------------------------------------------------
# build_gap_report — integration using tmp files
# ---------------------------------------------------------------------------

class TestBuildGapReport:
    def test_clean_run_produces_empty_gaps(self, tmp_path: Path) -> None:
        (tmp_path / "graph_selection_rationale.json").write_text(json.dumps(CLEAN_GSR))
        (tmp_path / "native_c03_final_evidence.json").write_text(json.dumps(CLEAN_C03))
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text(json.dumps(MINIMAL_LEDGER))

        report = build_gap_report(artifact_dir=tmp_path, ledger_path=ledger_path)

        assert report["schema"] == "candidate_skill_gap_report_v1"
        assert report["jd_rejected_skills"] == []
        assert report["summary"]["jd_rejected_count"] == 0
        assert "generated_at_utc" in report

    def test_rejected_skill_surfaces_in_report(self, tmp_path: Path) -> None:
        (tmp_path / "graph_selection_rationale.json").write_text(json.dumps(REJECTED_GSR))
        (tmp_path / "native_c03_final_evidence.json").write_text(json.dumps(CLEAN_C03))
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text(json.dumps(MINIMAL_LEDGER))

        report = build_gap_report(artifact_dir=tmp_path, ledger_path=ledger_path)

        assert report["summary"]["jd_rejected_count"] == 2
        ids = {r["skill_id"] for r in report["jd_rejected_skills"]}
        assert "skill_jd_only_inferred" in ids

    def test_draft_skills_in_report(self, tmp_path: Path) -> None:
        (tmp_path / "graph_selection_rationale.json").write_text(json.dumps(REJECTED_GSR))
        (tmp_path / "native_c03_final_evidence.json").write_text(json.dumps(CLEAN_C03))
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text(json.dumps(MINIMAL_LEDGER))

        report = build_gap_report(artifact_dir=tmp_path, ledger_path=ledger_path)

        assert report["summary"]["draft_skills_with_jd_overlap_or_no_facts"] >= 1

    def test_missing_gsr_produces_report_without_jd_data(self, tmp_path: Path) -> None:
        """Missing GSR should not crash — produce partial report."""
        (tmp_path / "native_c03_final_evidence.json").write_text(json.dumps(CLEAN_C03))
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text(json.dumps(MINIMAL_LEDGER))

        report = build_gap_report(artifact_dir=tmp_path, ledger_path=ledger_path)

        assert report["jd_rejected_skills"] == []
        assert report["summary"]["jd_rejected_count"] == 0

    def test_missing_c03_produces_report_without_uncited(self, tmp_path: Path) -> None:
        """Missing C03 should not crash — produce partial report."""
        (tmp_path / "graph_selection_rationale.json").write_text(json.dumps(CLEAN_GSR))
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text(json.dumps(MINIMAL_LEDGER))

        report = build_gap_report(artifact_dir=tmp_path, ledger_path=ledger_path)

        assert report["uncited_fact_ids"] == []
        assert report["summary"]["uncited_fact_ids_count"] == 0

    def test_resume_text_uncited_detection(self, tmp_path: Path) -> None:
        (tmp_path / "graph_selection_rationale.json").write_text(json.dumps(CLEAN_GSR))
        (tmp_path / "native_c03_final_evidence.json").write_text(json.dumps(CLEAN_C03))
        resume_path = tmp_path / "resume_display_text.txt"
        resume_path.write_text("fact_exec_001 only.")
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text(json.dumps(MINIMAL_LEDGER))

        report = build_gap_report(
            artifact_dir=tmp_path,
            ledger_path=ledger_path,
            resume_text_path=resume_path,
        )

        assert "fact_exec_002" in report["uncited_fact_ids"]
        assert "fact_platform_001" in report["uncited_fact_ids"]
        assert report["summary"]["uncited_fact_ids_count"] == 2
