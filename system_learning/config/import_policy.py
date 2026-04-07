"""
system_learning/config/import_policy.py

Defines the import policy for the system_learning package.

system_learning may only import from:
  - itself (system_learning.*)
  - agentic_core.types
  - agentic_core.interfaces
  - agentic_core.classification
  - standard library

Forbidden:
  - apps_lic, apps_rg, apps_shared (downstream domain logic)
  - agentic_core.L* (layer-internal modules — use interfaces shim instead)
"""

from typing import Final

APPS_LIC_DIR: Final[str] = "apps_lic"
APPS_RG_DIR: Final[str] = "apps_rg"
APPS_SHARED_DIR: Final[str] = "apps_shared"

FORBIDDEN_IMPORT_PREFIXES: Final[frozenset] = frozenset(
    {
        APPS_LIC_DIR,
        APPS_RG_DIR,
        APPS_SHARED_DIR,
        "agentic_core.L0_routing",
        "agentic_core.L1_cognition",
        "agentic_core.L2_execution",
        "agentic_core.L3_orchestration",
        "agentic_core.L4_state",
        "agentic_core.L5_safety",
        "agentic_core.L6_observability",
    },
)
ALLOWED_AGENTIC_CORE_PREFIXES: Final[frozenset] = frozenset(
    {"agentic_core.types", "agentic_core.interfaces", "agentic_core.classification", "agentic_core.runtime"},
)
STDLIB_PREFIXES: Final[frozenset] = frozenset(
    {
        "typing",
        "pathlib",
        "sys",
        "os",
        "json",
        "hashlib",
        "dataclasses",
        "enum",
        "abc",
        "collections",
        "functools",
        "itertools",
        "math",
        "re",
        "threading",
        "uuid",
        "__future__",
    },
)
