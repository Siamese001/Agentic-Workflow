from __future__ import annotations

"""Core L2 execution shim.

This module re-exports the historical top-level l2 functions so callers
can import from core.l2 without breaking existing code.
"""

from l2 import *  # noqa: F401,F403
