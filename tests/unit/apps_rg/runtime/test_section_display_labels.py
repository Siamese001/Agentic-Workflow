from __future__ import annotations

from apps_rg.runtime.section_display_labels import (
    CERTIFICATIONS_AND_CREDENTIALS_HEADING,
    ENGINEERING_PLATFORM_COMPETENCIES_HEADING,
    summary_section_label,
)


def test_summary_section_label_maps_competencies_aliases_to_operator_heading() -> None:
    for section_id in ("competencies", "skills", "skills_block"):
        assert summary_section_label(section_id) == ENGINEERING_PLATFORM_COMPETENCIES_HEADING


def test_summary_section_label_maps_certifications_and_preserves_unknowns() -> None:
    assert summary_section_label(" certifications ") == CERTIFICATIONS_AND_CREDENTIALS_HEADING
    assert summary_section_label("executive_summary") == "executive_summary"
    assert summary_section_label("") == ""
