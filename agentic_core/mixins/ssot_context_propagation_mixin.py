"""
SSOT Context Propagation Mixin — ContextVar-Based Trace/Policy Propagation.

Provides context propagation that:
  - Propagates trace_id and policy_hash via contextvars
  - Ensures async boundaries preserve context
  - No manual context mutation outside of managed scope

Layer: L2 Execution Aid
Authority: Context propagation only. No L4 mutation. No routing influence.
"""

from __future__ import annotations

import contextvars
import logging
from contextlib import contextmanager
from typing import Any, Generator

_logger = logging.getLogger("SSOTContextPropagation")
_TRACE_ID_VAR: contextvars.ContextVar[str] = contextvars.ContextVar("ssot_trace_id", default="unknown")
_POLICY_HASH_VAR: contextvars.ContextVar[str] = contextvars.ContextVar("ssot_policy_hash", default="unknown")
_REPLAY_MODE_VAR: contextvars.ContextVar[bool] = contextvars.ContextVar("ssot_replay_mode", default=False)


def get_propagated_trace_id() -> str:
    """Read the propagated trace_id from current context."""
    return _TRACE_ID_VAR.get()


def get_propagated_policy_hash() -> str:
    """Read the propagated policy_hash from current context."""
    return _POLICY_HASH_VAR.get()


def get_propagated_replay_mode() -> bool:
    """Read the propagated replay_mode from current context."""
    return _REPLAY_MODE_VAR.get()


class SSOTContextPropagationMixin:
    """Propagates trace_id and policy_hash via ContextVars.

    Reads ``active_policy_hash``, ``trace_id``, and ``is_replay_mode``
    from ReplayGuardMixin and installs them into ContextVars for
    cross-boundary (including async) propagation.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._propagate_context()

    def _propagate_context(self) -> None:
        """Install current trace/policy into ContextVars."""
        trace_id = getattr(self, "trace_id", "unknown")
        policy_hash = getattr(self, "active_policy_hash", "unknown")
        replay_mode = getattr(self, "is_replay_mode", False)
        _TRACE_ID_VAR.set(trace_id)
        _POLICY_HASH_VAR.set(policy_hash)
        _REPLAY_MODE_VAR.set(replay_mode)
        _logger.debug(
            "[SSOTContext] Propagated trace_id=%s policy_hash=%s replay=%s",
            trace_id,
            policy_hash[:12] if len(policy_hash) > 12 else policy_hash,
            replay_mode,
        )

    @contextmanager
    def propagation_scope(self) -> Generator[None, None, None]:
        """Context manager that ensures ContextVars are set for this scope.

        Useful when entering a new execution boundary (thread, async task).
        """
        old_trace = _TRACE_ID_VAR.get()
        old_policy = _POLICY_HASH_VAR.get()
        old_replay = _REPLAY_MODE_VAR.get()
        self._propagate_context()
        try:
            yield
        finally:
            _TRACE_ID_VAR.set(old_trace)
            _POLICY_HASH_VAR.set(old_policy)
            _REPLAY_MODE_VAR.set(old_replay)
