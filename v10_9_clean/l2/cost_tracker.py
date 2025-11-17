from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass
class SpanRecord:
    start: float
    end: Optional[float] = None

    def duration_ms(self) -> float:
        if self.end is None:
            return 0.0
        return max((self.end - self.start) * 1000.0, 0.0)


@dataclass
class TokenRecord:
    prompt: int = 0
    completion: int = 0

    @property
    def total(self) -> int:
        return self.prompt + self.completion


@dataclass
class CostTracker:
    spans: Dict[str, SpanRecord] = field(default_factory=dict)
    tokens: Dict[str, TokenRecord] = field(default_factory=dict)

    def start_span(self, name: str) -> None:
        self.spans[name] = SpanRecord(start=time.perf_counter())

    def end_span(self, name: str) -> None:
        span = self.spans.get(name)
        if span and span.end is None:
            span.end = time.perf_counter()

    def add_tokens(self, name: str, prompt_tokens: int = 0, completion_tokens: int = 0) -> None:
        rec = self.tokens.get(name, TokenRecord())
        rec.prompt += prompt_tokens
        rec.completion += completion_tokens
        self.tokens[name] = rec

    def snapshot(self) -> Dict[str, Any]:
        return {
            "spans": [
                {"name": k, "duration_ms": v.duration_ms()}
                for k, v in sorted(self.spans.items())
            ],
            "tokens": [
                {
                    "name": k,
                    "prompt_tokens": v.prompt,
                    "completion_tokens": v.completion,
                    "total_tokens": v.total,
                }
                for k, v in sorted(self.tokens.items())
            ],
        }
