"""
apps_eval Services Layer — Evaluation Lab Capabilities.

Discrete service units for test discovery, execution, and analysis.
Aligned with apps_lic services/ pattern.
"""

from __future__ import annotations

from .benchmark_runner_service import BenchmarkRunnerService
from .coverage_analyzer_service import CoverageAnalyzerService
from .metric_collector_service import MetricCollectorService
from .quality_assessor_service import QualityAssessorService
from .regression_detector_service import RegressionDetectorService
from .repo_signal_service import RepoSignalService
from .result_aggregator_service import ResultAggregatorService
from .scenario_loader_service import ScenarioLoaderService
from .test_discovery_service import TestDiscoveryService

__all__ = [
    "BenchmarkRunnerService",
    "CoverageAnalyzerService",
    "MetricCollectorService",
    "QualityAssessorService",
    "RegressionDetectorService",
    "ResultAggregatorService",
    "RepoSignalService",
    "ScenarioLoaderService",
    "TestDiscoveryService",
]
