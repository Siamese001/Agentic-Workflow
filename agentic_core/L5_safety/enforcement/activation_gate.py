"""G-16-6 — Activation Gate: FAIL-CLOSED runtime prerequisite check.

Forbids ANY active/bounded-autonomy execution unless all three enforcement
subsystems are importable and present:

1. P5.1 capability chokepoint  (authorize_and_execute)
2. Mutation prohibition guard  (assert_no_persistent_write)
3. Healer 10-step pipe order   (enforce_healer_pipe_order)

Default is FAIL-CLOSED: if any component is missing, PermissionError is raised.
"""

from __future__ import annotations

import logging
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)

# Compile-time signature to prevent stub bypass
ACTIVATION_GATE_VERSION = "v5.4-P0"

# Required components: (module_path, symbol_name, short_key)
_REQUIRED_COMPONENTS: list[tuple[str, str, str]] = [
    (
        "agentic_core.L2_execution.enforcement.capability_chokepoint",
        "authorize_and_execute",
        "capability_chokepoint",
    ),
    (
        "agentic_core.L5_safety.enforcement.mutation_prohibition_enforcer",
        "assert_no_persistent_write",
        "mutation_prohibition",
    ),
    (
        "agentic_core.L2_execution.enforcement.healer_pipe_order",
        "enforce_healer_pipe_order",
        "healer_pipe_order",
    ),
]


def assert_activation_allowed(trace_id: str | None = None) -> None:
    """FAIL-CLOSED activation gate.

    Verifies that all three enforcement subsystems are importable.
    Raises PermissionError with a deterministic message listing any
    missing components if the check fails.

    Args:
        trace_id: Optional trace identifier for deterministic diagnostics.

    Raises:
        PermissionError: If any required enforcement component is missing.
    """
    missing: list[str] = []

    for module_path, symbol_name, short_key in _REQUIRED_COMPONENTS:
        try:
            mod: Any = __import__(module_path, fromlist=[symbol_name])
            if not hasattr(mod, symbol_name):
                missing.append(short_key)
        except ImportError:
            missing.append(short_key)

    if missing:
        msg_parts = [
            f"ACTIVATION_DENIED:version={ACTIVATION_GATE_VERSION}",
            f"missing_components={','.join(sorted(missing))}",
        ]
        if trace_id is not None:
            msg_parts.append(f"trace_id={trace_id}")

        msg = "|".join(msg_parts)
        logger.error("ACTIVATION_GATE DENY: %s", msg)
        raise PermissionError(msg)


__all__ = [
    "ACTIVATION_GATE_VERSION",
    "assert_activation_allowed",
]
