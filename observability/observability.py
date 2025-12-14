"""Observability - Runtime Layer



logger = logging.getLogger(__name__)
This module provides observability compatibility shim.

Layer: Runtime/Infrastructure
Responsibilities:
- Forward to runtime.observability
- Maintain backward compatibility
- Provide unified observability API

Non-responsibilities:
- Business logic
- Layer-specific operations
"""

# FILE: observability.py


# from archives.legacy_root_folders.runtime.observability.spans import *  # DEPRECATED: Archive i...
# from archives.legacy_root_folders.runtime.observability.traces import *  # DEPRECATED: Archive ...
# from archives.legacy_root_folders.runtime.observability.metrics import *  # DEPRECATED: Archive...


def get_all_events() -> list:
    """Backward-compatible alias for get_events()."""

    return get_events()


def clear_events() -> None:  # type: ignore[override]
    """Backward-compatible alias for collectors.clear_events()."""

    _clear_events_impl()
