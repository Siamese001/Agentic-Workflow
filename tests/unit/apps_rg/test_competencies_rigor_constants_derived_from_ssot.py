"""W2.2 — competencies_rigor constants must match SSOT / competencies_x2."""

from __future__ import annotations

from apps_rg.runtime.sections import competencies_rigor
from apps_rg.runtime.sections.competencies_rigor import CANDIDATE_CATEGORY_COUNT
from apps_rg.runtime.sections.section_product_shape_ssot import (
    MAX_CATEGORY_COUNT,
    MAX_ITEMS_PER_CATEGORY,
    MIN_CATEGORY_COUNT,
    MIN_ITEMS_PER_CATEGORY,
    section_product_shape,
)


def test_competencies_rigor_matches_ssot() -> None:
    assert competencies_rigor.MIN_CATEGORY_COUNT == MIN_CATEGORY_COUNT
    assert competencies_rigor.MAX_CATEGORY_COUNT == MAX_CATEGORY_COUNT
    assert competencies_rigor.MIN_ITEMS_PER_CATEGORY == MIN_ITEMS_PER_CATEGORY
    assert competencies_rigor.MAX_ITEMS_PER_CATEGORY == MAX_ITEMS_PER_CATEGORY
    assert competencies_rigor.CANDIDATE_CATEGORY_COUNT == 10
    assert CANDIDATE_CATEGORY_COUNT == 10


def test_competencies_shape_gate_ids_include_rigor_anchors() -> None:
    shape = section_product_shape("competencies")
    assert "x2_competencies_min_category_count" in shape.required_gate_ids


def test_competencies_rigor_drift_would_fail_red_path() -> None:
    """Document: any drift from SSOT is detectable by equality assertions above."""
    assert competencies_rigor.MIN_CATEGORY_COUNT == MIN_CATEGORY_COUNT
    fake_ssot = MIN_CATEGORY_COUNT + 1
    assert competencies_rigor.MIN_CATEGORY_COUNT != fake_ssot
