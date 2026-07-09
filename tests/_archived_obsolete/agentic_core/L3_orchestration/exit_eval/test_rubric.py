"""Tests for rubric parsing and validation."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_eval.composition import CompositionMode
from agentic_core.L3_orchestration.exit_eval.dimension import GraderClass
from agentic_core.L3_orchestration.exit_eval.rubric import (
    RubricError,
    load_rubric,
    rubric_from_mapping,
)


def test_load_x1a_rubric(rubrics_dir: Path) -> None:
    rubric = load_rubric(rubrics_dir / "x1a_v1.yaml")
    assert rubric.gate == "X1A"
    assert rubric.version == "X1A@v1"
    assert rubric.composition is CompositionMode.BINARY
    assert len(rubric.dimensions) == 1


def test_load_x1d_weighted(rubrics_dir: Path) -> None:
    rubric = load_rubric(rubrics_dir / "x1d_v1.yaml")
    assert rubric.composition is CompositionMode.WEIGHTED
    assert rubric.aggregate_threshold == 0.75
    names = {d.name for d in rubric.dimensions}
    assert {"groundedness", "citation_support", "faithfulness"} == names


def test_load_x1f_hybrid_hard_gates(rubrics_dir: Path) -> None:
    rubric = load_rubric(rubrics_dir / "x1f_v1.yaml")
    assert rubric.composition is CompositionMode.HYBRID
    hard = [d for d in rubric.dimensions if d.is_hard_gate]
    assert {d.name for d in hard} == {
        "prompt_injection_resistance",
        "system_prompt_leakage",
        "jailbreak_detection",
    }


def test_all_golden_rubrics_load(rubrics_dir: Path) -> None:
    for name in ("x1a_v1", "x1b_v1", "x1c_v1", "x1d_v1", "x1e_v1", "x1f_v1"):
        load_rubric(rubrics_dir / f"{name}.yaml")


def test_duplicate_dimension_rejected() -> None:
    with pytest.raises(RubricError, match="duplicate"):
        rubric_from_mapping(
            {
                "gate": "X1",
                "version": "v1",
                "composition": "binary",
                "dimensions": [
                    {"name": "d", "grader_class": "code_based"},
                    {"name": "d", "grader_class": "code_based"},
                ],
            }
        )


def test_weighted_without_threshold_rejected() -> None:
    with pytest.raises(RubricError, match="aggregate_threshold"):
        rubric_from_mapping(
            {
                "gate": "X1",
                "version": "v1",
                "composition": "weighted",
                "dimensions": [{"name": "d", "grader_class": "code_based"}],
            }
        )


def test_hybrid_requires_hard_and_soft() -> None:
    with pytest.raises(RubricError, match="hard gate"):
        rubric_from_mapping(
            {
                "gate": "X1",
                "version": "v1",
                "composition": "hybrid",
                "aggregate_threshold": 0.5,
                "dimensions": [{"name": "d", "grader_class": "code_based"}],
            }
        )


def test_abstain_only_on_model_based() -> None:
    with pytest.raises(RubricError, match="abstain_allowed"):
        rubric_from_mapping(
            {
                "gate": "X1",
                "version": "v1",
                "composition": "binary",
                "dimensions": [
                    {
                        "name": "d",
                        "grader_class": "code_based",
                        "abstain_allowed": True,
                    }
                ],
            }
        )


def test_threshold_outside_scale_rejected() -> None:
    with pytest.raises(RubricError, match="outside scale"):
        rubric_from_mapping(
            {
                "gate": "X1",
                "version": "v1",
                "composition": "binary",
                "dimensions": [
                    {
                        "name": "d",
                        "grader_class": "code_based",
                        "scale": [0.0, 1.0],
                        "threshold": 2.0,
                    }
                ],
            }
        )


def test_missing_file_raises_rubric_error(tmp_path: Path) -> None:
    with pytest.raises(RubricError, match="cannot read"):
        load_rubric(tmp_path / "nonexistent.yaml")


def test_malformed_yaml_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text(":\n invalid::", encoding="utf-8")
    logging.info("C3 write receipt: tests/_archived_obsolete/agentic_core/L3_orchestration/exit_eval/test_rubric.py write side effect recorded")
    with pytest.raises(RubricError):
        load_rubric(bad)
