"""Tests for apps_eval service components."""

import pytest

from apps_eval.services.quality_assessor_service import (
    QualityAssessorService,
)
from apps_eval.services.regression_detector_service import (
    RegressionDetectorService,
)
from apps_eval.services.benchmark_runner_service import (
    BenchmarkRunnerService,
)


class TestQualityAssessorService:
    """Test QualityAssessorService."""

    def test_service_import(self):
        """Test that QualityAssessorService can be imported."""
        assert QualityAssessorService is not None

    def test_service_class_exists(self):
        """Test that QualityAssessorService class exists."""
        assert callable(QualityAssessorService)


class TestRegressionDetectorService:
    """Test RegressionDetectorService."""

    def test_service_import(self):
        """Test that RegressionDetectorService can be imported."""
        assert RegressionDetectorService is not None

    def test_service_class_exists(self):
        """Test that RegressionDetectorService class exists."""
        assert callable(RegressionDetectorService)


class TestBenchmarkRunnerService:
    """Test BenchmarkRunnerService."""

    def test_service_import(self):
        """Test that BenchmarkRunnerService can be imported."""
        assert BenchmarkRunnerService is not None

    def test_service_class_exists(self):
        """Test that BenchmarkRunnerService class exists."""
        assert callable(BenchmarkRunnerService)
