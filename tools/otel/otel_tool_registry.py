from __future__ import annotations

from typing import Any


def register_tools(mcp, lifecycle, ops_service, query_service, ingest_service) -> None:
    @mcp.tool()
    def otel_status() -> dict[str, Any]:
        lifecycle.register_once()
        return ops_service.status()

    @mcp.tool()
    def otel_server_info() -> dict[str, Any]:
        return ops_service.server_info()

    @mcp.tool()
    def otel_trace(trace_id: str) -> dict[str, Any]:
        lifecycle.register_once()
        return query_service.trace(trace_id)

    @mcp.tool()
    def otel_spans_by_agent(agent_class: str, limit: int = 50) -> dict[str, Any]:
        return query_service.spans_by_agent(agent_class, limit=limit)

    @mcp.tool()
    def otel_healing_chain(trace_id: str) -> dict[str, Any]:
        return query_service.healing_chain(trace_id)

    @mcp.tool()
    def otel_policy_decisions(time_window_hours: int = 24) -> dict[str, Any]:
        return query_service.policy_decisions(time_window_hours=time_window_hours)

    @mcp.tool()
    def otel_metrics_summary() -> dict[str, Any]:
        return query_service.metrics_summary()

    @mcp.tool()
    def otel_anomalies(severity: str = "any") -> dict[str, Any]:
        return query_service.anomalies(severity=severity)

    @mcp.tool()
    def otel_ingest_to_runtime_adg(trace_data: dict[str, Any]) -> dict[str, Any]:
        lifecycle.register_once()
        return ingest_service.ingest_to_runtime_adg(trace_data)
