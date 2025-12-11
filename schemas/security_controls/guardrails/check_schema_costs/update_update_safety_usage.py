"""Safety Usage Update Tracker - Updates and tracks safety usage metrics for schemas.

This module provides usage tracking for safety operations on schemas,
including validation counts, policy applications, and compliance metrics.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import logging
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class SchemaUsageType(Enum):
    """Types of schema usage metrics."""
    SCHEMA_VALIDATION = "schema_validation"
    POLICY_APPLICATION = "policy_application"
    FILTER_ENFORCEMENT = "filter_enforcement"
    ETHICS_CHECK = "ethics_check"
    COMPLIANCE_VALIDATION = "compliance_validation"
    TRANSFORMATION = "transformation"
    ACCESS_REQUEST = "access_request"


@dataclass
class SchemaUsageMetric:
    """Individual schema usage metric record."""
    metric_type: SchemaUsageType
    value: Union[int, float]
    unit: str
    schema_id: Optional[str] = None
    operation_id: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemaUsageAggregation:
    """Aggregated schema usage metrics."""
    metric_type: SchemaUsageType
    total_value: float
    count: int
    average_value: float
    min_value: float
    max_value: float
    unit: str
    period_start: datetime
    period_end: datetime


@dataclass
class SchemaUsageState:
    """Current schema usage state."""
    metrics: List[SchemaUsageMetric] = field(default_factory=list)
    aggregations: Dict[str, SchemaUsageAggregation] = field(default_factory=dict)
    schema_counts: Dict[str, int] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    total_operations: int = 0


@dataclass
class SchemaSafetyUsageConfig:
    """Configuration for schema safety usage tracking."""
    enable_real_time_updates: bool = True
    aggregation_intervals: List[str] = field(default_factory=lambda: ["hourly", "daily", "weekly"])
    max_metrics_in_memory: int = 10000
    enable_persistence: bool = True
    storage_path: Optional[str] = None
    cleanup_interval_hours: int = 24
    log_level: str = "INFO"


class SchemaSafetyUsageUpdater:
    """Main class for updating schema safety usage state."""

    def __init__(self, config: Optional[SchemaSafetyUsageConfig] = None):
        self.config = config or SchemaSafetyUsageConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)
        self._state = SchemaUsageState()
        
        # Load existing state if persistence is enabled
        if self.config.enable_persistence:
            self._load_state()

    def update_usage(self, metric: SchemaUsageMetric) -> bool:
        """Update usage with a new metric.
        
        Args:
            metric: Usage metric to add
            
        Returns:
            bool: True if update was successful
        """
        try:
            self.logger.debug(f"Updating schema usage metric: {metric.metric_type.value} = {metric.value} {metric.unit}")
            
            # Add metric to state
            self._state.metrics.append(metric)
            
            # Update schema counts
            if metric.schema_id:
                self._state.schema_counts[metric.schema_id] = self._state.schema_counts.get(metric.schema_id, 0) + 1
            
            # Update total operations
            if metric.metric_type == SchemaUsageType.SCHEMA_VALIDATION:
                self._state.total_operations += int(metric.value)
            
            # Update timestamp
            self._state.last_updated = datetime.utcnow()
            
            # Trigger aggregation if needed
            if self.config.enable_real_time_updates:
                self._trigger_aggregation()
            
            # Check if cleanup is needed
            if len(self._state.metrics) > self.config.max_metrics_in_memory:
                self._cleanup_old_metrics()
            
            # Persist state if enabled
            if self.config.enable_persistence:
                self._save_state()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update schema usage metric: {str(e)}")
            return False

    def get_usage_summary(self, metric_type: Optional[SchemaUsageType] = None, period: str = "total") -> Dict[str, Any]:
        """Get usage summary for metrics.
        
        Args:
            metric_type: Specific metric type to summarize
            period: Time period for summary
            
        Returns:
            Dict: Usage summary
        """
        try:
            # Filter metrics by type and period
            filtered_metrics = self._filter_metrics(metric_type, period)
            
            if not filtered_metrics:
                return {"message": "No metrics found for the specified criteria"}
            
            # Group by metric type
            summary = {
                "period": period,
                "generated_at": datetime.utcnow().isoformat(),
                "total_metrics": len(filtered_metrics),
                "metric_summaries": {}
            }
            
            # Group metrics by type
            metric_groups = {}
            for metric in filtered_metrics:
                if metric.metric_type not in metric_groups:
                    metric_groups[metric.metric_type] = []
                metric_groups[metric.metric_type].append(metric)
            
            # Calculate summaries for each metric type
            for mtype, metrics in metric_groups.items():
                values = [m.value for m in metrics if isinstance(m.value, (int, float))]
                
                if values:
                    summary["metric_summaries"][mtype.value] = {
                        "total": sum(values),
                        "count": len(values),
                        "average": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "unit": metrics[0].unit
                    }
            
            # Add schema summary
            summary["schemas"] = {
                "total_schemas": len(self._state.schema_counts),
                "most_used": sorted(self._state.schema_counts.items(), key=lambda x: x[1], reverse=True)[:10],
                "total_operations": self._state.total_operations
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get schema usage summary: {str(e)}")
            return {"error": str(e)}

    def get_aggregated_metrics(self, metric_type: SchemaUsageType, interval: str = "hourly") -> Optional[SchemaUsageAggregation]:
        """Get aggregated metrics for a type and interval.
        
        Args:
            metric_type: Type of metric to aggregate
            interval: Aggregation interval
            
        Returns:
            SchemaUsageAggregation: Aggregated metrics or None
        """
        try:
            aggregation_key = f"{metric_type.value}_{interval}"
            return self._state.aggregations.get(aggregation_key)
            
        except Exception as e:
            self.logger.error(f"Failed to get aggregated metrics: {str(e)}")
            return None

    def get_schema_usage(self, schema_id: str, period: str = "total") -> Dict[str, Any]:
        """Get usage statistics for a specific schema.
        
        Args:
            schema_id: ID of the schema
            period: Time period for summary
            
        Returns:
            Dict: Schema usage statistics
        """
        try:
            # Filter metrics for schema
            schema_metrics = [m for m in self._state.metrics if m.schema_id == schema_id]
            filtered_metrics = self._filter_metrics_by_period(schema_metrics, period)
            
            if not filtered_metrics:
                return {"schema_id": schema_id, "usage": 0, "message": "No usage found"}
            
            # Group by metric type
            usage_by_type = {}
            for metric in filtered_metrics:
                metric_type = metric.metric_type.value
                if metric_type not in usage_by_type:
                    usage_by_type[metric_type] = {"count": 0, "total": 0}
                
                usage_by_type[metric_type]["count"] += 1
                if isinstance(metric.value, (int, float)):
                    usage_by_type[metric_type]["total"] += metric.value
            
            return {
                "schema_id": schema_id,
                "period": period,
                "total_usage": len(filtered_metrics),
                "usage_by_type": usage_by_type,
                "first_used": min(m.timestamp for m in filtered_metrics).isoformat(),
                "last_used": max(m.timestamp for m in filtered_metrics).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get schema usage: {str(e)}")
            return {"error": str(e)}

    def reset_metrics(self, metric_type: Optional[SchemaUsageType] = None, schema_id: Optional[str] = None) -> bool:
        """Reset metrics for a type, schema, or all metrics.
        
        Args:
            metric_type: Specific metric type to reset
            schema_id: Specific schema ID to reset
            
        Returns:
            bool: True if reset was successful
        """
        try:
            original_count = len(self._state.metrics)
            
            if metric_type and schema_id:
                # Remove metrics of specific type and schema
                self._state.metrics = [m for m in self._state.metrics 
                                     if m.metric_type != metric_type or m.schema_id != schema_id]
            elif metric_type:
                # Remove metrics of specific type
                self._state.metrics = [m for m in self._state.metrics if m.metric_type != metric_type]
            elif schema_id:
                # Remove metrics for specific schema
                self._state.metrics = [m for m in self._state.metrics if m.schema_id != schema_id]
            else:
                # Reset all metrics
                self._state.metrics.clear()
                self._state.aggregations.clear()
                self._state.schema_counts.clear()
                self._state.total_operations = 0
            
            removed_count = original_count - len(self._state.metrics)
            
            # Remove related aggregations
            keys_to_remove = []
            for key in self._state.aggregations:
                if metric_type and key.startswith(metric_type.value):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self._state.aggregations[key]
            
            # Update schema counts if needed
            if schema_id and schema_id in self._state.schema_counts:
                del self._state.schema_counts[schema_id]
            
            self.logger.info(f"Reset {removed_count} schema usage metrics")
            
            self._state.last_updated = datetime.utcnow()
            
            if self.config.enable_persistence:
                self._save_state()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset metrics: {str(e)}")
            return False

    def _filter_metrics(self, metric_type: Optional[SchemaUsageType], period: str) -> List[SchemaUsageMetric]:
        """Filter metrics by type and period."""
        filtered = self._state.metrics
        
        # Filter by type
        if metric_type:
            filtered = [m for m in filtered if m.metric_type == metric_type]
        
        # Filter by period
        if period != "total":
            filtered = self._filter_metrics_by_period(filtered, period)
        
        return filtered

    def _filter_metrics_by_period(self, metrics: List[SchemaUsageMetric], period: str) -> List[SchemaUsageMetric]:
        """Filter metrics by time period."""
        if period == "total":
            return metrics
        
        now = datetime.utcnow()
        
        if period == "hourly":
            start_time = now.replace(minute=0, second=0, microsecond=0)
        elif period == "daily":
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "weekly":
            start_time = now - timedelta(days=now.weekday())
            start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            return metrics
        
        return [m for m in metrics if m.timestamp >= start_time]

    def _trigger_aggregation(self) -> None:
        """Trigger metric aggregation."""
        try:
            for interval in self.config.aggregation_intervals:
                self._aggregate_metrics(interval)
                
        except Exception as e:
            self.logger.warning(f"Failed to trigger aggregation: {str(e)}")

    def _aggregate_metrics(self, interval: str) -> None:
        """Aggregate metrics by interval."""
        try:
            # Group metrics by type
            metric_groups = {}
            for metric in self._state.metrics:
                if metric.metric_type not in metric_groups:
                    metric_groups[metric.metric_type] = []
                metric_groups[metric.metric_type].append(metric)
            
            # Aggregate each metric type
            for metric_type, metrics in metric_groups.items():
                # Filter metrics for the interval
                interval_metrics = self._filter_metrics_by_interval(metrics, interval)
                
                if interval_metrics:
                    # Calculate aggregation
                    values = [m.value for m in interval_metrics if isinstance(m.value, (int, float))]
                    
                    if values:
                        aggregation = SchemaUsageAggregation(
                            metric_type=metric_type,
                            total_value=sum(values),
                            count=len(values),
                            average_value=sum(values) / len(values),
                            min_value=min(values),
                            max_value=max(values),
                            unit=interval_metrics[0].unit,
                            period_start=min(m.timestamp for m in interval_metrics),
                            period_end=max(m.timestamp for m in interval_metrics)
                        )
                        
                        # Store aggregation
                        aggregation_key = f"{metric_type.value}_{interval}"
                        self._state.aggregations[aggregation_key] = aggregation
            
        except Exception as e:
            self.logger.warning(f"Failed to aggregate metrics for {interval}: {str(e)}")

    def _filter_metrics_by_interval(self, metrics: List[SchemaUsageMetric], interval: str) -> List[SchemaUsageMetric]:
        """Filter metrics by aggregation interval."""
        now = datetime.utcnow()
        
        if interval == "hourly":
            start_time = now.replace(minute=0, second=0, microsecond=0)
        elif interval == "daily":
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif interval == "weekly":
            start_time = now - timedelta(days=now.weekday())
            start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            return metrics
        
        return [m for m in metrics if m.timestamp >= start_time]

    def _cleanup_old_metrics(self) -> None:
        """Clean up old metrics to prevent memory issues."""
        try:
            # Keep metrics for the last 7 days
            cutoff_time = datetime.utcnow() - timedelta(days=7)
            original_count = len(self._state.metrics)
            
            self._state.metrics = [m for m in self._state.metrics if m.timestamp >= cutoff_time]
            
            cleaned_count = original_count - len(self._state.metrics)
            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} old schema usage metrics")
                
        except Exception as e:
            self.logger.warning(f"Failed to cleanup old metrics: {str(e)}")

    def _save_state(self) -> None:
        """Save state to persistent storage."""
        if not self.config.storage_path:
            return
        
        try:
            import json
            state_data = {
                "metrics": [
                    {
                        "metric_type": m.metric_type.value,
                        "value": m.value,
                        "unit": m.unit,
                        "schema_id": m.schema_id,
                        "operation_id": m.operation_id,
                        "user_id": m.user_id,
                        "timestamp": m.timestamp.isoformat(),
                        "metadata": m.metadata
                    }
                    for m in self._state.metrics
                ],
                "aggregations": {
                    k: {
                        "metric_type": v.metric_type.value,
                        "total_value": v.total_value,
                        "count": v.count,
                        "average_value": v.average_value,
                        "min_value": v.min_value,
                        "max_value": v.max_value,
                        "unit": v.unit,
                        "period_start": v.period_start.isoformat(),
                        "period_end": v.period_end.isoformat()
                    }
                    for k, v in self._state.aggregations.items()
                },
                "schema_counts": self._state.schema_counts,
                "last_updated": self._state.last_updated.isoformat(),
                "total_operations": self._state.total_operations
            }
            
            with open(self.config.storage_path, "w") as f:
                json.dump(state_data, f, indent=2)
            
            self.logger.debug(f"Schema usage state saved to {self.config.storage_path}")
            
        except Exception as e:
            self.logger.warning(f"Failed to save state: {str(e)}")

    def _load_state(self) -> None:
        """Load state from persistent storage."""
        if not self.config.storage_path:
            return
        
        try:
            import os
            
            if os.path.exists(self.config.storage_path):
                with open(self.config.storage_path, "r") as f:
                    state_data = json.load(f)
                
                # Load metrics
                self._state.metrics = []
                for m_data in state_data.get("metrics", []):
                    metric = SchemaUsageMetric(
                        metric_type=SchemaUsageType(m_data["metric_type"]),
                        value=m_data["value"],
                        unit=m_data["unit"],
                        schema_id=m_data.get("schema_id"),
                        operation_id=m_data.get("operation_id"),
                        user_id=m_data.get("user_id"),
                        timestamp=datetime.fromisoformat(m_data["timestamp"]),
                        metadata=m_data.get("metadata", {})
                    )
                    self._state.metrics.append(metric)
                
                # Load aggregations
                self._state.aggregations = {}
                for k, v_data in state_data.get("aggregations", {}).items():
                    aggregation = SchemaUsageAggregation(
                        metric_type=SchemaUsageType(v_data["metric_type"]),
                        total_value=v_data["total_value"],
                        count=v_data["count"],
                        average_value=v_data["average_value"],
                        min_value=v_data["min_value"],
                        max_value=v_data["max_value"],
                        unit=v_data["unit"],
                        period_start=datetime.fromisoformat(v_data["period_start"]),
                        period_end=datetime.fromisoformat(v_data["period_end"])
                    )
                    self._state.aggregations[k] = aggregation
                
                # Load other state
                self._state.schema_counts = state_data.get("schema_counts", {})
                self._state.last_updated = datetime.fromisoformat(state_data.get("last_updated", datetime.utcnow().isoformat()))
                self._state.total_operations = state_data.get("total_operations", 0)
                
                self.logger.info(f"Schema usage state loaded from {self.config.storage_path}")
            
        except Exception as e:
            self.logger.warning(f"Failed to load state: {str(e)}")


# Factory function for easy instantiation
def create_schema_safety_usage_updater(
    enable_real_time_updates: bool = True,
    aggregation_intervals: List[str] = None,
    enable_persistence: bool = True,
    **kwargs
) -> SchemaSafetyUsageUpdater:
    """Create a configured schema safety usage updater."""
    config = SchemaSafetyUsageConfig(
        enable_real_time_updates=enable_real_time_updates,
        aggregation_intervals=aggregation_intervals or ["hourly", "daily"],
        enable_persistence=enable_persistence,
        **kwargs
    )
    updater = SchemaSafetyUsageUpdater(config)
    return updater


# Convenience function for direct usage
def update_safety_usage(
    metric_type: str,
    value: Union[int, float],
    unit: str,
    schema_id: Optional[str] = None,
    operation_id: Optional[str] = None,
    user_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None
) -> bool:
    """Update schema safety usage metric.
    
    Args:
        metric_type: Type of usage metric
        value: Metric value
        unit: Unit of measurement
        schema_id: Optional schema ID
        operation_id: Optional operation ID
        user_id: Optional user ID
        metadata: Optional metadata
        config: Optional updater configuration
        
    Returns:
        bool: True if update was successful
    """
    # Create updater and update
    updater_config = SchemaSafetyUsageConfig(**config or {})
    updater = SchemaSafetyUsageUpdater(updater_config)
    
    metric = SchemaUsageMetric(
        metric_type=SchemaUsageType(metric_type),
        value=value,
        unit=unit,
        schema_id=schema_id,
        operation_id=operation_id,
        user_id=user_id,
        metadata=metadata or {}
    )
    
    return updater.update_usage(metric)
