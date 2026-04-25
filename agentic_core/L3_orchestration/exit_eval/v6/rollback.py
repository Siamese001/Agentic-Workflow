"""UWG rollback executor.

Consumes the ``rollback_plan`` carried in an ``X3CommitRequestPacket`` (and
threaded into the ledger payload at U4) so that a U5 read-surface refresh
failure does not leave the system in an inconsistent state.

A rollback plan is a list of ordered steps. Each step has a ``kind`` that
maps to a ``RollbackHandler`` registered with the executor. Built-in handler
``NoopRollbackHandler`` records calls without performing real work — useful
for tests and for environments where the ledger is the only durable surface.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

logger = logging.getLogger(__name__)


class RollbackOutcome(str, Enum):
    EXECUTED = "EXECUTED"
    SKIPPED_NO_PLAN = "SKIPPED_NO_PLAN"
    FAILED = "FAILED"


@dataclass(slots=True)
class RollbackStep:
    """One reversal step in a rollback plan."""

    kind: str
    target: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    description: str = ""


@dataclass(slots=True)
class RollbackPlan:
    """Bounded ordered sequence of rollback steps."""

    steps: list[RollbackStep] = field(default_factory=list)
    abort_on_first_failure: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "RollbackPlan":
        """Parse a packet's ``rollback_plan`` dict.

        Tolerates the legacy ``{"steps": [...]}`` shape used in tests as well
        as a top-level list shape.
        """
        if not data:
            return cls()
        steps_raw: Iterable[Any]
        if isinstance(data, list):
            steps_raw = data
            abort = True
        else:
            steps_raw = data.get("steps") or []
            abort = bool(data.get("abort_on_first_failure", True))
        steps: list[RollbackStep] = []
        for raw in steps_raw:
            if isinstance(raw, str):
                steps.append(RollbackStep(kind=raw))
            elif isinstance(raw, dict):
                steps.append(
                    RollbackStep(
                        kind=str(raw.get("kind") or raw.get("op") or "noop"),
                        target=str(raw.get("target", "")),
                        payload=dict(raw.get("payload", {}) or {}),
                        description=str(raw.get("description", "")),
                    )
                )
        return cls(steps=steps, abort_on_first_failure=abort)


@dataclass(slots=True)
class RollbackResult:
    """Outcome of running a rollback plan."""

    outcome: RollbackOutcome
    executed: list[str] = field(default_factory=list)
    failed_step: str = ""
    error: str = ""


class RollbackHandler(Protocol):
    """Per-step handler. Raises on failure."""

    def execute(self, step: RollbackStep) -> None: ...


class NoopRollbackHandler:
    """Records calls but does no real work."""

    def __init__(self) -> None:
        self.calls: list[RollbackStep] = []

    def execute(self, step: RollbackStep) -> None:
        self.calls.append(step)


class FailingRollbackHandler:
    """Always raises — used in tests and as a fail-fast sentinel."""

    def __init__(self, message: str = "rollback handler not configured") -> None:
        self._message = message

    def execute(self, step: RollbackStep) -> None:
        raise RuntimeError(f"{self._message}: kind={step.kind!r}")


class SequentialRollbackExecutor:
    """Runs each step in order via a kind→handler dispatch table."""

    def __init__(
        self,
        handlers: dict[str, RollbackHandler] | None = None,
        *,
        default_handler: RollbackHandler | None = None,
    ) -> None:
        self._handlers: dict[str, RollbackHandler] = dict(handlers or {})
        self._default = default_handler

    def register(self, kind: str, handler: RollbackHandler) -> None:
        self._handlers[kind] = handler

    def _resolve(self, kind: str) -> RollbackHandler:
        if kind in self._handlers:
            return self._handlers[kind]
        if self._default is not None:
            return self._default
        raise KeyError(f"no rollback handler registered for kind={kind!r}")

    def execute(self, plan: RollbackPlan) -> RollbackResult:
        if not plan.steps:
            return RollbackResult(outcome=RollbackOutcome.SKIPPED_NO_PLAN)
        executed: list[str] = []
        for step in plan.steps:
            try:
                handler = self._resolve(step.kind)
                handler.execute(step)
                executed.append(step.kind)
            except (KeyError, RuntimeError, OSError, ValueError) as exc:
                logger.warning(
                    "rollback: step kind=%s target=%s failed: %s",
                    step.kind,
                    step.target,
                    exc,
                )
                if plan.abort_on_first_failure:
                    return RollbackResult(
                        outcome=RollbackOutcome.FAILED,
                        executed=executed,
                        failed_step=step.kind,
                        error=str(exc),
                    )
        return RollbackResult(outcome=RollbackOutcome.EXECUTED, executed=executed)


__all__ = [
    "FailingRollbackHandler",
    "NoopRollbackHandler",
    "RollbackHandler",
    "RollbackOutcome",
    "RollbackPlan",
    "RollbackResult",
    "RollbackStep",
    "SequentialRollbackExecutor",
]
