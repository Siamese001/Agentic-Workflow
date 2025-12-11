"""Safety Usage State Updater - Updates and tracks safety usage metrics.

This module provides state management for safety usage tracking,
including resource consumption, policy violations, and safety metrics.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import logging
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class UsageType(Enum):
    """Types of safety usage metrics."""
    POLICY_CHECKS = "policy_checks"
    VIOLATION_COUNT = "violation_count"
    RESOURCE_CONSUMPTION = "resource_consumption"
    API_CALLS = "api_calls"
    DATA_PROCESSED = "data_processed"
    FILTER_APPLICATIONS = "filter_applications"
    ETHICS_VALIDATIONS = "ethics_validations"


@dataclass
class UsageMetric:
    """Definition of a usage metric."""
    metric_type: UsageType
    value: Union[int, float]
    unit: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UsageState:
    """Current usage state."""
    total_metrics: Dict[str, float] = field(default_factory=dict)
    daily_metrics: Dict[str, float] = field(default_factory=dict)
    hourly_metrics: Dict[str, float] = field(default_factory=dict)
    violation_counts: Dict[str, int] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SafetyUsageConfig:
    """Configuration for safety usage tracking."""
    track_daily_usage: bool = True
    track_hourly_usage: bool = True
    retention_days: int = 30
    aggregation_interval: int = 300  # 5 minutes
    enable_persistence: bool = True
    storage_path: Optional[str] = None
    log_level: str = "INFO"


class SafetyUsageStateUpdater:
    """Main class for updating safety usage state."""

    def __init__(self, config: Optional[SafetyUsageConfig] = None):
        self.config = config or SafetyUsageConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)
        self._state = UsageState()
        self._metric_history: List[UsageMetric] = []

    def update_usage(self, metric: UsageMetric) -> bool:
        """Update usage with a new metric.
        
        Args:
            metric: Usage metric to record
            
        Returns:
            bool: True if update was successful
        """
        try:
            self.logger.info(f"Updating usage metric: {metric.metric_type.value} = {metric.value} {metric.unit}")
            
            # Add to history
            self._metric_history.append(metric)
            
            # Update total metrics
            metric_key = f"{metric.metric_type.value}_{metric.unit}"
            self._state.total_metrics[metric_key] = self._state.total_metrics.get(metric_key, 0) + metric.value
            
            # Update daily metrics
            if self.config.track_daily_usage:
                daily_key = f"{metric_key}_{metric.timestamp.date()}"
                self._state.daily_metrics[daily_key] = self._state.daily_metrics.get(daily_key, 0) + metric.value
            
            # Update hourly metrics
            if self.config.track_hourly_usage:
                hour_key = f"{metric_key}_{metric.timestamp.date()}_{metric.timestamp.hour}"
                self._state.hourly_metrics[hour_key] = self._state.hourly_metrics.get(hour_key, 0) + metric.value
            
            # Update violation counts if applicable
            if metric.metric_type == UsageType.VIOLATION_COUNT:
                violation_type = metric.metadata.get("violation_type", "unknown")
                self._state.violation_counts[violation_type] = self._state.violation_counts.get(violation_type, 0) + int(metric.value)
            
            # Update last updated timestamp
            self._state.last_updated = datetime.utcnow()
            
            # Persist state if enabled
            if self.config.enable_persistence:
                self._persist_state()
            
            # Clean old metrics if needed
            self._cleanup_old_metrics()
            
            self.logger.info(f"Usage metric updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update usage metric: {str(e)}")
            return False

    def get_usage_summary(self, time_range: str = "total") -> Dict[str, Any]:
        """Get usage summary for a time range.
        
        Args:
            time_range: Time range for summary (total, daily, hourly)
            
        Returns:
            Dict: Usage summary
        """
        try:
            summary = {
                "time_range": time_range,
                "generated_at": datetime.utcnow().isoformat(),
                "metrics": {},
                "violations": self._state.violation_counts.copy()
            }
            
            if time_range == "total":
                summary["metrics"] = self._state.total_metrics.copy()
            elif time_range == "daily":
                # Get today's metrics
                today = datetime.utcnow().date()
                daily_metrics = {k: v for k, v in self._state.daily_metrics.items() if str(today) in k}
                summary["metrics"] = daily_metrics
            elif time_range == "hourly":
                # Get current hour's metrics
                now = datetime.utcnow()
                hour_key = f"{now.date()}_{now.hour}"
                hourly_metrics = {k: v for k, v in self._state.hourly_metrics.items() if hour_key in k}
                summary["metrics"] = hourly_metrics
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get usage summary: {str(e)}")
            return {"error": str(e)}

    def reset_usage(self, time_range: str = "total") -> bool:
        """Reset usage metrics for a time range.
        
        Args:
            time_range: Time range to reset (total, daily, hourly)
            
        Returns:
            bool: True if reset was successful
        """
        try:
            self.logger.info(f"Resetting usage metrics for range: {time_range}")
            
            if time_range == "total":
                self._state.total_metrics.clear()
            elif time_range == "daily":
                self._state.daily_metrics.clear()
            elif time_range == "hourly":
                self._state.hourly_metrics.clear()
            elif time_range == "all":
                self._state.total_metrics.clear()
                self._state.daily_metrics.clear()
                self._state.hourly_metrics.clear()
                self._state.violation_counts.clear()
            
            self._state.last_updated = datetime.utcnow()
            
            if self.config.enable_persistence:
                self._persist_state()
            
            self.logger.info(f"Usage metrics reset successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset usage metrics: {str(e)}")
            return False

    def get_violation_trends(self, days: int = 7) -> Dict[str, Any]:
        """Get violation trends over time.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict: Violation trends data
        """
        try:
            trends = {
                "period_days": days,
                "daily_violations": {},
                "violation_types": {},
                "total_violations": 0
            }
            
            # Calculate daily violations
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days)
            
            current_date = start_date
            while current_date <= end_date:
                daily_count = 0
                for key, value in self._state.daily_metrics.items():
                    if "violation_count_count" in key and str(current_date) in key:
                        daily_count += int(value)
                
                trends["daily_violations"][str(current_date)] = daily_count
                trends["total_violations"] += daily_count
                current_date += timedelta(days=1)
            
            # Aggregate by violation type
            trends["violation_types"] = self._state.violation_counts.copy()
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Failed to get violation trends: {str(e)}")
            return {"error": str(e)}

    def _persist_state(self) -> None:
        """Persist state to storage."""
        if not self.config.storage_path:
            return
        
        try:
            import json
            state_data = {
                "total_metrics": self._state.total_metrics,
                "daily_metrics": self._state.daily_metrics,
                "hourly_metrics": self._state.hourly_metrics,
                "violation_counts": self._state.violation_counts,
                "last_updated": self._state.last_updated.isoformat()
            }
            
            with open(self.config.storage_path, "w") as f:
                json.dump(state_data, f, indent=2)
            
            self.logger.debug(f"State persisted to {self.config.storage_path}")
            
        except Exception as e:
            self.logger.warning(f"Failed to persist state: {str(e)}")

    def _load_state(self) -> None:
        """Load state from storage."""
        if not self.config.storage_path:
            return
        
        try:
            import json
            import os
            
            if os.path.exists(self.config.storage_path):
                with open(self.config.storage_path, "r") as f:
                    state_data = json.load(f)
                
                self._state.total_metrics = state_data.get("total_metrics", {})
                self._state.daily_metrics = state_data.get("daily_metrics", {})
                self._state.hourly_metrics = state_data.get("hourly_metrics", {})
                self._state.violation_counts = state_data.get("violation_counts", {})
                
                if state_data.get("last_updated"):
                    self._state.last_updated = datetime.fromisoformat(state_data["last_updated"])
                
                self.logger.info(f"State loaded from {self.config.storage_path}")
            
        except Exception as e:
            self.logger.warning(f"Failed to load state: {str(e)}")

    def _cleanup_old_metrics(self) -> None:
        """Clean up old metrics based on retention policy."""
        if not self.config.retention_days:
            return
        
        try:
            cutoff_date = datetime.utcnow().date() - timedelta(days=self.config.retention_days)
            
            # Clean daily metrics
            daily_keys_to_remove = []
            for key in self._state.daily_metrics:
                try:
                    date_str = key.split("_")[-1]
                    metric_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    if metric_date < cutoff_date:
                        daily_keys_to_remove.append(key)
                except:
                    continue
            
            for key in daily_keys_to_remove:
                del self._state.daily_metrics[key]
            
            # Clean hourly metrics
            hourly_keys_to_remove = []
            for key in self._state.hourly_metrics:
                try:
                    date_str = "_".join(key.split("_")[-2:])
                    metric_date = datetime.strptime(date_str, "%Y-%m-%d_%H").date()
                    if metric_date < cutoff_date:
                        hourly_keys_to_remove.append(key)
                except:
                    continue
            
            for key in hourly_keys_to_remove:
                del self._state.hourly_metrics[key]
            
            # Clean metric history
            self._metric_history = [
                m for m in self._metric_history 
                if m.timestamp.date() >= cutoff_date
            ]
            
            if daily_keys_to_remove or hourly_keys_to_remove:
                self.logger.info(f"Cleaned up {len(daily_keys_to_remove)} daily and {len(hourly_keys_to_remove)} hourly metrics")
            
        except Exception as e:
            self.logger.warning(f"Failed to cleanup old metrics: {str(e)}")


# Factory function for easy instantiation
def create_safety_usage_state_updater(
    track_daily_usage: bool = True,
    track_hourly_usage: bool = True,
    retention_days: int = 30,
    enable_persistence: bool = True,
    **kwargs
) -> SafetyUsageStateUpdater:
    """Create a configured safety usage state updater."""
    config = SafetyUsageConfig(
        track_daily_usage=track_daily_usage,
        track_hourly_usage=track_hourly_usage,
        retention_days=retention_days,
        enable_persistence=enable_persistence,
        **kwargs
    )
    updater = SafetyUsageStateUpdater(config)
    updater._load_state()
    return updater


# Convenience function for direct usage
def update_safety_usage(
    metric_type: str,
    value: Union[int, float],
    unit: str,
    metadata: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None
) -> bool:
    """Update safety usage metric.
    
    Args:
        metric_type: Type of usage metric
        value: Metric value
        unit: Unit of measurement
        metadata: Optional metadata
        config: Optional updater configuration
        
    Returns:
        bool: True if update was successful
    """
    # Create updater and update
    updater_config = SafetyUsageConfig(**config or {})
    updater = SafetyUsageStateUpdater(updater_config)
    
    metric = UsageMetric(
        metric_type=UsageType(metric_type),
        value=value,
        unit=unit,
        metadata=metadata or {}
    )
    
    return updater.update_usage(metric)
