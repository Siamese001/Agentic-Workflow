"""
C1 Feature Extractor

Extracts features for C1 query optimization model including
query complexity, execution patterns, resource requirements,
optimization opportunities, and performance metrics.
"""

import math
from typing import Any

from ..config.feature_schemas import FeatureSchema, FeatureSchemas
from .base_extractor import DeterministicFeatureExtractor


class C1FeatureExtractor(DeterministicFeatureExtractor):
    """
    Feature extractor for C1 query optimization.

    Extracts deterministic features for query optimization:
    - Query complexity and structure metrics
    - Execution patterns and performance history
    - Resource requirements and utilization
    - Optimization opportunity scoring
    - Index usage and effectiveness
    - Query plan analysis
    - Cache hit rates and patterns
    """

    def __init__(self):
        schema = FeatureSchemas().get_schema("c1_query_optimizer")
        if not schema:
            # Create schema for C1 query optimizer
            schema = self._create_c1_schema()
        super().__init__(schema)

    def _create_c1_schema(self) -> FeatureSchema:
        """Create feature schema for C1 query optimizer."""
        from ..config.feature_schemas import FeatureDefinition, FeatureSchema, FeatureType

        features = [
            FeatureDefinition(
                name="query_complexity_score",
                feature_type=FeatureType.NUMERIC,
                description="Complexity score of the query",
                provenance="query.complexity.score",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="execution_time_trend",
                feature_type=FeatureType.NUMERIC,
                description="Trend in query execution times",
                provenance="query.execution.time_trend",
                validation_rules={"min_value": -1.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="resource_intensity",
                feature_type=FeatureType.NUMERIC,
                description="Resource intensity of query execution",
                provenance="query.resource.intensity",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="index_utilization",
                feature_type=FeatureType.NUMERIC,
                description="Index utilization effectiveness",
                provenance="query.index.utilization",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="cache_hit_rate",
                feature_type=FeatureType.NUMERIC,
                description="Cache hit rate for query results",
                provenance="query.cache.hit_rate",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="optimization_potential",
                feature_type=FeatureType.NUMERIC,
                description="Potential for query optimization",
                provenance="query.optimization.potential",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="join_complexity",
                feature_type=FeatureType.NUMERIC,
                description="Complexity of join operations",
                provenance="query.join.complexity",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="data_volume_impact",
                feature_type=FeatureType.NUMERIC,
                description="Impact of data volume on performance",
                provenance="query.data.volume_impact",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="concurrency_factor",
                feature_type=FeatureType.NUMERIC,
                description="Concurrency impact on query performance",
                provenance="query.concurrency.factor",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
            FeatureDefinition(
                name="plan_stability",
                feature_type=FeatureType.NUMERIC,
                description="Stability of query execution plan",
                provenance="query.plan.stability",
                validation_rules={"min_value": 0.0, "max_value": 1.0},
            ),
        ]

        return FeatureSchema(
            schema_name="c1_query_optimizer",
            schema_version="1.0",
            description="Features for C1 query optimization model",
            features=features,
        )

    def _register_extraction_functions(self) -> None:
        """Register C1-specific feature extraction functions."""
        self.register_extraction_function("query_complexity_score", self._extract_query_complexity_score)
        self.register_extraction_function("execution_time_trend", self._extract_execution_time_trend)
        self.register_extraction_function("resource_intensity", self._extract_resource_intensity)
        self.register_extraction_function("index_utilization", self._extract_index_utilization)
        self.register_extraction_function("cache_hit_rate", self._extract_cache_hit_rate)
        self.register_extraction_function("optimization_potential", self._extract_optimization_potential)
        self.register_extraction_function("join_complexity", self._extract_join_complexity)
        self.register_extraction_function("data_volume_impact", self._extract_data_volume_impact)
        self.register_extraction_function("concurrency_factor", self._extract_concurrency_factor)
        self.register_extraction_function("plan_stability", self._extract_plan_stability)

    def _extract_query_complexity_score(self, context: dict[str, Any]) -> float:
        """Extract query complexity score (0.0 to 1.0)."""
        query = context.get("query", {})

        # Direct complexity score if provided
        if "complexity_score" in query:
            return float(query["complexity_score"])

        # Calculate from query characteristics
        complexity_indicators = {
            "table_count": 0.2,
            "join_count": 0.25,
            "subquery_depth": 0.2,
            "where_conditions": 0.15,
            "aggregation_functions": 0.1,
            "window_functions": 0.1,
        }

        score = 0.0

        # Table count contribution
        tables = query.get("tables", [])
        if tables:
            table_score = min(1.0, len(tables) / 10.0)  # Normalize to 10 tables
            score += complexity_indicators["table_count"] * table_score

        # Join count contribution
        joins = query.get("joins", [])
        if joins:
            join_score = min(1.0, len(joins) / 8.0)  # Normalize to 8 joins
            score += complexity_indicators["join_count"] * join_score

        # Subquery depth contribution
        subquery_depth = query.get("subquery_depth", 0)
        depth_score = min(1.0, subquery_depth / 5.0)  # Normalize to 5 levels
        score += complexity_indicators["subquery_depth"] * depth_score

        # WHERE conditions contribution
        where_conditions = query.get("where_conditions", [])
        if where_conditions:
            condition_score = min(1.0, len(where_conditions) / 15.0)  # Normalize to 15 conditions
            score += complexity_indicators["where_conditions"] * condition_score

        # Aggregation functions contribution
        aggregations = query.get("aggregation_functions", [])
        if aggregations:
            agg_score = min(1.0, len(aggregations) / 8.0)  # Normalize to 8 aggregations
            score += complexity_indicators["aggregation_functions"] * agg_score

        # Window functions contribution
        window_functions = query.get("window_functions", [])
        if window_functions:
            window_score = min(1.0, len(window_functions) / 5.0)  # Normalize to 5 window functions
            score += complexity_indicators["window_functions"] * window_score

        return round(min(1.0, score), 3)

    def _extract_execution_time_trend(self, context: dict[str, Any]) -> float:
        """Extract execution time trend (-1.0 to 1.0, negative = improving)."""
        query = context.get("query", {})

        # Direct trend if provided
        if "execution_time_trend" in query:
            return float(query["execution_time_trend"])

        # Calculate from execution time history
        execution_times = query.get("execution_times", [])

        if len(execution_times) < 2:
            return 0.0  # No trend data

        # Calculate trend similar to other extractors
        n = len(execution_times)
        if n < 5:
            return 0.0

        recent_count = min(5, n // 3)
        recent_avg = sum(execution_times[-recent_count:]) / recent_count
        older_avg = sum(execution_times[:-recent_count]) / (n - recent_count)

        if older_avg > 0:
            trend = (recent_avg - older_avg) / older_avg
            trend = max(-1.0, min(1.0, trend))
        else:
            trend = 0.0

        return round(trend, 3)

    def _extract_resource_intensity(self, context: dict[str, Any]) -> float:
        """Extract resource intensity (0.0 to 1.0)."""
        query = context.get("query", {})

        # Direct intensity if provided
        if "resource_intensity" in query:
            return float(query["resource_intensity"])

        # Calculate from resource usage metrics
        resource_metrics = query.get("resource_metrics", {})

        if not resource_metrics:
            return 0.0  # No resource data

        # Combine different resource metrics
        cpu_usage = resource_metrics.get("cpu_usage", 0)
        memory_usage = resource_metrics.get("memory_usage", 0)
        io_operations = resource_metrics.get("io_operations", 0)
        network_io = resource_metrics.get("network_io", 0)

        # Normalize each metric to 0-1 scale
        cpu_score = min(1.0, cpu_usage / 100.0)  # Assume percentage
        memory_score = min(1.0, memory_usage / 100.0)  # Assume percentage
        io_score = min(1.0, io_operations / 10000.0)  # Normalize to 10K ops
        network_score = min(1.0, network_io / 1000.0)  # Normalize to 1MB

        # Weighted combination
        intensity = (cpu_score * 0.3) + (memory_score * 0.3) + (io_score * 0.2) + (network_score * 0.2)

        return round(min(1.0, intensity), 3)

    def _extract_index_utilization(self, context: dict[str, Any]) -> float:
        """Extract index utilization effectiveness (0.0 to 1.0)."""
        query = context.get("query", {})

        # Direct utilization if provided
        if "index_utilization" in query:
            return float(query["index_utilization"])

        # Calculate from index usage data
        index_usage = query.get("index_usage", {})

        if not index_usage:
            return 0.0  # No index data

        # Calculate index effectiveness
        total_scans = index_usage.get("total_scans", 1)
        index_scans = index_usage.get("index_scans", 0)
        table_scans = index_usage.get("table_scans", 0)

        if total_scans > 0:
            # Higher index scan ratio is better
            index_ratio = index_scans / total_scans

            # Penalize full table scans
            table_scan_penalty = table_scans / total_scans

            utilization = index_ratio * 0.8 + (1.0 - table_scan_penalty) * 0.2
        else:
            utilization = 0.0

        return round(max(0.0, min(1.0, utilization)), 3)

    def _extract_cache_hit_rate(self, context: dict[str, Any]) -> float:
        """Extract cache hit rate (0.0 to 1.0)."""
        query = context.get("query", {})

        # Direct hit rate if provided
        if "cache_hit_rate" in query:
            return float(query["cache_hit_rate"])

        # Calculate from cache statistics
        cache_stats = query.get("cache_stats", {})

        if not cache_stats:
            return 0.0  # No cache data

        cache_hits = cache_stats.get("hits", 0)
        cache_misses = cache_stats.get("misses", 0)
        total_requests = cache_hits + cache_misses

        if total_requests > 0:
            hit_rate = cache_hits / total_requests
        else:
            hit_rate = 0.0

        return round(max(0.0, min(1.0, hit_rate)), 3)

    def _extract_optimization_potential(self, context: dict[str, Any]) -> float:
        """Extract optimization potential (0.0 to 1.0)."""
        query = context.get("query", {})

        # Direct potential if provided
        if "optimization_potential" in query:
            return float(query["optimization_potential"])

        # Calculate from various optimization indicators
        indicators = {
            "high_execution_time": 0.3,
            "low_cache_hit_rate": 0.25,
            "poor_index_usage": 0.2,
            "resource_intensive": 0.15,
            "unstable_plan": 0.1,
        }

        potential_score = 0.0

        # High execution time
        execution_times = query.get("execution_times", [])
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            target_time = query.get("target_execution_time", 1000)  # 1 second default

            if avg_time > target_time:
                excess_ratio = (avg_time - target_time) / target_time
                potential_score += indicators["high_execution_time"] * min(1.0, excess_ratio)

        # Low cache hit rate
        cache_hit_rate = self._extract_cache_hit_rate(context)
        if cache_hit_rate < 0.5:  # Less than 50% hit rate
            potential_score += indicators["low_cache_hit_rate"] * (1.0 - cache_hit_rate)

        # Poor index usage
        index_util = self._extract_index_utilization(context)
        if index_util < 0.7:  # Less than 70% index utilization
            potential_score += indicators["poor_index_usage"] * (1.0 - index_util)

        # Resource intensive
        resource_intensity = self._extract_resource_intensity(context)
        if resource_intensity > 0.7:  # More than 70% resource utilization
            potential_score += indicators["resource_intensive"] * resource_intensity

        # Unstable plan
        plan_stability = self._extract_plan_stability(context)
        if plan_stability < 0.5:  # Less than 50% plan stability
            potential_score += indicators["unstable_plan"] * (1.0 - plan_stability)

        return round(min(1.0, potential_score), 3)

    def _extract_join_complexity(self, context: dict[str, Any]) -> float:
        """Extract join complexity (0.0 to 1.0)."""
        query = context.get("query", {})

        # Direct complexity if provided
        if "join_complexity" in query:
            return float(query["join_complexity"])

        # Calculate from join information
        joins = query.get("joins", [])

        if not joins:
            return 0.0  # No joins

        complexity_score = 0.0

        # Number of joins
        join_count = len(joins)
        count_score = min(1.0, join_count / 8.0)  # Normalize to 8 joins
        complexity_score += count_score * 0.4

        # Join types (some are more complex)
        join_types = [join.get("type", "inner").lower() for join in joins]
        complex_types = ["outer", "full", "cross", "self"]

        complex_join_count = sum(1 for jt in join_types if jt in complex_types)
        if join_count > 0:
            type_score = complex_join_count / join_count
            complexity_score += type_score * 0.3

        # Join conditions complexity
        total_conditions = sum(len(join.get("conditions", [])) for join in joins)
        if join_count > 0:
            avg_conditions = total_conditions / join_count
            condition_score = min(1.0, avg_conditions / 5.0)  # Normalize to 5 conditions per join
            complexity_score += condition_score * 0.3

        return round(min(1.0, complexity_score), 3)

    def _extract_data_volume_impact(self, context: dict[str, Any]) -> float:
        """Extract data volume impact (0.0 to 1.0)."""
        query = context.get("query", {})

        # Direct impact if provided
        if "data_volume_impact" in query:
            return float(query["data_volume_impact"])

        # Calculate from data volume metrics
        data_metrics = query.get("data_metrics", {})

        if not data_metrics:
            return 0.0  # No data volume data

        # Rows processed
        rows_processed = data_metrics.get("rows_processed", 0)
        rows_returned = data_metrics.get("rows_returned", 1)

        if rows_returned > 0:
            rows_ratio = rows_processed / rows_returned
            rows_impact = min(1.0, math.log10(max(1, rows_ratio)) / 3.0)  # Log scale, normalize
        else:
            rows_impact = 0.0

        # Data size processed
        data_size = data_metrics.get("data_size_mb", 0)
        size_impact = min(1.0, data_size / 1000.0)  # Normalize to 1GB

        # Combine factors
        volume_impact = (rows_impact * 0.6) + (size_impact * 0.4)

        return round(min(1.0, volume_impact), 3)

    def _extract_concurrency_factor(self, context: dict[str, Any]) -> float:
        """Extract concurrency impact factor (0.0 to 1.0)."""
        query = context.get("query", {})

        # Direct factor if provided
        if "concurrency_factor" in query:
            return float(query["concurrency_factor"])

        # Calculate from concurrency metrics
        concurrency = query.get("concurrency", {})

        if not concurrency:
            return 0.0  # No concurrency data

        # Concurrent executions
        concurrent_executions = concurrency.get("concurrent_executions", 0)
        max_concurrent = concurrency.get("max_concurrent", 1)

        if max_concurrent > 0:
            concurrency_ratio = concurrent_executions / max_concurrent
            concurrency_impact = min(1.0, concurrency_ratio)
        else:
            concurrency_impact = 0.0

        # Lock contention
        lock_waits = concurrency.get("lock_waits", 0)
        total_executions = concurrency.get("total_executions", 1)

        if total_executions > 0:
            lock_contention = lock_waits / total_executions
        else:
            lock_contention = 0.0

        # Combine factors
        factor = (concurrency_impact * 0.7) + (lock_contention * 0.3)

        return round(min(1.0, factor), 3)

    def _extract_plan_stability(self, context: dict[str, Any]) -> float:
        """Extract query plan stability (0.0 to 1.0)."""
        query = context.get("query", {})

        # Direct stability if provided
        if "plan_stability" in query:
            return float(query["plan_stability"])

        # Calculate from execution plan history
        plan_history = query.get("plan_history", [])

        if not plan_history:
            return 0.5  # No plan history

        # Calculate plan hash consistency
        plan_hashes = [plan.get("plan_hash", "") for plan in plan_history if plan.get("plan_hash")]

        if len(plan_hashes) < 2:
            return 1.0  # Only one plan, stable by default

        # Calculate how many unique plans we have
        unique_plans = len(set(plan_hashes))
        total_plans = len(plan_hashes)

        if total_plans > 0:
            stability = 1.0 - ((unique_plans - 1) / total_plans)  # Fewer unique plans = more stable
        else:
            stability = 0.5

        return round(max(0.0, min(1.0, stability)), 3)
