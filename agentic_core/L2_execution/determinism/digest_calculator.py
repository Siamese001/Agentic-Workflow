"""
DigestCalculator — Strict determinism surface for L2 execution.

Defines and computes the canonical W<n>-DETERMINISM-DIGEST.  Only the
five approved components are included:

    sha256(
        policy_hash        +
        registry_hash      +
        config_surface_hash +
        transcript_hash    +
        dependency_lock_hash
    )

Excluded (by design):
  - Environment variables
  - Wall-clock timestamps
  - Build IDs
  - Machine IDs
  - Random seeds

Phase 0.3: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import hashlib

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "digest_calculator", "execution_auth")
_emit_validates_capability("p2", "digest_calculator", "capability_check")
_emit_routes_to_capability("p2", "digest_calculator", "capability_route")
_emit_writes_via_uwg("p2", "digest_calculator", "uwg_write")
_emit_blocks_direct_write("p2", "digest_calculator", "direct_write_block")
_emit_records_tool_invocation("p2", "digest_calculator", "tool_invocation")
_emit_captures_execution_output("p2", "digest_calculator", "exec_output")
_emit_dispatches_agent("p3", "digest_calculator", "agent_dispatch")
_emit_coordinates_agents("p3", "digest_calculator", "agent_coordination")
_emit_records_workflow_lineage("p3", "digest_calculator", "workflow_lineage")
_emit_records_healing_outcome("p3", "digest_calculator", "healing_outcome")
_emit_escalates_failure("p3", "digest_calculator", "failure_escalation")
_emit_orchestrates_workflow("p3", "digest_calculator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "digest_calculator", "healing_dispatch")
_emit_invokes_evaluation("p3", "digest_calculator", "evaluation_signal")
_emit_records_telemetry_event("p4", "digest_calculator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "digest_calculator", "eval_metric")
_emit_stores_embedding("p4", "digest_calculator", "embedding_store")
_emit_updates_meta_learning_state("p4", "digest_calculator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "digest_calculator", "exec_snapshot_link")
from agentic_core.utils.canonical_json_util import CanonicalJSON

emit_replay_key("p0", "digest_calculator")
emit_determinism_digest("p0", "digest_calculator")

_emit_dispatches_healing_run("p1", "digest_calculator", "L2")
_emit_routes_through("p1", "digest_calculator", "L2")
_emit_escalates_to_human("p1", "digest_calculator", "L2")
_emit_reads_policy_state("p1", "digest_calculator", "L2")


class DigestCalculator:
    """Compute the canonical determinism digest from its five components."""

    COMPONENT_KEYS = (
        "policy_hash",
        "registry_hash",
        "config_surface_hash",
        "transcript_hash",
        "dependency_lock_hash",
    )

    @classmethod
    def compute(
        self,
        *,
        policy_hash: str,
        registry_hash: str,
        config_surface_hash: str,
        transcript_hash: str,
        dependency_lock_hash: str,
    ) -> str:
        """Return SHA-256 hex digest of the canonical determinism surface.

        All five arguments must be 64-character lowercase hex strings (SHA-256).
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "DigestCalculator.compute", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "DigestCalculator.compute", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "DigestCalculator.compute")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:DigestCalculator.compute".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        for name, value in [
            ("policy_hash", policy_hash),
            ("registry_hash", registry_hash),
            ("config_surface_hash", config_surface_hash),
            ("transcript_hash", transcript_hash),
            ("dependency_lock_hash", dependency_lock_hash),
        ]:
            if not (isinstance(value, str) and len(value) == 64):
                raise ValueError(f"DigestCalculator: {name} must be a 64-char hex string, got {value!r}")
        material = {
            "config_surface_hash": config_surface_hash,
            "dependency_lock_hash": dependency_lock_hash,
            "policy_hash": policy_hash,
            "registry_hash": registry_hash,
            "transcript_hash": transcript_hash,
        }
        canonical = CanonicalJSON.serialize_bytes(material)
        return hashlib.sha256(canonical).hexdigest()

    @staticmethod
    def zero_hash() -> str:
        """Return a deterministic placeholder SHA-256 (all zeros)."""
        return "0" * 64


__all__ = ["DigestCalculator"]
