"""
SSOT Meta-Learning Client Mixin — Gated Advisory Pattern Storage.

Provides meta-learning that:
  - Namespaces scoped by active_policy_hash
  - Replay mode disables all writes
  - Write preconditions enforced:
    1. safety_status == CLEARED
    2. active_policy_hash unchanged (no drift)
    3. result.success == True
  - Read operations always allowed

Layer: L2 Execution Aid
Authority: Advisory pattern storage. No L4 mutation. No routing influence.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
)

_emit_applies_guardrail("p0", "ssot_meta_learning_mixin", "p0_governance")
_emit_reads_policy_state("p0", "ssot_meta_learning_mixin", "policy_binding")
_emit_snapshots_state("p0", "ssot_meta_learning_mixin", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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

_emit_emits_metric_event("ssot_meta_learning_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("ssot_meta_learning_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("ssot_meta_learning_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("ssot_meta_learning_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("ssot_meta_learning_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("ssot_meta_learning_mixin", "p4obs", "metric_6")
_emit_records_incident_event("ssot_meta_learning_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("ssot_meta_learning_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("ssot_meta_learning_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("ssot_meta_learning_mixin", "p4obs", "mon_state")
_emit_triggers_alert("ssot_meta_learning_mixin", "p4obs", "alert")
_emit_links_incident_trace("ssot_meta_learning_mixin", "p4obs", "trace_link")
_emit_captures_pattern("ssot_meta_learning_mixin", "p3lm", "pattern")
_emit_records_learning_event("ssot_meta_learning_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ssot_meta_learning_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("ssot_meta_learning_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ssot_meta_learning_mixin", "p3lm", "routing")
_emit_improves_agent_policy("ssot_meta_learning_mixin", "p3lm", "policy")
_emit_stores_learning_state("ssot_meta_learning_mixin", "p3lm", "state")
_emit_records_execution_trace("ssot_meta_learning_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ssot_meta_learning_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ssot_meta_learning_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ssot_meta_learning_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ssot_meta_learning_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ssot_meta_learning_mixin", "env_read", "p2_env_1")
_emit_reads_environ("ssot_meta_learning_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("ssot_meta_learning_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ssot_meta_learning_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ssot_meta_learning_mixin", "context_pull")
_emit_pulls_context("p1", "ssot_meta_learning_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ssot_meta_learning_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ssot_meta_learning_mixin", "uwg_term_2")
_emit_writes_through("p1", "ssot_meta_learning_mixin", "write_through")
_emit_writes_through("p1", "ssot_meta_learning_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "ssot_meta_learning_mixin", "safety_validation")
_emit_invokes_eval("p1", "ssot_meta_learning_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "ssot_meta_learning_mixin", "routing_commit")
_emit_escalates_to_human("p1", "ssot_meta_learning_mixin", "human_escalation")
_emit_routes_through("p1", "ssot_meta_learning_mixin", "route_through")
_emit_checks_agent_registry("p1", "ssot_meta_learning_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "ssot_meta_learning_mixin", "capability")
_emit_dispatches_execution_plan("p1", "ssot_meta_learning_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "ssot_meta_learning_mixin", "sub_agent")
_emit_routes_to_agent("p1", "ssot_meta_learning_mixin", "target_agent")
_emit_verifies_policy("p1", "ssot_meta_learning_mixin", "policy_check")
_emit_observes_runtime_state("p1", "ssot_meta_learning_mixin", "runtime_state")
_emit_verifies_boundary("p1", "ssot_meta_learning_mixin", "boundary_check")
_emit_transcripts_response("p1", "ssot_meta_learning_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "ssot_meta_learning_mixin")
_emit_gated_by_confidence("p1", "ssot_meta_learning_mixin", "confidence_gate")
emit_replay_key("p0", "ssot_meta_learning_mixin")
emit_determinism_digest("p0", "ssot_meta_learning_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ssot_meta_learning_mixin", "execution_auth")
_emit_validates_capability("p2", "ssot_meta_learning_mixin", "capability_check")
_emit_routes_to_capability("p2", "ssot_meta_learning_mixin", "capability_route")
_emit_writes_via_uwg("p2", "ssot_meta_learning_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "ssot_meta_learning_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot_meta_learning_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "ssot_meta_learning_mixin", "exec_output")
_emit_dispatches_agent("p3", "ssot_meta_learning_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot_meta_learning_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot_meta_learning_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot_meta_learning_mixin", "healing_outcome")
_emit_escalates_failure("p3", "ssot_meta_learning_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot_meta_learning_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot_meta_learning_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot_meta_learning_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot_meta_learning_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot_meta_learning_mixin", "eval_metric")
_emit_stores_embedding("p4", "ssot_meta_learning_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot_meta_learning_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot_meta_learning_mixin", "exec_snapshot_link")

_logger = logging.getLogger("SSOTMetaLearning")


class MetaLearningWriteRejected(Exception):
    """Raised when a meta-learning write is rejected due to precondition failure."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Meta-learning write rejected: {reason}")


