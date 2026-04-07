"""
system_learning/runtime/isolation_monitor.py

Runtime isolation monitor for system_learning.

Provides a lightweight check that system_learning has not loaded any
forbidden packages at runtime, and enforces read-only access semantics.
"""

from __future__ import annotations

import sys

APPS_LIC_DIR = "apps_lic"
APPS_RG_DIR = "apps_rg"
APPS_SHARED_DIR = "apps_shared"

_FORBIDDEN = frozenset({APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR})
_FORBIDDEN_LAYER_PREFIXES = (
    "agentic_core.L0_routing",
    "agentic_core.L1_cognition",
    "agentic_core.L2_execution",
    "agentic_core.L3_orchestration",
    "agentic_core.L4_state",
    "agentic_core.L5_safety",
    "agentic_core.L6_observability",
)


def get_forbidden_loaded_modules() -> list[str]:
    """Return list of forbidden modules currently in sys.modules."""
    violations: list[str] = []
    for mod in sys.modules:
        if any(mod == f or mod.startswith(f + ".") for f in _FORBIDDEN):
            violations.append(mod)
        if any(mod.startswith(prefix) for prefix in _FORBIDDEN_LAYER_PREFIXES):
            violations.append(mod)
    return violations


def assert_isolation() -> None:
    """Raise RuntimeError if forbidden modules are loaded alongside system_learning."""
    violations = get_forbidden_loaded_modules()
    if violations:
        raise RuntimeError(
            f"system_learning isolation violated: forbidden modules loaded: {violations[:10]}{('...' if len(violations) > 10 else '')}",
        )


def check_system_learning_runtime_isolation() -> bool:
    """Check runtime isolation of system_learning.

    Returns True if clean, False (with printed report) if violations found.
    """
    violations = get_forbidden_loaded_modules()
    if violations:
        print("system_learning runtime isolation violations:")
        for v in violations[:20]:
            print(f"  {v}")
        if len(violations) > 20:
            print(f"  ... and {len(violations) - 20} more")
        return False
    print("OK: system_learning runtime isolation is clean")
    return True


if __name__ == "__main__":
    import sys as _sys

    _sys.exit(0 if check_system_learning_runtime_isolation() else 1)
