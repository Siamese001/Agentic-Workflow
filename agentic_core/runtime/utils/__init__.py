"""Runtime Utils - Utility functions for runtime operations."""


from .main_util import main

try:
    from .runtime_bootstrapper import *
except ImportError:  # guardian: allow-silent-swallow
    pass
__all__ = ["main"]
