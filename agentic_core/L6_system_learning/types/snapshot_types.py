"""G-16-10: Deterministic snapshot types for System Learning Meta-Learning Bus.

MetaLearningSnapshot is the canonical input unit for all optimization cycles.
It is immutable, content-addressed, and bitwise deterministic.

Invariants:
  - snapshot_id = SHA-256(canonical_concatenation_of_inputs)
  - Same inputs => same snapshot_id (bitwise identical)
  - No wall-clock time, no randomness
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.interfaces.determinism_types import SemanticClockSnapshot


@dataclass(frozen=True, slots=True)
class MetaLearningSnapshot:
    """Immutable, content-addressed snapshot for one optimization cycle.

    All fields are deterministic. snapshot_id is the SHA-256 of the canonical
    concatenation of all other fields (see snapshot_factory.create_snapshot).

    Fields
    ------
    snapshot_id : str
        SHA-256 hex digest over canonical concatenation of all other fields.
        Computed by snapshot_factory; do not set manually.
    engine_version : str
        Semantic version of the optimization engine (e.g., "1.0.0").
    config_surface_version : str
        Version string identifying the mutable config surface set.
    audit_window_start_utc : int
        Unix timestamp (inclusive) for the audit data window.
    audit_window_end_utc : int
        Unix timestamp (exclusive) for the audit data window.
    telemetry_hash : str
        SHA-256 hex digest of the telemetry data slice bytes.
    policy_config_hash : str
        SHA-256 hex digest of the L4 policy config bytes at snapshot time.
    routing_config_hash : str
        SHA-256 hex digest of the L4 routing config bytes at snapshot time.
    model_config_hash : str
        SHA-256 hex digest of the L4 model config bytes at snapshot time.
    semantic_clock : SemanticClockSnapshot
        Immutable clock reference (no wall-clock time).
    """

    snapshot_id: str
    engine_version: str
    config_surface_version: str
    audit_window_start_utc: int
    audit_window_end_utc: int
    telemetry_hash: str
    policy_config_hash: str
    routing_config_hash: str
    model_config_hash: str
    semantic_clock: SemanticClockSnapshot

    def to_dict(self) -> dict[str, object]:
        """Deterministic serialization (keys sorted alphabetically)."""
        return {
            "audit_window_end_utc": self.audit_window_end_utc,
            "audit_window_start_utc": self.audit_window_start_utc,
            "config_surface_version": self.config_surface_version,
            "engine_version": self.engine_version,
            "model_config_hash": self.model_config_hash,
            "policy_config_hash": self.policy_config_hash,
            "routing_config_hash": self.routing_config_hash,
            "semantic_clock": self.semantic_clock.to_dict(),
            "snapshot_id": self.snapshot_id,
            "telemetry_hash": self.telemetry_hash,
        }
