"""Judge packet rubrics must not be looser than SSOT for shape lanes."""

from __future__ import annotations

from apps_rg.runtime.judges import executive_summary_judge_packet as judge_mod
from apps_rg.runtime.sections.section_product_shape_parity import judge_rubric_shape_constraints
from apps_rg.runtime.sections.section_product_shape_ssot import section_product_shape


def test_executive_summary_judge_rubrics_align_with_ssot() -> None:
    shape = section_product_shape("executive_summary")
    for rubric in (judge_mod.SRFS_GRADE_ONLY_RUBRIC, judge_mod.GRAPH_ONLY_GRADE_ONLY_RUBRIC):
        assert judge_rubric_shape_constraints(shape, rubric) == []
