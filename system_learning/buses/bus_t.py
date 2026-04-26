"""BUS_T — Telemetry signal bus.

Receives observability and metric signals from sealed completed runs.
Future-run-only: never accepts a record whose run_id matches the
currently-active run (v34 §future-run-only invariant).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from system_learning.buses._base import BaseBus


@dataclass(frozen=True)
class TelemetryRecord:
    """One sealed telemetry observation."""

    run_id: str
    sealed_at_unix: float
    trace_id: str
    request_id: str
    metric_name: str
    metric_value: float
    layer: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)


class BusT(BaseBus[TelemetryRecord]):
    """Append-only telemetry bus."""

    def __init__(self) -> None:
        super().__init__(name="BUS_T")

    def publish(self, record: TelemetryRecord) -> None:
        """Append a telemetry record. Enforces future-run-only invariant."""
        self._gate_future_run_only(record)
        self.records.append(record)


__all__ = ["BusT", "TelemetryRecord"]
