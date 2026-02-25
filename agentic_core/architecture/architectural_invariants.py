"""
Architectural Invariants - Agentic Core

This module defines the explicit architectural invariants that govern the
agentic system's behavior. These invariants are enforced through tests
and runtime checks to maintain system integrity.

DO NOT VIOLATE THESE INVARIANTS WITHOUT EXPLICIT ARCHITECTURE REVIEW.
"""

# =============================================================================
# LAYER SOVEREIGNTY INVARIANTS
# =============================================================================

INVARIANT_LAYER_SOVEREIGNTY = """
L0-L6 Layer Sovereignty Invariant:

- L6 (Observability) must not mutate L2 execution logic
- L6 outputs may inform meta-learning but cannot directly alter routing/safety at runtime
- L0-L6 responsibilities remain strictly separated
- No layer may directly invoke another layer's internal functions
- Layer boundaries must be enforced through explicit interfaces only

Layer Responsibilities:
L0: Maintenance and routing
L1: Cognition and reasoning
L2: Execution and operational control
L3: Orchestration and coordination
L4: State management and persistence
L5: Safety and enforcement
L6: Observability and monitoring
"""

# =============================================================================
# EMBEDDING INVARIANTS
# =============================================================================

INVARIANT_C0_ONLY_EMBEDDINGS = """
C0-Only Embeddings Invariant:

- Embedding retrieval is informational (C0) only
- Embedding outputs cannot:
    - alter tier selection
    - alter routing thresholds
    - alter safety policies
    - alter execution control flow
- Embedding metadata must not be read inside routing/tiering logic
- Embedding results are for context enrichment only, never decision control

C0 Context: Information-only data that may be presented to agents but
cannot influence system control flow or safety decisions.
"""

INVARIANT_EMBEDDING_KILLSWITCH_GLOBAL = """
Global Embedding Kill-Switch Invariant:

- EMBEDDING_ENABLED=false disables all embedding retrieval
- All embedding access must go through embedding_service_factory
- No silent fallback to alternate retrieval
- Kill-switch must be respected at all levels of the system
- Embedding service factory must return disabled service when disabled
- Runtime injection must not attempt retrieval when disabled
"""

# =============================================================================
# GATEWAY TOPOLOGY INVARIANTS
# =============================================================================

INVARIANT_GATEWAY_TOPOLOGY = """
Gateway Topology Invariant:

- SovereignLLMGateway is the sole outbound LLM seam
- It exists as an external enforcement seam relative to L0-L6
- No agent may call provider SDKs directly
- No model literal may exist outside allowlisted modules
- All LLM interactions must pass through the gateway
- Gateway enforces rate limiting, safety, and audit requirements

Allowlisted modules for model literals:
- SovereignLLMGateway
- healing_provider_adapters
"""

# =============================================================================
# REPLAY KEY SCHEMA INVARIANTS
# =============================================================================

INVARIANT_REPLAY_KEY_SCHEMA = """
Replay Key Schema Invariant:

Replay keys must include (where applicable):
- model version
- embedding pack hash
- cutoff
- k
- BLAS implementation
- config version
- engine version
- transcript hash (if execution)
- tier decision (if healing)

Determinism proof must derive from canonical serialization.
All replay keys must be complete and deterministic.
"""

# =============================================================================
# INVARIANT ENFORCEMENT CONSTANTS
# =============================================================================

# Modules allowed to import provider SDKs
ALLOWLISTED_PROVIDER_SDK_MODULES = {
    "SovereignLLMGateway",
    "healing_provider_adapters",
}

# Modules allowed to contain model literals
ALLOWLISTED_MODEL_LITERAL_MODULES = {
    "SovereignLLMGateway",
    "healing_provider_adapters",
}

# Required replay key fields
REQUIRED_REPLAY_KEY_FIELDS = {
    "model_version",
    "embedding_pack_hash",
    "cutoff",
    "k",
    "blas_implementation",
    "config_version",
    "engine_version",
    "transcript_hash",  # conditional: if execution
    "tier_decision",  # conditional: if healing
}

# Environment variable for embedding kill-switch
EMBEDDING_ENABLED_VAR = "EMBEDDING_ENABLED"

# Environment variable for negative control testing
NEGATIVE_CONTROL_TAMPER_VAR = "W0_NEGCTRL_TAMPER"

# =============================================================================
# INVARIANT DIGIT SIGNATURE
# =============================================================================

INVARIANT_DIGEST_PREFIX = "W0-INVARIANT-DIGEST"

# =============================================================================
# INVARIANT VIOLATION EXCEPTIONS
# =============================================================================


class InvariantViolationError(Exception):
    """Raised when an architectural invariant is violated."""

    pass


class LayerSovereigntyViolationError(InvariantViolationError):
    """Raised when layer sovereignty invariant is violated."""

    pass


class EmbeddingInvariantViolationError(InvariantViolationError):
    """Raised when embedding invariants are violated."""

    pass


class GatewayTopologyViolationError(InvariantViolationError):
    """Raised when gateway topology invariant is violated."""

    pass


class ReplayKeySchemaViolationError(InvariantViolationError):
    """Raised when replay key schema invariant is violated."""

    pass
