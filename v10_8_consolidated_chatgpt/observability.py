"""Observability module consolidating telemetry and optimization helpers."""


from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CostTracker:
    spans: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def start_span(self, name: str) -> None:
        self.spans[name] = {"start": time.perf_counter(), "end": None}

    def end_span(self, name: str) -> None:
        if name in self.spans and self.spans[name]["end"] is None:
            self.spans[name]["end"] = time.perf_counter()

    def snapshot(self) -> Dict[str, Any]:
        snapshot_spans: List[Dict[str, float]] = []
        for span_name in sorted(self.spans.keys()):
            span = self.spans[span_name]
            start = span.get("start", 0.0) or 0.0
            end = span.get("end", start)
            duration_ms = max((end - start) * 1000.0, 0.0)
            snapshot_spans.append({"name": span_name, "duration_ms": duration_ms})
        return {"spans": snapshot_spans}
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class MetricEvent:
    name: str
    value: float
    tags: Dict[str, Any]


@dataclass
class SpanEvent:
    name: str
    start_time_ms: int
    end_time_ms: int
    tags: Dict[str, Any]


@dataclass
class TraceContext:
    trace_id: str
    spans: Dict[str, SpanEvent]
TELEMETRY_EVENTS = []


def record_event(name: str, payload: dict):
    TELEMETRY_EVENTS.append({"name": name, "payload": payload})


def get_events():
    return list(TELEMETRY_EVENTS)
from typing import Any, Dict


def compute_optimization_hint(spans: list) -> Dict[str, Any]:
    """
    Deterministic optimization hint based on span durations.
    """
    planning = next((s for s in spans if s.get("name") == "planning"), {"duration_ms": 0})
    execution = next((s for s in spans if s.get("name") == "execution"), {"duration_ms": 0})

    if float(planning.get("duration_ms", 0)) > float(execution.get("duration_ms", 0)):
        return {"suggestion": "reroute_fast"}
    return {"suggestion": "normal"}
class PredictiveCache:
    def __init__(self):
        self.cache = {}

    def get(self, signature: str):
        return self.cache.get(signature)

    def set(self, signature: str, value):
        self.cache[signature] = value

    def snapshot(self):
        return self.cache.copy()
class PolicyAutoTunerStub:
    def suggest_config(self, state, metrics):
        # deterministic suggestion stub
        return {
            "temperature": 0.3,
            "max_tokens": 500,
            "routing_adjustment": "none",
        }
