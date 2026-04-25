"""Unit tests for ``agentic_core.L3_orchestration.reasoning.workflow_shape_calibration``.

Plan: ``.windsurf/plans/routing-decision-process-enhancement-9c7e4d.md`` W7.
"""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.reasoning.workflow_shape_calibration import (
    cascade_path_distribution,
    cascade_skip_rate,
    oscillation_amplitude,
    recommend_max_iterations,
)


def test_recommend_falls_back_when_insufficient_data() -> None:
    rec = recommend_max_iterations(
        {"summary": [1, 2, 3]},
        min_observations=30,
        fallback_max=3,
    )
    assert rec["summary"].confident is False
    assert rec["summary"].recommended_max == 3


def test_recommend_uses_p95_when_confident() -> None:
    # 100 observations with most converging at 2 iter, a few at 5
    obs = [2] * 90 + [5] * 10  # p95 should be 5 (or close)
    rec = recommend_max_iterations(
        {"complex_task": obs},
        min_observations=30,
        hard_ceiling=10,
    )
    r = rec["complex_task"]
    assert r.confident is True
    assert r.recommended_max == 5
    assert r.p95_iterations == 5


def test_recommend_respects_hard_ceiling() -> None:
    obs = [50] * 100  # would yield p95=50, but ceiling caps it
    rec = recommend_max_iterations({"runaway": obs}, min_observations=10, hard_ceiling=8)
    assert rec["runaway"].recommended_max == 8


def test_recommend_skips_empty_class() -> None:
    rec = recommend_max_iterations({"empty": []})
    assert "empty" not in rec


def test_oscillation_short_sequence_returns_empty() -> None:
    assert oscillation_amplitude([[1.0, 0.0]]) == []
    assert oscillation_amplitude([[1.0, 0.0], [0.5, 0.5]]) == []


def test_oscillation_orbit_detected() -> None:
    """Iter N == Iter N-2 → cosine 1.0."""
    embeddings = [
        [1.0, 0.0],  # 0
        [0.0, 1.0],  # 1
        [1.0, 0.0],  # 2 — same as 0
        [0.0, 1.0],  # 3 — same as 1
    ]
    amps = oscillation_amplitude(embeddings)
    assert len(amps) == 2
    assert amps[0] == pytest.approx(1.0)
    assert amps[1] == pytest.approx(1.0)


def test_oscillation_diverging_low_amplitude() -> None:
    embeddings = [
        [1.0, 0.0],
        [0.5, 0.5],
        [0.0, 1.0],  # orthogonal to embeddings[0]
    ]
    amps = oscillation_amplitude(embeddings)
    assert amps[0] == pytest.approx(0.0, abs=1e-9)


def test_oscillation_inconsistent_dim_raises() -> None:
    with pytest.raises(ValueError):
        oscillation_amplitude([[1.0, 0.0], [0.0, 1.0], [1.0]])


def test_cascade_skip_rate_zero_when_empty() -> None:
    assert cascade_skip_rate([]) == 0.0


def test_cascade_skip_rate_detects_s_to_l_skip() -> None:
    paths = [
        ["TIER_S", "TIER_L"],  # skip
        ["TIER_S", "TIER_M", "TIER_L"],  # full ladder
        ["TIER_S"],  # no escalation
        ["TIER_S", "TIER_L"],  # skip
    ]
    assert cascade_skip_rate(paths) == 0.5


def test_cascade_path_distribution() -> None:
    paths = [
        ["TIER_S", "TIER_L"],
        ["TIER_S", "TIER_L"],
        ["TIER_S", "TIER_M"],
    ]
    dist = cascade_path_distribution(paths)
    assert dist["TIER_S→TIER_L"] == 2
    assert dist["TIER_S→TIER_M"] == 1
