"""Unit tests for C0 dense-retrieval section assignment in build_section_fact_vectors."""

from __future__ import annotations

from tools.apps_rg.build_section_fact_vectors import (
    ALL_SECTIONS,
    CROSS_SECTION_TARGETS,
    assign_sections_for_fact,
)


def test_assign_sections_always_includes_cross_section_targets() -> None:
    targets = assign_sections_for_fact({"company": "", "role_families_supported": []})
    for section in CROSS_SECTION_TARGETS:
        assert section in targets
    assert all(s in ALL_SECTIONS for s in targets)


def test_assign_sections_ibm_employer_adds_ibm_lanes() -> None:
    targets = assign_sections_for_fact(
        {"company": "IBM Global Services", "role_families_supported": []},
    )
    assert "ibm_bullets" in targets
    assert "ibm_narrative" in targets
    assert "unify_bullets" not in targets


def test_assign_sections_unify_employer_adds_unify_lanes() -> None:
    targets = assign_sections_for_fact(
        {"company": "Unify Platform Inc", "role_families_supported": []},
    )
    assert "unify_bullets" in targets
    assert "unify_narrative" in targets
    assert "ibm_bullets" not in targets


def test_assign_sections_engineering_role_family_adds_unify_lanes() -> None:
    targets = assign_sections_for_fact(
        {
            "company": "Independent Consultant",
            "role_families_supported": ["ENGINEERING_PLATFORM"],
        },
    )
    assert "unify_bullets" in targets
    assert "unify_narrative" in targets


def test_assign_sections_sorted_and_unique() -> None:
    targets = assign_sections_for_fact(
        {
            "company": "IBM",
            "role_families_supported": ["ENGINEERING_PLATFORM", "AI_SOLUTIONS_ARCHITECTURE"],
        },
    )
    assert targets == sorted(set(targets))
