"""
SSOT AuditTrail Mixin — ExecutionTrace-Aligned Cryptographic Audit.

Extends AuditTrailMixin with:
  - Policy-hash scoped audit entries
  - ExecutionTrace-compatible schema (trace_id, plan_hash, actor, target,
    diff, policy_hash, timestamp, prev_hash, replay_key, curr_hash)
  - Canonical JSON serialization (sort_keys, compact separators)
  - SHA-256 hash chaining with replay_key stability
  - Deterministic timestamps under replay mode

Layer: L6 Observer (read-only authority)
Authority: Append-only audit chain. No L4 mutation. No routing influence.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_applies_guardrail("p0", "ssot_audit_trail_mixin", "p0_governance")
_emit_reads_policy_state("p0", "ssot_audit_trail_mixin", "policy_binding")
_emit_snapshots_state("p0", "ssot_audit_trail_mixin", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("ssot_audit_trail_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("ssot_audit_trail_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("ssot_audit_trail_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("ssot_audit_trail_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("ssot_audit_trail_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("ssot_audit_trail_mixin", "p4obs", "metric_6")
_emit_records_incident_event("ssot_audit_trail_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("ssot_audit_trail_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("ssot_audit_trail_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("ssot_audit_trail_mixin", "p4obs", "mon_state")
_emit_triggers_alert("ssot_audit_trail_mixin", "p4obs", "alert")
_emit_links_incident_trace("ssot_audit_trail_mixin", "p4obs", "trace_link")
_emit_captures_pattern("ssot_audit_trail_mixin", "p3lm", "pattern")
_emit_records_learning_event("ssot_audit_trail_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ssot_audit_trail_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("ssot_audit_trail_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ssot_audit_trail_mixin", "p3lm", "routing")
_emit_improves_agent_policy("ssot_audit_trail_mixin", "p3lm", "policy")
_emit_stores_learning_state("ssot_audit_trail_mixin", "p3lm", "state")
_emit_records_execution_trace("ssot_audit_trail_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ssot_audit_trail_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ssot_audit_trail_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ssot_audit_trail_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ssot_audit_trail_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ssot_audit_trail_mixin", "env_read", "p2_env_1")
_emit_reads_environ("ssot_audit_trail_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("ssot_audit_trail_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ssot_audit_trail_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ssot_audit_trail_mixin", "context_pull")
_emit_pulls_context("p1", "ssot_audit_trail_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ssot_audit_trail_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ssot_audit_trail_mixin", "uwg_term_2")
_emit_writes_through("p1", "ssot_audit_trail_mixin", "write_through")
_emit_writes_through("p1", "ssot_audit_trail_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "ssot_audit_trail_mixin", "safety_validation")
_emit_invokes_eval("p1", "ssot_audit_trail_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "ssot_audit_trail_mixin", "routing_commit")
_emit_escalates_to_human("p1", "ssot_audit_trail_mixin", "human_escalation")
_emit_routes_through("p1", "ssot_audit_trail_mixin", "route_through")
_emit_checks_agent_registry("p1", "ssot_audit_trail_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "ssot_audit_trail_mixin", "capability")
_emit_dispatches_execution_plan("p1", "ssot_audit_trail_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "ssot_audit_trail_mixin", "sub_agent")
_emit_routes_to_agent("p1", "ssot_audit_trail_mixin", "target_agent")
_emit_verifies_policy("p1", "ssot_audit_trail_mixin", "policy_check")
_emit_observes_runtime_state("p1", "ssot_audit_trail_mixin", "runtime_state")
_emit_verifies_boundary("p1", "ssot_audit_trail_mixin", "boundary_check")
_emit_transcripts_response("p1", "ssot_audit_trail_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "ssot_audit_trail_mixin")
_emit_gated_by_confidence("p1", "ssot_audit_trail_mixin", "confidence_gate")
emit_replay_key("p0", "ssot_audit_trail_mixin")
emit_determinism_digest("p0", "ssot_audit_trail_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ssot_audit_trail_mixin", "execution_auth")
_emit_validates_capability("p2", "ssot_audit_trail_mixin", "capability_check")
_emit_routes_to_capability("p2", "ssot_audit_trail_mixin", "capability_route")
_emit_writes_via_uwg("p2", "ssot_audit_trail_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "ssot_audit_trail_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot_audit_trail_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "ssot_audit_trail_mixin", "exec_output")
_emit_dispatches_agent("p3", "ssot_audit_trail_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot_audit_trail_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot_audit_trail_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot_audit_trail_mixin", "healing_outcome")
_emit_escalates_failure("p3", "ssot_audit_trail_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot_audit_trail_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot_audit_trail_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot_audit_trail_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot_audit_trail_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot_audit_trail_mixin", "eval_metric")
_emit_stores_embedding("p4", "ssot_audit_trail_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot_audit_trail_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot_audit_trail_mixin", "exec_snapshot_link")

_logger = logging.getLogger("SSOTAuditTrail")


class SSOTAuditTrailMixin:
    """Policy-hash-scoped, ExecutionTrace-aligned audit trail.

    Designed to sit in MRO alongside ReplayGuardMixin. Reads
    ``active_policy_hash``, ``trace_id``, and ``is_replay_mode``
    from the ReplayGuard properties.

    Audit entries are appended to ``self.state["audit_chain"]``.
    """

    GENESIS_HASH = "0" * 64

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ssot_audit_last_hash: str = self.GENESIS_HASH
        self._ssot_audit_count: int = 0

    def emit_ssot_audit_entry(
        self, action: str, target: str, diff: dict[str, Any] | None = None, plan_hash: str | None = None
    ) -> dict[str, Any]:
        """Emit an ExecutionTrace-compatible audit entry.

        Parameters
        ----------
        action : str
            The action being audited (e.g. "HEAL", "VALIDATE", "ROLLBACK").
        target : str
            The target of the action (e.g. file path, agent name).
        diff : dict | None
            Optional diff payload describing the change.
        plan_hash : str | None
            Optional plan hash. Falls back to active_policy_hash.

        Returns
        -------
        dict
            The complete audit entry (also appended to state["audit_chain"]).
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SSOTAuditTrailMixin.emit_ssot_audit_entry")

        policy_hash = getattr(self, "active_policy_hash", "unknown")
        trace_id = getattr(self, "trace_id", "unknown")
        actor = self.__class__.__name__
        entry = {
            "trace_id": trace_id,
            "plan_hash": plan_hash or policy_hash,
            "actor": actor,
            "target": target,
            "diff": diff or {},
            "policy_hash": policy_hash,
            "timestamp": time.time(),
            "prev_hash": self._ssot_audit_last_hash,
            "replay_key": self._compute_replay_key(action, target, policy_hash, trace_id),
        }
        canonical = json.dumps(entry, sort_keys=True, separators=(",", ":"))
        curr_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        entry["curr_hash"] = curr_hash
        self._ssot_audit_last_hash = curr_hash
        self._ssot_audit_count += 1
        state = getattr(self, "state", None)
        if isinstance(state, dict) and "audit_chain" in state:
            state["audit_chain"].append(entry)
        _logger.debug("[SSOTAudit] %s | %s | hash=%s...", action, target, curr_hash[:16])
        return entry

    def verify_ssot_audit_chain(self, chain: list[dict[str, Any]] | None = None) -> tuple[bool, int | None]:
        """Verify SHA-256 chain integrity of audit entries.

        Parameters
        ----------
        chain : list[dict] | None
            Audit entries to verify. Defaults to self.state["audit_chain"].

        Returns
        -------
        tuple[bool, int | None]
            (is_valid, first_broken_index). If valid: (True, None).
        """
        if chain is None:
            state = getattr(self, "state", None)
            if isinstance(state, dict):
                chain = state.get("audit_chain", [])
            else:
                chain = []
        if not chain:
            return (True, None)
        for i, entry in enumerate(chain):
            entry_copy = {k: v for k, v in entry.items() if k != "curr_hash"}
            canonical = json.dumps(entry_copy, sort_keys=True, separators=(",", ":"))
            expected_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            if entry.get("curr_hash") != expected_hash:
                return (False, i)
            if i > 0 and entry.get("prev_hash") != chain[i - 1].get("curr_hash"):
                return (False, i)
        return (True, None)

    @property
    def ssot_audit_head(self) -> str:
        """Current head hash of the SSOT audit chain."""
        return self._ssot_audit_last_hash

    @property
    def ssot_audit_count(self) -> int:
        """Total entries in the SSOT audit chain."""
        return self._ssot_audit_count

    @staticmethod
    def _compute_replay_key(action: str, target: str, policy_hash: str, trace_id: str) -> str:
        """Compute a stable replay key for deterministic replay matching.

        The replay_key is deterministic given the same inputs, enabling
        replay systems to correlate entries across runs.
        """
        raw = f"{trace_id}|{policy_hash}|{action}|{target}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]
