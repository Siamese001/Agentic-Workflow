from __future__ import annotations

"""Core L1 planning shim.

This module re-exports the historical top-level l1 functions so callers
can import from core.l1 without breaking existing code.
"""

from l1 import *  # noqa: F401,F403
