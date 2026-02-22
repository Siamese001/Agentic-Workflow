"""G-16-15: Config surface allowlists and bounds for System Learning optimization.

Defines exhaustive allowlisted tunables with:
  - Bounds (min/max)
  - Max delta per cycle
  - Type constraints
  - Forbidden surfaces (tool/file scope expansion, safety relaxation)

All constraints are frozen dataclasses (immutable).
"""

from __future__ import annotations

from dataclasses import dataclass


# =============================================================================
# Constraint Types
# =============================================================================


@dataclass(frozen=True, slots=True)
class FloatConstraint:
    """Constraint for float-valued config parameters.

    Fields
    ------
    min_value : float
        Minimum allowed value (inclusive).
    max_value : float
        Maximum allowed value (inclusive).
    max_delta_per_cycle : float
        Maximum absolute change allowed per optimization cycle.
    """

    min_value: float
    max_value: float
    max_delta_per_cycle: float


@dataclass(frozen=True, slots=True)
class IntConstraint:
    """Constraint for int-valued config parameters.

    Fields
    ------
    min_value : int
        Minimum allowed value (inclusive).
    max_value : int
        Maximum allowed value (inclusive).
    max_delta_per_cycle : int
        Maximum absolute change allowed per optimization cycle.
    """

    min_value: int
    max_value: int
    max_delta_per_cycle: int


@dataclass(frozen=True, slots=True)
class PointerConstraint:
    """Constraint for pointer-valued config parameters (e.g., model names).

    Fields
    ------
    allowlist : frozenset[str]
        Exhaustive set of allowed pointer values.
    """

    allowlist: frozenset[str]


# =============================================================================
# L0 Routing Thresholds
# =============================================================================

L0_ROUTING_CONSTRAINTS: dict[str, FloatConstraint] = {
    "escalation_threshold": FloatConstraint(
        min_value=0.70,
        max_value=0.95,
        max_delta_per_cycle=0.05,
    ),
    "anomaly_routing_threshold": FloatConstraint(
        min_value=0.65,
        max_value=0.85,
        max_delta_per_cycle=0.05,
    ),
}

L0_ROUTING_INT_CONSTRAINTS: dict[str, IntConstraint] = {
    "depth_breaker": IntConstraint(
        min_value=5,
        max_value=20,
        max_delta_per_cycle=2,
    ),
}

# =============================================================================
# RAG Parameters
# =============================================================================

RAG_CONSTRAINTS: dict[str, IntConstraint] = {
    "retrieval_top_k": IntConstraint(
        min_value=3,
        max_value=20,
        max_delta_per_cycle=3,
    ),
    "rerank_top_n": IntConstraint(
        min_value=1,
        max_value=10,
        max_delta_per_cycle=2,
    ),
}

# =============================================================================
# L1 Model Config Pointers
# =============================================================================

L1_MODEL_POINTER_CONSTRAINTS: dict[str, PointerConstraint] = {
    "cognition_model": PointerConstraint(
        allowlist=frozenset({"gpt-4o", "gpt-4o-mini", "claude-3.5-sonnet"}),
    ),
    "embedding_model": PointerConstraint(
        allowlist=frozenset({"text-embedding-3-small", "text-embedding-3-large"}),
    ),
}

# =============================================================================
# L5 Policy Tunables
# =============================================================================

L5_POLICY_INT_CONSTRAINTS: dict[str, IntConstraint] = {
    "token_budget": IntConstraint(
        min_value=500_000,
        max_value=2_000_000,
        max_delta_per_cycle=100_000,
    ),
    "max_k": IntConstraint(
        min_value=5,
        max_value=15,
        max_delta_per_cycle=2,
    ),
    "max_retries": IntConstraint(
        min_value=2,
        max_value=5,
        max_delta_per_cycle=1,
    ),
}

# =============================================================================
# Forbidden Surfaces (Immutable Components)
# =============================================================================

FORBIDDEN_SURFACES: frozenset[str] = frozenset(
    {
        # Tool/file scope expansion forbidden
        "tool_allowlist",
        "file_scope_whitelist",
        # Safety rule removal forbidden
        "guardian_contracts",
        "capability_enforcement",
        "inventory_schema",
        "evidence_hashing",
        "territory_map",
        # Execution path bypass forbidden
        "routing_bypass",
        "execution_shortcut",
        "sandbox_escape",
    }
)

# =============================================================================
# All Allowed Surfaces (Exhaustive Registry)
# =============================================================================

ALLOWED_SURFACES: frozenset[str] = frozenset(
    set(L0_ROUTING_CONSTRAINTS.keys())
    | set(L0_ROUTING_INT_CONSTRAINTS.keys())
    | set(RAG_CONSTRAINTS.keys())
    | set(L1_MODEL_POINTER_CONSTRAINTS.keys())
    | set(L5_POLICY_INT_CONSTRAINTS.keys())
)
