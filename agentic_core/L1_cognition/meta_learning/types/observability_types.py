"""
agentic_core/L1_cognition/meta_learning/types/observability_types.py

Passive data structures for MetaLearningObservability.
Extracted from engine/meta_observability.py to prevent circular dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class MetricPoint:
    """A single metric data point."""

    name: str
    value: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class HealthStatus:
    """Health status for a component."""

    component: str
    healthy: bool
    message: str
    last_check: str = field(default_factory=lambda: datetime.now().isoformat())
    details: dict[str, Any] = field(default_factory=dict)
