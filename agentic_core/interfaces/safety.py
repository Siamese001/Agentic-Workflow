"""
agentic_core/interfaces/safety.py

Sovereign Safety and Validation interfaces for L1_cognition consumption.

Re-exports safety and validation components so L1_cognition can
access validation services without directly importing from L5_safety.

AUTHORITY CONSTRAINTS:
- Safety components provide validation and enforcement services
- No direct safety bypass through these interfaces
- All validation decisions are recorded for audit

USAGE (L1_cognition):
    from agentic_core.interfaces.safety import (
        UnifiedCSTHealer,
        # Add other safety components as needed
    )
"""

from __future__ import annotations


class _MissingOptionalDependency:
    def __init__(self, symbol: str, reason: str) -> None:
        self._symbol = symbol
        self._reason = reason

    def __getattr__(self, attr: str):
        raise ModuleNotFoundError(f"{self._symbol} is unavailable because {self._reason}")

    def __call__(self, *args, **kwargs):
        raise ModuleNotFoundError(f"{self._symbol} is unavailable because {self._reason}")


try:
    from agentic_core.L5_safety.validators.unified_cst_healer import UnifiedCSTHealer
except ImportError as exc:
    UnifiedCSTHealer = _MissingOptionalDependency("UnifiedCSTHealer", str(exc))

__all__ = ["UnifiedCSTHealer"]
