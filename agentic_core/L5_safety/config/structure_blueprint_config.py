"""
Structure Blueprint Config — DEPRECATED Re-export Shim.

DEPRECATED: Import from agentic_core.L0_routing.config.path_constants (constants)
or agentic_core.L5_safety.config.structure_enforcement_util (enforcement functions).
This shim will be removed after all 9 remaining consumers are migrated.

SSOT: agentic_core.L5_safety.config.structure_blueprint/

This file contains NO data definitions and NO domain logic.  It re-exports
names from the modular package so that every existing
``from structure_blueprint_config import X`` continues to work unchanged.

The only "logic" present is structural contract enforcement:
  1. ``from package import *`` to pull in the canonical public API.
  2. Explicit re-imports for 18 backward-compat names.
  3. ``__all__ = list(_pkg_all)`` to mirror the package surface.

Import-Path Policy
~~~~~~~~~~~~~~~~~~
- **Supported import path (external consumers):**
  ``from agentic_core.L5_safety.config.structure_blueprint_config import X``
  This is the stable backward-compatible entry point.

- **SSOT import path (package internals / new code):**
  ``from agentic_core.L5_safety.config.structure_blueprint import X``
  The package ``__all__`` (163 names) is the canonical public API.

Contract
~~~~~~~~
- ``__all__`` mirrors the package's ``__all__`` exactly (163 names).
  ``from structure_blueprint_config import *`` exposes only these names.
- 18 additional internal/scaffolding names (types, builders, lazy getters,
  derived registries) are explicitly re-exported below for backward
  compatibility.  They are importable via
  ``from structure_blueprint_config import X`` but are NOT in ``__all__``
  and are NOT exposed by ``import *``.

DO NOT add new definitions here. Add them to the modular package instead.
"""
# noqa: F401 — re-exports for backward compatibility

from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Re-export the entire public API from the package.
# The canonical __all__ lives in the package __init__.py; this shim mirrors it.
from agentic_core.L5_safety.config.structure_blueprint import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
    __all__,
    _pkg_all,
)

# Wave 3: SOVEREIGN_TERRITORIES removed - use get_all_territories() from territories module
# Backward-compat alias: SOVEREIGN_REGISTRY -> SOVEREIGN_TERRITORIES
# Now imports from main package which uses __getattr__ fallback to get_all_territories()
from agentic_core.L5_safety.config.structure_blueprint import (  # noqa: F401
    SOVEREIGN_TERRITORIES as SOVEREIGN_REGISTRY,
)
from agentic_core.L5_safety.config.structure_blueprint import __all__ as _pkg_all
from agentic_core.L5_safety.config.structure_blueprint._constants import (  # noqa: F401
    AGENT_RESILIENCE_CONFIG,
    DOWNSTREAM_ROOTS,
    GRAVITY_CONFIG,
    GRAVITY_SURGERY_ENABLED,
    HEALING_CONFIG,
    # LAYER_OVERRIDES removed in Wave 1 - use yaml_loader.load_layer_overrides()
    MCP_CAPABILITIES,
    MISSION_CONFIG,
    UPSTREAM_SOVEREIGN_ROOTS,
    SubfolderDefinition,
    TerritoryDefinition,
    # build_sovereign_territories removed - internal only
)
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
    get_apps_eval_subfolder_map,
    get_apps_exec_subfolder_map,
    get_apps_lic_subfolder_map,
    get_apps_research_subfolder_map,
    get_apps_rfp_subfolder_map,
    get_apps_rg_subfolder_map,
    get_apps_shared_subfolder_map,
    get_core_subfolder_map,
    get_sovereign_territories,
    get_subfolder_metadata,
)

# __all__ mirrors the package's __all__ exactly (163 names).
# The 18 backward-compat re-exports above are importable by explicit import
# but are intentionally excluded from __all__ / import *.
__all__ = list(_pkg_all)
