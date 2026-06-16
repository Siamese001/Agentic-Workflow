"""Whole-résumé flatten text — gap placeholders for incomplete sections."""

from __future__ import annotations

from apps_rg.runtime.assembly.full_resume_text import flatten_final_resume_to_text


def test_flatten_emits_not_completed_markers_when_sections_empty() -> None:
    text = flatten_final_resume_to_text(
        {
            "candidate_identity": {"candidate_name": "Test Candidate", "header_contact": {}},
            "sections": [],
        }
    )
    assert "[NOT COMPLETED: headline — missing_or_empty_headline]" in text
    assert "[NOT COMPLETED: insurtech — missing_generated_role_section]" in text
    assert "[NOT COMPLETED: competencies —" in text
