"""
agentic_core/runtime/boundary_validator.py

Runtime boundary validator for agentic_core.

Provides lightweight runtime assertions that can be placed at module
boundaries to detect and fail-fast on illegal cross-layer imports
that slipped through static analysis.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from agentic_core.runtime.sovereignty_exceptions import SovereigntyViolationError

_FORBIDDEN_IN_AGENTIC_CORE = frozenset({"apps_lic", "apps_rg", "apps_shared"})


def assert_no_apps_imports(caller_module: str) -> None:
    """Raise SovereigntyViolationError if caller_module imports any apps_* package.

    Call this at the top of any agentic_core module to enforce the boundary
    at import time rather than relying solely on static analysis.
    """
    loaded = set(sys.modules.keys())
    for forbidden in _FORBIDDEN_IN_AGENTIC_CORE:
        if any(m == forbidden or m.startswith(forbidden + ".") for m in loaded):
            raise SovereigntyViolationError(
                f"Module '{caller_module}' loaded while forbidden package "
                f"'{forbidden}' is present in sys.modules. "
                f"agentic_core must not depend on apps_* packages."
            )


def validate_layer_direction(
    source_module: str,
    target_module: str,
    source_layer: Optional[int] = None,
    target_layer: Optional[int] = None,
) -> None:
    """Raise SovereigntyViolationError if import direction violates layer gravity.

    Higher numeric layer (e.g. L5=5) may import from lower (e.g. L0=0).
    Lower may NOT import from higher (gravity violation).
    """
    if source_layer is None or target_layer is None:
        return
    if source_layer < target_layer:
        raise SovereigntyViolationError(
            f"Layer gravity violation: '{source_module}' (L{source_layer}) "
            f"imports '{target_module}' (L{target_layer}). "
            f"Lower layers must not import from higher layers."
        )


def check_runtime_boundaries() -> bool:
    """Scan sys.modules for any agentic_core module that co-loaded apps_* packages.

    Returns True if clean, False (and prints report) if violations found.
    """
    agentic_modules = [
        m for m in sys.modules if m.startswith("agentic_core")
    ]
    forbidden_loaded = [
        m
        for m in sys.modules
        if any(
            m == f or m.startswith(f + ".") for f in _FORBIDDEN_IN_AGENTIC_CORE
        )
    ]

    if agentic_modules and forbidden_loaded:
        print("Runtime boundary violations detected:")
        print(f"  agentic_core modules loaded: {len(agentic_modules)}")
        print(f"  Forbidden packages also loaded: {forbidden_loaded}")
        return False

    print("OK: No runtime boundary violations detected")
    return True
