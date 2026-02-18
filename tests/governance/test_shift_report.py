"""H4 governance tests: Multivariate drift detection with ShiftReport.

Validates:
- ShiftReport immutability (frozen dataclass)
- Minimum sample guard (n < 30 skips detection)
- MMD detects multivariate shift
- PSI detects per-feature drift
- Joint shift flag logic
- Skipped report factory
- CovariateShiftDetector integration
"""

import pytest

from agentic_core.L5_safety.types.shift_report import (
    MIN_SAMPLE_SIZE,
    CovariateShiftDetector,
    ShiftReport,
)

pytestmark = pytest.mark.governance


def _make_baseline(n: int, dim: int = 2) -> list[list[float]]:
    """Generate stable baseline data."""
    return [[float(i) / n for _ in range(dim)] for i in range(n)]


def _make_shifted(n: int, dim: int = 2) -> list[list[float]]:
    """Generate shifted treatment data."""
    return [[float(i) / n + 10.0 for _ in range(dim)] for i in range(n)]


class TestShiftReportImmutability:
    """ShiftReport must be frozen."""

    def test_cannot_mutate_field(self):
        report = ShiftReport.create(
            joint_shift=False,
            per_feature={},
            mmd_score=0.0,
            psi_scores={},
            sample_size_ok=True,
        )
        with pytest.raises(AttributeError):
            report.joint_shift = True  # type: ignore[misc]

    def test_timestamp_is_set(self):
        report = ShiftReport.create(
            joint_shift=False,
            per_feature={},
            mmd_score=0.0,
            psi_scores={},
            sample_size_ok=True,
        )
        assert report.timestamp is not None
        assert len(report.timestamp) > 0


class TestMinimumSampleGuard:
    """Detection must skip if n < 30 per stratum."""

    def test_min_sample_size_is_30(self):
        assert MIN_SAMPLE_SIZE == 30

    def test_small_sample_skips(self):
        detector = CovariateShiftDetector(feature_names=["f1", "f2"])
        baseline = _make_baseline(10, dim=2)
        treatment = _make_shifted(10, dim=2)
        report = detector.detect_shift(baseline, treatment)
        assert report.sample_size_ok is False
        assert report.joint_shift is False

    def test_sufficient_sample_runs(self):
        detector = CovariateShiftDetector(feature_names=["f1", "f2"])
        baseline = _make_baseline(35, dim=2)
        treatment = _make_shifted(35, dim=2)
        report = detector.detect_shift(baseline, treatment)
        assert report.sample_size_ok is True


class TestMMDDetection:
    """MMD must detect multivariate shift."""

    def test_identical_data_no_shift(self):
        detector = CovariateShiftDetector(
            feature_names=["f1"],
            mmd_threshold=0.1,
        )
        data = _make_baseline(40, dim=1)
        report = detector.detect_shift(data, data)
        assert report.mmd_score < 0.01

    def test_shifted_data_detected(self):
        detector = CovariateShiftDetector(
            feature_names=["f1"],
            mmd_threshold=0.01,
        )
        baseline = _make_baseline(40, dim=1)
        treatment = _make_shifted(40, dim=1)
        report = detector.detect_shift(baseline, treatment)
        assert report.mmd_score > 0.01
        assert report.joint_shift is True


class TestPSIDetection:
    """PSI must detect per-feature drift."""

    def test_per_feature_flags(self):
        detector = CovariateShiftDetector(
            feature_names=["f1", "f2"],
            psi_threshold=0.1,
        )
        baseline = _make_baseline(40, dim=2)
        treatment = _make_shifted(40, dim=2)
        report = detector.detect_shift(baseline, treatment)
        assert "f1" in report.per_feature
        assert "f2" in report.per_feature
        assert "f1" in report.psi_scores
        assert "f2" in report.psi_scores

    def test_no_drift_low_psi(self):
        detector = CovariateShiftDetector(
            feature_names=["f1"],
            psi_threshold=0.2,
            mmd_threshold=1.0,
        )
        data = _make_baseline(40, dim=1)
        report = detector.detect_shift(data, data)
        assert report.per_feature.get("f1") is False


class TestSkippedReport:
    """Skipped report factory."""

    def test_skipped_report_fields(self):
        report = ShiftReport.skipped()
        assert report.joint_shift is False
        assert report.sample_size_ok is False
        assert report.per_feature == {}
        assert report.psi_scores == {}
        assert report.mmd_score == 0.0
        assert report.timestamp is not None


class TestJointShiftLogic:
    """Joint shift = MMD exceeds OR any PSI exceeds."""

    def test_joint_true_when_mmd_exceeds(self):
        detector = CovariateShiftDetector(
            feature_names=["f1"],
            mmd_threshold=0.001,
            psi_threshold=999.0,
        )
        baseline = _make_baseline(40, dim=1)
        treatment = _make_shifted(40, dim=1)
        report = detector.detect_shift(baseline, treatment)
        assert report.joint_shift is True

    def test_joint_true_when_psi_exceeds(self):
        detector = CovariateShiftDetector(
            feature_names=["f1"],
            mmd_threshold=999.0,
            psi_threshold=0.01,
        )
        baseline = _make_baseline(40, dim=1)
        treatment = _make_shifted(40, dim=1)
        report = detector.detect_shift(baseline, treatment)
        assert report.joint_shift is True