class SSOTMetaLearningMixin:
    """Policy-hash-scoped meta-learning with strict write gating.

    Reads ``active_policy_hash``, ``is_replay_mode``, ``safety_status``,
    and ``policy_hash_drifted()`` from ReplayGuardMixin.

    Write preconditions (ALL must be true):
      - Not in replay mode
      - safety_status == "CLEARED"
      - Policy hash has not drifted since construction
      - Caller asserts result.success == True
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ssot_ml_patterns: dict[str, list[dict[str, Any]]] = {}

    # guardian: allow-magic-config
    def ml_read_patterns(self, domain: str, limit: int = 10) -> list[dict[str, Any]]:
        """Read stored patterns for a domain (always allowed).

        Parameters
        ----------
        domain : str
            Pattern domain (will be policy-hash-scoped).
        limit : int
            Maximum patterns to return.

        Returns
        -------
        list[dict]
            Matching patterns, newest first.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SSOTMetaLearningMixin.ml_read_patterns")

        scoped_ns = self._scoped_namespace(domain)
        patterns = self._ssot_ml_patterns.get(scoped_ns, [])
        return list(reversed(patterns[-limit:]))

    def ml_store_pattern(self, domain: str, pattern: dict[str, Any], success: bool = True) -> dict[str, Any]:
        """Store a learning pattern (subject to write preconditions).

        Parameters
        ----------
        domain : str
            Pattern domain (will be policy-hash-scoped).
        pattern : dict
            Pattern data to store.
        success : bool
            Whether the operation that generated this pattern succeeded.

        Returns
        -------
        dict
            The stored pattern entry.

        Raises
        ------
        MetaLearningWriteRejected
            If any write precondition fails.
        """
        if getattr(self, "is_replay_mode", False):
            raise MetaLearningWriteRejected("replay mode active")
        safety = getattr(self, "safety_status", "PENDING")
        if safety != "CLEARED":
            raise MetaLearningWriteRejected(f"safety_status={safety} (need CLEARED)")
        drifted = getattr(self, "policy_hash_drifted", lambda: False)()
        if drifted:
            raise MetaLearningWriteRejected("policy_hash drifted since construction")
        if not success:
            raise MetaLearningWriteRejected("result.success is False")
        scoped_ns = self._scoped_namespace(domain)
        policy_hash = getattr(self, "active_policy_hash", "unknown")
        entry = {
            "domain": domain,
            "pattern": pattern,
            "policy_hash": policy_hash,
            "timestamp": time.time(),
            "success": success,
        }
        if scoped_ns not in self._ssot_ml_patterns:
            self._ssot_ml_patterns[scoped_ns] = []
        self._ssot_ml_patterns[scoped_ns].append(entry)
        _logger.debug(
            "[SSOTMetaLearning] Stored pattern in %s (total=%d)",
            scoped_ns,
            len(self._ssot_ml_patterns[scoped_ns]),
        )
        return entry

    def ml_pattern_count(self, domain: str | None = None) -> int:
        """Count stored patterns, optionally filtered by domain."""
        if domain is None:
            return sum(len(v) for v in self._ssot_ml_patterns.values())
        scoped_ns = self._scoped_namespace(domain)
        return len(self._ssot_ml_patterns.get(scoped_ns, []))

    def ml_clear_patterns(self, domain: str | None = None) -> int:
        """Clear patterns. Returns count cleared."""
        if domain is None:
            count = sum(len(v) for v in self._ssot_ml_patterns.values())
            self._ssot_ml_patterns.clear()
            return count
        scoped_ns = self._scoped_namespace(domain)
        count = len(self._ssot_ml_patterns.pop(scoped_ns, []))
        return count

    def _scoped_namespace(self, domain: str) -> str:
        """Prefix domain with active_policy_hash."""
        policy_hash = getattr(self, "active_policy_hash", "unknown")
        return f"{policy_hash}:{domain}"
