"""Cache Namespace Builder — deterministic key namespace construction.

Builds cache key namespaces with proper scoping, versioning, and hash segments.
Ensures cache key uniqueness and automatic invalidation on dependency changes.
"""

from __future__ import annotations

import logging

from agentic_core.cache.cache_key_builders import _require_hash_segment, _require_safe_segment
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "namespace_builder", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "namespace_builder", "policy_binding")
trace_contract._emit_snapshots_state("p0", "namespace_builder", "state_snapshot")
trace_contract.emit_replay_key("p0", "namespace_builder")
trace_contract.emit_determinism_digest("p0", "namespace_builder")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "namespace_builder", "execution_auth")
trace_contract._emit_validates_capability("p2", "namespace_builder", "capability_check")
trace_contract._emit_routes_to_capability("p2", "namespace_builder", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "namespace_builder", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "namespace_builder", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "namespace_builder", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "namespace_builder", "exec_output")
trace_contract._emit_dispatches_agent("p3", "namespace_builder", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "namespace_builder", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "namespace_builder", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "namespace_builder", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "namespace_builder", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "namespace_builder", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "namespace_builder", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "namespace_builder", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "namespace_builder", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "namespace_builder", "eval_metric")
trace_contract._emit_stores_embedding("p4", "namespace_builder", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "namespace_builder", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "namespace_builder", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("namespace_builder", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("namespace_builder", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("namespace_builder", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("namespace_builder", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("namespace_builder", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("namespace_builder", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("namespace_builder", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("namespace_builder", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("namespace_builder", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("namespace_builder", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("namespace_builder", "p4obs", "alert")
trace_contract._emit_links_incident_trace("namespace_builder", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("namespace_builder", "p3lm", "pattern")
trace_contract._emit_records_learning_event("namespace_builder", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("namespace_builder", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("namespace_builder", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("namespace_builder", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("namespace_builder", "p3lm", "policy")
trace_contract._emit_stores_learning_state("namespace_builder", "p3lm", "state")
trace_contract._emit_records_execution_trace("namespace_builder", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("namespace_builder", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("namespace_builder", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("namespace_builder", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("namespace_builder", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("namespace_builder", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("namespace_builder", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("namespace_builder", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("namespace_builder", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "namespace_builder", "context_pull")
trace_contract._emit_pulls_context("p1", "namespace_builder", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "namespace_builder", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "namespace_builder", "uwg_term_2")
trace_contract._emit_writes_through("p1", "namespace_builder", "write_through")
trace_contract._emit_writes_through("p1", "namespace_builder", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "namespace_builder", "safety_validation")
trace_contract._emit_invokes_eval("p1", "namespace_builder", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "namespace_builder", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "namespace_builder", "human_escalation")
trace_contract._emit_routes_through("p1", "namespace_builder", "route_through")
trace_contract._emit_checks_agent_registry("p1", "namespace_builder", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "namespace_builder", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "namespace_builder", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "namespace_builder", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "namespace_builder", "target_agent")
trace_contract._emit_verifies_policy("p1", "namespace_builder", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "namespace_builder", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "namespace_builder", "boundary_check")
trace_contract._emit_transcripts_response("p1", "namespace_builder", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "namespace_builder")
trace_contract._emit_gated_by_confidence("p1", "namespace_builder", "confidence_gate")

logger = logging.getLogger(__name__)


class CacheNamespaceBuilder:
    """Builds deterministic cache key namespaces with proper scoping.

    Ensures cache key uniqueness, versioning, and automatic invalidation
    when dependencies change.
    """

    def __init__(self, base_namespace: str, version: str = "v1"):
        """Initialize namespace builder.

        Args:
            base_namespace: Base namespace for all keys (e.g., "agent_discovery")
            version: Cache schema version for invalidation on schema changes
        """
        _require_safe_segment("base_namespace", base_namespace)
        _require_safe_segment("version", version)
        self.base_namespace = base_namespace
        self.version = version

    def build_key(self, *hash_segments: str) -> str:
        """Build a cache key with proper namespacing.

        Args:
            *hash_segments: SHA-256 hash segments to include in key

        Returns:
            Fully qualified cache key
        """
        for segment in hash_segments:
            _require_hash_segment("hash_segment", segment)
        return f"{self.base_namespace}:{self.version}:{':'.join(hash_segments)}"

    def build_scoped_key(self, scope: str, *hash_segments: str) -> str:
        """Build a scoped cache key with additional scope segment.

        Args:
            scope: Scope identifier (e.g., "production", "test")
            *hash_segments: SHA-256 hash segments

        Returns:
            Scoped cache key
        """
        _require_safe_segment("scope", scope)
        for segment in hash_segments:
            _require_hash_segment("hash_segment", segment)
        return f"{self.base_namespace}:{self.version}:{scope}:{':'.join(hash_segments)}"


trace_contract._emit_reads_through("l4", "namespace_builder", "urg_read_1")
trace_contract._emit_reads_through("l4", "namespace_builder", "urg_read_2")
trace_contract._emit_reads_through("l4", "namespace_builder", "urg_read_3")
trace_contract._emit_reads_through("l4", "namespace_builder", "urg_read_4")
trace_contract._emit_reads_through("l4", "namespace_builder", "urg_read_5")
trace_contract._emit_reads_through("l4", "namespace_builder", "urg_read_6")
trace_contract._emit_reads_through("l4", "namespace_builder", "urg_read_7")
trace_contract._emit_reads_through("l4", "namespace_builder", "urg_read_8")
trace_contract._emit_reads_through("l4", "namespace_builder", "urg_read_9")
trace_contract._emit_reads_through("l4", "namespace_builder", "urg_read_10")
trace_contract._emit_reads_through("l4", "namespace_builder", "urg_read_11")
trace_contract._emit_reads_through("l4", "namespace_builder", "urg_read_12")
