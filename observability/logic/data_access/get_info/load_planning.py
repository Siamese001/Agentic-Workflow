"""Observability Load Planner - Plans data loading operations for observability metrics and logs.

This planner manages the loading phase for observability data operations,
including metric collection, log aggregation, and monitoring data optimization.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics to load."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class LogLevel(Enum):
    """Log levels for log data."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class DataSource(Enum):
    """Types of observability data sources."""
    PROMETHEUS = "prometheus"
    ELASTICSEARCH = "elasticsearch"
    LOKI = "loki"
    JAEGER = "jaeger"
    ZIPKIN = "zipkin"
    CUSTOM_API = "custom_api"

@dataclass
class MetricDefinition:
    """Definition of a metric to load."""
    id: str
    name: str
    metric_type: MetricType
    query: str
    labels: Dict[str, str] = field(default_factory=dict)
    sampling_rate: float = 1.0

@dataclass
class LogQuery:
    """Definition of a log query to load."""
    id: str
    name: str
    query: str
    log_level: LogLevel
    time_range: str  # e.g., "1h", "24h", "7d"
    fields: List[str] = field(default_factory=list)

@dataclass
class TraceQuery:
    """Definition of a trace query to load."""
    id: str
    name: str
    service_name: str
    operation_name: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    time_range: str = "1h"

@dataclass
class ObservabilityLoadPlan:
    """Complete plan for observability data loading."""
    id: str
    name: str
    metrics: List[MetricDefinition] = field(default_factory=list)
    logs: List[LogQuery] = field(default_factory=list)
    traces: List[TraceQuery] = field(default_factory=list)
    data_sources: List[DataSource] = field(default_factory=list)
    batch_size: int = 1000
    retention_hours: int = 24
    aggregation_rules: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ObservabilityLoadConfig:
    """Configuration for observability load planning."""
    enable_metrics: bool = True
    enable_logs: bool = True
    enable_traces: bool = True
    enable_aggregation: bool = True
    max_queries_per_plan: int = 50
    default_retention_hours: int = 24
    log_level: str = "INFO"

