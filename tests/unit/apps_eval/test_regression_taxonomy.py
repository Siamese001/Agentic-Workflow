"""Tests for taxonomy-aware regression tolerance (G9).

Covers apps_eval/engines/_taxonomy.py and the integration with
apps_eval/engines/regression_detector.py.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_eval.engines._taxonomy import (
    load_taxonomy_policy,
    resolve_taxonomy_class,
    tolerance_for_class,
)
from apps_eval.engines.regression_detector import RegressionDetector
from apps_eval.types.eval_types import ScorecardRow


# ---- _taxonomy.py unit tests ----


def test_resolve_explicit_class_wins_over_suite_id() -> None:
    klass = resolve_taxonomy_class(
        explicit_class="capability",
        suite_id="reg_safety_suite",
    )
    assert klass == "capability"


def test_resolve_suite_id_prefix_capability() -> None:
    klass = resolve_taxonomy_class(suite_id="cap_xyz")
    assert klass == "capability"
    klass = resolve_taxonomy_class(suite_id="capability_xyz")
    assert klass == "capability"


def test_resolve_suite_id_prefix_regression() -> None:
    klass = resolve_taxonomy_class(suite_id="reg_xyz")
    assert klass == "regression"
    klass = resolve_taxonomy_class(suite_id="regression_xyz")
    assert klass == "regression"


def test_resolve_unknown_falls_back_to_default() -> None:
    klass = resolve_taxonomy_class(suite_id="unknown_prefix_suite")
    # Default policy declares fail-safe = regression
    assert klass == "regression"


def test_resolve_invalid_explicit_falls_through() -> None:
    klass = resolve_taxonomy_class(
        explicit_class="nonsense",
        suite_id="cap_xyz",
    )
    assert klass == "capability"


def test_tolerance_capability_looser_than_regression() -> None:
    cap = tolerance_for_class("capability")
    reg = tolerance_for_class("regression")
    assert cap > reg, "capability tolerance must be looser than regression"
    assert cap == pytest.approx(0.05, abs=1e-6)
    assert reg == pytest.approx(0.005, abs=1e-6)


def test_load_taxonomy_policy_returns_block_or_fallback(tmp_path: Path) -> None:
    # Real policy file
    pol = load_taxonomy_policy()
    assert "capability" in pol
    assert "regression" in pol

    # Missing file -> fallback
    missing = tmp_path / "does-not-exist.yaml"
    pol2 = load_taxonomy_policy(missing)
    assert pol2["default_class"] == "regression"


def test_load_taxonomy_policy_handles_malformed_yaml(tmp_path: Path) -> None:
    bad = tmp_path / "broken.yaml"
    bad.write_text(":not yaml :: nope::", encoding="utf-8")
    pol = load_taxonomy_policy(bad)
    assert "capability" in pol  # fallback kicked in


# ---- RegressionDetector integration tests ----


def _row(dim: str, score: float, *, suite_id: str = "", taxonomy_class: str = "") -> ScorecardRow:
    return ScorecardRow(
        dimension_id=dim,
        display_name=dim,
        score=score,
        weight=1.0,
        weighted_score=score,
        verdict="PASS",
        suite_id=suite_id,
        taxonomy_class=taxonomy_class,
    )


def _write_baseline(baseline_dir: Path, scores: dict[str, float]) -> None:
    import json

    baseline_dir.mkdir(parents=True, exist_ok=True)
    (baseline_dir / "eval_baseline.json").write_text(
        json.dumps({"trace_id": "test", "scores": scores}),
        encoding="utf-8",
    )


def test_regression_strict_for_regression_class(tmp_path: Path) -> None:
    """A 0.01 score drop on a regression-class suite should flag REGRESSION
    (strict tolerance 0.005), but the same drop on a capability-class suite
    should be PASS (looser tolerance 0.05)."""
    _write_baseline(tmp_path, {"groundedness": 0.85})

    detector = RegressionDetector(baseline_dir=str(tmp_path))

    # Regression-class: -0.01 delta exceeds strict 0.005 threshold -> REGRESSION
    rows_reg = [_row("groundedness", 0.84, suite_id="reg_safety")]
    res_reg = detector.detect(rows_reg, trace_id="t1")
    assert res_reg.records[0].verdict == "REGRESSION"

    # Capability-class: -0.01 delta is within 0.05 threshold -> WARN (negative but acceptable)
    rows_cap = [_row("groundedness", 0.84, suite_id="cap_creative")]
    res_cap = detector.detect(rows_cap, trace_id="t2")
    assert res_cap.records[0].verdict == "WARN"


def test_regression_explicit_class_overrides_suite_id(tmp_path: Path) -> None:
    _write_baseline(tmp_path, {"score": 0.90})
    detector = RegressionDetector(baseline_dir=str(tmp_path))

    # suite says regression but explicit class says capability -> looser tolerance applied
    rows = [_row("score", 0.88, suite_id="reg_xyz", taxonomy_class="capability")]
    res = detector.detect(rows, trace_id="t3")
    # 0.02 delta is within capability 0.05 -> WARN, not REGRESSION
    assert res.records[0].verdict == "WARN"


def test_regression_fallback_when_taxonomy_disabled(tmp_path: Path) -> None:
    _write_baseline(tmp_path, {"score": 0.90})
    detector = RegressionDetector(
        baseline_dir=str(tmp_path),
        tolerance_delta=0.05,
        taxonomy_aware=False,
    )
    # 0.02 delta with legacy 0.05 -> WARN regardless of suite prefix
    rows = [_row("score", 0.88, suite_id="reg_xyz")]
    res = detector.detect(rows, trace_id="t4")
    assert res.records[0].verdict == "WARN"


def test_regression_unknown_suite_treated_as_regression(tmp_path: Path) -> None:
    """Default policy is fail-safe: unknown class -> regression-strict."""
    _write_baseline(tmp_path, {"score": 0.90})
    detector = RegressionDetector(baseline_dir=str(tmp_path))
    rows = [_row("score", 0.89, suite_id="unrecognized_suite")]  # 0.01 drop
    res = detector.detect(rows, trace_id="t5")
    # 0.01 > regression-strict 0.005 -> REGRESSION
    assert res.records[0].verdict == "REGRESSION"


def test_regression_record_carries_suite_id(tmp_path: Path) -> None:
    _write_baseline(tmp_path, {"score": 0.90})
    detector = RegressionDetector(baseline_dir=str(tmp_path))
    rows = [_row("score", 0.91, suite_id="cap_creative")]
    res = detector.detect(rows, trace_id="t6")
    assert res.records[0].suite_id == "cap_creative"
