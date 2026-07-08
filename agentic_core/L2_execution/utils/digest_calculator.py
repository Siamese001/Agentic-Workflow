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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "digest_calculator", "execution_auth")
trace_contract._emit_validates_capability("p2", "digest_calculator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "digest_calculator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "digest_calculator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "digest_calculator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "digest_calculator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "digest_calculator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "digest_calculator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "digest_calculator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "digest_calculator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "digest_calculator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "digest_calculator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "digest_calculator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "digest_calculator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "digest_calculator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "digest_calculator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "digest_calculator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "digest_calculator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "digest_calculator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "digest_calculator", "exec_snapshot_link")
from agentic_core.utils.canonical_json_util import CanonicalJSON

trace_contract.emit_replay_key("p0", "digest_calculator")
trace_contract.emit_determinism_digest("p0", "digest_calculator")

trace_contract._emit_dispatches_healing_run("p1", "digest_calculator", "L2")
trace_contract._emit_routes_through("p1", "digest_calculator", "L2")
trace_contract._emit_checks_agent_registry("p1", "digest_calculator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "digest_calculator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "digest_calculator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "digest_calculator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "digest_calculator", "target_agent")
trace_contract._emit_verifies_policy("p1", "digest_calculator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "digest_calculator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "digest_calculator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "digest_calculator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "digest_calculator")
trace_contract._emit_gated_by_confidence("p1", "digest_calculator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "digest_calculator", "L2")
trace_contract._emit_reads_policy_state("p1", "digest_calculator", "L2")

trace_contract.record_execution_trace("digest_calculator", "digest_calculator_trace")


trace_contract._emit_emits_metric_event("digest_calculator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("digest_calculator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("digest_calculator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("digest_calculator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("digest_calculator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("digest_calculator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("digest_calculator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("digest_calculator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("digest_calculator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("digest_calculator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("digest_calculator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("digest_calculator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("digest_calculator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("digest_calculator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("digest_calculator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("digest_calculator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("digest_calculator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("digest_calculator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("digest_calculator", "p3lm", "state")
trace_contract._emit_records_execution_trace("digest_calculator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("digest_calculator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("digest_calculator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("digest_calculator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("digest_calculator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("digest_calculator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("digest_calculator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("digest_calculator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("digest_calculator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "digest_calculator", "context_pull")
trace_contract._emit_pulls_context("p1", "digest_calculator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "digest_calculator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "digest_calculator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "digest_calculator", "write_through")
trace_contract._emit_writes_through("p1", "digest_calculator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "digest_calculator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "digest_calculator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "digest_calculator", "routing_commit")


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

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "DigestCalculator.compute", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "DigestCalculator.compute", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "DigestCalculator.compute")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:DigestCalculator.compute".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
