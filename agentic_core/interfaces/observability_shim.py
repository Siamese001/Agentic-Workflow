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
    from agentic_core.interfaces.observability_shim import (
        SystemTelemetry,
        CircuitBreakerState,
    )
"""

from __future__ import annotations

from agentic_core.L6_observability.utils.system_telemetry_util import SystemTelemetry
from agentic_core.runtime.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)
from agentic_core.runtime.types.circuit_breaker_types import CircuitBreakerState

emit_determinism_digest("observability", "observability_digest")
record_execution_trace("observability", "observability_trace")


__all__ = ["SystemTelemetry", "CircuitBreakerState"]
