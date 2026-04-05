"""
agentic_core/runtime/sovereignty_exceptions.py

Exception types raised by runtime sovereignty and boundary validators.
"""

from __future__ import annotations


class SovereigntyViolationError(RuntimeError):
    """Raised when a runtime sovereignty boundary is crossed.

    Examples:
    - An ``agentic_core`` module was imported while a forbidden ``apps_*``
      package was present in ``sys.modules``.
    - An import violated the layer-gravity rule (lower layer importing
      from a higher layer).
    """


class IsolationViolationError(RuntimeError):
    """Raised when a write or mutation occurs outside the permitted boundary.

    Examples:
    - A module attempted to write to a path outside its sovereign territory.
    - An agent tried to mutate state belonging to another layer.
    """


class CapabilityTokenError(RuntimeError):
    """Raised when a capability token is invalid, expired, or missing.

    Examples:
    - An execution attempted to proceed without a valid capability token.
    - A token was presented after its TTL expired.
    """


class DeterminismViolationError(RuntimeError):
    """Raised when a determinism contract is violated.

    Examples:
    - A replay produced a different hash than the original execution.
    - A non-deterministic operation was detected in a deterministic context.
    """


__all__ = [
    "SovereigntyViolationError",
    "IsolationViolationError",
    "CapabilityTokenError",
    "DeterminismViolationError",
]
