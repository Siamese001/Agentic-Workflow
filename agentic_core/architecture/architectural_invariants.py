"""
Architectural Invariants & Topology Lock — HF Embeddings Edition

This module defines the canonical architectural invariants for the Agentic Workflow system.
These invariants are enforced by governance tests and must never be violated.

Phase 0: Architectural Invariants & Topology Lock
Objective: Formally encode and enforce L0-L6 layer sovereignty, gateway topology,
         C0-only embedding doctrine, and HF embedder pinning with determinism.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Final

# =============================================================================
# LAYER SOVEREIGNTY INVARIANTS
# =============================================================================

INVARIANT_LAYER_SOVEREIGNTY: Final[dict[str, str]] = {
    "description": "L0-L6 layer boundaries must be respected",
    "rules": [
        "L6 (Observability) cannot mutate L2 execution logic",
        "No upward mutation across L0-L6 boundaries",
        "Meta-learning proposals cannot directly alter runtime execution without activation gate",
    ],
    "enforcement": "AST-based layer boundary detection tests",
}

# =============================================================================
# GATEWAY TOPOLOGY INVARIANTS
# =============================================================================

INVARIANT_GATEWAY_TOPOLOGY: Final[dict[str, str]] = {
    "description": "SovereignLLMGateway is the sole outbound LLM seam",
    "rules": [
        "SovereignLLMGateway is the sole outbound LLM seam",
        "It exists external to L0-L6",
        "No agent may call provider SDK directly",
        "No model literals outside allowlisted modules",
    ],
    "enforcement": "Import analysis and literal detection tests",
}

# =============================================================================
# C0-ONLY EMBEDDING DOCTRINE
# =============================================================================

INVARIANT_C0_ONLY_EMBEDDINGS: Final[dict[str, str]] = {
    "description": "Embedding retrieval is informational (C0) only",
    "rules": [
        "Embedding retrieval is informational (C0) only",
        "Embedding outputs cannot alter tier selection",
        "Embedding outputs cannot alter routing thresholds",
        "Embedding outputs cannot alter safety policy",
        "Embedding outputs cannot alter execution flow",
        "Routing/tiering modules must not import embedding metadata types",
    ],
    "enforcement": "Import boundary and usage analysis tests",
}

# =============================================================================
# EMBEDDING PROVIDER PIN INVARIANTS
# =============================================================================

INVARIANT_EMBEDDING_PROVIDER_PIN: Final[dict[str, Any]] = {
    "description": "HF embedder must be pinned to exact specifications",
    "repo": "BAAI/bge-large-en-v1.5",
    "revision": "a2d9d1b65626c9905c821c9a3c5a5aee0f28e8ef",  # Pinned revision SHA
    "tokenizer_revision": "a2d9d1b65626c9905c821c9a3c5a5aee0f28e8ef",  # Same as model revision
    "dtype": "float32",
    "normalize": True,
    "device": "cpu",
    "thread_locks": {"OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"},
    "enforcement": "Configuration validation and runtime verification tests",
}

# =============================================================================
# EMBEDDING KILL-SWITCH GLOBAL INVARIANTS
# =============================================================================

INVARIANT_EMBEDDING_KILLSWITCH_GLOBAL: Final[dict[str, str]] = {
    "description": "Global embedding kill-switch must be respected",
    "rules": [
        "EMBEDDING_ENABLED=false disables all retrieval",
        "All embedding access must go through EmbeddingServiceFactory",
        "No silent fallback to alternate retrieval paths",
    ],
    "enforcement": "Service factory and kill-switch propagation tests",
}

# =============================================================================
# REPLAY KEY SCHEMA COMPLETENESS
# =============================================================================

INVARIANT_REPLAY_KEY_SCHEMA: Final[dict[str, Any]] = {
    "description": "Replay key must include all deterministic fields",
    "required_fields": [
        "embedder_repo",
        "embedder_revision",
        "tokenizer_revision",
        "embedding_dim",
        "dtype",
        "normalize_flag",
        "backend_version",
        "thread_locks_signature",
        "pack_hash",
        "cutoff",
        "k",
        "generation_model_id",
        "routing_tier",  # if healing
        "transcript_hash",  # if execution
    ],
    "enforcement": "Schema completeness validation tests",
}

# =============================================================================
# CANONICAL INVARIANT DIGEST COMPUTATION
# =============================================================================


def compute_invariant_digest() -> str:
    """
    Compute deterministic SHA256 digest over all invariant constants.

    This digest serves as the W0-INVARIANT-DIGEST and must remain
    identical across runs for the same invariant configuration.

    Returns:
        SHA256 hex digest of canonical invariant JSON
    """
    # Create canonical representation of all invariants
    invariants_canonical = {
        "layer_sovereignty": INVARIANT_LAYER_SOVEREIGNTY,
        "gateway_topology": INVARIANT_GATEWAY_TOPOLOGY,
        "c0_only_embeddings": INVARIANT_C0_ONLY_EMBEDDINGS,
        "embedding_provider_pin": INVARIANT_EMBEDDING_PROVIDER_PIN,
        "embedding_killswitch_global": INVARIANT_EMBEDDING_KILLSWITCH_GLOBAL,
        "replay_key_schema": INVARIANT_REPLAY_KEY_SCHEMA,
    }

    # Sort keys for deterministic ordering
    canonical_json = json.dumps(invariants_canonical, sort_keys=True, separators=(",", ":"))

    # Compute SHA256 digest
    digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    return digest


# =============================================================================
# INVARIANT VALIDATION HELPERS
# =============================================================================


def validate_hf_embedder_config(config: dict[str, Any]) -> bool:
    """
    Validate HF embedder configuration against invariant requirements.

    Args:
        config: Embedder configuration dictionary

    Returns:
        True if configuration matches invariants, False otherwise
    """
    required_pin = INVARIANT_EMBEDDING_PROVIDER_PIN

    # Check all required fields match exactly
    required_fields = ["repo", "revision", "tokenizer_revision", "dtype", "normalize", "device"]
    for field in required_fields:
        if config.get(field) != required_pin.get(field):
            return False

    # Check thread locks configuration
    if "thread_locks" not in config:
        return False

    required_locks = required_pin["thread_locks"]
    config_locks = config["thread_locks"]

    for key, value in required_locks.items():
        if config_locks.get(key) != value:
            return False

    return True


def validate_replay_key_completeness(replay_key: dict[str, Any]) -> bool:
    """
    Validate replay key contains all required fields per invariants.

    Args:
        replay_key: Replay key dictionary to validate

    Returns:
        True if all required fields present, False otherwise
    """
    required_fields = INVARIANT_REPLAY_KEY_SCHEMA["required_fields"]

    for field in required_fields:
        if field not in replay_key:
            return False

    return True


# =============================================================================
# MODULE METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = "Phase 0: Architectural Invariants & Topology Lock"
__description__ = "Canonical architectural invariants for Agentic Workflow system"

# Export main invariant constants for external validation
__all__ = [
    "INVARIANT_LAYER_SOVEREIGNTY",
    "INVARIANT_GATEWAY_TOPOLOGY",
    "INVARIANT_C0_ONLY_EMBEDDINGS",
    "INVARIANT_EMBEDDING_PROVIDER_PIN",
    "INVARIANT_EMBEDDING_KILLSWITCH_GLOBAL",
    "INVARIANT_REPLAY_KEY_SCHEMA",
    "compute_invariant_digest",
    "validate_hf_embedder_config",
    "validate_replay_key_completeness",
]
