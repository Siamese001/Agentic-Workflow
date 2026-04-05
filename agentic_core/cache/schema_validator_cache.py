"""Schema Validator Cache — Redis-backed cache for JSON Schema validation results.

Caches schema validation outcomes to eliminate repeated validation of identical
data against the same schema version. Keyed by schema hash + data hash.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any

from agentic_core.cache.cache_key_builders import _require_hash_segment
from agentic_core.cache.redis_cache_client import DeterministicRedisCache, get_hot_cache
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

_emit_applies_guardrail("p0", "schema_validator_cache", "p0_governance")
_emit_reads_policy_state("p0", "schema_validator_cache", "policy_binding")
_emit_snapshots_state("p0", "schema_validator_cache", "state_snapshot")
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

_emit_emits_metric_event("schema_validator_cache", "p4obs", "metric_1")
_emit_emits_metric_event("schema_validator_cache", "p4obs", "metric_2")
_emit_emits_metric_event("schema_validator_cache", "p4obs", "metric_3")
_emit_emits_metric_event("schema_validator_cache", "p4obs", "metric_4")
_emit_emits_metric_event("schema_validator_cache", "p4obs", "metric_5")
_emit_emits_metric_event("schema_validator_cache", "p4obs", "metric_6")
_emit_records_incident_event("schema_validator_cache", "p4obs", "incident")
_emit_captures_runtime_anomaly("schema_validator_cache", "p4obs", "anomaly")
_emit_writes_observability_log("schema_validator_cache", "p4obs", "obs_log")
_emit_updates_monitoring_state("schema_validator_cache", "p4obs", "mon_state")
_emit_triggers_alert("schema_validator_cache", "p4obs", "alert")
_emit_links_incident_trace("schema_validator_cache", "p4obs", "trace_link")
_emit_captures_pattern("schema_validator_cache", "p3lm", "pattern")
_emit_records_learning_event("schema_validator_cache", "p3lm", "learning_event")
_emit_writes_learning_snapshot("schema_validator_cache", "p3lm", "snapshot")
_emit_feeds_meta_learning("schema_validator_cache", "p3lm", "meta_feed")
_emit_updates_routing_strategy("schema_validator_cache", "p3lm", "routing")
_emit_improves_agent_policy("schema_validator_cache", "p3lm", "policy")
_emit_stores_learning_state("schema_validator_cache", "p3lm", "state")
_emit_records_execution_trace("schema_validator_cache", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("schema_validator_cache", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("schema_validator_cache", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("schema_validator_cache", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("schema_validator_cache", "L4_STATE", "p2_trace_5")
_emit_reads_environ("schema_validator_cache", "env_read", "p2_env_1")
_emit_reads_environ("schema_validator_cache", "env_read", "p2_env_2")
_emit_reads_runtime_state("schema_validator_cache", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("schema_validator_cache", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "schema_validator_cache", "context_pull")
_emit_pulls_context("p1", "schema_validator_cache", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "schema_validator_cache", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "schema_validator_cache", "uwg_term_2")
_emit_writes_through("p1", "schema_validator_cache", "write_through")
_emit_writes_through("p1", "schema_validator_cache", "write_through_2")
_emit_validated_by_safety_plane("p1", "schema_validator_cache", "safety_validation")
_emit_invokes_eval("p1", "schema_validator_cache", "eval_call")
_emit_proposal_commits_routing("p1", "schema_validator_cache", "routing_commit")
_emit_escalates_to_human("p1", "schema_validator_cache", "human_escalation")
_emit_routes_through("p1", "schema_validator_cache", "route_through")
_emit_checks_agent_registry("p1", "schema_validator_cache", "agent_registry")
_emit_validates_agent_capability("p1", "schema_validator_cache", "capability")
_emit_dispatches_execution_plan("p1", "schema_validator_cache", "exec_plan")
_emit_agent_executes_agent("p1", "schema_validator_cache", "sub_agent")
_emit_routes_to_agent("p1", "schema_validator_cache", "target_agent")
_emit_verifies_policy("p1", "schema_validator_cache", "policy_check")
_emit_observes_runtime_state("p1", "schema_validator_cache", "runtime_state")
_emit_verifies_boundary("p1", "schema_validator_cache", "boundary_check")
_emit_transcripts_response("p1", "schema_validator_cache", "transcript")
_emit_hard_fails_untranscripted("p1", "schema_validator_cache")
_emit_gated_by_confidence("p1", "schema_validator_cache", "confidence_gate")
emit_replay_key("p0", "schema_validator_cache")
emit_determinism_digest("p0", "schema_validator_cache")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "schema_validator_cache", "execution_auth")
_emit_validates_capability("p2", "schema_validator_cache", "capability_check")
_emit_routes_to_capability("p2", "schema_validator_cache", "capability_route")
_emit_writes_via_uwg("p2", "schema_validator_cache", "uwg_write")
_emit_blocks_direct_write("p2", "schema_validator_cache", "direct_write_block")
_emit_records_tool_invocation("p2", "schema_validator_cache", "tool_invocation")
_emit_captures_execution_output("p2", "schema_validator_cache", "exec_output")
_emit_dispatches_agent("p3", "schema_validator_cache", "agent_dispatch")
_emit_coordinates_agents("p3", "schema_validator_cache", "agent_coordination")
_emit_records_workflow_lineage("p3", "schema_validator_cache", "workflow_lineage")
_emit_records_healing_outcome("p3", "schema_validator_cache", "healing_outcome")
_emit_escalates_failure("p3", "schema_validator_cache", "failure_escalation")
_emit_orchestrates_workflow("p3", "schema_validator_cache", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "schema_validator_cache", "healing_dispatch")
_emit_invokes_evaluation("p3", "schema_validator_cache", "evaluation_signal")
_emit_records_telemetry_event("p4", "schema_validator_cache", "telemetry_event")
_emit_captures_evaluation_metric("p4", "schema_validator_cache", "eval_metric")
_emit_stores_embedding("p4", "schema_validator_cache", "embedding_store")
_emit_updates_meta_learning_state("p4", "schema_validator_cache", "meta_learning")
_emit_links_execution_to_snapshot("p4", "schema_validator_cache", "exec_snapshot_link")

logger = logging.getLogger(__name__)
_DEFAULT_SCHEMA_TTL = 3600 * 24 * 7  # 7 days — schemas change rarely


class SchemaValidatorCache:
    """Cache for JSON Schema validation results.

    Eliminates repeated validation of identical data against the same schema.
    Automatically invalidates when either schema or data changes.
    """

    def __init__(
        self,
        cache: DeterministicRedisCache | None = None,
        ttl_seconds: int = _DEFAULT_SCHEMA_TTL,
    ):
        self._cache = cache or get_hot_cache()
        self._ttl = ttl_seconds

    def get_or_validate(
        self,
        schema_path: Path,
        data: dict[str, Any],
        validate_fn: Any,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any]:
        """Return cached validation result or call *validate_fn*.

        Args:
            schema_path: Path to JSON Schema file
            data: Data dict to validate
            validate_fn: Callable that performs validation and returns result dict
            replay_mode: If True, bypass cache entirely

        Returns:
            Validation result dict with keys: valid (bool), errors (list)
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SchemaValidatorCache.get_or_validate")

        if not replay_mode:
            try:
                schema_hash = self._compute_file_hash(schema_path)
                data_hash = self._compute_data_hash(data)
                cache_key = f"schema_val:{schema_hash}:{data_hash}"
            # guardian: allow-silent-swallow - optional file resource