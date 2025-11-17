# telemetry.py
"""
Shared Telemetry — v10_9
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List
from datetime import datetime


@dataclass
class MetricEvent:
    name: str
    value: float
    tags: Dict[str, Any]


@dataclass
class SpanEvent:
    name: str
    start_time_ms: float
    end_time_ms: float
    tags: Dict[str, Any]


TELEMETRY_EVENTS: List[Dict[str, Any]] = []
SAFETY_LOG: List[Dict[str, Any]] = []


def record_event(name: str, payload: Dict[str, Any]) -> None:
    TELEMETRY_EVENTS.append(
        {"name": name, "payload": payload, "ts": datetime.utcnow().isoformat()}
    )


def get_events() -> List[Dict[str, Any]]:
    return list(TELEMETRY_EVENTS)


@dataclass
class CostTracker:
    spans: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def start_span(self, name: str) -> None:
        self.spans[name] = {"start": time.perf_counter(), "end": None}

    def end_span(self, name: str) -> None:
        if name in self.spans and self.spans[name]["end"] is None:
            self.spans[name]["end"] = time.perf_counter()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "spans": [
                {
                    "name": k,
                    "duration_ms": max((v["end"] - v["start"]) * 1000.0, 0.0)
                    if v["end"]
                    else 0.0,
                }
                for k, v in self.spans.items()
            ]
        }


def log_safety_decision(payload: Dict[str, Any], patch: Dict[str, Any]):
    SAFETY_LOG.append(
        {"payload": payload, "patch": patch, "ts": datetime.utcnow().isoformat()}
    )
