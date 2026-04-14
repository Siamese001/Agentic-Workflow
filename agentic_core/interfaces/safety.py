"""
agentic_core/interfaces/safety.py

Sovereign safety interface for L1_cognition consumption.
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
