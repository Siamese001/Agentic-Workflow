"""
agentic_core/L1_cognition/reasoning/types/cache_types.py

Passive data structures and constants for CacheStrategyManager.
Extracted from engine/cache_manager.py to prevent circular dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_emits_metric_event("cache_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("cache_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("cache_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("cache_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("cache_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("cache_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("cache_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("cache_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("cache_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("cache_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("cache_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("cache_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("cache_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("cache_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("cache_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("cache_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("cache_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("cache_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("cache_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("cache_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("cache_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("cache_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("cache_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("cache_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("cache_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("cache_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("cache_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("cache_types", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "cache_types")
trace_contract.emit_determinism_digest("p0", "cache_types")

trace_contract._emit_dispatches_healing_run("p1", "cache_types", "L1")
trace_contract._emit_routes_through("p1", "cache_types", "L1")
trace_contract._emit_checks_agent_registry("p1", "cache_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "cache_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "cache_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "cache_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "cache_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "cache_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "cache_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "cache_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "cache_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "cache_types")
trace_contract._emit_gated_by_confidence("p1", "cache_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "cache_types", "L1")
trace_contract._emit_reads_policy_state("p1", "cache_types", "L1")
trace_contract._emit_pulls_context("p1", "cache_types", "context_pull")
trace_contract._emit_pulls_context("p1", "cache_types", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "cache_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "cache_types", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "cache_types", "write_through")
trace_contract._emit_writes_through("p1", "cache_types", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "cache_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "cache_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "cache_types", "routing_commit")

trace_contract._emit_snapshots_state("p0", "cache_types", "state_snapshot")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "cache_types", "p0_governance")
trace_contract._emit_records_execution_trace("p0", "evidence", "cache_types")
trace_contract._emit_authorize_and_execute("p2", "cache_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "cache_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "cache_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "cache_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "cache_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "cache_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "cache_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "cache_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "cache_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "cache_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "cache_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "cache_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "cache_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "cache_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "cache_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "cache_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "cache_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "cache_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "cache_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "cache_types", "exec_snapshot_link")

DEFAULT_TTL_SECONDS: Final[int] = 3600
MIN_TTL_SECONDS: Final[int] = 60
MAX_TTL_SECONDS: Final[int] = 86400
DEFAULT_SIMILARITY_THRESHOLD: Final[float] = 0.85
MIN_SIMILARITY_THRESHOLD: Final[float] = 0.7
MAX_SIMILARITY_THRESHOLD: Final[float] = 0.99
MAX_CACHE_SIZE: Final[int] = 10000
MAX_HEALING_DEPTH: Final[int] = 5


class EvictionPolicy(Enum):
    """Cache eviction policies."""

    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"


@dataclass
class DomainConfig:
    """
    Domain-specific configuration for cache strategy.

    Attributes:
        domain: Domain name (agentic_core, apps_lic, apps_rg)
        ttl_seconds: Time-to-live for cache entries
        similarity_threshold: Minimum similarity for pattern matching
        max_cache_size: Maximum number of entries in domain cache
        eviction_policy: Cache eviction policy
        max_healing_depth: Maximum healing recursion depth
    """

    domain: str
    ttl_seconds: int = DEFAULT_TTL_SECONDS
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD
    max_cache_size: int = MAX_CACHE_SIZE
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    max_healing_depth: int = MAX_HEALING_DEPTH

    def __post_init__(self) -> None:
        """Validate configuration values."""
        self.ttl_seconds = max(MIN_TTL_SECONDS, min(MAX_TTL_SECONDS, self.ttl_seconds))
        self.similarity_threshold = max(
            MIN_SIMILARITY_THRESHOLD,
            min(MAX_SIMILARITY_THRESHOLD, self.similarity_threshold),
        )
        self.max_healing_depth = max(1, min(10, self.max_healing_depth))
