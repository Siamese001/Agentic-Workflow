"""
Monitor Types - Data models for agent execution monitoring.

Extracted from schemas/UnifiedAgent_monitor_types.py during Schema Dissolution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@dataclass
class ExecutionMetrics:
    """Metrics for a single execution."""

    agent_name: str
    category: str
    strategy_type: str
    execution_time_ms: float
    success: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregatedMetrics:
    """Aggregated metrics for monitoring."""

    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_execution_time_ms: float = 0.0
    avg_execution_time_ms: float = 0.0
    min_execution_time_ms: float = float("inf")
    max_execution_time_ms: float = 0.0
    executions_by_category: dict[str, int] = field(default_factory=dict)
    executions_by_strategy: dict[str, int] = field(default_factory=dict)
    # Phase 4: Facade migration tracking
    facade_executions: int = 0
    facade_agents: dict[str, int] = field(default_factory=dict)


__all__ = [
    "ExecutionMetrics",
    "AggregatedMetrics",
]
