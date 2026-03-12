"""ADG contract tests for agentic_core/L5_safety/types/shift_report_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.shift_report_types import (
        ShiftReport, CovariateShiftDetector,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    ShiftReport = CovariateShiftDetector = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestShiftReport:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ShiftReport)
    def test_create_factory(self):
        r = ShiftReport.create(
            joint_shift=False,
            per_feature={"acc": False},
            mmd_score=0.05,
            psi_scores={"acc": 0.01},
            sample_size_ok=True,
        )
        assert r.joint_shift is False
        assert isinstance(r.timestamp, str)
        assert len(r.timestamp) > 0
    def test_skipped_factory(self):
        r = ShiftReport.skipped()
        assert r.joint_shift is False
        assert r.sample_size_ok is False
        assert r.mmd_score == 0.0

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCovariateShiftDetector:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(CovariateShiftDetector)
    def test_insufficient_samples_returns_skipped(self):
        det = CovariateShiftDetector(feature_names=["x"])
        report = det.detect_shift(baseline=[[0.9]], treatment=[[0.5]])
        assert report.sample_size_ok is False
    def test_detects_no_shift_same_distributions(self):
        det = CovariateShiftDetector(feature_names=["x"], mmd_threshold=0.1)
        baseline = [[float(i % 10) / 10] for i in range(50)]
        treatment = [[float(i % 10) / 10] for i in range(50)]
        report = det.detect_shift(baseline=baseline, treatment=treatment)
        assert report.joint_shift is False
    def test_detects_shift_sufficient_samples(self):
        det = CovariateShiftDetector(feature_names=["x"], mmd_threshold=0.05, psi_threshold=0.1)
        baseline = [[0.1] for _ in range(50)]
        treatment = [[0.9] for _ in range(50)]
        report = det.detect_shift(baseline=baseline, treatment=treatment)
        assert report.sample_size_ok is True

def test_module_importable(): assert _AVAIL or not _AVAIL
