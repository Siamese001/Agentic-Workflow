"""Unit tests for ``check_rubric_diff_review.py``.

Exercises the pure-logic auditor functions with synthesized old/new
rubrics — no git invocation, no subprocess, so tests run anywhere.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_module():
    path = REPO_ROOT / "ops_scripts" / "ci" / "check_rubric_diff_review.py"
    spec = importlib.util.spec_from_file_location("_crdr_under_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_mod = _load_module()
_check_abstain_monotonic = _mod._check_abstain_monotonic
_check_dimension_removal = _mod._check_dimension_removal
_check_threshold_loosening = _mod._check_threshold_loosening
_check_version_bumped = _mod._check_version_bumped


def _rubric(**kw):
    base = {
        "gate": "X1D",
        "version": "X1D@v1",
        "composition": "weighted",
        "aggregate_threshold": 0.75,
        "dimensions": [
            {
                "name": "groundedness",
                "grader_class": "model_based",
                "weight": 0.5,
                "threshold": 0.8,
                "abstain_allowed": True,
            },
            {
                "name": "citation_support",
                "grader_class": "code_based",
                "is_hard_gate": False,
                "weight": 0.5,
                "threshold": 1.0,
            },
        ],
    }
    base.update(kw)
    return base


class TestVersionBumped:
    def test_same_version_flags(self) -> None:
        errs = _check_version_bumped(_rubric(), _rubric(), "x.yaml")
        assert any("version unchanged" in e for e in errs)

    def test_increment_passes(self) -> None:
        errs = _check_version_bumped(_rubric(version="X1D@v1"), _rubric(version="X1D@v2"), "x.yaml")
        assert errs == []

    def test_decrement_flags(self) -> None:
        errs = _check_version_bumped(_rubric(version="X1D@v3"), _rubric(version="X1D@v2"), "x.yaml")
        assert any("must increase" in e for e in errs)


class TestAbstainMonotonic:
    def test_removing_abstain_flags(self) -> None:
        old = _rubric()  # groundedness: abstain_allowed=True
        new_dims = [dict(d) for d in old["dimensions"]]
        new_dims[0]["abstain_allowed"] = False
        new = {**old, "dimensions": new_dims}
        errs = _check_abstain_monotonic(old, new, "x.yaml")
        assert any("removed abstain_allowed" in e for e in errs)

    def test_keeping_abstain_passes(self) -> None:
        assert _check_abstain_monotonic(_rubric(), _rubric(), "x.yaml") == []

    def test_new_dimension_with_abstain_false_not_flagged(self) -> None:
        """Dimension only in new rubric isn't a regression."""
        old_dims = [_rubric()["dimensions"][0]]  # just groundedness
        new = _rubric()  # has citation_support too
        errs = _check_abstain_monotonic({"dimensions": old_dims}, new, "x.yaml")
        assert errs == []


class TestThresholdLoosening:
    def test_aggregate_drop_without_justification_flags(self) -> None:
        old = _rubric(aggregate_threshold=0.75)
        new = _rubric(aggregate_threshold=0.60, version="X1D@v2")
        errs = _check_threshold_loosening(old, new, "x.yaml", commit_msg="routine")
        assert any("aggregate_threshold dropped" in e for e in errs)

    def test_aggregate_drop_with_justification_passes(self) -> None:
        old = _rubric(aggregate_threshold=0.75)
        new = _rubric(aggregate_threshold=0.60, version="X1D@v2")
        errs = _check_threshold_loosening(
            old, new, "x.yaml", commit_msg="RUBRIC_LOOSENING: recalibration vs golden set"
        )
        assert errs == []

    def test_dim_threshold_drop_flags(self) -> None:
        old = _rubric()
        new_dims = [dict(d) for d in old["dimensions"]]
        new_dims[0]["threshold"] = 0.5  # was 0.8
        new = {**old, "version": "X1D@v2", "dimensions": new_dims}
        errs = _check_threshold_loosening(old, new, "x.yaml", commit_msg="")
        assert any("groundedness" in e for e in errs)

    def test_tightening_not_flagged(self) -> None:
        old = _rubric(aggregate_threshold=0.75)
        new = _rubric(aggregate_threshold=0.90, version="X1D@v2")
        errs = _check_threshold_loosening(old, new, "x.yaml", commit_msg="")
        assert errs == []


class TestDimensionRemoval:
    def test_removal_without_adr_flags(self) -> None:
        old = _rubric()  # two dims
        new_dims = [old["dimensions"][0]]  # drop citation_support
        new = {**old, "version": "X1D@v2", "dimensions": new_dims}
        errs = _check_dimension_removal(old, new, "x.yaml", commit_msg="routine")
        assert any("citation_support" in e for e in errs)

    def test_removal_with_adr_passes(self) -> None:
        old = _rubric()
        new_dims = [old["dimensions"][0]]
        new = {**old, "version": "X1D@v2", "dimensions": new_dims}
        errs = _check_dimension_removal(old, new, "x.yaml", commit_msg="per ADR-099 retire citation_support")
        assert errs == []

    def test_no_removal_no_error(self) -> None:
        assert _check_dimension_removal(_rubric(), _rubric(), "x.yaml", commit_msg="") == []
