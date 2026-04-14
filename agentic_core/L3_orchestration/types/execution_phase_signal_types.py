"""Execution phase signal types shim used by ADG contract tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_VALID_LEVELS = {"debug", "info", "warning", "error", "critical"}


@dataclass(frozen=True)
class ExecutionPhaseSignal:
    name: str = "noop"
    level: str = "info"
    phase: str = "execute"
    payload: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", str(self.name or "noop"))
        normalized_level = str(self.level or "info").lower()
        if normalized_level not in _VALID_LEVELS:
            normalized_level = "info"
        object.__setattr__(self, "level", normalized_level)
        object.__setattr__(self, "phase", str(self.phase or "execute"))
        object.__setattr__(self, "payload", dict(self.payload or {}))

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "level": self.level,
            "phase": self.phase,
            "payload": dict(self.payload),
        }


__all__ = ["ExecutionPhaseSignal"]
