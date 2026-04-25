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

# Wildcard re-export so all path/numeric constants defined in the L0 SSOT
# become importable from this shim (e.g., `from agentic_core.interfaces.path_constants
# import DEFAULT_SLEEP, THRESHOLD`). Adding a new constant in the L0 SSOT makes
# it appear here automatically without any change to this file.
from agentic_core.L0_routing.config.path_constants import *  # noqa: F401,F403  # guardian: allow-star-import -- this module IS a wildcard re-export shim by design; the star import is the contract that lets new constants in the L0 SSOT appear here automatically without a code change. Removing the star would break the documented `from agentic_core.interfaces.path_constants import <CONST>` pattern that ~70 callers use.
from agentic_core.L0_routing.config.path_constants import __all__ as _pc_all

__all__ = list(_pc_all)
