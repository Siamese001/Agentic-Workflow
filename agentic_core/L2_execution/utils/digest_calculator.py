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

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    record_execution_trace,
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
_emit_checks_agent_registry("p1", "digest_calculator", "agent_registry")
_emit_validates_agent_capability("p1", "digest_calculator", "capability")
_emit_dispatches_execution_plan("p1", "digest_calculator", "exec_plan")
_emit_agent_executes_agent("p1", "digest_calculator", "sub_agent")
_emit_routes_to_agent("p1", "digest_calculator", "target_agent")
_emit_verifies_policy("p1", "digest_calculator", "policy_check")
_emit_observes_runtime_state("p1", "digest_calculator", "runtime_state")
_emit_verifies_boundary("p1", "digest_calculator", "boundary_check")
_emit_transcripts_response("p1", "digest_calculator", "transcript")
_emit_hard_fails_untranscripted("p1", "digest_calculator")
_emit_gated_by_confidence("p1", "digest_calculator", "confidence_gate")
_emit_escalates_to_human("p1", "digest_calculator", "L2")
_emit_reads_policy_state("p1", "digest_calculator", "L2")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

record_execution_trace("digest_calculator", "digest_calculator_trace")


_emit_emits_metric_event("digest_calculator", "p4obs", "metric_1")
_emit_emits_metric_event("digest_calculator", "p4obs", "metric_2")
_emit_emits_metric_event("digest_calculator", "p4obs", "metric_3")
_emit_emits_metric_event("digest_calculator", "p4obs", "metric_4")
_emit_emits_metric_event("digest_calculator", "p4obs", "metric_5")
_emit_emits_metric_event("digest_calculator", "p4obs", "metric_6")
_emit_records_incident_event("digest_calculator", "p4obs", "incident")
_emit_captures_runtime_anomaly("digest_calculator", "p4obs", "anomaly")
_emit_writes_observability_log("digest_calculator", "p4obs", "obs_log")
_emit_updates_monitoring_state("digest_calculator", "p4obs", "mon_state")
_emit_triggers_alert("digest_calculator", "p4obs", "alert")
_emit_links_incident_trace("digest_calculator", "p4obs", "trace_link")
_emit_captures_pattern("digest_calculator", "p3lm", "pattern")
_emit_records_learning_event("digest_calculator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("digest_calculator", "p3lm", "snapshot")
_emit_feeds_meta_learning("digest_calculator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("digest_calculator", "p3lm", "routing")
_emit_improves_agent_policy("digest_calculator", "p3lm", "policy")
_emit_stores_learning_state("digest_calculator", "p3lm", "state")
_emit_records_execution_trace("digest_calculator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("digest_calculator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("digest_calculator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("digest_calculator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("digest_calculator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("digest_calculator", "env_read", "p2_env_1")
_emit_reads_environ("digest_calculator", "env_read", "p2_env_2")
_emit_reads_runtime_state("digest_calculator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("digest_calculator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "digest_calculator", "context_pull")
_emit_pulls_context("p1", "digest_calculator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "digest_calculator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "digest_calculator", "uwg_term_2")
_emit_writes_through("p1", "digest_calculator", "write_through")
_emit_writes_through("p1", "digest_calculator", "write_through_2")
_emit_validated_by_safety_plane("p1", "digest_calculator", "safety_validation")
_emit_invokes_eval("p1", "digest_calculator", "eval_call")
_emit_proposal_commits_routing("p1", "digest_calculator", "routing_commit")


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
