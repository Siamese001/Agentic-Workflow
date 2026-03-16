"""
agentic_core/runtime/boundary_validator.py

Runtime boundary validator for agentic_core.

Provides lightweight runtime assertions that can be placed at module
boundaries to detect and fail-fast on illegal cross-layer imports
that slipped through static analysis.
"""

from __future__ import annotations

import sys

from agentic_core.L0_routing.config.path_constants import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from agentic_core.runtime.sovereignty_exceptions import SovereigntyViolationError

_emit_records_execution_trace("p0", "evidence", "boundary_validator")
_emit_applies_guardrail("p0", "boundary_validator", "p0_governance")
_emit_reads_policy_state("p0", "boundary_validator", "policy_binding")
_emit_snapshots_state("p0", "boundary_validator", "state_snapshot")
emit_replay_key("p0", "boundary_validator")
emit_determinism_digest("p0", "boundary_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_FORBIDDEN_IN_AGENTIC_CORE = frozenset({APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR})


def assert_no_apps_imports(caller_module: str) -> None:
    """Raise SovereigntyViolationError if caller_module imports any apps_* package.

    Call this at the top of any agentic_core module to enforce the boundary
    at import time rather than relying solely on static analysis.
    """
    loaded = set(sys.modules.keys())
    for forbidden in _FORBIDDEN_IN_AGENTIC_CORE:
        if any(m == forbidden or m.startswith(forbidden + ".") for m in loaded):
            raise SovereigntyViolationError(
                f"Module '{caller_module}' loaded while forbidden package '{forbidden}' is present in sys.modules. agentic_core must not depend on apps_* packages."
            )


def validate_layer_direction(
    source_module: str, target_module: str, source_layer: int | None = None, target_layer: int | None = None
) -> None:
    """Raise SovereigntyViolationError if import direction violates layer gravity.

    Higher numeric layer (e.g. L5=5) may import from lower (e.g. L0=0).
    Lower may NOT import from higher (gravity violation).
    """
    if source_layer is None or target_layer is None:
        return
    if source_layer < target_layer:
        raise SovereigntyViolationError(
            f"Layer gravity violation: '{source_module}' (L{source_layer}) imports '{target_module}' (L{target_layer}). Lower layers must not import from higher layers."
        )


def check_runtime_boundaries() -> bool:
    """Scan sys.modules for any agentic_core module that co-loaded apps_* packages.

    Returns True if clean, False (and prints report) if violations found.
    """
    agentic_modules = [m for m in sys.modules if m.startswith("agentic_core")]
    forbidden_loaded = [
        m for m in sys.modules if any(m == f or m.startswith(f + ".") for f in _FORBIDDEN_IN_AGENTIC_CORE)
    ]
    if agentic_modules and forbidden_loaded:
        print("Runtime boundary violations detected:")
        print(f"  agentic_core modules loaded: {len(agentic_modules)}")
        print(f"  Forbidden packages also loaded: {forbidden_loaded}")
        return False
    print("OK: No runtime boundary violations detected")
    return True
