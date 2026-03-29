"""
apps_eval Services Layer — Evaluation Lab Capabilities.

Discrete service units for test discovery, execution, and analysis.
Aligned with apps_lic services/ pattern.
"""

from apps_eval.services.test_discovery_service import TestDiscoveryService
from apps_eval.services.scenario_loader_service import ScenarioLoaderService
from apps_eval.services.metric_collector_service import MetricCollectorService
from apps_eval.services.benchmark_runner_service import BenchmarkRunnerService
from apps_eval.services.result_aggregator_service import ResultAggregatorService
from apps_eval.services.regression_detector_service import RegressionDetectorService
from apps_eval.services.coverage_analyzer_service import CoverageAnalyzerService
from apps_eval.services.quality_assessor_service import QualityAssessorService

__all__ = [
    "TestDiscoveryService",
    "ScenarioLoaderService",
    "MetricCollectorService",
    "BenchmarkRunnerService",
    "ResultAggregatorService",
    "RegressionDetectorService",
    "CoverageAnalyzerService",
    "QualityAssessorService",
]
