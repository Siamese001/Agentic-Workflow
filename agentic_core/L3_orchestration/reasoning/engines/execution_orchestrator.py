"""Execution orchestrator shim with deterministic state handling."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from time import time
from typing import Any


def _coerce_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dict or None")
    return dict(payload)


@dataclass
class ExecutionOrchestrator:
    """Small placeholder object used by import-and-contract tests.

    The implementation stays intentionally compact but provides deterministic
    merge semantics, immutable snapshots, and a bounded run history that is
    useful when these shims are exercised outside the test suite.
    """

    state: dict[str, Any] = field(default_factory=dict)
    max_history: int = 50
    run_count: int = 0
    _history: list[dict[str, Any]] = field(default_factory=list, init=False, repr=False)

    def run(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        normalized = _coerce_payload(payload)
        self.run_count += 1
        if normalized:
            self.state.update(normalized)
        self.state["run_count"] = self.run_count
        snapshot = self.snapshot()
        self._history.append({"timestamp": time(), "state": snapshot})
        if len(self._history) > max(1, int(self.max_history)):
            self._history = self._history[-int(self.max_history) :]
        return snapshot

    def snapshot(self) -> dict[str, Any]:
        return deepcopy(self.state)

    def history(self) -> list[dict[str, Any]]:
        return deepcopy(self._history)

    def reset(self) -> None:
        self.state.clear()
        self.run_count = 0
        self._history.clear()


def validate_execution_orchestrator() -> bool:
    probe = ExecutionOrchestrator()
    result = probe.run({"status": "ok"})
    return result.get("status") == "ok" and len(probe.history()) == 1


__all__ = ["ExecutionOrchestrator", "validate_execution_orchestrator"]
