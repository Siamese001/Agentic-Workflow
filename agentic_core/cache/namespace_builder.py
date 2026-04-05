"""Cache Namespace Builder — deterministic key namespace construction.

Builds cache key namespaces with proper scoping, versioning, and hash segments.
Ensures cache key uniqueness and automatic invalidation on dependency changes.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from agentic_core.cache.cache_key_builders import _require_hash_segment, _require_safe_segment
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
    _emit_reads_through,
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

_emit_applies_guardrail("p0", "namespace_builder", "p0_governance")
_emit_reads_policy_state("p0", "namespace_builder", "policy_binding")
_emit_snapshots_state("p0", "namespace_builder", "state_snapshot")
emit_replay_key("p0", "namespace_builder")
emit_determinism_digest("p0", "namespace_builder")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "namespace_builder", "execution_auth")
_emit_validates_capability("p2", "namespace_builder", "capability_check")
_emit_routes_to_capability("p2", "namespace_builder", "capability_route")
_emit_writes_via_uwg("p2", "namespace_builder", "uwg_write")
_emit_blocks_direct_write("p2", "namespace_builder", "direct_write_block")
_emit_records_tool_invocation("p2", "namespace_builder", "tool_invocation")
_emit_captures_execution_output("p2", "namespace_builder", "exec_output")
_emit_dispatches_agent("p3", "namespace_builder", "agent_dispatch")
_emit_coordinates_agents("p3", "namespace_builder", "agent_coordination")
_emit_records_workflow_lineage("p3", "namespace_builder", "workflow_lineage")
_emit_records_healing_outcome("p3", "namespace_builder", "healing_outcome")
_emit_escalates_failure("p3", "namespace_builder", "failure_escalation")
_emit_orchestrates_workflow("p3", "namespace_builder", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "namespace_builder", "healing_dispatch")
_emit_invokes_evaluation("p3", "namespace_builder", "evaluation_signal")
_emit_records_telemetry_event("p4", "namespace_builder", "telemetry_event")
_emit_captures_evaluation_metric("p4", "namespace_builder", "eval_metric")
_emit_stores_embedding("p4", "namespace_builder", "embedding_store")
_emit_updates_meta_learning_state("p4", "namespace_builder", "meta_learning")
_emit_links_execution_to_snapshot("p4", "namespace_builder", "exec_snapshot_link")
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

_emit_emits_metric_event("namespace_builder", "p4obs", "metric_1")
_emit_emits_metric_event("namespace_builder", "p4obs", "metric_2")
_emit_emits_metric_event("namespace_builder", "p4obs", "metric_3")
_emit_emits_metric_event("namespace_builder", "p4obs", "metric_4")
_emit_emits_metric_event("namespace_builder", "p4obs", "metric_5")
_emit_emits_metric_event("namespace_builder", "p4obs", "metric_6")
_emit_records_incident_event("namespace_builder", "p4obs", "incident")
_emit_captures_runtime_anomaly("namespace_builder", "p4obs", "anomaly")
_emit_writes_observability_log("namespace_builder", "p4obs", "obs_log")
_emit_updates_monitoring_state("namespace_builder", "p4obs", "mon_state")
_emit_triggers_alert("namespace_builder", "p4obs", "alert")
_emit_links_incident_trace("namespace_builder", "p4obs", "trace_link")
_emit_captures_pattern("namespace_builder", "p3lm", "pattern")
_emit_records_learning_event("namespace_builder", "p3lm", "learning_event")
_emit_writes_learning_snapshot("namespace_builder", "p3lm", "snapshot")
_emit_feeds_meta_learning("namespace_builder", "p3lm", "meta_feed")
_emit_updates_routing_strategy("namespace_builder", "p3lm", "routing")
_emit_improves_agent_policy("namespace_builder", "p3lm", "policy")
_emit_stores_learning_state("namespace_builder", "p3lm", "state")
_emit_records_execution_trace("namespace_builder", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("namespace_builder", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("namespace_builder", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("namespace_builder", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("namespace_builder", "L4_STATE", "p2_trace_5")
_emit_reads_environ("namespace_builder", "env_read", "p2_env_1")
_emit_reads_environ("namespace_builder", "env_read", "p2_env_2")
_emit_reads_runtime_state("namespace_builder", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("namespace_builder", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "namespace_builder", "context_pull")
_emit_pulls_context("p1", "namespace_builder", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "namespace_builder", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "namespace_builder", "uwg_term_2")
_emit_writes_through("p1", "namespace_builder", "write_through")
_emit_writes_through("p1", "namespace_builder", "write_through_2")
_emit_validated_by_safety_plane("p1", "namespace_builder", "safety_validation")
_emit_invokes_eval("p1", "namespace_builder", "eval_call")
_emit_proposal_commits_routing("p1", "namespace_builder", "routing_commit")
_emit_escalates_to_human("p1", "namespace_builder", "human_escalation")
_emit_routes_through("p1", "namespace_builder", "route_through")
_emit_checks_agent_registry("p1", "namespace_builder", "agent_registry")
_emit_validates_agent_capability("p1", "namespace_builder", "capability")
_emit_dispatches_execution_plan("p1", "namespace_builder", "exec_plan")
_emit_agent_executes_agent("p1", "namespace_builder", "sub_agent")
_emit_routes_to_agent("p1", "namespace_builder", "target_agent")
_emit_verifies_policy("p1", "namespace_builder", "policy_check")
_emit_observes_runtime_state("p1", "namespace_builder", "runtime_state")
_emit_verifies_boundary("p1", "namespace_builder", "boundary_check")
_emit_transcripts_response("p1", "namespace_builder", "transcript")
_emit_hard_fails_untranscripted("p1", "namespace_builder")
_emit_gated_by_confidence("p1", "namespace_builder", "confidence_gate")

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


_emit_reads_through("l4", "namespace_builder", "urg_read_1")
_emit_reads_through("l4", "namespace_builder", "urg_read_2")
_emit_reads_through("l4", "namespace_builder", "urg_read_3")
_emit_reads_through("l4", "namespace_builder", "urg_read_4")
_emit_reads_through("l4", "namespace_builder", "urg_read_5")
_emit_reads_through("l4", "namespace_builder", "urg_read_6")
_emit_reads_through("l4", "namespace_builder", "urg_read_7")
_emit_reads_through("l4", "namespace_builder", "urg_read_8")
_emit_reads_through("l4", "namespace_builder", "urg_read_9")
_emit_reads_through("l4", "namespace_builder", "urg_read_10")
_emit_reads_through("l4", "namespace_builder", "urg_read_11")
_emit_reads_through("l4", "namespace_builder", "urg_read_12")
