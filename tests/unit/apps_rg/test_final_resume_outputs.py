from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.final_resume_outputs import emit_final_resume_product_outputs
from apps_rg.runtime.run_output_contract import (
    FINAL_RESUME_ASSEMBLY_JSON_RELPATH,
    FINAL_RESUME_DOCX_RELPATH,
    FINAL_RESUME_OUTPUT_JSON,
    FINAL_RESUME_OUTPUT_TXT,
)


def _section(order: int, section_id: str, snapshot: dict) -> dict:
    return {
        "assemble_order": order,
        "section_id": section_id,
        "section_kind": "generated_lane",
        "l2_output_snapshot": snapshot,
        "section_hash": "h",
        "section_digest": "d",
        "source_artifact_refs": {"l2_output.json": "x"},
        "disposition_refs": {"generated_lane": {"x3_disposition_json": "x", "rollup_lane_key": section_id}},
    }


def _final_resume_blob() -> dict:
    base_companies = [
        "Unify Consulting",
        "IBM",
        "InsurTech Cloud Solutions",
        "Ernst & Young",
        "Early Career Roles",
    ]
    base_titles = [
        "SVP Engineering, Agentic AI Platforms",
        "Partner",
        "Chief Technology Officer",
        "Principal",
        "Actuarial Consultant and Quantitative Roles",
    ]
    base_locations = ["Boca Raton, FL", "Edgewater, NJ", "New York, NY", "New York, NY", "Philadelphia, PA"]
    base_dates = [
        {"start_date": "2023-02", "end_date": "present", "is_current": True},
        {"start_date": "2017-04", "end_date": "2022-10", "is_current": False},
        {"start_date": "2014-04", "end_date": "2017-03", "is_current": False},
        {"start_date": "2009-10", "end_date": "2014-03", "is_current": False},
        {"start_date": "2002-10", "end_date": "2009-09", "is_current": False},
    ]
    wrong = {"employer": "WrongCo", "title": "WrongTitle", "location": "Nowhere", "start_date": "1900-01", "end_date": "1901-01"}
    education = [
        {"degree": "Master of Science in Biostatistics", "institution": "Columbia University", "honors": "Graduated with Distinction"},
        {"degree": "Bachelor of Arts in Biology", "institution": "Brown University", "honors": "Graduated Cum Laude"},
    ]
    certifications = [
        {"name": "Certified Machine Learning Engineer - Associate", "issuing_organization": "AWS", "year": "2025"},
        {"name": "Databricks Lakehouse Fundamentals Accreditation", "year": "2023"},
        {"name": "Certified Solutions Architect - Professional", "issuing_organization": "AWS", "year": "2023"},
        {"name": "Fellow of the Society of Actuaries", "year": "2010"},
    ]
    return {
        "candidate_identity": {
            "candidate_name": "Amit Ayer",
            "header_contact": {
                "phone": "+1-917-239-3830",
                "email": "amitayer1@gmail.com",
                "linkedin": "linkedin.com/in/amitayer1",
                "github": "github.com/Siamese001/Agentic-Workflow",
                "location": "Boca Raton, FL",
            },
        },
        "sections": [
            _section(0, "headline", {"headline_line": "Generated Headline"}),
            _section(1, "executive_summary", {"resume_display_text": "Generated executive summary."}),
            _section(
                2,
                "competencies",
                {"competencies": [{"category_label": "AI Platforms", "terms": [{"text": "Agentic AI platforms"}]}]},
            ),
            _section(3, "unify_narrative", {"unify_header": wrong, "narrative_sentence": "Generated Unify narrative."}),
            _section(4, "unify_bullets", {"unify_header": wrong, "bullets": [{"bullet_text": "Generated Unify bullet."}]}),
            _section(5, "ibm_narrative", {"ibm_header": wrong, "narrative_sentence": "Generated IBM narrative."}),
            _section(6, "ibm_bullets", {"ibm_header": wrong, "bullets": [{"bullet_text": "Generated IBM bullet."}]}),
            _section(7, "insurtech_narrative", {"insurtech_header": wrong, "narrative_sentence": "Generated InsurTech narrative."}),
            _section(8, "insurtech_bullets", {"insurtech_header": wrong, "bullets": [{"bullet_text": "Generated InsurTech bullet."}]}),
            _section(9, "ey_narrative", {"ey_header": wrong, "narrative_sentence": "Generated EY narrative."}),
            _section(10, "ey_bullets", {"ey_header": wrong, "bullets": [{"bullet_text": "Generated EY bullet."}]}),
            {
                "assemble_order": 11,
                "section_id": "early_career",
                "section_kind": "locked_copy_inline",
                "copied_text_exact": json.dumps({"role_narrative": "Base early career narrative.", "bullets": [{"text": "Base early bullet."}]}),
            },
            {
                "assemble_order": 12,
                "section_id": "education",
                "section_kind": "locked_copy_inline",
                "copied_text_exact": json.dumps(education),
            },
            {
                "assemble_order": 13,
                "section_id": "certifications",
                "section_kind": "locked_copy_inline",
                "copied_text_exact": json.dumps(certifications),
            },
        ],
        "locked_copy_invariants": {
            "company_names": {"copied_text_exact": json.dumps(base_companies)},
            "titles": {"copied_text_exact": json.dumps(base_titles)},
            "locations": {"copied_text_exact": json.dumps(base_locations)},
            "dates": {"copied_text_exact": json.dumps(base_dates)},
        },
    }


def _write_final_resume(run: Path) -> Path:
    path = run / FINAL_RESUME_ASSEMBLY_JSON_RELPATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_final_resume_blob(), indent=2) + "\n", encoding="utf-8")
    return path


def test_final_resume_outputs_preserve_base_facts_and_docx_order(tmp_path: Path) -> None:
    _write_final_resume(tmp_path)

    contract = emit_final_resume_product_outputs(tmp_path, repo_root=tmp_path, required=True)

    assert contract["status"] == "PASS"
    assert (tmp_path / FINAL_RESUME_OUTPUT_TXT).is_file()
    assert (tmp_path / FINAL_RESUME_OUTPUT_JSON).is_file()
    assert (tmp_path / FINAL_RESUME_DOCX_RELPATH).is_file()
    text = (tmp_path / FINAL_RESUME_OUTPUT_TXT).read_text(encoding="utf-8")
    assert text.index("EXECUTIVE SUMMARY") < text.index("ENGINEERING & PLATFORM COMPETENCIES")
    assert text.index("ENGINEERING & PLATFORM COMPETENCIES") < text.index("PROFESSIONAL EXPERIENCE")
    assert "Unify Consulting - SVP Engineering" not in text
    assert "Unify Consulting \u2014 SVP Engineering, Agentic AI Platforms" in text
    assert "IBM \u2014 Partner" in text
    assert "WrongCo" not in text
    assert "Master of Science in Biostatistics, Columbia University" in text
    assert "Fellow of the Society of Actuaries, 2010" in text
    gate_ids = {g["gate_id"]: g["pass"] for g in contract["gates"]}
    assert gate_ids["final_resume_docx_order_valid"] is True
    assert gate_ids["final_resume_docx_base_role_headers_preserved"] is True
    assert gate_ids["final_resume_docx_education_copied_from_base"] is True
    assert gate_ids["final_resume_docx_certifications_copied_from_base"] is True
