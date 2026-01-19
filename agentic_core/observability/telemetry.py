from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Dict, Optional

Logger = logging.getLogger(__name__)


class OperationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    CIRCUIT_OPEN = "CIRCUIT_OPEN"


class SystemTelemetry:
    def log_success(
        self,
        *,
        component: str,
        operation: str,
        latency_ms: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        Logger.debug(
            f"[TELEMETRY] {component}.{operation} {OperationStatus.SUCCESS} {latency_ms:.1f}ms {metadata or {}}"
        )

    def log_failure(
        self,
        *,
        component: str,
        operation: str,
        latency_ms: float,
        error_type: str,
        error_message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        Logger.warning(
            f"[TELEMETRY] {component}.{operation} {OperationStatus.FAILURE} {latency_ms:.1f}ms {error_type}: {error_message} {metadata or {}}"
        )

    def log_circuit_breaker(
        self,
        *,
        component: str,
        breaker_name: str,
        state: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        Logger.warning(
            f"[TELEMETRY] {component} breaker={breaker_name} state={state} {metadata or {}}"
        )


_default_telemetry: Optional[SystemTelemetry] = None


def get_telemetry() -> SystemTelemetry:
    global _default_telemetry
    if _default_telemetry is None:
        _default_telemetry = SystemTelemetry()
    return _default_telemetry
