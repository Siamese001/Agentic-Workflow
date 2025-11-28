from __future__ import annotations

from typing import Dict

from prompt_taxonomy import PromptSection


def validate_sections(sections: Dict[str, str]) -> dict:
    """Validate prompt sections against taxonomy ordering and completeness."""

    expected_order = [section.value for section in PromptSection]
    present_sections = [key for key in sections.keys() if key in expected_order]

    missing_sections = [section for section in expected_order if section not in sections]
    empty_sections = [
        section
        for section in expected_order
        if section in sections and not sections.get(section, "").strip()
    ]

    out_of_order = []
    for idx, section in enumerate(present_sections):
        if idx >= len(expected_order) or section != expected_order[idx]:
            out_of_order.append(section)

    valid = not (missing_sections or empty_sections or out_of_order)

    return {
        "valid": valid,
        "missing_sections": missing_sections,
        "out_of_order": out_of_order,
        "empty_sections": empty_sections,
    }
