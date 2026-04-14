"""Runtime-safe orchestrator retry shim."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


@dataclass
class OrchestratorStateRetry:
    """Small placeholder object used by import-and-contract tests."""

    state: dict[str, Any] = field(default_factory=dict)
    attempts: int = 0
    max_attempts: int = 3

    def run(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        normalized = dict(payload or {})
        self.attempts += 1
        exhausted = self.attempts > max(1, int(self.max_attempts))
        self.state["retry_exhausted"] = exhausted
        self.state["attempts"] = self.attempts
        if normalized:
            self.state.update(normalized)
        return deepcopy(self.state)

    def can_retry(self) -> bool:
        return self.attempts < max(1, int(self.max_attempts))

    def reset(self) -> None:
        self.attempts = 0
        self.state.clear()
        self.state["attempts"] = 0
        self.state["retry_exhausted"] = False


def validate_orchestrator_state_retry() -> bool:
    probe = OrchestratorStateRetry(max_attempts=2)
    probe.run()
    state = probe.run()
    return state.get("attempts") == 2 and not state.get("retry_exhausted", False)


__all__ = ["OrchestratorStateRetry", "validate_orchestrator_state_retry"]
