from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class CostTracker:
    spans: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def start_span(self, name: str):
        self.spans[name] = {"start": 0, "end": None, "tokens": 0, "cost": 0.0}

    def end_span(self, name: str, tokens: int = 0, cost: float = 0.0):
        if name in self.spans:
            self.spans[name]["end"] = 1
            self.spans[name]["tokens"] = tokens
            self.spans[name]["cost"] = cost

    def snapshot(self) -> Dict[str, Any]:
        return self.spans.copy()
