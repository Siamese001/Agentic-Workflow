"""Runtime Utils - Utility functions for runtime operations."""

from .main_util import main

try:
    from .runtime_bootstrapper import *  # noqa: F401,F403
except ImportError:
    pass

__all__ = [
    "main",
]
