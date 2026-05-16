"""Unit tests: résumé output shape classification (apps_rg)."""

from __future__ import annotations

from types import SimpleNamespace

from apps_rg.l2_recipe.resume_output_shape import (
    INCOMPLETE_STRUCTURE,
    MALFORMED_MODEL_OUTPUT,
    NO_RESUME_PAYLOAD,
    REAL_RESUME,
    ResumeShapeReport,
    STRUCTURED_RESUME_OK,
    classify_resume_payload,
    is_raw_text_only_wrapper,
)
from apps_rg.l2_recipe.sealed_resume_extract import generated_resume_from_sealed_l2


def test_raw_text_only_wrapper_classification() -> None:
    payload = {"raw_text": "# Resume\n\nSome markdown prose."}
    assert is_raw_text_only_wrapper(payload)
    rep = classify_resume_payload(payload)
    assert rep == ResumeShapeReport(
        generation_status=MALFORMED_MODEL_OUTPUT,
        full_resume_generated=False,
        resume_shape="RAW_TEXT_ONLY",
    )


def test_structured_resume_ok() -> None:
    payload = {
        "headline": "SVP Engineering",
        "executive_summary": "Executive leader.",
        "competencies": ["AI strategy"],
        "professional_experience": [
            {
                "company": "Co",
                "title": "VP",
                "location": "FL",
                "dates": "2020 - Present",
                "summary": "Led teams.",
                "bullets": ["Shipped products."],
            }
        ],
        "education": [],
        "certifications": [],
    }
    rep = classify_resume_payload(payload)
    assert rep.generation_status == STRUCTURED_RESUME_OK
    assert rep.full_resume_generated is True
    assert rep.resume_shape == REAL_RESUME


def test_rg_output_schema_nested_sections_classifies_ok() -> None:
    """``rg_output_schema`` shape (sections.*) maps to classifier STRUCTURED_RESUME_OK."""
    payload = {
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
    rep = classify_resume_payload(payload)
    assert rep.generation_status == STRUCTURED_RESUME_OK
    assert rep.full_resume_generated is True


def test_incomplete_missing_keys() -> None:
    rep = classify_resume_payload({"headline": "Only headline"})
    assert rep.generation_status == INCOMPLETE_STRUCTURE
    assert rep.full_resume_generated is False


def test_generated_resume_from_sealed_top_level_raw_text() -> None:
    sealed = SimpleNamespace(
        proposed_state_diff={"raw_text": "plain text fallback"},
        generated_content="",
    )
    gr = generated_resume_from_sealed_l2(sealed)
    assert gr == {"raw_text": "plain text fallback"}
    assert classify_resume_payload(gr).generation_status == MALFORMED_MODEL_OUTPUT


def test_empty_payload() -> None:
    rep = classify_resume_payload(None)
    assert rep.resume_shape == "EMPTY"
    assert rep.generation_status == NO_RESUME_PAYLOAD
