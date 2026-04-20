"""
agentic_core/interfaces/path_constants.py

Interface shim — re-exports path/numeric constants from the L0 SSOT so that
``apps_*`` code can import them without creating a direct L*-layer dependency.

Consumers in ``apps_*`` should import from this module:
    from agentic_core.interfaces.path_constants import DEFAULT_SLEEP, THRESHOLD

DO NOT add new constants here; add them to
``agentic_core.L0_routing.config.path_constants`` and they will appear here
automatically via the wildcard re-export.
"""

from __future__ import annotations

from agentic_core.L0_routing.config.path_constants import __all__, _pc_all
from agentic_core.L0_routing.config.path_constants import __all__ as _pc_all  # noqa: F401

__all__ = list(_pc_all) if hasattr(_pc_all, "__iter__") else []
