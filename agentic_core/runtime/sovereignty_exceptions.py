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


__all__ = ["SovereigntyViolationError"]
