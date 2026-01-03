from __future__ import annotations

import functools
from typing import Callable

from .shared_counters import counters


def layer_entry(layer: str, subterritory: str | None = None):
    """Decorator: Auto-increment counter on method entry, safe in exceptions."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            counters.increment(layer, subterritory)
            try:
                return func(*args, **kwargs)
            finally:
                # Optional: decrement on error if needed; here count attempts
                pass
        return wrapper
    return decorator
