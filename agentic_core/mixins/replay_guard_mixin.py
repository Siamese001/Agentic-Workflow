"""
ReplayGuardMixin — Deterministic Replay Foundation for SSOT Mixin Integration.

Provides the base replay-mode enforcement layer that all stateful mixins
depend on. Accepts an injected ExecutionContext (never reads environment
variables directly) and loads the active policy hash from L4 config.

Layer: L2 Execution Aid
Authority: Guard only — no L4 mutation, no L5 bypass, no routing influence.

When replay_mode is True:
  - Installs deterministic providers (time, random, uuid) via L2 module.
  - Locks replay_mode immutably for the lifetime of the instance.
  - Exposes properties consumed by downstream mixins to disable TTL,
    adaptive switching, breaker mutation, and ML writes.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agentic_core.L0_routing.scripts.execution_context import ExecutionContext
_logger = logging.getLogger(__name__)


class ReplayGuardMixin:
    """Base mixin providing replay-mode awareness and policy-hash scoping.

    Must appear rightmost in MRO so that all other mixins can access
    ``is_replay_mode``, ``active_policy_hash``, and ``trace_id``.

    Constructor Parameters
    ----------------------
    execution_context : ExecutionContext | None
        Injected by the caller (entrypoint / test harness).
        If None, defaults to non-replay mode with L4-derived policy hash.
    """

    def __init__(self, execution_context: ExecutionContext | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if execution_context is not None:
            self._replay_mode: bool = bool(execution_context.replay_mode)
            self._trace_id: str = execution_context.trace_id or "no-trace"
            self._active_policy_hash: str = (
                execution_context.active_policy_hash or self._load_policy_hash_from_l4()
            )
            self._safety_status: str = execution_context.safety_status
            self._initial_policy_hash: str = self._active_policy_hash
        else:
            self._replay_mode = False
            self._trace_id = "no-trace"
            self._active_policy_hash = self._load_policy_hash_from_l4()
            self._safety_status = "PENDING"
            self._initial_policy_hash = self._active_policy_hash
        if self._replay_mode:
            self._install_deterministic_providers()
            _logger.info(
                "[ReplayGuard] Replay mode ACTIVE | trace_id=%s | policy_hash=%s",
                self._trace_id,
                self._active_policy_hash[:12] + "...",
            )

    @property
    def is_replay_mode(self) -> bool:
        """True if execution is a deterministic replay."""
        return self._replay_mode

    @property
    def active_policy_hash(self) -> str:
        """Current L4 policy hash scoping all mixin state."""
        return self._active_policy_hash

    @property
    def trace_id(self) -> str:
        """Immutable trace identifier for this execution run."""
        return self._trace_id

    @property
    def safety_status(self) -> str:
        """Current L5 safety gate status."""
        return self._safety_status

    @property
    def initial_policy_hash(self) -> str:
        """Policy hash captured at construction time for drift detection."""
        return self._initial_policy_hash

    def policy_hash_drifted(self) -> bool:
        """Return True if active_policy_hash differs from initial snapshot."""
        return self._active_policy_hash != self._initial_policy_hash

    @staticmethod
    def _load_policy_hash_from_l4() -> str:
        """Load active policy hash from L4 versioned config SSOT."""
        try:
            from agentic_core.L4_state.config.versioned_configs import get_active_configs

            return get_active_configs().policy.config_hash
        except ImportError:
            _logger.warning("[ReplayGuard] L4 versioned_configs unavailable; using fallback policy hash.")
            return "fallback-no-l4"

    def _install_deterministic_providers(self) -> None:
        """Activate deterministic time/random/uuid for replay mode."""
        try:
            from agentic_core.L2_execution.deterministic_providers import patch_deterministic

            providers = patch_deterministic(self._trace_id)
            _logger.debug("[ReplayGuard] Deterministic providers installed: %s", list(providers.keys()))
        except ImportError:
            _logger.error(
                "[ReplayGuard] deterministic_providers module not found; replay determinism NOT enforced."
            )
        except Exception as exc:
            _logger.error("[ReplayGuard] Failed to install deterministic providers: %s", exc)
            raise
