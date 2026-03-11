"""
SSOT Adaptive Execution Mixin — L4-Derived Execution Mode Selection.

Provides adaptive execution that:
  - Derives execution mode from L4 aggregate signals
  - Replay mode locks to "standard" (no adaptive switching)
  - Must not override should_proceed_with_healing

Layer: L2 Execution Aid
Authority: Mode selection only. No L4 mutation. No routing override.
"""

from __future__ import annotations

import logging
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

_logger = logging.getLogger("SSOTAdaptiveExecution")

EXECUTION_MODES = ("standard", "aggressive", "conservative", "minimal")


class SSOTAdaptiveExecutionMixin:
    """L4-derived execution mode with replay lock.

    Reads ``active_policy_hash`` and ``is_replay_mode`` from ReplayGuardMixin.
    Under replay mode, execution mode is locked to "standard".
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ssot_execution_mode: str = "standard"

    @property
    def execution_mode(self) -> str:
        """Current execution mode. Locked to 'standard' under replay."""
        if getattr(self, "is_replay_mode", False):
            return "standard"
        return self._ssot_execution_mode

    def set_execution_mode(self, mode: str) -> bool:
        """Set execution mode. Rejected under replay mode.

        Parameters
        ----------
        mode : str
            One of: standard, aggressive, conservative, minimal.

        Returns
        -------
        bool
            True if mode was set, False if rejected (replay mode or invalid).
        """
        if getattr(self, "is_replay_mode", False):
            _logger.warning("[SSOTAdaptive] Mode change rejected: replay mode active")
            return False

        if mode not in EXECUTION_MODES:
            _logger.warning("[SSOTAdaptive] Invalid mode: %s (valid: %s)", mode, EXECUTION_MODES)
            return False

        old = self._ssot_execution_mode
        self._ssot_execution_mode = mode
        _logger.info("[SSOTAdaptive] Mode: %s -> %s", old, mode)
        return True

    def derive_mode_from_signals(
        self,
        failure_rate: float = 0.0,
        violation_count: int = 0,
    ) -> str:
        """Derive execution mode from L4 aggregate signals.

        Under replay mode, always returns "standard".

        Parameters
        ----------
        failure_rate : float
            Recent failure rate (0.0 to 1.0).
        violation_count : int
            Number of active violations.

        Returns
        -------
        str
            Recommended execution mode.
        """
        if getattr(self, "is_replay_mode", False):
            return "standard"

        if failure_rate > 0.5 or violation_count > 50:
            return "conservative"
        if failure_rate > 0.2 or violation_count > 20:
            return "standard"
        if violation_count < 5:
            return "aggressive"
        return "standard"
