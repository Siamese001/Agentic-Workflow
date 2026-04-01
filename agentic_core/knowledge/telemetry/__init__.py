"""Telemetry Module.

Pipeline D Phase D1: Structured logging, query tagging, and performance attribution.
"""

from .telemetry_collector import TelemetryCollector, TelemetryEvent
from .query_tagger import QueryTagger, QueryTags
from .performance_attribution import PerformanceAttribution, PerformanceReport

__all__ = [
    "TelemetryCollector",
    "TelemetryEvent",
    "QueryTagger",
    "QueryTags",
    "PerformanceAttribution",
    "PerformanceReport",
]
