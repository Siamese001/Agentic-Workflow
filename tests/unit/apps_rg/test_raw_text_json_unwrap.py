"""RAW_TEXT_JSON_UNWRAP honest repair (apps_rg)."""

from __future__ import annotations

import json

from apps_rg.l2_recipe.raw_text_json_unwrap import try_unwrap_raw_text_to_resume


def _valid_resume_object() -> dict:
    return {
        "schema_version": "master_resume_v2.16",
        "candidate_name": "Ada Lovelace",
        "target_role": "SVP Engineering",
        "target_company": "Example Corp",
        "generated_at": "2026-05-16T12:00:00Z",
        "sections": {
            "summary": {"text": "Executive summary prose here for the candidate.", "word_count": 42},
            "experience": [
                {
                    "title": "Director",
                    "company": "Co",
                    "dates": "2020—Present",
                    "bullets": ["Shipped products."],
                }
            ],
            "skills": {"categories": [{"name": "Other", "items": ["Python", "Leadership"]}]},
            "education": [{"degree": "BS", "institution": "State University", "year": "2010"}],
            "certifications": [],
        },
        "citations": [],
        "gaps": [],
        "metadata": {},
    }


def test_unwrap_raw_text_fenced_valid_schema() -> None:
    inner = _valid_resume_object()
    raw = '```json\n' + json.dumps(inner, ensure_ascii=False) + "\n```"
    wrapper_json = json.dumps({"raw_text": raw}, ensure_ascii=False)
    d = json.loads(wrapper_json)
    got, rcp = try_unwrap_raw_text_to_resume(str(d["raw_text"]))
    assert got is not None
    assert got["candidate_name"] == "Ada Lovelace"
    assert rcp["repair_applied"] is True
    assert rcp["validation_status"] == "PASS"
    assert rcp["repair_type"] == "RAW_TEXT_JSON_UNWRAP"


def test_unwrap_prose_only_fails() -> None:
    got, rcp = try_unwrap_raw_text_to_resume("Here is my resume in prose. No JSON.")
    assert got is None
    assert rcp["repair_applied"] is False


def test_unwrap_incomplete_json_fails() -> None:
    got, rcp = try_unwrap_raw_text_to_resume('{"schema_version": "master_resume_v2.16", ')
    assert got is None
    assert rcp["repair_applied"] is False


def test_unwrap_json_missing_required_section_fails() -> None:
    bad = {
        "schema_version": "master_resume_v2.16",
        "candidate_name": "A",
        "target_role": "R",
        "target_company": "C",
        "generated_at": "2026-05-16T12:00:00Z",
        "sections": {
            "summary": {"text": "x" * 50, "word_count": 10},
            # missing experience, skills, education
        },
        "citations": [],
        "gaps": [],
        "metadata": {},
    }    
    raw_inner = json.dumps(bad)
    got, rcp = try_unwrap_raw_text_to_resume(raw_inner)
    assert got is None
    assert rcp["repair_applied"] is False
    assert "minimal_schema_reason" in rcp


def test_unwrap_nested_valid_inside_wrapper_string() -> None:
    inner = _valid_resume_object()
    raw = json.dumps(inner)
    got, rcp = try_unwrap_raw_text_to_resume(raw)
    assert got is not None
    assert rcp["repair_applied"] is True
