"""Guardian Enforcement Exceptions — Zero-dependency module to break circular imports.

This module contains ONLY the guardian enforcement exception classes and check functions,
with no imports from other agentic_core modules. This breaks the circular
dependency between guardian_contract_types and enforcement modules.

SSOT for guardian enforcement exception types consumed by:
- ExecutionGateway (enforcement)
- RuntimeGuard (enforcement)
- GuardianContractTypes (types)
- All guardian-related tests
"""

from __future__ import annotations

import os


class V15EnforcementError(RuntimeError):
    """Raised when a V15 invariant is violated in enforced mode."""


class V15SoftFailAbort(Exception):
    """Raised internally when SOFT_FAIL mode detects a contract violation.

    Caught by V15ExecutionGateway.execute() to produce a structured
    GatewayResult with success=False instead of crashing the process.
    """


class V15HardFailAbort(Exception):
    """Raised when HARD_FAIL mode detects a contract violation.

    Single deterministic exception type for all HARD_FAIL aborts.
    Propagates out of V15ExecutionGateway.execute() uncaught —
    callers must handle or let the process terminate.
    """


def is_v15_enforced() -> bool:
    """Return True when V15 enforcement is active (fail-closed: default ON).

    Unset / absent env var → True (fail-closed production default).
    Explicit opt-out: "0", "false", "no", "off" (case-insensitive) → False.
    Explicit opt-in: "1", "true", "yes", "on", "log", "soft" (case-insensitive) → True.
    Any other value → ValueError (deterministic misconfig rejection).
    Use ``is_v15_hard_fail()`` / ``is_v15_soft_fail()`` for mode selection.
    """
    raw = os.environ.get("V15_ENFORCEMENT")
    if raw is None:
        return True
    normalized = raw.strip().lower()
    if normalized in ("0", "false", "no", "off"):
        return False
    if normalized in ("1", "true", "yes", "on", "log", "soft"):
        return True
    raise ValueError(
        f"V15_ENFORCEMENT={raw!r} is not a recognized value. "
        f"Use: 1/true/yes/on/log/soft (enabled) or 0/false/no/off (disabled).",
    )


def is_v15_hard_fail() -> bool:
    """Return True only when V15_ENFORCEMENT demands hard blocking on violation.

    Hard-fail values: "1", "true", "yes" (case-insensitive).
    "log" and "soft" return False — violations are logged, not blocked.
    """
    return os.environ.get("V15_ENFORCEMENT", "").strip().lower() in ("1", "true", "yes")


def is_v15_soft_fail() -> bool:
    """Return True when V15_ENFORCEMENT is set to SOFT_FAIL mode.

    SOFT_FAIL mode: violations produce a controlled abort (structured failure
    return via ``V15SoftFailAbort``) without crashing the process.
    Only the literal value "soft" (case-insensitive) activates this mode.
    """
    return os.environ.get("V15_ENFORCEMENT", "").strip().lower() == "soft"


__all__ = [
    "V15EnforcementError",
    "V15SoftFailAbort",
    "V15HardFailAbort",
    "is_v15_enforced",
    "is_v15_hard_fail",
    "is_v15_soft_fail",
]
