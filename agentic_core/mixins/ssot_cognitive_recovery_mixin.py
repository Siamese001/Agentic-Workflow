"""
SSOT Cognitive Recovery Mixin — Advisory Healing Hints.

Provides cognitive recovery that:
  - Advisory hints only — no mutation authority
  - Replay mode enforces read-only behavior
  - Policy-hash-scoped recovery context

Layer: L6 Observer
Authority: Advisory only. No mutation. No L4 writes. No routing influence.
"""

from __future__ import annotations

import logging
import time
from typing import Any

_logger = logging.getLogger("SSOTCognitiveRecovery")


class SSOTCognitiveRecoveryMixin:
    """Advisory cognitive recovery hints for healing operations.

    Reads ``active_policy_hash`` and ``is_replay_mode`` from ReplayGuardMixin.
    Recovery suggestions are advisory — they never mutate state or payloads.
    Under replay mode, suggestions are read-only (no new suggestions generated).
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ssot_recovery_hints: list[dict[str, Any]] = []

    def suggest_recovery(
        self, failure_type: str, failure_context: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Generate an advisory recovery suggestion.

        Under replay mode, returns None (read-only).

        Parameters
        ----------
        failure_type : str
            Type of failure to recover from.
        failure_context : dict | None
            Additional context about the failure.

        Returns
        -------
        dict | None
            Recovery suggestion, or None if replay mode.
        """
        if getattr(self, "is_replay_mode", False):
            _logger.debug("[SSOTRecovery] Replay mode: skipping suggestion for %s", failure_type)
            return None
        policy_hash = getattr(self, "active_policy_hash", "unknown")
        suggestion = {
            "failure_type": failure_type,
            "strategy": self._derive_strategy(failure_type),
            "confidence": self._estimate_recovery_confidence(failure_type),
            "policy_hash": policy_hash,
            "timestamp": time.time(),
            "context": failure_context or {},
        }
        self._ssot_recovery_hints.append(suggestion)
        _logger.debug(
            "[SSOTRecovery] Suggestion: %s -> %s (confidence=%.2f)",
            failure_type,
            suggestion["strategy"],
            suggestion["confidence"],
        )
        return suggestion

    @property
    def recovery_hints(self) -> list[dict[str, Any]]:
        """All recorded recovery hints."""
        return list(self._ssot_recovery_hints)

    @staticmethod
    def _derive_strategy(failure_type: str) -> str:
        """Derive a recovery strategy from failure type."""
        strategies = {
            "import_error": "fix_imports",
            "naming_violation": "rename_file",
            "hierarchy_violation": "relocate_file",
            "syntax_error": "ast_repair",
            "test_failure": "regenerate_test",
        }
        ft_lower = failure_type.lower()
        for key, strategy in strategies.items():
            if key in ft_lower:
                return strategy
        return "manual_review"

    @staticmethod
    def _estimate_recovery_confidence(failure_type: str) -> float:
        """Estimate confidence in recovery success."""
        high_confidence = {"import_error", "naming_violation", "syntax_error"}
        ft_lower = failure_type.lower()
        for pattern in high_confidence:
            if pattern in ft_lower:
                return 0.85
        return 0.5
