"""
agentic_core/interfaces/observability.py

Sovereign observability interface for apps_* consumption.

Re-exports L6 telemetry and circuit breaker types so apps_* strategy/executor
files can import from the approved interface boundary.

AUTHORITY CONSTRAINTS:
- Telemetry is observation-only — no routing influence
- Circuit breaker state is read-only from apps_* perspective
- No direct L6 mutation authority

USAGE (apps_*):
    from agentic_core.interfaces.observability import (
        SystemTelemetry,
        CircuitBreakerState,
    )
"""

from __future__ import annotations

from agentic_core.L6_observability.utils.system_telemetry_util import SystemTelemetry
from agentic_core.runtime.types.circuit_breaker_types import CircuitBreakerState

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

__all__ = [
    "SystemTelemetry",
    "CircuitBreakerState",
]
