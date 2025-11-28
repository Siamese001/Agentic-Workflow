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