@dataclass
class ObservabilityLoadResult:
    """Result of observability load planning."""
    success: bool
    load_plan: Optional[ObservabilityLoadPlan] = None
    estimated_data_points: int = 0
    storage_requirements: Dict[str, int] = field(default_factory=dict)
    processing_time: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ObservabilityLoadPlanner:
    """Planner for observability data loading operations."""

    def __init__(self, config: Optional[ObservabilityLoadConfig] = None):
        self.config = config or ObservabilityLoadConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def plan_load(self, load_request: Dict[str, Any]) -> ObservabilityLoadResult:
        """Plan observability data loading operations.

        Args:
            load_request: Dictionary containing load requirements and queries

        Returns:
            ObservabilityLoadResult: Complete planning result with load plan
        """
        self.logger.info(f"Starting observability load planning for: {load_request.get('plan_name', 'unknown')}")

        try:
            # Validate input request
            self._validate_request(load_request)

            # Parse metrics
            metrics = self._parse_metrics(load_request) if self.config.enable_metrics else []

            # Parse logs
            logs = self._parse_logs(load_request) if self.config.enable_logs else []

            # Parse traces
            traces = self._parse_traces(load_request) if self.config.enable_traces else []

            # Parse data sources
            data_sources = self._parse_data_sources(load_request)

            # Create load plan
            load_plan = self._create_load_plan(
                load_request, metrics, logs, traces, data_sources
            )

            # Estimate data points
            estimated_points = self._estimate_data_points(load_plan)

            # Calculate storage requirements
            storage_requirements = self._calculate_storage_requirements(load_plan)

            # Estimate processing time
            processing_time = self._estimate_processing_time(load_plan)

            result = ObservabilityLoadResult(
                success=True,
                load_plan=load_plan,
                estimated_data_points=estimated_points,
                storage_requirements=storage_requirements,
                processing_time=processing_time,
                metadata={
                    "planned_at": datetime.utcnow().isoformat(),
                    "plan_name": load_request.get("plan_name"),
                    "metric_count": len(metrics),
                    "log_count": len(logs),
                    "trace_count": len(traces),
                    "planner": "ObservabilityLoadPlanner"
                }
            )

            self.logger.info(
                f"Successfully planned observability load: "
                f"{len(metrics)} metrics, {len(logs)} logs, {len(traces)} traces"
            )
            return result

        except Exception as e:
            self.logger.error(f"Observability load planning failed: {str(e)}")
            return ObservabilityLoadResult(
                success=False,
                errors=[str(e)],
                metadata={
                    "failed_at": datetime.utcnow().isoformat(),
                    "planner": "ObservabilityLoadPlanner"
                }
            )

    def _validate_request(self, request: Dict[str, Any]) -> None:
        """Validate observability load planning request."""
        if not request:
            raise ValueError("Observability load planning request cannot be empty")

        if "plan_name" not in request:
            raise ValueError("Plan name is required in observability load planning request")

    def _parse_metrics(self, request: Dict[str, Any]) -> List[MetricDefinition]:
        """Parse metric definitions from request."""
        metrics = []
        raw_metrics = request.get("metrics", [])

        for raw_metric in raw_metrics:
            if isinstance(raw_metric, dict):
                # Map strings to enums
                metric_type_mapping = {
                    "counter": MetricType.COUNTER,
                    "gauge": MetricType.GAUGE,
                    "histogram": MetricType.HISTOGRAM,
                    "summary": MetricType.SUMMARY
                }

                metric = MetricDefinition(
                    id=raw_metric.get("id", f"metric_{len(metrics)}"),
                    name=raw_metric.get("name", "unnamed"),
                    metric_type=metric_type_mapping.get(
                        raw_metric.get("metric_type", "counter"),
                        MetricType.COUNTER
                    ),
                    query=raw_metric.get("query", ""),
                    labels=raw_metric.get("labels", {}),
                    sampling_rate=raw_metric.get("sampling_rate", 1.0)
                )
                metrics.append(metric)

        return metrics

    def _parse_logs(self, request: Dict[str, Any]) -> List[LogQuery]:
        """Parse log queries from request."""
        logs = []
        raw_logs = request.get("logs", [])

        for raw_log in raw_logs:
            if isinstance(raw_log, dict):
                # Map strings to enums
                log_level_mapping = {
                    "debug": LogLevel.DEBUG,
                    "info": LogLevel.INFO,
                    "warning": LogLevel.WARNING,
                    "error": LogLevel.ERROR,
                    "critical": LogLevel.CRITICAL
                }

                log = LogQuery(
                    id=raw_log.get("id", f"log_{len(logs)}"),
                    name=raw_log.get("name", "unnamed"),
                    query=raw_log.get("query", ""),
                    log_level=log_level_mapping.get(
                        raw_log.get("log_level", "info"),
                        LogLevel.INFO
                    ),
                    time_range=raw_log.get("time_range", "1h"),
                    fields=raw_log.get("fields", [])
                )
                logs.append(log)

        return logs

    def _parse_traces(self, request: Dict[str, Any]) -> List[TraceQuery]:
        """Parse trace queries from request."""
        traces = []
        raw_traces = request.get("traces", [])

        for raw_trace in raw_traces:
            if isinstance(raw_trace, dict):
                trace = TraceQuery(
                    id=raw_trace.get("id", f"trace_{len(traces)}"),
                    name=raw_trace.get("name", "unnamed"),
                    service_name=raw_trace.get("service_name", ""),
                    operation_name=raw_trace.get("operation_name"),
                    tags=raw_trace.get("tags", {}),
                    time_range=raw_trace.get("time_range", "1h")
                )
                traces.append(trace)

        return traces

    def _parse_data_sources(self, request: Dict[str, Any]) -> List[DataSource]:
        """Parse data sources from request."""
        sources = []
        raw_sources = request.get("data_sources", [])

        # Map strings to enums
        source_mapping = {
            "prometheus": DataSource.PROMETHEUS,
            "elasticsearch": DataSource.ELASTICSEARCH,
            "loki": DataSource.LOKI,
            "jaeger": DataSource.JAEGER,
            "zipkin": DataSource.ZIPKIN,
            "custom_api": DataSource.CUSTOM_API
        }

        for raw_source in raw_sources:
            if isinstance(raw_source, str):
                source = source_mapping.get(raw_source.lower())
                if source:
                    sources.append(source)
            elif isinstance(raw_source, dict):
                source_type = raw_source.get("type")
                source = source_mapping.get(source_type.lower())
                if source:
                    sources.append(source)

        # Default to prometheus if no sources specified
        if not sources:
            sources.append(DataSource.PROMETHEUS)

        return sources

    def _create_load_plan(
        self,
        request: Dict[str, Any],
        metrics: List[MetricDefinition],
        logs: List[LogQuery],
        traces: List[TraceQuery],
        data_sources: List[DataSource]
    ) -> ObservabilityLoadPlan:
        """Create observability load plan from parsed components."""
        total_queries = len(metrics) + len(logs) + len(traces)

        if total_queries > self.config.max_queries_per_plan:
            raise ValueError(
                f"Number of queries ({total_queries}) exceeds maximum "
                f"({self.config.max_queries_per_plan})"
            )

        return ObservabilityLoadPlan(
            id=request.get("plan_id", f"plan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"),
            name=request.get("plan_name", "unnamed_plan"),
            metrics=metrics,
            logs=logs,
            traces=traces,
            data_sources=data_sources,
            batch_size=request.get("batch_size", 1000),
            retention_hours=request.get("retention_hours", self.config.default_retention_hours),
            aggregation_rules=request.get("aggregation_rules", {}),
            metadata=request.get("metadata", {})
        )

    def _estimate_data_points(self, plan: ObservabilityLoadPlan) -> int:
        """Estimate total number of data points to be loaded."""
        total_points = 0

        # Estimate metrics (assume 1 point per minute per metric)
        for metric in plan.metrics:
            points_per_hour = 60 * metric.sampling_rate
            total_points += points_per_hour * plan.retention_hours

        # Estimate logs (assume 100 logs per hour per query)
        for log in plan.logs:
            logs_per_hour = 100
            total_points += logs_per_hour * plan.retention_hours

        # Estimate traces (assume 50 traces per hour per query)
        for trace in plan.traces:
            traces_per_hour = 50
            total_points += traces_per_hour * plan.retention_hours

        return int(total_points)

    def _calculate_storage_requirements(self, plan: ObservabilityLoadPlan) -> Dict[str, int]:
        """Calculate storage requirements in MB."""
        requirements = {
            "metrics_mb": 0,
            "logs_mb": 0,
            "traces_mb": 0,
            "total_mb": 0
        }

        # Metrics: ~100 bytes per point
        metric_points = len(plan.metrics) * 60 * plan.retention_hours
        requirements["metrics_mb"] = (metric_points * 100) // (1024 * 1024)

        # Logs: ~1KB per log entry
        log_entries = len(plan.logs) * 100 * plan.retention_hours
        requirements["logs_mb"] = (log_entries * 1024) // (1024 * 1024)

        # Traces: ~500 bytes per span
        trace_spans = len(plan.traces) * 50 * plan.retention_hours
        requirements["traces_mb"] = (trace_spans * 500) // (1024 * 1024)

        requirements["total_mb"] = (
            requirements["metrics_mb"] +
            requirements["logs_mb"] +
            requirements["traces_mb"]
        )

        return requirements

    def _estimate_processing_time(self, plan: ObservabilityLoadPlan) -> int:
        """Estimate processing time in seconds."""
        base_time = 5  # Base setup time

        # Add time per query
        query_time = (
            len(plan.metrics) * 2 +
            len(plan.logs) * 5 +
            len(plan.traces) * 3
        )

        # Add time for aggregation if enabled
        aggregation_time = 10 if self.config.enable_aggregation else 0

        total_time = base_time + query_time + aggregation_time

        return int(total_time)

