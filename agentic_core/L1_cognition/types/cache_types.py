"""
agentic_core/L1_cognition/reasoning/types/cache_types.py

Passive data structures and constants for CacheStrategyManager.
Extracted from engine/cache_manager.py to prevent circular dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "cache_types")
emit_determinism_digest("p0", "cache_types")

_emit_dispatches_healing_run("p1", "cache_types", "L1")
_emit_routes_through("p1", "cache_types", "L1")
_emit_escalates_to_human("p1", "cache_types", "L1")
_emit_reads_policy_state("p1", "cache_types", "L1")

_emit_snapshots_state("p0", "cache_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "cache_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "cache_types")
_emit_authorize_and_execute("p2", "cache_types", "execution_auth")
_emit_validates_capability("p2", "cache_types", "capability_check")
_emit_routes_to_capability("p2", "cache_types", "capability_route")
_emit_writes_via_uwg("p2", "cache_types", "uwg_write")
_emit_blocks_direct_write("p2", "cache_types", "direct_write_block")
_emit_records_tool_invocation("p2", "cache_types", "tool_invocation")
_emit_captures_execution_output("p2", "cache_types", "exec_output")
_emit_dispatches_agent("p3", "cache_types", "agent_dispatch")
_emit_coordinates_agents("p3", "cache_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "cache_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "cache_types", "healing_outcome")
_emit_escalates_failure("p3", "cache_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "cache_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "cache_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "cache_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "cache_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "cache_types", "eval_metric")
_emit_stores_embedding("p4", "cache_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "cache_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "cache_types", "exec_snapshot_link")

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
            MIN_SIMILARITY_THRESHOLD, min(MAX_SIMILARITY_THRESHOLD, self.similarity_threshold)
        )
        self.max_healing_depth = max(1, min(10, self.max_healing_depth))
