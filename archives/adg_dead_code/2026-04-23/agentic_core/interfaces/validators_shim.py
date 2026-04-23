"""
agentic_core/interfaces/validators_shim.py

Sovereign validators interface for apps_* consumption.
"""

from __future__ import annotations


def _missing_rule_failure(reason: str):
    class RuleFailure:  # type: ignore[no-redef]
        """Fail-fast stub when the validator package is unavailable."""

        def __init__(self, *args, **kwargs) -> None:
            raise ModuleNotFoundError(f"RuleFailure is unavailable because {reason}")

    return RuleFailure


try:
    from agentic_core.L5_safety.validators import RuleFailure
except ImportError as exc:
    RuleFailure = _missing_rule_failure(str(exc))

__all__ = ["RuleFailure"]
