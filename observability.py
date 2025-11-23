# FILE: observability.py
"""Compatibility shim for observability.

This module now forwards to the runtime.observability package, which
contains the actual implementations for spans, events, emitters, and
collectors. Existing imports of `observability` continue to work.
"""

from __future__ import annotations

from runtime.observability.spans import *  # noqa: F401,F403
from runtime.observability.events import *  # noqa: F401,F403
from runtime.observability.emitters import *  # noqa: F401,F403
from runtime.observability.collectors import (  # noqa: F401
    get_events,
    clear_events as _clear_events_impl,
)


def get_all_events():
    """Backward-compatible alias for get_events()."""

    return get_events()


def clear_events() -> None:  # type: ignore[override]
    """Backward-compatible alias for collectors.clear_events()."""

    _clear_events_impl()

