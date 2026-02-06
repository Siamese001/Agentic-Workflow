"""observability Request Understanding Load Planner - Plans data loading for observability request understanding.

This planner manages the loading phase for understanding observability requests,
including metric parsing, log analysis, and trace extraction.
Follows the canonical pattern with dataclass-first design and proper logging.
"""

import logging
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class RequestType(Enum):
    """Types of observability requests."""

    METRIC_QUERY = "metric_query"
    LOG_SEARCH = "log_search"
    TRACE_LOOKUP = "trace_lookup"
    AGGREGATION = "aggregation"
    ANOMALY_DETECTION = "anomaly_detection"


class DataSource(Enum):
    """Data sources for observability."""

    PROMETHEUS = "prometheus"
    ELASTICSEARCH = "elasticsearch"
    JAEGER = "jaeger"
    ZIPKIN = "zipkin"
    GRAFANA = "grafana"
    DATADOG = "datadog"


class AggregationType(Enum):
    """Types of aggregations."""

    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE = "percentile"


@dataclass
class MetricDefinition:
    """Definition of a metric to be loaded."""

    name: str
    query: str
    labels: dict[str, str] = field(default_factory=dict)
    aggregation: AggregationType | None = None
    time_range: str = "1h"
    step: int = 60


@dataclass
class LogQuery:
    """Definition of a log search query."""

    index: str
    query: str
    filters: dict[str, Any] = field(default_factory=dict)
    time_range: str = "1h"
    size: int = 1000
    sort_field: str = "@timestamp"
    sort_order: str = "desc"


@dataclass
class TraceQuery:
    """Definition of a trace lookup query."""

    service: str | None = None
    operation: str | None = None
    trace_id: str | None = None
    tags: dict[str, str] = field(default_factory=dict)
    time_range: str = "1h"
    limit: int = 100


@dataclass
class ObservabilityLoadPlan:
    """Complete plan for observability data loading."""

    id: str
    name: str
    request_type: RequestType
    data_source: DataSource
    metrics: list[MetricDefinition] = field(default_factory=list)
    log_queries: list[LogQuery] = field(default_factory=list)
    trace_queries: list[TraceQuery] = field(default_factory=list)
    enable_caching: bool = True
    cache_ttl: int = 300
    enable_sampling: bool = False
    sample_rate: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ObservabilityLoadConfig:
    """configuration for observability load planning."""

    enable_metrics: bool = True
    enable_logs: bool = True
    enable_traces: bool = True
    max_queries_per_plan: int = 50
    default_time_range: str = "1h"
    max_time_range: str = "24h"
    log_level: str = "INFO"


