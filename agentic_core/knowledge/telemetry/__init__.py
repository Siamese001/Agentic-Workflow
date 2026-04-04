"""Telemetry Module.

Pipeline D Phase D1: Structured logging, query tagging, and performance attribution.
"""

from .performance_attribution import PerformanceAttribution, PerformanceReport
from .query_tagger import QueryTagger, QueryTags
from .telemetry_collector import TelemetryCollector, TelemetryEvent

__all__ = [
    "TelemetryCollector",
    "TelemetryEvent",
    "QueryTagger",
    "QueryTags",
    "PerformanceAttribution",
    "PerformanceReport",
]
