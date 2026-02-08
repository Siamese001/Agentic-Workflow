"""
Structure Blueprint Config — Pure Re-export Shim (Hard Shim Strategy).

SSOT: agentic_core.L5_safety.config.structure_blueprint/

This file contains NO data definitions and NO logic.  It strictly imports
from the modular package and re-exports names so that every existing
``from structure_blueprint_config import X`` continues to work unchanged.

DO NOT add new definitions here. Add them to the modular package instead.
"""
# noqa: F401 — re-exports for backward compatibility

from __future__ import annotations

# Re-export the entire public API from the package.
# The canonical __all__ lives in the package __init__.py; this shim mirrors it.
from agentic_core.L5_safety.config.structure_blueprint import *  # noqa: F401,F403
from agentic_core.L5_safety.config.structure_blueprint import __all__ as _pkg_all
from agentic_core.L5_safety.config.structure_blueprint.artifacts import (  # noqa: F401
    get_app_specific_patterns_compiled,
)
from agentic_core.L5_safety.config.structure_blueprint.classification import (  # noqa: F401
    get_classification_suffix_patterns_compiled,
    get_compound_suffix_patterns_compiled,
)

# Backward-compat re-exports: names that have active consumers but were
# removed from the package's public __all__ (internal/scaffolding names).
# These are importable via ``from structure_blueprint_config import X``
# but NOT via ``from structure_blueprint_config import *``.
from agentic_core.L5_safety.config.structure_blueprint.derived import (  # noqa: F401
    L4_APPROVED_FOLDERS,
    L4_SUBFOLDER_MAP,
    SCRIPTS_PLACEMENT_RULES,
    agentic_core_registry,
    verify_derived_registries,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (  # noqa: F401
    get_apps_lic_subfolder_map,
    get_apps_rg_subfolder_map,
    get_apps_shared_subfolder_map,
    get_core_subfolder_map,
    get_sovereign_territories,
    get_subfolder_metadata,
)
from agentic_core.L5_safety.config.structure_blueprint.territories import (  # noqa: F401
    LAYER_OVERRIDES,
    SubfolderDefinition,
    TerritoryDefinition,
    build_sovereign_territories,
)

# Mirror the package's __all__ exactly — no additions, no removals.
__all__ = list(_pkg_all)
