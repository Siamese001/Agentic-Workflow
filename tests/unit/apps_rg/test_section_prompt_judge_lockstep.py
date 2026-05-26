"""Lockstep: PA prompt corpus vs X1D judge rubric criteria per generated resume section."""

from __future__ import annotations

import pytest

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.judges.graph_skills_x1d_rubric_contract import LANE_RUBRIC_MODULES
from apps_rg.runtime.sections.section_prompt_judge_alignment import (
    assert_all_sections_prompt_judge_lockstep,
    audit_all_generated_sections_prompt_judge,
    audit_section_prompt_judge_alignment,
    collect_section_judge_corpus,
    collect_section_prompt_corpus,
    extract_rubric_dimensions,
)
from apps_rg.runtime.sections.section_product_shape_ssot import section_product_shape


def test_all_generated_sections_prompt_judge_lockstep() -> None:
    assert_all_sections_prompt_judge_lockstep()


def test_audit_reports_zero_violations() -> None:
    violations = audit_all_generated_sections_prompt_judge()
    assert violations == [], "\n".join(f"{v.section_id}:{v.kind}:{v.detail}" for v in violations)


@pytest.mark.parametrize("section_id", list(GENERATED_LANES))
def test_section_prompt_corpus_non_empty(section_id: str) -> None:
    corpus = collect_section_prompt_corpus(section_id)
    assert len(corpus) > 200, section_id
    assert "PRODUCT_SHAPE" in corpus or section_id == "headline"


@pytest.mark.parametrize("section_id", list(GENERATED_LANES))
def test_section_judge_corpus_has_dimensions(section_id: str) -> None:
    rubric = collect_section_judge_corpus(section_id)
    dims = extract_rubric_dimensions(rubric)
    assert len(dims) >= 4, f"{section_id} dimensions={dims}"


@pytest.mark.parametrize("section_id", list(GENERATED_LANES))
def test_per_section_zero_alignment_drift(section_id: str) -> None:
    violations = audit_section_prompt_judge_alignment(section_product_shape(section_id))
    assert not violations, "\n".join(f"{v.kind}: {v.detail}" for v in violations)


def test_lane_rubric_modules_cover_all_generated_lanes() -> None:
    covered = {lane for _f, lane, _m in LANE_RUBRIC_MODULES}
    assert covered == set(GENERATED_LANES)


def test_executive_summary_prompt_includes_judge_alignment_marker() -> None:
    corpus = collect_section_prompt_corpus("executive_summary")
    assert "EXEC_SUMMARY_PROMPT_JUDGE_ALIGNED" in corpus or "judge_alignment" in corpus.lower()
    assert "fit_to_evidence" in corpus
    assert "targeting_only" in corpus
