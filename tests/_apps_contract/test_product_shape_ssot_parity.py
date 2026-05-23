"""SSOT seam parity — export, judge, graph-only, IBM bounds."""

from __future__ import annotations

from apps_rg.runtime.judges import executive_summary_judge_packet as judge_mod
from apps_rg.runtime.sections.section_product_shape_parity import (
    assert_ssot_seam_parity,
    judge_rubric_shape_constraints,
)
from apps_rg.runtime.sections.section_product_shape_ssot import section_product_shape


def test_ssot_seam_parity_harness_clean() -> None:
    assert_ssot_seam_parity()


def test_judge_rubrics_not_looser_than_ssot_exec_summary() -> None:
    shape = section_product_shape("executive_summary")
    issues = judge_rubric_shape_constraints(shape, judge_mod.SRFS_GRADE_ONLY_RUBRIC)
    issues += judge_rubric_shape_constraints(shape, judge_mod.GRAPH_ONLY_GRADE_ONLY_RUBRIC)
    assert issues == [], f"judge rubric drift: {issues}"


def test_ibm_narrative_ssot_includes_word_budget_gate() -> None:
    shape = section_product_shape("ibm_narrative")
    assert "x2_ibm_narrative_word_budget" in shape.bounds_gate_ids
