"""Wave 4.2 — unit tests for apps_rg.runtime.graph.ratio_floor_policy.

Covers per-section fact-to-skill ratio floors (GSR and C03), default fallbacks,
and the check_*_ratio helpers including the zero-skill divide-by-zero guard.
"""

from __future__ import annotations

import pytest

from apps_rg.runtime.graph.ratio_floor_policy import (
    DEFAULT_C03_FLOOR,
    DEFAULT_GSR_FLOOR,
    SECTION_C03_FLOORS,
    SECTION_GSR_FLOORS,
    c03_floor,
    check_c03_ratio,
    check_gsr_ratio,
    gsr_floor,
)


class TestFloorLookups:
    @pytest.mark.parametrize("section", list(SECTION_GSR_FLOORS))
    def test_gsr_floor_matches_table(self, section: str) -> None:
        assert gsr_floor(section) == SECTION_GSR_FLOORS[section]

    @pytest.mark.parametrize("section", list(SECTION_C03_FLOORS))
    def test_c03_floor_matches_table(self, section: str) -> None:
        assert c03_floor(section) == SECTION_C03_FLOORS[section]

    def test_gsr_default_for_unknown_section(self) -> None:
        assert gsr_floor("nonexistent_section") == DEFAULT_GSR_FLOOR

    def test_c03_default_for_unknown_section(self) -> None:
        assert c03_floor("nonexistent_section") == DEFAULT_C03_FLOOR

    def test_known_floor_values(self) -> None:
        assert gsr_floor("executive_summary") == 0.35
        assert c03_floor("executive_summary") == 0.25


class TestCheckGsrRatio:
    def test_zero_skills_passes_vacuously(self) -> None:
        passes, ratio, floor = check_gsr_ratio(
            "executive_summary", allowed_fact_count=5, selected_skill_count=0
        )
        assert passes is True
        assert ratio == 0.0
        assert floor == 0.35

    def test_ratio_above_floor_passes(self) -> None:
        passes, ratio, floor = check_gsr_ratio(
            "executive_summary", allowed_fact_count=4, selected_skill_count=10
        )
        assert ratio == 0.4
        assert ratio >= floor
        assert passes is True

    def test_ratio_below_floor_fails(self) -> None:
        passes, ratio, _ = check_gsr_ratio(
            "headline", allowed_fact_count=1, selected_skill_count=10
        )
        assert ratio == 0.1
        assert passes is False

    def test_ratio_equal_floor_passes(self) -> None:
        # floor for executive_summary is 0.35
        passes, ratio, floor = check_gsr_ratio(
            "executive_summary", allowed_fact_count=7, selected_skill_count=20
        )
        assert ratio == floor == 0.35
        assert passes is True

    def test_unknown_section_uses_default_floor(self) -> None:
        passes, ratio, floor = check_gsr_ratio(
            "weird", allowed_fact_count=3, selected_skill_count=10
        )
        assert floor == DEFAULT_GSR_FLOOR
        assert ratio == 0.3
        assert passes is True  # 0.3 >= 0.25


class TestCheckC03Ratio:
    def test_zero_skills_passes_vacuously(self) -> None:
        passes, ratio, floor = check_c03_ratio(
            "competencies", fact_count=2, selected_skill_count=0
        )
        assert passes is True
        assert ratio == 0.0
        assert floor == 0.18

    def test_ratio_above_floor_passes(self) -> None:
        passes, ratio, _ = check_c03_ratio(
            "headline", fact_count=4, selected_skill_count=10
        )
        assert ratio == 0.4
        assert passes is True

    def test_ratio_below_floor_fails(self) -> None:
        passes, ratio, floor = check_c03_ratio(
            "executive_summary", fact_count=1, selected_skill_count=10
        )
        assert ratio == 0.1
        assert floor == 0.25
        assert passes is False
