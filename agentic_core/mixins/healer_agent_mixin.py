"""
HealerAgentMixin — Canonical location.

Relocated from agentic_core/L3_orchestration/types/healer_types.py to satisfy
the mixin location invariant (all *Mixin classes under agentic_core/mixins/).

Original file re-exports this class for backward compatibility.
"""
from __future__ import annotations
import logging
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class HealerAgentMixin:
    """
    Mixin for NEW agents. Enforces strict interface compliance.
    Inherit from this to automatically get input validation.
    """

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Template method that handles validation and error wrapping.
        Subclasses should implement `_heal_impl`.
        """
        if not isinstance(violation, dict):
            return {'status': 'failed', 'errors': ['Violation must be a dictionary']}
        try:
            result = self._heal_impl(violation)
            return self._normalize_result(result)
        except Exception as e:
            logging.error(f'Heal operation failed in {self.__class__.__name__}: {e}')
            return {'status': 'failed', 'errors': [str(e)]}

    def _heal_impl(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Override this in your agent."""
        raise NotImplementedError('Agents must implement _heal_impl')

    def _normalize_result(self, result: Any) -> dict[str, Any]:
        """Ensures result matches HEAL_RESULT_SCHEMA."""
        if not isinstance(result, dict):
            return {'status': 'success' if result else 'failed', 'details': str(result), 'artifacts': [], 'errors': []}
        defaults = {'status': 'success', 'details': 'Fixed', 'artifacts': [], 'errors': []}
        for k, v in defaults.items():
            if k not in result:
                result[k] = v
        return result
