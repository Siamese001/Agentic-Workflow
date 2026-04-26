"""BUS_P — Preference / Eval signal bus.

Receives preference + evaluation signals from sealed completed runs:
rubric scores, judge calibration, HITL accept/reject. Future-run-only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from system_learning.buses._base import BaseBus


@dataclass(frozen=True)
class PreferenceRecord:
    """One sealed preference / evaluation observation."""

    run_id: str
    sealed_at_unix: float
    request_id: str
    signal_type: str  # "rubric" | "judge" | "hitl_accept" | "hitl_reject" | ...
    score: float
    rubric_version: str = ""
    judge_id: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)


class BusP(BaseBus[PreferenceRecord]):
    """Append-only preference / eval bus."""

    def __init__(self) -> None:
        super().__init__(name="BUS_P")

    def publish(self, record: PreferenceRecord) -> None:
        self._gate_future_run_only(record)
        self.records.append(record)


__all__ = ["BusP", "PreferenceRecord"]
