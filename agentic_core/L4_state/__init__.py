"""
L4 Persistence Layer — Governed runtime persistence with state lifecycle governance.

This layer provides persistence, state management, and lifecycle governance.
No orchestration, execution, or routing logic belongs in this layer.
Only persistence contracts, state lifecycle, and governance are exported.
"""

from enum import Enum
from importlib import import_module

# P3/L4 State Lifecycle Governance exports
from agentic_core.L4_state.utils.lifecycle.lifecycle_policy_applier import (
    StateLifecycleContext,
    apply_state_lifecycle_policy,
    lifecycle_policy_applied,
    lifecycle_transition_recorded,
    query_state_lifecycle,
    record_lifecycle_transition,
    record_state_archival,
    record_state_deletion,
    state_active,
    state_archived,
    state_deleted,
)
from agentic_core.L4_state.utils.lifecycle.state_lifecycle import (
    # Enum values for ADG scanner detection
    ACTIVE,
    ARCHIVED,
    DELETED,
    EXPIRED,
    LONG_TERM,
    MEDIUM_TERM,
    PENDING_DELETION,
    PERMANENT,
    SHORT_TERM,
    STALE,
    LifecyclePolicy,
    LifecycleStatus,
    RetentionClass,
    StateLifecycleError,
    StateLifecycleRecord,
    get_state_lifecycle_registry,
    reset_state_lifecycle_registry,
)


def __getattr__(name: str):
    """Lazily expose heavyweight L4 subpackages on explicit access."""
    if name == "cache":
        return import_module("agentic_core.L4_state.cache")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    # Lifecycle Records
    "StateLifecycleRecord",
    "LifecyclePolicy",
    # Enums
    "LifecycleStatus",
    "RetentionClass",
    # Exception Classes
    "StateLifecycleError",
    # Context Classes
    "StateLifecycleContext",
    # Emission Functions
    "apply_state_lifecycle_policy",
    "record_lifecycle_transition",
    "record_state_archival",
    "record_state_deletion",
    "query_state_lifecycle",
    # Registry Access
    "get_state_lifecycle_registry",
    "reset_state_lifecycle_registry",
    # ADG Edge Emitters
    "lifecycle_policy_applied",
    "lifecycle_transition_recorded",
    "state_archived",
    "state_deleted",
    # Enum values for ADG scanner detection
    "ACTIVE",
    "STALE",
    "EXPIRED",
    "ARCHIVED",
    "PENDING_DELETION",
    "DELETED",
    "SHORT_TERM",
    "MEDIUM_TERM",
    "LONG_TERM",
    "PERMANENT",
]

# Sovereignty assertion: This layer contains NO orchestration or execution logic
# L4 may only persist governed state; orchestration belongs to L3, execution to L2
