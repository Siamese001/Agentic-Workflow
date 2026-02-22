"""G-16-11: Deterministic snapshot factory for System Learning Meta-Learning Bus.

create_snapshot() is the sole entry point for producing MetaLearningSnapshot
instances. It is bitwise deterministic: same inputs => same snapshot_id.

Invariants:
  - MUST NOT read wall-clock time or timezone data.
  - MUST NOT use randomness.
  - snapshot_id = SHA-256(canonical_concatenation) using b"\\x1f" as delimiter.
  - Canonical concatenation order (strict):
      engine_version, config_surface_version, window_start, window_end,
      telemetry_hash, policy_hash, routing_hash, model_hash, semantic_clock_hash
"""

from __future__ import annotations

import hashlib

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from system_learning.enforcement.authority_invariants import (
    AuthorityContext,
    assert_zero_execution_authority,
)
from system_learning.types.snapshot_types import MetaLearningSnapshot

# Canonical delimiter between segments in snapshot_id computation.
_SEGMENT_DELIMITER: bytes = b"\x1f"


def _sha256_hex(data: bytes) -> str:
    """Return SHA-256 hex digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def create_snapshot(
    *,
    engine_version: str,
    config_surface_version: str,
    audit_window_start_utc: int,
    audit_window_end_utc: int,
    telemetry_bytes: bytes,
    policy_config_bytes: bytes,
    routing_config_bytes: bytes,
    model_config_bytes: bytes,
    semantic_clock_bytes: bytes,
    semantic_clock: SemanticClockSnapshot,
) -> MetaLearningSnapshot:
    """Create a deterministic, immutable MetaLearningSnapshot.

    Parameters
    ----------
    engine_version : str
        Semantic version of the optimization engine (e.g., "1.0.0").
    config_surface_version : str
        Version string identifying the mutable config surface set.
    audit_window_start_utc : int
        Unix timestamp (inclusive) for the audit data window.
    audit_window_end_utc : int
        Unix timestamp (exclusive) for the audit data window.
    telemetry_bytes : bytes
        Raw bytes of the telemetry data slice. Hashed deterministically.
    policy_config_bytes : bytes
        Canonical bytes of L4 policy config at snapshot time.
    routing_config_bytes : bytes
        Canonical bytes of L4 routing config at snapshot time.
    model_config_bytes : bytes
        Canonical bytes of L4 model config at snapshot time.
    semantic_clock_bytes : bytes
        Canonical bytes of the semantic clock snapshot.
    semantic_clock : SemanticClockSnapshot
        Immutable clock reference embedded in the snapshot.

    Returns
    -------
    MetaLearningSnapshot
        Frozen, content-addressed snapshot.

    Raises
    ------
    ValueError
        If audit_window_start_utc >= audit_window_end_utc.
    AuthorityViolation
        If called in an execution or activation context (fail-closed guard).
    """
    # Authority guard: snapshot creation is READ/WRITE to versioned store only.
    _ctx = AuthorityContext(
        caller_layer="system_learning.snapshots.snapshot_factory",
        operation="create_snapshot",
        target="l4_versioned_store",
        mode="WRITE",
    )
    assert_zero_execution_authority(_ctx)

    # Validate window ordering.
    if audit_window_start_utc >= audit_window_end_utc:
        raise ValueError(
            f"INVALID_AUDIT_WINDOW: start ({audit_window_start_utc}) must be < end ({audit_window_end_utc})"
        )

    # Compute per-input hashes.
    telemetry_hash = _sha256_hex(telemetry_bytes)
    policy_config_hash = _sha256_hex(policy_config_bytes)
    routing_config_hash = _sha256_hex(routing_config_bytes)
    model_config_hash = _sha256_hex(model_config_bytes)
    semantic_clock_hash = _sha256_hex(semantic_clock_bytes)

    # Compute snapshot_id: SHA-256 over canonical concatenation.
    # Strict order: engine_version, config_surface_version, window_start,
    # window_end, telemetry_hash, policy_hash, routing_hash, model_hash,
    # semantic_clock_hash.
    segments: list[bytes] = [
        engine_version.encode("utf-8"),
        config_surface_version.encode("utf-8"),
        str(audit_window_start_utc).encode("utf-8"),
        str(audit_window_end_utc).encode("utf-8"),
        telemetry_hash.encode("utf-8"),
        policy_config_hash.encode("utf-8"),
        routing_config_hash.encode("utf-8"),
        model_config_hash.encode("utf-8"),
        semantic_clock_hash.encode("utf-8"),
    ]
    canonical_bytes = _SEGMENT_DELIMITER.join(segments)
    snapshot_id = _sha256_hex(canonical_bytes)

    return MetaLearningSnapshot(
        snapshot_id=snapshot_id,
        engine_version=engine_version,
        config_surface_version=config_surface_version,
        audit_window_start_utc=audit_window_start_utc,
        audit_window_end_utc=audit_window_end_utc,
        telemetry_hash=telemetry_hash,
        policy_config_hash=policy_config_hash,
        routing_config_hash=routing_config_hash,
        model_config_hash=model_config_hash,
        semantic_clock=semantic_clock,
    )
