"""G-16-19: RAG optimizer — proposal-only optimizer for RAG parameters.

Proposes changes to RAG parameters based on metrics, enforcing:
  - Allowlist constraints (only allowed surfaces)
  - Bounds + max-delta enforcement
  - Cooldown + sample-size dampening
  - Deterministic inputs only (no wall-clock)
  - Proposal-only (no activation)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from system_learning.constraints.delta_enforcer import validate_surface_change
from system_learning.validators.dampening import (
    CooldownPolicy,
    SampleSizePolicy,
    assert_cooldown_ok,
    assert_min_sample_size,
)

_emit_applies_guardrail("p0", "rag_optimizer", "p0_governance")
_emit_reads_policy_state("p0", "rag_optimizer", "policy_binding")
_emit_snapshots_state("p0", "rag_optimizer", "state_snapshot")
emit_replay_key("p0", "rag_optimizer")
emit_determinism_digest("p0", "rag_optimizer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# =============================================================================
# ChangePackage (Minimal Implementation for Phase 3)
# =============================================================================


@dataclass(frozen=True, slots=True)
class RAGChangePackage:
    """Immutable ChangePackage for RAG parameter changes.

    Fields
    ------
    surface_name : str
        The config surface being changed.
    old_value : int
        The current value.
    new_value : int
        The proposed new value.
    justification : str
        Rationale for the change.
    snapshot_id : str
        The snapshot this proposal is based on.
    """

    surface_name: str
    old_value: int
    new_value: int
    justification: str
    snapshot_id: str

    def canonical_bytes(self) -> bytes:
        """Return deterministic canonical byte representation."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RAGChangePackage.canonical_bytes")

        # Canonical concatenation with delimiter
        parts = [
            self.surface_name.encode("utf-8"),
            str(self.old_value).encode("utf-8"),
            str(self.new_value).encode("utf-8"),
            self.justification.encode("utf-8"),
            self.snapshot_id.encode("utf-8"),
        ]
        return b"\x1f".join(parts)

    def content_hash(self) -> str:
        """Return SHA-256 hash of canonical bytes."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


# =============================================================================
# RAG Optimizer
# =============================================================================


def propose_rag_param_changes(
    snapshot_id: str,
    metrics: dict[str, float],
    current_config: dict[str, int],
    now_utc: int,
    history: dict[str, int],
    cooldown_policy: CooldownPolicy,
    sample_policy: SampleSizePolicy,
    mean_cosine_similarity: float | None = None,
) -> RAGChangePackage | None:
    """Propose RAG parameter changes based on metrics.

    Proposal-only: does NOT activate or commit. Returns a ChangePackage
    that can be committed via Phase 2 version store.

    Parameters
    ----------
    snapshot_id : str
        The snapshot this proposal is based on.
    metrics : dict[str, float]
        Observed metrics (e.g., {"retrieval_precision": 0.65}).
    current_config : dict[str, int]
        Current RAG parameter values.
    now_utc : int
        Current time (injected, not wall-clock).
    history : dict[str, int]
        Last update timestamps and observation counts per surface.
        Format: {"retrieval_top_k_last_update": 1700000000,
                 "retrieval_top_k_n_obs": 2000}
    cooldown_policy : CooldownPolicy
        Cooldown policy to enforce.
    sample_policy : SampleSizePolicy
        Sample size policy to enforce.

    Returns
    -------
    RAGChangePackage | None
        Proposed change, or None if no change needed or dampening violated.

    Raises
    ------
    ConstraintViolation
        If proposed change violates constraints.
    """
    # Example: tune retrieval_top_k based on retrieval_precision
    surface_name = "retrieval_top_k"
    retrieval_precision = metrics.get("retrieval_precision", 0.0)
    current_value = current_config.get(surface_name, 10)

    # Check dampening policies
    last_update = history.get(f"{surface_name}_last_update", 0)
    n_obs = history.get(f"{surface_name}_n_obs", 0)

    try:
        assert_cooldown_ok(last_update, now_utc, cooldown_policy)
        assert_min_sample_size(n_obs, sample_policy)
    except (ValueError, AssertionError) as e:
        # Dampening violated - no proposal
        logger.debug(f"Dampening check failed: {e}")
        return None

    # Heuristic now includes semantic quality signal
    justification_parts = [f"retrieval_precision={retrieval_precision:.2f}"]
    proposed_value = current_value

    if mean_cosine_similarity is not None:
        justification_parts.append(f"mean_cosine_similarity={mean_cosine_similarity:.2f}")
        if mean_cosine_similarity < 0.65:
            proposed_value = min(current_value + 2, 20)
        elif mean_cosine_similarity > 0.85 and retrieval_precision > 0.85:
            proposed_value = max(current_value - 2, 3)

    if proposed_value == current_value:  # If semantic signal didn't trigger a change, check precision
        if retrieval_precision < 0.70:
            proposed_value = min(current_value + 2, 20)
        elif retrieval_precision > 0.85:
            proposed_value = max(current_value - 2, 3)

    if proposed_value == current_value:
        return None

    # Validate constraint
    validate_surface_change(surface_name, current_value, proposed_value)

    # Create proposal
    justification = ", ".join(justification_parts) + ", adjusting top_k"
    return RAGChangePackage(
        surface_name=surface_name,
        old_value=current_value,
        new_value=proposed_value,
        justification=justification,
        snapshot_id=snapshot_id,
    )
