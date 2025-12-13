"""
System Telemetry - Structured logging and metrics for hardening infrastructure.

Provides centralized telemetry for tracking operation performance, failures,
and system health across all hardened components.
"""

import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class OperationMetrics:
    """Metrics for a single operation."""
    component: str
    operation: str
    duration_ms: float
    tokens_used: int = 0
    success: bool = True
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "component": self.component,
            "operation": self.operation,
            "duration_ms": self.duration_ms,
            "tokens_used": self.tokens_used,
            "success": self.success,
            "error": self.error,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat()
        }

class SystemTelemetry:
    """
    Centralized telemetry system for hardening infrastructure.

    Tracks operation metrics, aggregates statistics, and provides
    structured logging for monitoring and debugging.
    """

    def __init__(self):
        """Initialize telemetry system."""
        self._metrics: List[OperationMetrics] = []
        self._component_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "total_operations": 0,
                "successful_operations": 0,
                "failed_operations": 0,
                "total_duration_ms": 0.0,
                "total_tokens": 0,
                "errors": []
            }
        )

        logger.info("SystemTelemetry initialized")

    def log_operation(
        self,
        component: str,
        operation: str,
        duration: float,
        tokens: int = 0,
        error: Optional[str] = None
    ) -> None:
        """Log an operation with metrics.

        Args:
            component: Component name (e.g., "HardenedGeminiExecutor")
            operation: Operation name (e.g., "execute_k_node")
            duration: Duration in seconds
            tokens: Number of tokens used
            error: Error message if operation failed
        """
        duration_ms = duration * 1000
        success = error is None

        # Create metrics entry
        metrics = OperationMetrics(
            component=component,
            operation=operation,
            duration_ms=duration_ms,
            tokens_used=tokens,
            success=success,
            error=error
        )

        # Store metrics
        self._metrics.append(metrics)

        # Update component statistics
        stats = self._component_stats[component]
        stats["total_operations"] += 1
        stats["total_duration_ms"] += duration_ms
        stats["total_tokens"] += tokens

        if success:
            stats["successful_operations"] += 1
            logger.info(
                f"✓ {component}.{operation} completed in {duration_ms:.2f}ms "
                f"(tokens: {tokens})"
            )
        else:
            stats["failed_operations"] += 1
            stats["errors"].append({
                "operation": operation,
                "error": error,
                "timestamp": metrics.timestamp
            })
            logger.error(
                f"✗ {component}.{operation} failed after {duration_ms:.2f}ms: {error}"
            )

        # Keep only last 10000 metrics to prevent memory bloat
        if len(self._metrics) > 10000:
            self._metrics = self._metrics[-10000:]

    def get_component_stats(self, component: str) -> Dict[str, Any]:
        """Get statistics for a specific component.

        Args:
            component: Component name

        Returns:
            Statistics dictionary
        """
        stats = self._component_stats[component]

        # Calculate derived metrics
        total_ops = stats["total_operations"]
        success_rate = (
            stats["successful_operations"] / total_ops
            if total_ops > 0 else 0.0
        )
        avg_duration = (
            stats["total_duration_ms"] / total_ops
            if total_ops > 0 else 0.0
        )

        return {
            "component": component,
            "total_operations": total_ops,
            "successful_operations": stats["successful_operations"],
            "failed_operations": stats["failed_operations"],
            "success_rate": success_rate,
            "total_duration_ms": stats["total_duration_ms"],
            "avg_duration_ms": avg_duration,
            "total_tokens": stats["total_tokens"],
            "recent_errors": stats["errors"][-5:]  # Last 5 errors
        }

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all components.

        Returns:
            Dictionary mapping component names to their statistics
        """
        return {
            component: self.get_component_stats(component)
            for component in self._component_stats.keys()
        }

    def get_recent_metrics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent operation metrics.

        Args:
            limit: Maximum number of metrics to return

        Returns:
            List of metrics dictionaries
        """
        return [m.to_dict() for m in self._metrics[-limit:]]

    def clear_metrics(self) -> None:
        """Clear all stored metrics and statistics."""
        self._metrics.clear()
        self._component_stats.clear()
        logger.info("SystemTelemetry metrics cleared")

    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics and statistics.

        Returns:
            Complete telemetry data
        """
        return {
            "metrics": [m.to_dict() for m in self._metrics],
            "component_stats": self.get_all_stats(),
            "export_timestamp": datetime.now().isoformat()
        }

# Global telemetry instance
_TELEMETRY: Optional[SystemTelemetry] = None

def get_telemetry() -> SystemTelemetry:
    """Get or create global telemetry instance.

    Returns:
        SystemTelemetry instance
    """
    global _TELEMETRY
    if _TELEMETRY is None:
        _TELEMETRY = SystemTelemetry()
    return _TELEMETRY
