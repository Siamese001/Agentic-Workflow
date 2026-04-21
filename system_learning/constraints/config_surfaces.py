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

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
        allowlist=frozenset({"gpt-4o", "gpt-4o-mini", "claude-sonnet-4-6"}),
    ),
    "embedding_model": PointerConstraint(
        allowlist=frozenset({"text-embedding-3-small", "text-embedding-3-large", "BAAI/bge-m3"}),
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
# Embedding Governance (W1 - Zero-Loss Compliant)
# =============================================================================

EMBEDDING_GOVERNANCE_BOOL: dict[str, bool] = {
    "embedding_enabled": True,  # kill-switch; only L4 may mutate
}

EMBEDDING_GOVERNANCE_POINTER: dict[str, PointerConstraint] = {
    "active_embedder_id": PointerConstraint(
        allowlist=frozenset({"text-embedding-3-large", "text-embedding-3-small", "BAAI/bge-m3"}),
    ),
    "vector_pack_hash": PointerConstraint(
        allowlist=frozenset({"5d94b5b12ec92312d0240be9984ff92b9478f74ed6f1335511a202c5351520d9"}),
    ),  # sealed at deploy
    "normalized_pack_hash": PointerConstraint(
        allowlist=frozenset({""}),  # computed W1 init; placeholder
    ),  # computed W1 init
    "retrieval_backend_mode": PointerConstraint(
        allowlist=frozenset({"LOCAL_FIRST", "EXTERNAL_FIRST", "STRICT_EXTERNAL", "FAIL_CLOSED"}),
    ),
}

EMBEDDING_GOVERNANCE_FLOAT: dict[str, FloatConstraint] = {
    "similarity_cutoff": FloatConstraint(
        min_value=0.5,
        max_value=0.99,
        max_delta_per_cycle=0.05,
    ),
    "retrieval_alpha": FloatConstraint(
        min_value=0.2,
        max_value=0.6,
        max_delta_per_cycle=0.10,
    ),
    "embedding_influence_cap": FloatConstraint(
        min_value=0.05,
        max_value=0.25,
        max_delta_per_cycle=0.05,
    ),  # anchored at 0.25; >0.25 degrades under correlated features
}

EMBEDDING_GOVERNANCE_INT: dict[str, IntConstraint] = {
    "top_k_cap": IntConstraint(
        min_value=3,
        max_value=20,
        max_delta_per_cycle=3,
    ),
    "episodic_ttl_cycles": IntConstraint(
        min_value=1,
        max_value=100,
        max_delta_per_cycle=10,
    ),  # logical time, not wall-clock
    "min_sample_threshold": IntConstraint(
        min_value=5,
        max_value=100,
        max_delta_per_cycle=5,
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
    },
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
    | set(EMBEDDING_GOVERNANCE_BOOL.keys())
    | set(EMBEDDING_GOVERNANCE_POINTER.keys())
    | set(EMBEDDING_GOVERNANCE_FLOAT.keys())
    | set(EMBEDDING_GOVERNANCE_INT.keys()),
)
