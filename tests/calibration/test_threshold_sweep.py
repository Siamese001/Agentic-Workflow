"""Unit tests for the W0.P2 threshold-sweep harness."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.calibration.feature_vector import (
    CalibrationFixture,
    FixtureRecord,
    load_fixture,
)
from tools.calibration.threshold_sweep import (
    DEFAULT_SWEEP_POINTS,
    PRPoint,
    VERTEX_DEFAULT_THRESHOLD,
    area_under_pr,
    format_report_table,
    select_optimal_threshold,
    sweep_thresholds,
    write_report,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_FIXTURE_DIR = _REPO_ROOT / "tests" / "calibration" / "fixtures"


def _make_fixture(
    path: str,
    records: list[FixtureRecord],
    *,
    invert: bool = False,
) -> CalibrationFixture:
    return CalibrationFixture(
        path=path,  # type: ignore[arg-type]
        description="synthetic",
        signal="test",
        invert_score=invert,
        records=tuple(records),
    )


# ---------------------------------------------------------------------------
# load_fixture
# ---------------------------------------------------------------------------


class TestLoadFixture:
    def test_loads_all_shipped_fixtures(self) -> None:
        fixtures = sorted(_FIXTURE_DIR.glob("*.json"))
        assert len(fixtures) == 5, "expected 5 path fixtures (R1A/R1B/R5/R3/C0)"
        for fx_path in fixtures:
            fixture = load_fixture(fx_path)
            assert fixture.path in ("R1A", "R1B", "R3", "R5", "C0")
            assert len(fixture.records) >= 10, f"{fx_path.name} too small"
            for rec in fixture.records:
                assert 0.0 <= rec.score <= 1.0

    def test_r5_fixture_is_inverted(self) -> None:
        fixture = load_fixture(_FIXTURE_DIR / "r5_abstain.json")
        assert fixture.invert_score is True

    def test_non_r5_fixtures_are_not_inverted(self) -> None:
        for name in (
            "r1a_exact_cache.json",
            "r1b_semantic_cache.json",
            "r3_grounding.json",
            "c0_coverage.json",
        ):
            assert load_fixture(_FIXTURE_DIR / name).invert_score is False

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_fixture(tmp_path / "does_not_exist.json")

    def test_invalid_path_rejected(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text(
            json.dumps({"path": "XX", "signal": "s", "records": []}),
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="invalid path"):
            load_fixture(bad)

    def test_non_numeric_score_rejected(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text(
            json.dumps(
                {
                    "path": "R1B",
                    "signal": "s",
                    "records": [{"score": "hi", "label": True}],
                },
            ),
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="'score' must be numeric"):
            load_fixture(bad)


# ---------------------------------------------------------------------------
# sweep_thresholds — correctness
# ---------------------------------------------------------------------------


class TestSweepCorrectness:
    def test_separable_fixture_reaches_perfect_f1(self) -> None:
        records = [
            FixtureRecord(score=0.90, label=True),
            FixtureRecord(score=0.85, label=True),
            FixtureRecord(score=0.80, label=True),
            FixtureRecord(score=0.30, label=False),
            FixtureRecord(score=0.20, label=False),
            FixtureRecord(score=0.10, label=False),
        ]
        fixture = _make_fixture("R1B", records)
        report = sweep_thresholds(fixture, points=101, show_progress=False)
        assert report.optimal_max_f1 is not None
        assert report.optimal_max_f1.f1 == pytest.approx(1.0)
        assert 0.3 < report.optimal_max_f1.threshold <= 0.80

    def test_invert_score_fixture_flips_semantics(self) -> None:
        # R5-style: low scores are positive class.
        records = [
            FixtureRecord(score=0.05, label=True),
            FixtureRecord(score=0.15, label=True),
            FixtureRecord(score=0.25, label=True),
            FixtureRecord(score=0.75, label=False),
            FixtureRecord(score=0.85, label=False),
            FixtureRecord(score=0.95, label=False),
        ]
        fixture = _make_fixture("R5", records, invert=True)
        report = sweep_thresholds(fixture, points=101, show_progress=False)
        assert report.optimal_max_f1 is not None
        assert report.optimal_max_f1.f1 == pytest.approx(1.0)
        # Inverted: threshold around 0.25–0.75 separates cleanly.
        assert 0.20 <= report.optimal_max_f1.threshold <= 0.80

    def test_sweep_point_count_matches(self) -> None:
        records = [
            FixtureRecord(score=0.9, label=True),
            FixtureRecord(score=0.1, label=False),
        ]
        fixture = _make_fixture("R3", records)
        report = sweep_thresholds(fixture, points=21, show_progress=False)
        assert len(report.points) == 21

    def test_sample_and_support_counts(self) -> None:
        records = [
            FixtureRecord(score=0.9, label=True),
            FixtureRecord(score=0.8, label=True),
            FixtureRecord(score=0.2, label=False),
        ]
        fixture = _make_fixture("R1A", records)
        report = sweep_thresholds(fixture, points=51, show_progress=False)
        assert report.sample_count == 3
        assert report.positive_count == 2
        assert report.negative_count == 1

    def test_empty_namespace_raises(self) -> None:
        fixture = _make_fixture(
            "R1B",
            [FixtureRecord(score=0.9, label=True, namespace="rg")],
        )
        with pytest.raises(ValueError, match="empty sweep"):
            sweep_thresholds(fixture, namespace="no-such-ns", show_progress=False)

    def test_points_minimum_validated(self) -> None:
        fixture = _make_fixture("R1A", [FixtureRecord(score=0.5, label=True)])
        with pytest.raises(ValueError, match="points must be >= 2"):
            sweep_thresholds(fixture, points=1, show_progress=False)


# ---------------------------------------------------------------------------
# select_optimal_threshold — per objective
# ---------------------------------------------------------------------------


class TestObjectives:
    @pytest.fixture()
    def sample_points(self) -> tuple[PRPoint, ...]:
        return (
            PRPoint(0.10, 5, 4, 1, 0, 0.556, 1.000, 0.714, 5, 5),
            PRPoint(0.40, 5, 1, 4, 0, 0.833, 1.000, 0.909, 5, 5),
            PRPoint(0.60, 4, 0, 5, 1, 1.000, 0.800, 0.889, 5, 5),
            PRPoint(0.80, 2, 0, 5, 3, 1.000, 0.400, 0.571, 5, 5),
            PRPoint(0.95, 0, 0, 5, 5, 0.000, 0.000, 0.000, 5, 5),
        )

    def test_max_f1(self, sample_points: tuple[PRPoint, ...]) -> None:
        best = select_optimal_threshold(sample_points, "max_f1")
        assert best is not None
        assert best.threshold == pytest.approx(0.40)

    def test_precision_first_respects_floor(
        self, sample_points: tuple[PRPoint, ...]
    ) -> None:
        best = select_optimal_threshold(
            sample_points,
            "precision_first",
            precision_floor=0.95,
        )
        # Only thresholds 0.60 and 0.80 satisfy precision>=0.95.
        # Among those, pick highest recall -> 0.60.
        assert best is not None
        assert best.threshold == pytest.approx(0.60)

    def test_precision_first_unreachable_returns_none(
        self, sample_points: tuple[PRPoint, ...]
    ) -> None:
        assert (
            select_optimal_threshold(
                sample_points,
                "precision_first",
                precision_floor=1.01,
            )
            is None
        )

    def test_recall_first_respects_floor(
        self, sample_points: tuple[PRPoint, ...]
    ) -> None:
        best = select_optimal_threshold(
            sample_points,
            "recall_first",
            recall_floor=0.80,
        )
        # Thresholds 0.10, 0.40, 0.60 satisfy recall>=0.80. Pick highest precision
        # -> 0.60 (P=1.0).
        assert best is not None
        assert best.threshold == pytest.approx(0.60)

    def test_vertex_default_floor(self, sample_points: tuple[PRPoint, ...]) -> None:
        best = select_optimal_threshold(sample_points, "vertex_default")
        # Closest to 0.7 from above -> 0.80.
        assert best is not None
        assert best.threshold >= VERTEX_DEFAULT_THRESHOLD

    def test_unknown_objective_raises(
        self, sample_points: tuple[PRPoint, ...]
    ) -> None:
        with pytest.raises(ValueError, match="Unknown objective"):
            select_optimal_threshold(sample_points, "nonsense")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# area_under_pr + report IO
# ---------------------------------------------------------------------------


class TestReporting:
    def test_area_under_pr_monotone_case(self) -> None:
        points = (
            PRPoint(0.1, 0, 0, 0, 0, 0.50, 0.20, 0.286, 0, 0),
            PRPoint(0.5, 0, 0, 0, 0, 0.75, 0.50, 0.600, 0, 0),
            PRPoint(0.9, 0, 0, 0, 0, 1.00, 0.80, 0.889, 0, 0),
        )
        auc = area_under_pr(points)
        # Hand-computed trapezoidal area: 0.3*(0.5+0.75)/2 + 0.3*(0.75+1.0)/2
        #   = 0.1875 + 0.2625 = 0.45.
        assert auc == pytest.approx(0.45)

    def test_area_under_pr_empty_returns_zero(self) -> None:
        assert area_under_pr(()) == 0.0

    def test_write_report_roundtrip(self, tmp_path: Path) -> None:
        fixture = _make_fixture(
            "R3",
            [
                FixtureRecord(score=0.9, label=True),
                FixtureRecord(score=0.1, label=False),
            ],
        )
        report = sweep_thresholds(fixture, points=11, show_progress=False)
        out = tmp_path / "r3_sweep.json"
        resolved = write_report(report, out)
        assert resolved == out
        assert out.is_file()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["path"] == "R3"
        assert data["sample_count"] == 2
        assert len(data["points"]) == 11
        assert data["optimal_max_f1"]["f1"] == pytest.approx(1.0)

    def test_format_report_table_mentions_all_objectives(self) -> None:
        fixture = _make_fixture(
            "C0",
            [
                FixtureRecord(score=0.9, label=True),
                FixtureRecord(score=0.1, label=False),
            ],
        )
        report = sweep_thresholds(fixture, points=11, show_progress=False)
        text = format_report_table(report)
        for label in ("max_f1", "precision_first", "recall_first", "vertex_default"):
            assert label in text


# ---------------------------------------------------------------------------
# default resolution sanity
# ---------------------------------------------------------------------------


def test_default_sweep_points_is_odd_and_includes_both_endpoints() -> None:
    # 101 points -> step 0.01, includes 0.00 and 1.00.
    assert DEFAULT_SWEEP_POINTS == 101
    assert 1.0 / (DEFAULT_SWEEP_POINTS - 1) == pytest.approx(0.01)
