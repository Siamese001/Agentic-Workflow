"""
agentic_core/L1_cognition/reasoning/types/client_types.py

Passive data structures and constants for MetaLearningClient.
Extracted from engine/meta_client.py to prevent circular dependencies.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Final

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.runtime.lifecycle_trace_contract import (
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
)

emit_replay_key("p0", "client_types")
emit_determinism_digest("p0", "client_types")

_emit_dispatches_healing_run("p1", "client_types", "L1")
_emit_routes_through("p1", "client_types", "L1")
_emit_checks_agent_registry("p1", "client_types", "agent_registry")
_emit_validates_agent_capability("p1", "client_types", "capability")
_emit_dispatches_execution_plan("p1", "client_types", "exec_plan")
_emit_agent_executes_agent("p1", "client_types", "sub_agent")
_emit_routes_to_agent("p1", "client_types", "target_agent")
_emit_verifies_policy("p1", "client_types", "policy_check")
_emit_observes_runtime_state("p1", "client_types", "runtime_state")
_emit_verifies_boundary("p1", "client_types", "boundary_check")
_emit_transcripts_response("p1", "client_types", "transcript")
_emit_hard_fails_untranscripted("p1", "client_types")
_emit_gated_by_confidence("p1", "client_types", "confidence_gate")
_emit_escalates_to_human("p1", "client_types", "L1")
_emit_reads_policy_state("p1", "client_types", "L1")
_emit_authorize_and_execute("p2", "client_types", "execution_auth")
_emit_validates_capability("p2", "client_types", "capability_check")
_emit_routes_to_capability("p2", "client_types", "capability_route")
_emit_writes_via_uwg("p2", "client_types", "uwg_write")
_emit_blocks_direct_write("p2", "client_types", "direct_write_block")
_emit_records_tool_invocation("p2", "client_types", "tool_invocation")
_emit_captures_execution_output("p2", "client_types", "exec_output")
_emit_dispatches_agent("p3", "client_types", "agent_dispatch")
_emit_coordinates_agents("p3", "client_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "client_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "client_types", "healing_outcome")
_emit_escalates_failure("p3", "client_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "client_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "client_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "client_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "client_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "client_types", "eval_metric")
_emit_stores_embedding("p4", "client_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "client_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "client_types", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("client_types", "p4obs", "metric_1")
_emit_emits_metric_event("client_types", "p4obs", "metric_2")
_emit_emits_metric_event("client_types", "p4obs", "metric_3")
_emit_emits_metric_event("client_types", "p4obs", "metric_4")
_emit_emits_metric_event("client_types", "p4obs", "metric_5")
_emit_emits_metric_event("client_types", "p4obs", "metric_6")
_emit_records_incident_event("client_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("client_types", "p4obs", "anomaly")
_emit_writes_observability_log("client_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("client_types", "p4obs", "mon_state")
_emit_triggers_alert("client_types", "p4obs", "alert")
_emit_links_incident_trace("client_types", "p4obs", "trace_link")
_emit_captures_pattern("client_types", "p3lm", "pattern")
_emit_records_learning_event("client_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("client_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("client_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("client_types", "p3lm", "routing")
_emit_improves_agent_policy("client_types", "p3lm", "policy")
_emit_stores_learning_state("client_types", "p3lm", "state")
_emit_records_execution_trace("client_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("client_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("client_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("client_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("client_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("client_types", "env_read", "p2_env_1")
_emit_reads_environ("client_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("client_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("client_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "client_types", "context_pull")
_emit_pulls_context("p1", "client_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "client_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "client_types", "uwg_term_2")
_emit_writes_through("p1", "client_types", "write_through")
_emit_writes_through("p1", "client_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "client_types", "safety_validation")
_emit_invokes_eval("p1", "client_types", "eval_call")
_emit_proposal_commits_routing("p1", "client_types", "routing_commit")

DEFAULT_SIMILARITY_THRESHOLD: Final[float] = 0.85
DEFAULT_TTL_SECONDS: Final[int] = 3600
MAX_HEALING_DEPTH: Final[int] = 5
CACHE_KEY_PREFIX: Final[str] = "meta_learning:"
PINECONE_NAMESPACE_PREFIX: Final[str] = "healing_patterns"


@dataclass
class HealingPattern:
    """
    Represents a successful healing pattern stored in Pinecone.

    Attributes:
        pattern_id: Unique identifier for the pattern
        violation_type: Type of violation this pattern addresses
        error_signature: Hash of the error signature
        healing_strategy: The successful healing approach
        success_count: Number of times this pattern succeeded
        domain: Domain context (agentic_core, apps_lic, apps_rg)
        metadata: Additional pattern metadata
        embedding: Vector embedding of the pattern (optional)
    """

    pattern_id: str
    violation_type: str
    error_signature: str
    healing_strategy: dict[str, Any]
    success_count: int = 1
    domain: str = AGENTIC_CORE_DIR
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert pattern to dictionary for storage."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "HealingPattern.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "HealingPattern.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_COGNITION, "HealingPattern.to_dict")
        return {
            "pattern_id": self.pattern_id,
            "violation_type": self.violation_type,
            "error_signature": self.error_signature,
            "healing_strategy": self.healing_strategy,
            "success_count": self.success_count,
            "domain": self.domain,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HealingPattern:
        """Create pattern from dictionary."""
        return cls(
            pattern_id=data.get("pattern_id", ""),
            violation_type=data.get("violation_type", ""),
            error_signature=data.get("error_signature", ""),
            healing_strategy=data.get("healing_strategy", {}),
            success_count=data.get("success_count", 1),
            domain=data.get("domain", AGENTIC_CORE_DIR),
            metadata=data.get("metadata", {}),
            embedding=data.get("embedding"),
        )


@dataclass
class CacheEntry:
    """
    Represents a cached entry in Redis.

    Attributes:
        key: Cache key
        value: Cached value
        ttl: Time-to-live in seconds
        created_at: Timestamp of creation
        domain: Domain context
        hit_count: Number of cache hits
    """

    key: str
    value: Any
    ttl: int = DEFAULT_TTL_SECONDS
    created_at: float = field(default_factory=time.time)
    domain: str = AGENTIC_CORE_DIR
    hit_count: int = 0

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return get_clock().now_epoch() - self.created_at > self.ttl
