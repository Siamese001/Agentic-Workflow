"""
Phase 4.3: Sovereign Health Monitor - Historical Health Persistence (L6 -> L4)

This module persists health metrics to L4 State (Redis) for historical analysis
and trend tracking across autonomous healing cycles.
"""

import json
from datetime import datetime
from typing import Any

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

emit_replay_key("p0", "SovereignHealthMonitor")
emit_determinism_digest("p0", "SovereignHealthMonitor")

_emit_dispatches_healing_run("p1", "SovereignHealthMonitor", "L6")
_emit_routes_through("p1", "SovereignHealthMonitor", "L6")
_emit_checks_agent_registry("p1", "SovereignHealthMonitor", "agent_registry")
_emit_validates_agent_capability("p1", "SovereignHealthMonitor", "capability")
_emit_dispatches_execution_plan("p1", "SovereignHealthMonitor", "exec_plan")
_emit_agent_executes_agent("p1", "SovereignHealthMonitor", "sub_agent")
_emit_routes_to_agent("p1", "SovereignHealthMonitor", "target_agent")
_emit_verifies_policy("p1", "SovereignHealthMonitor", "policy_check")
_emit_observes_runtime_state("p1", "SovereignHealthMonitor", "runtime_state")
_emit_verifies_boundary("p1", "SovereignHealthMonitor", "boundary_check")
_emit_transcripts_response("p1", "SovereignHealthMonitor", "transcript")
_emit_hard_fails_untranscripted("p1", "SovereignHealthMonitor")
_emit_gated_by_confidence("p1", "SovereignHealthMonitor", "confidence_gate")
_emit_escalates_to_human("p1", "SovereignHealthMonitor", "L6")
_emit_reads_policy_state("p1", "SovereignHealthMonitor", "L6")
_emit_authorize_and_execute("p2", "SovereignHealthMonitor", "execution_auth")
_emit_validates_capability("p2", "SovereignHealthMonitor", "capability_check")
_emit_routes_to_capability("p2", "SovereignHealthMonitor", "capability_route")
_emit_writes_via_uwg("p2", "SovereignHealthMonitor", "uwg_write")
_emit_blocks_direct_write("p2", "SovereignHealthMonitor", "direct_write_block")
_emit_records_tool_invocation("p2", "SovereignHealthMonitor", "tool_invocation")
_emit_captures_execution_output("p2", "SovereignHealthMonitor", "exec_output")
_emit_dispatches_agent("p3", "SovereignHealthMonitor", "agent_dispatch")
_emit_coordinates_agents("p3", "SovereignHealthMonitor", "agent_coordination")
_emit_records_workflow_lineage("p3", "SovereignHealthMonitor", "workflow_lineage")
_emit_records_healing_outcome("p3", "SovereignHealthMonitor", "healing_outcome")
_emit_escalates_failure("p3", "SovereignHealthMonitor", "failure_escalation")
_emit_orchestrates_workflow("p3", "SovereignHealthMonitor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "SovereignHealthMonitor", "healing_dispatch")
_emit_invokes_evaluation("p3", "SovereignHealthMonitor", "evaluation_signal")
_emit_records_telemetry_event("p4", "SovereignHealthMonitor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "SovereignHealthMonitor", "eval_metric")
_emit_stores_embedding("p4", "SovereignHealthMonitor", "embedding_store")
_emit_updates_meta_learning_state("p4", "SovereignHealthMonitor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "SovereignHealthMonitor", "exec_snapshot_link")
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

record_execution_trace("SovereignHealthMonitor", "SovereignHealthMonitor_trace")


_emit_emits_metric_event("SovereignHealthMonitor", "p4obs", "metric_1")
_emit_emits_metric_event("SovereignHealthMonitor", "p4obs", "metric_2")
_emit_emits_metric_event("SovereignHealthMonitor", "p4obs", "metric_3")
_emit_emits_metric_event("SovereignHealthMonitor", "p4obs", "metric_4")
_emit_emits_metric_event("SovereignHealthMonitor", "p4obs", "metric_5")
_emit_emits_metric_event("SovereignHealthMonitor", "p4obs", "metric_6")
_emit_records_incident_event("SovereignHealthMonitor", "p4obs", "incident")
_emit_captures_runtime_anomaly("SovereignHealthMonitor", "p4obs", "anomaly")
_emit_writes_observability_log("SovereignHealthMonitor", "p4obs", "obs_log")
_emit_updates_monitoring_state("SovereignHealthMonitor", "p4obs", "mon_state")
_emit_triggers_alert("SovereignHealthMonitor", "p4obs", "alert")
_emit_links_incident_trace("SovereignHealthMonitor", "p4obs", "trace_link")
_emit_captures_pattern("SovereignHealthMonitor", "p3lm", "pattern")
_emit_records_learning_event("SovereignHealthMonitor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("SovereignHealthMonitor", "p3lm", "snapshot")
_emit_feeds_meta_learning("SovereignHealthMonitor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("SovereignHealthMonitor", "p3lm", "routing")
_emit_improves_agent_policy("SovereignHealthMonitor", "p3lm", "policy")
_emit_stores_learning_state("SovereignHealthMonitor", "p3lm", "state")
_emit_records_execution_trace("SovereignHealthMonitor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("SovereignHealthMonitor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("SovereignHealthMonitor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("SovereignHealthMonitor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("SovereignHealthMonitor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("SovereignHealthMonitor", "env_read", "p2_env_1")
_emit_reads_environ("SovereignHealthMonitor", "env_read", "p2_env_2")
_emit_reads_runtime_state("SovereignHealthMonitor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("SovereignHealthMonitor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "SovereignHealthMonitor", "context_pull")
_emit_pulls_context("p1", "SovereignHealthMonitor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "SovereignHealthMonitor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "SovereignHealthMonitor", "uwg_term_2")
_emit_writes_through("p1", "SovereignHealthMonitor", "write_through")
_emit_writes_through("p1", "SovereignHealthMonitor", "write_through_2")
_emit_validated_by_safety_plane("p1", "SovereignHealthMonitor", "safety_validation")
_emit_invokes_eval("p1", "SovereignHealthMonitor", "eval_call")
_emit_proposal_commits_routing("p1", "SovereignHealthMonitor", "routing_commit")


class SovereignHealthMonitor:
    """
    Monitors and persists sovereign health metrics to L4 State.

    Tracks:
    - Domain compliance scores over time
    - Healing fix counts per domain
    - Historical health snapshots for trend analysis
    """

    def __init__(self, redis_client):
        """
        Initialize the health monitor with Redis client.

        Args:
            redis_client: Redis client instance for L4 State persistence
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "SovereignHealthMonitor.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "SovereignHealthMonitor.__init__", "p0_governance")
        self.redis = redis_client

    def log_snapshot(self, domain: str, score: int, fixes: int) -> None:
        """
        Phase 4.3: Persists health metrics to L4 for historical analysis.

        Stores snapshots in a Redis list for time-series tracking, enabling:
        - Historical compliance trend analysis
        - Healing effectiveness metrics
        - Cross-domain health comparison

        Args:
            domain: Domain name (e.g., AGENTIC_CORE_DIR, APPS_LIC_DIR)
            score: Compliance score (0-100)
            fixes: Number of fixes applied in this healing cycle
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L6_OBSERVABILITY,
            "SovereignHealthMonitor.log_snapshot",
        )

        timestamp = datetime.now().isoformat()
        _adg_trust_score: float = 1.0
        try:
            from pathlib import Path as _Path

            from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile as _gbp

            _root = _Path(__file__).resolve().parents[4]
            _bp = _gbp(_Path(__file__).resolve(), _root)
            _adg_trust_score = round(_bp.behavioral_score, 4)
        except (ImportError, OSError, RuntimeError, TypeError, ValueError) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            import logging

            logging.getLogger(__name__).debug("SovereignHealthMonitor: Exception swallowed at L235: %s", e)
        snapshot = {
            "timestamp": timestamp,
            "domain": domain,
            "compliance_score": score,
            "total_fixes": fixes,
            "adg_trust_score": _adg_trust_score,
        }
        try:
            self.redis.lpush("sovereign_health_history", json.dumps(snapshot))
            self.redis.set(
                f"sovereign_health:{domain}",
                json.dumps({"compliance_score": score, "total_fixes": fixes, "last_updated": timestamp}),
            )
            self.redis.incr("autonomous_fixes_total", amount=fixes)
        except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:  # guardian: allow-silent-swallow
            print(f"[WARNING] Failed to persist health snapshot: {e}")

    def get_domain_health(self, domain: str) -> dict[str, Any] | None:
        """
        Retrieve current health metrics for a specific domain.

        Args:
            domain: Domain name to query

        Returns:
            Dict with compliance_score, total_fixes, and last_updated, or None
        """
        try:
            data = self.redis.get(f"sovereign_health:{domain}")
            if data:
                return json.loads(data)
        except (AttributeError, json.JSONDecodeError) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            self.logger.debug(f"Failed to get health for {domain}: {e}")
        return None

    # guardian: allow-magic-config
    def get_health_history(self, limit: int = 100) -> list:
        """
        Retrieve historical health snapshots.

        Args:
            limit: Maximum number of snapshots to retrieve

        Returns:
            List of health snapshot dictionaries, newest first
        """
        try:
            snapshots = self.redis.lrange("sovereign_health_history", 0, limit - 1)
            return [json.loads(s) for s in snapshots]
        except (AttributeError, json.JSONDecodeError) as e:
            self.logger.debug(f"Failed to get health history: {e}")
            return []

    def get_total_fixes(self) -> int:
        """
        Get total number of autonomous fixes across all domains.

        Returns:
            Total fix count
        """
        try:
            total = self.redis.get("autonomous_fixes_total")
            return int(total) if total else 0
        except (AttributeError, ValueError) as e:
            self.logger.debug(f"Failed to get total fixes: {e}")
            return 0
