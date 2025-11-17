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
