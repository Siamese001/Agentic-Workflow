"""Thin execution context shared by RG scripts (`generate_resume`, `rg_live_fire`)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


_MISSING = object()


@dataclass
class _SovereignBuffer:
    _data: dict[str, Any] = field(default_factory=dict)

    def read(self, key: str, default: Any | object = _MISSING) -> Any:
        """Read a keyed hop payload; single-arg reads return ``None`` when absent."""
        if default is _MISSING:
            return self._data.get(key)
        return self._data.get(key, default)

    def write(self, key: str, value: Any) -> None:
        self._data[key] = value


@dataclass
class _SovereignTrace:
    failure_count: int = 0
    span_total: int = 0

    def get_summary(self) -> dict[str, int]:
        return {"total_spans": self.span_total, "failures": self.failure_count}


@dataclass
class SovereignContext:
    """Minimal wiring surface for deterministic resume orchestrator scripts."""

    master_resume: dict[str, Any] = field(default_factory=dict)
    buffer: _SovereignBuffer = field(default_factory=_SovereignBuffer)
    trace: _SovereignTrace = field(default_factory=_SovereignTrace)
