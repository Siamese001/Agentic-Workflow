"""
agentic_core/interfaces/validators.py

Sovereign validators interface for apps_* consumption.

Re-exports validator types from L5_safety so apps_* reasoning files
can import from the approved interface boundary.

AUTHORITY CONSTRAINTS:
- Type re-exports only — no validation execution authority
- No access to enforcement logic

USAGE (apps_*):
    from agentic_core.interfaces.validators_shim import RuleFailure
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
