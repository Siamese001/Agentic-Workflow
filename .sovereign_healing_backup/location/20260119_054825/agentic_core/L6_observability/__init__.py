"""
L6 Observability Layer - SSOT for all observability, dashboards, reports, and telemetry.

Subfolders:
- dashboards/: HTML dashboards (autonomy_dashboard.html, etc.)
- reports/: Generated reports and analysis documents
- metrics/: Metric collection and aggregation
- telemetry/: Runtime telemetry and performance monitoring
- tracing/: Distributed tracing and span management
- compliance/: Compliance auditing and reporting
- agents/: Observability-related agents (RuntimeTelemetryAgent, etc.)
"""

__all__ = [
    "L6ObservabilityBaseAgent",
    "AgentPerformanceMetrics",
    "CritiqueReport",
]


def __getattr__(name: str):
    if name in __all__:
        from archives.location_violations.L6ObservabilityBaseAgent import (
            L6ObservabilityBaseAgent,
            AgentPerformanceMetrics,
            CritiqueReport,
        )
        return {
            "L6ObservabilityBaseAgent": L6ObservabilityBaseAgent,
            "AgentPerformanceMetrics": AgentPerformanceMetrics,
            "CritiqueReport": CritiqueReport,
        }[name]
    raise AttributeError(name)