@dataclass
class ObservabilityLoadResult:
    """Result of observability load planning."""

    success: bool
    load_plan: ObservabilityLoadPlan | None = None
    estimated_data_points: int = 0
    query_count: int = 0
    load_time_estimate: int = 0
    memory_estimate: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ObservabilityLoadPlanner:
    """Planner for observability data loading operations."""

    def __init__(self, config: ObservabilityLoadConfig | None = None):
        self.config = config or ObservabilityLoadConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)

    def plan_load(self, load_request: dict[str, Any]) -> ObservabilityLoadResult:
        """Plan observability data loading operations.

        Args:
            load_request: Dictionary containing load requirements and queries

        Returns:
            ObservabilityLoadResult: Complete planning result with load plan
        """
        self.logger.info(
            f"Starting observability load planning for: {load_request.get('plan_name', 'unknown')}",
        )

        try:
            # Validate input request
            self._validate_request(load_request)

            # Parse request type
            request_type = self._parse_request_type(load_request)

            # Parse data source
            data_source = self._parse_data_source(load_request)

            # Parse metrics if enabled
            metrics = self._parse_metrics(load_request) if self.config.enable_metrics else []

            # Parse log queries if enabled
            log_queries = self._parse_log_queries(load_request) if self.config.enable_logs else []

            # Parse trace queries if enabled
            trace_queries = self._parse_trace_queries(load_request) if self.config.enable_traces else []

            # Create load plan
            load_plan = self._create_load_plan(
                load_request,
                request_type,
                data_source,
                metrics,
                log_queries,
                trace_queries,
            )

            # Estimate data points
            estimated_data_points = self._estimate_data_points(load_plan)

            # Count queries
            query_count = len(metrics) + len(log_queries) + len(trace_queries)

            # Estimate load time
            load_time = self._estimate_load_time(load_plan)

            # Estimate memory usage
            memory_estimate = self._estimate_memory_usage(load_plan)

            result = ObservabilityLoadResult(
                success=True,
                load_plan=load_plan,
                estimated_data_points=estimated_data_points,
                query_count=query_count,
                load_time_estimate=load_time,
                memory_estimate=memory_estimate,
                metadata={
                    "planned_at": datetime.utcnow().isoformat(),
                    "plan_name": load_request.get("plan_name"),
                    "request_type": request_type.value,
                    "data_source": data_source.value,
                    "planner": "ObservabilityLoadPlanner",
                },
            )

            self.logger.info(
                f"Successfully planned observability load: "
                f"{query_count} queries, ~{estimated_data_points} data points",
            )
            return result

        except Exception as e:
            self.logger.error(f"observability load planning failed: {str(e)}")
            return ObservabilityLoadResult(
                success=False,
                errors=[str(e)],
                metadata={
                    "failed_at": datetime.utcnow().isoformat(),
                    "planner": "ObservabilityLoadPlanner",
                },
            )

    def _validate_request(self, request: dict[str, Any]) -> None:
        """Validate observability load planning request."""
        if not request:
            raise ValueError("observability load planning request cannot be empty")

        if "plan_name" not in request:
            raise ValueError("Plan name is required in observability load planning request")

        if "request_type" not in request:
            raise ValueError("Request type is required in observability load planning request")

    def _parse_request_type(self, request: dict[str, Any]) -> RequestType:
        """Parse request type from request."""
        type_mapping = {
            "metric_query": RequestType.METRIC_QUERY,
            "log_search": RequestType.LOG_SEARCH,
            "trace_lookup": RequestType.TRACE_LOOKUP,
            "aggregation": RequestType.AGGREGATION,
            "anomaly_detection": RequestType.ANOMALY_DETECTION,
        }

        request_type_str = request.get("request_type", "metric_query")
        return type_mapping.get(request_type_str, RequestType.METRIC_QUERY)

    def _parse_data_source(self, request: dict[str, Any]) -> DataSource:
        """Parse data source from request."""
        source_mapping = {
            "prometheus": DataSource.PROMETHEUS,
            "elasticsearch": DataSource.ELASTICSEARCH,
            "jaeger": DataSource.JAEGER,
            "zipkin": DataSource.ZIPKIN,
            "grafana": DataSource.GRAFANA,
            "datadog": DataSource.DATADOG,
        }

        source_str = request.get("data_source", "prometheus")
        return source_mapping.get(source_str, DataSource.PROMETHEUS)

    def _parse_metrics(self, request: dict[str, Any]) -> list[MetricDefinition]:
        """Parse metrics from request."""
        metrics = []
        raw_metrics = request.get("metrics", [])

        for raw_metric in raw_metrics:
            if isinstance(raw_metric, dict):
                # Parse aggregation if present
                aggregation = None
                if "aggregation" in raw_metric:
                    agg_mapping = {
                        "sum": AggregationType.SUM,
                        "avg": AggregationType.AVG,
                        "min": AggregationType.MIN,
                        "max": AggregationType.MAX,
                        "count": AggregationType.COUNT,
                        "percentile": AggregationType.PERCENTILE,
                    }
                    aggregation = agg_mapping.get(
                        raw_metric.get("aggregation"),
                        AggregationType.AVG,
                    )

                metric = MetricDefinition(
                    name=raw_metric.get("name", "unnamed"),
                    query=raw_metric.get("query", ""),
                    labels=raw_metric.get("labels", {}),
                    aggregation=aggregation,
                    time_range=raw_metric.get("time_range", self.config.default_time_range),
                    step=raw_metric.get("step", 60),
                )
                metrics.append(metric)

        # Validate metric count
        if len(metrics) > self.config.max_queries_per_plan:
            raise ValueError(
                f"Number of metrics ({len(metrics)}) exceeds maximum ({self.config.max_queries_per_plan})",
            )

        return metrics

    def _parse_log_queries(self, request: dict[str, Any]) -> list[LogQuery]:
        """Parse log queries from request."""
        queries = []
        raw_queries = request.get("log_queries", [])

        for raw_query in raw_queries:
            if isinstance(raw_query, dict):
                query = LogQuery(
                    index=raw_query.get("index", "logs-*"),
                    query=raw_query.get("query", "*"),
                    filters=raw_query.get("filters", {}),
                    time_range=raw_query.get("time_range", self.config.default_time_range),
                    size=raw_query.get("size", 1000),
                    sort_field=raw_query.get("sort_field", "@timestamp"),
                    sort_order=raw_query.get("sort_order", "desc"),
                )
                queries.append(query)

        # Validate query count
        if len(queries) > self.config.max_queries_per_plan:
            raise ValueError(
                f"Number of log queries ({len(queries)}) exceeds maximum "
                f"({self.config.max_queries_per_plan})",
            )

        return queries

    def _parse_trace_queries(self, request: dict[str, Any]) -> list[TraceQuery]:
        """Parse trace queries from request."""
        queries = []
        raw_queries = request.get("trace_queries", [])

        for raw_query in raw_queries:
            if isinstance(raw_query, dict):
                query = TraceQuery(
                    service=raw_query.get("service"),
                    operation=raw_query.get("operation"),
                    trace_id=raw_query.get("trace_id"),
                    tags=raw_query.get("tags", {}),
                    time_range=raw_query.get("time_range", self.config.default_time_range),
                    limit=raw_query.get("limit", 100),
                )
                queries.append(query)

        # Validate query count
        if len(queries) > self.config.max_queries_per_plan:
            raise ValueError(
                f"Number of trace queries ({len(queries)}) exceeds maximum "
                f"({self.config.max_queries_per_plan})",
            )

        return queries

    def _create_load_plan(
        self,
        request: dict[str, Any],
        request_type: RequestType,
        data_source: DataSource,
        metrics: list[MetricDefinition],
        log_queries: list[LogQuery],
        trace_queries: list[TraceQuery],
    ) -> ObservabilityLoadPlan:
        """Create observability load plan from parsed components."""
        return ObservabilityLoadPlan(
            id=request.get("plan_id", f"plan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"),
            name=request.get("plan_name", "unnamed_plan"),
            request_type=request_type,
            data_source=data_source,
            metrics=metrics,
            log_queries=log_queries,
            trace_queries=trace_queries,
            enable_caching=request.get("enable_caching", True),
            cache_ttl=request.get("cache_ttl", 300),
            enable_sampling=request.get("enable_sampling", False),
            sample_rate=request.get("sample_rate", 1.0),
            metadata=request.get("metadata", {}),
        )

    def _estimate_data_points(self, plan: ObservabilityLoadPlan) -> int:
        """Estimate total number of data points."""
        total_points = 0

        # Estimate metric data points
        for metric in plan.metrics:
            # Rough estimate: 1 data point per step
            time_range_minutes = self._parse_time_range(metric.time_range)
            points_per_metric = time_range_minutes * 60 // metric.step
            total_points += points_per_metric

        # Estimate log entries
        for query in plan.log_queries:
            # Assume average of 1000 results per query
            total_points += query.size

        # Estimate trace spans
        for query in plan.trace_queries:
            # Assume average of 50 spans per trace
            total_points += query.limit * 50

        return total_points

    def _parse_time_range(self, time_range: str) -> int:
        """Parse time range string to minutes."""
        if time_range.endswith("m"):
            return int(time_range[:-1])
        elif time_range.endswith("h"):
            return int(time_range[:-1]) * 60
        elif time_range.endswith("d"):
            return int(time_range[:-1]) * 60 * 24
        else:
            return 60  # Default to 1 hour

    def _estimate_load_time(self, plan: ObservabilityLoadPlan) -> int:
        """Estimate load time in seconds."""
        base_time = 5  # Base setup time

        # Add time per query
        query_time = (len(plan.metrics) + len(plan.log_queries) + len(plan.trace_queries)) * 2

        # Add time for data processing
        data_points = self._estimate_data_points(plan)
        processing_time = data_points * 0.001  # 1ms per data point

        total_time = base_time + query_time + processing_time

        return int(total_time)

    def _estimate_memory_usage(self, plan: ObservabilityLoadPlan) -> int:
        """Estimate memory usage in MB."""
        # Base memory usage
        base_memory = 50  # 50MB base

        # Memory for metrics (assume 100 bytes per data point)
        metric_memory = 0
        for metric in plan.metrics:
            time_range_minutes = self._parse_time_range(metric.time_range)
            points_per_metric = time_range_minutes * 60 // metric.step
            metric_memory += points_per_metric * 100

        # Memory for logs (assume 1KB per log entry)
        log_memory = sum(query.size * 1024 for query in plan.log_queries)

        # Memory for traces (assume 500 bytes per span)
        trace_memory = sum(query.limit * 50 * 500 for query in plan.trace_queries)

        total_memory_bytes = base_memory * 1024 * 1024 + metric_memory + log_memory + trace_memory

        return total_memory_bytes // (1024 * 1024)  # Convert to MB