# Factory function for easy instantiation
def create_observability_load_planner(
    max_metrics: int = 100,
    max_logs: int = 100,
    max_traces: int = 100,
    **kwargs: object
) -> ObservabilityLoadPlanner:
    """Create a configured observability load planner."""
    config = ObservabilityLoadConfig(
        max_metrics=max_metrics,
        max_logs=max_logs,
        max_traces=max_traces,
        **kwargs
    )
    return ObservabilityLoadPlanner(config)

# Convenience function for direct usage
def plan_observability_load(
    plan_name: str,
    metrics: Optional[List[Dict[str, Any]]] = None,
    logs: Optional[List[Dict[str, Any]]] = None,
    traces: Optional[List[Dict[str, Any]]] = None,
    data_sources: Optional[List[str]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Plan observability data load from simple parameters.

    Args:
        plan_name: Name of the load plan
        metrics: Optional list of metric definitions
        logs: Optional list of log queries
        traces: Optional list of trace queries
        data_sources: Optional list of data source types
        config: Optional planner configuration overrides

    Returns:
        Dict: Planning result with load plan and resource requirements
    """
    # Build request
    request = {
        "plan_name": plan_name,
        "metrics": metrics or [],
        "logs": logs or [],
        "traces": traces or [],
        "data_sources": data_sources or ["prometheus"]
    }

    # Create planner and execute
    planner_config = ObservabilityLoadConfig(**config) if config else None
    planner = ObservabilityLoadPlanner(planner_config)
    result = planner.plan_load(request)

    # Convert result to dict for JSON serialization
    return {
        "success": result.success,
        "load_plan": {
            "id": result.load_plan.id,
            "name": result.load_plan.name,
            "metrics": [
                {
                    "id": m.id,
                    "name": m.name,
                    "metric_type": m.metric_type.value,
                    "query": m.query,
                    "labels": m.labels,
                    "sampling_rate": m.sampling_rate
                }
                for m in result.load_plan.metrics
            ],
            "logs": [
                {
                    "id": l.id,
                    "name": l.name,
                    "query": l.query,
                    "log_level": l.log_level.value,
                    "time_range": l.time_range,
                    "fields": l.fields
                }
                for l in result.load_plan.logs
            ],
            "traces": [
                {
                    "id": t.id,
                    "name": t.name,
                    "service_name": t.service_name,
                    "operation_name": t.operation_name,
                    "tags": t.tags,
                    "time_range": t.time_range
                }
                for t in result.load_plan.traces
            ],
            "data_sources": [s.value for s in result.load_plan.data_sources],
            "batch_size": result.load_plan.batch_size,
            "retention_hours": result.load_plan.retention_hours,
            "aggregation_rules": result.load_plan.aggregation_rules,
            "metadata": result.load_plan.metadata
        } if result.load_plan else None,
        "estimated_data_points": result.estimated_data_points,
        "storage_requirements": result.storage_requirements,
        "processing_time": result.processing_time,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata
    }