# Factory function for easy instantiation
def create_observability_load_planner(
    enable_metrics: bool = True,
    enable_logs: bool = True,
    enable_traces: bool = True,
    **kwargs: object,
) -> ObservabilityLoadPlanner:
    """Create a configured observability load planner."""
    config = ObservabilityLoadConfig(
        enable_metrics=enable_metrics,
        enable_logs=enable_logs,
        enable_traces=enable_traces,
        **kwargs,
    )
    return ObservabilityLoadPlanner(config)


# Convenience function for direct usage
def plan_observability_load(
    plan_name: str,
    request_type: str,
    data_source: str = "prometheus",
    metrics: list[dict[str, Any]] | None = None,
    log_queries: list[dict[str, Any]] | None = None,
    trace_queries: list[dict[str, Any]] | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Plan observability data load from simple parameters.

    Args:
        plan_name: Name of the load plan
        request_type: Type of observability request
        data_source: Data source to use
        metrics: Optional list of metric definitions
        log_queries: Optional list of log query definitions
        trace_queries: Optional list of trace query definitions
        config: Optional planner configuration overrides

    Returns:
        Dict: Planning result with load plan and resource requirements
    """
    # Build request
    request = {
        "plan_name": plan_name,
        "request_type": request_type,
        "data_source": data_source,
        "metrics": metrics or [],
        "log_queries": log_queries or [],
        "trace_queries": trace_queries or [],
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
            "request_type": result.load_plan.request_type.value,
            "data_source": result.load_plan.data_source.value,
            "metrics": [
                {
                    "name": m.name,
                    "query": m.query,
                    "labels": m.labels,
                    "aggregation": m.aggregation.value if m.aggregation else None,
                    "time_range": m.time_range,
                    "step": m.step,
                }
                for m in result.load_plan.metrics
            ],
            "log_queries": [
                {
                    "index": q.index,
                    "query": q.query,
                    "filters": q.filters,
                    "time_range": q.time_range,
                    "size": q.size,
                    "sort_field": q.sort_field,
                    "sort_order": q.sort_order,
                }
                for q in result.load_plan.log_queries
            ],
            "trace_queries": [
                {
                    "service": q.service,
                    "operation": q.operation,
                    "trace_id": q.trace_id,
                    "tags": q.tags,
                    "time_range": q.time_range,
                    "limit": q.limit,
                }
                for q in result.load_plan.trace_queries
            ],
            "enable_caching": result.load_plan.enable_caching,
            "cache_ttl": result.load_plan.cache_ttl,
            "enable_sampling": result.load_plan.enable_sampling,
            "sample_rate": result.load_plan.sample_rate,
            "metadata": result.load_plan.metadata,
        }
        if result.load_plan
        else None,
        "estimated_data_points": result.estimated_data_points,
        "query_count": result.query_count,
        "load_time_estimate": result.load_time_estimate,
        "memory_estimate": result.memory_estimate,
        "warnings": result.warnings,
        "errors": result.errors,
        "metadata": result.metadata,
    }


class LoadDataPlanningPlanImpl(LoadDataPlanningPlanProcessor):
    """
    L5 Implementation - L1 Cognitive Planning Layer
    Pure planning functionality with no side effects
    """

    def __init__(self, constraints: LoadDataPlanningPlanConstraints | None = None):
        self.constraints = constraints or LoadDataPlanningPlanConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)

    def process(self, input_data: dict[str, object]) -> LoadDataPlanningPlanResult:
        """Process input following L5 architecture principles"""
        self.logger.info(f"Processing {input_data}")

        # L5 Input validation
        self._validate_input(input_data)

        # L5 Safety validation - fail-closed
        if not self.validate_safety(input_data):
            raise SecurityError("Input failed L5 safety validation")

        # Create result with L5 structure
        result = LoadDataPlanningPlanResult(
            success=True,
            data={"processed": True, "input": input_data},
            safety_validated=True,
            timestamp=self._get_timestamp(),
        )

        self.logger.info(f"Successfully processed: {result.success}")
        return result

    def validate_safety(self, data: dict[str, object]) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check for dangerous patterns
            dangerous_patterns = [
                "<script>",
                "javascript:",
                "ast.literal_eval(",
                "pass  # exec disabled: ",
                "__import__",
            ]
            data_str = str(data).lower()
            for pattern in dangerous_patterns:
                if pattern in data_str:
                    self.logger.error(f" Dangerous pattern detected: {pattern}")
                    return False

            # Check data size
            if len(str(data)) > 1000000:  # 1MB limit
                self.logger.error("Data exceeds size limit")
                return False

            self.logger.info("Data passed L5 safety validation")
            return True
        except (ValueError, TypeError, RuntimeError, KeyError) as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed

    def _validate_input(self, input_data: dict[str, object]) -> None:
        """L5 Input validation"""
        if not isinstance(input_data, dict):
            raise ValueError("Input must be a dictionary")

        if not input_data:
            raise ValueError("Input cannot be empty")

    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime

        return datetime.utcnow().isoformat()


class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""

    ...


# L5 Interface compliance
class LoadDataPlanningPlanInterface:
    """L5 Interface - ensures contract compliance"""

    def __init__(self, engine: LoadDataPlanningPlanProcessor):
        self._processor = engine

    def execute(self, input_data: dict[str, object]) -> dict[str, object]:
        """L5 Interface method - executes safely"""
        try:
            result = self._processor.process(input_data)
            return {
                "success": result.success,
                "data": result.data,
                "errors": result.errors,
                "safety_validated": result.safety_validated,
                "timestamp": result.timestamp,
            }
        except (ValueError, TypeError, RuntimeError, KeyError) as e:
            raise SecurityError(f"Execution failed: {e}")


# L5 builder
class LoadDataPlanningPlanFactory:
    """L5 builder for creating processors with proper configuration"""

    @staticmethod
    def create_processor(safety_level: str = "strict") -> LoadDataPlanningPlanInterface:
        """Create configured engine"""
        constraints = LoadDataPlanningPlanConstraints(safety_level=safety_level)
        engine = LoadDataPlanningPlanImpl(constraints)
        return LoadDataPlanningPlanInterface(engine)


# L5 Main execution point
def load_data_planning(input_data: dict[str, object]) -> dict[str, object]:
    """
    L5 Main function - load data planning operations

    Args:
        input_data: Input data to process

    Returns:
        Dict: Processed result

    Raises:
        SecurityError: If execution fails any safety check
    """
    builder = LoadDataPlanningPlanFactory()
    engine = builder.create_processor()
    return engine.execute(input_data)


if __name__ == "__main__":
    # L5 Test execution
    try:
        test_data = {"test": True}
        result = load_data_planning(test_data)
        logger.info(f"L5 Execution successful: {result}")
    except SecurityError as e:
        logger.error(f"L5 Security error: {e}")
    except (ValueError, TypeError, RuntimeError, KeyError) as e:
        logger.error(f"L5 Unexpected error: {e}")
