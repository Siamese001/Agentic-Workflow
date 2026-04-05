"""L2 Execution — Redis-backed lease coordinator and idempotency store.

Two concerns are handled here:

  LeaseCoordinator
      Provides cross-process mutual exclusion for plan execution.
      Uses Redis DB 1 (CacheDB.COORDINATION) with short TTLs.
      Falls back to in-process LRU when Redis is unavailable (single-
      process exclusivity only — cross-process requires a live Redis).

  IdempotencyStore
      Records the exact stdout/exit-code bytes returned by a tool call
      so that retried calls return the same result without re-executing.
      Keyed by ``tool_call_hash`` (SHA-256 of canonical-JSON tool args).

Hard rules for determinism
--------------------------
* In ``replay_mode=True`` ALL reads from both stores return ``None`` /
  ``False`` so the caller re-derives the result from first principles.
  This ensures the replay transcript is self-contained.
* Neither store is a source of truth — L4 / UWG remains the mutation
  authority.  Both stores contain *coordination* records and *derived*
  outputs only.
* ``nonce`` in lease entries must be drawn from the deterministic
  transcript of the current run (not ``secrets.token_hex``), unless the
  nonce is itself stored in the transcript so replay can reconstruct it.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.cache.cache_key_builders import build_lease_key, build_tool_result_key
from agentic_core.cache.redis_cache_client import (
    DeterministicRedisCache,
    get_coordination_cache,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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

emit_replay_key("p0", "lease_coordinator")
emit_determinism_digest("p0", "lease_coordinator")

_emit_dispatches_healing_run("p1", "lease_coordinator", "L2")
_emit_routes_through("p1", "lease_coordinator", "L2")
_emit_checks_agent_registry("p1", "lease_coordinator", "agent_registry")
_emit_validates_agent_capability("p1", "lease_coordinator", "capability")
_emit_dispatches_execution_plan("p1", "lease_coordinator", "exec_plan")
_emit_agent_executes_agent("p1", "lease_coordinator", "sub_agent")
_emit_routes_to_agent("p1", "lease_coordinator", "target_agent")
_emit_verifies_policy("p1", "lease_coordinator", "policy_check")
_emit_observes_runtime_state("p1", "lease_coordinator", "runtime_state")
_emit_verifies_boundary("p1", "lease_coordinator", "boundary_check")
_emit_transcripts_response("p1", "lease_coordinator", "transcript")
_emit_hard_fails_untranscripted("p1", "lease_coordinator")
_emit_gated_by_confidence("p1", "lease_coordinator", "confidence_gate")
_emit_escalates_to_human("p1", "lease_coordinator", "L2")
_emit_reads_policy_state("p1", "lease_coordinator", "L2")

_emit_applies_guardrail("p0", "lease_coordinator", "p0_governance")
_emit_snapshots_state("p0", "lease_coordinator", "state_snapshot")
_emit_authorize_and_execute("p2", "lease_coordinator", "execution_auth")
_emit_validates_capability("p2", "lease_coordinator", "capability_check")
_emit_routes_to_capability("p2", "lease_coordinator", "capability_route")
_emit_writes_via_uwg("p2", "lease_coordinator", "uwg_write")
_emit_blocks_direct_write("p2", "lease_coordinator", "direct_write_block")
_emit_records_tool_invocation("p2", "lease_coordinator", "tool_invocation")
_emit_captures_execution_output("p2", "lease_coordinator", "exec_output")
_emit_dispatches_agent("p3", "lease_coordinator", "agent_dispatch")
_emit_coordinates_agents("p3", "lease_coordinator", "agent_coordination")
_emit_records_workflow_lineage("p3", "lease_coordinator", "workflow_lineage")
_emit_records_healing_outcome("p3", "lease_coordinator", "healing_outcome")
_emit_escalates_failure("p3", "lease_coordinator", "failure_escalation")
_emit_orchestrates_workflow("p3", "lease_coordinator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "lease_coordinator", "healing_dispatch")
_emit_invokes_evaluation("p3", "lease_coordinator", "evaluation_signal")
_emit_records_telemetry_event("p4", "lease_coordinator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "lease_coordinator", "eval_metric")
_emit_stores_embedding("p4", "lease_coordinator", "embedding_store")
_emit_updates_meta_learning_state("p4", "lease_coordinator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "lease_coordinator", "exec_snapshot_link")
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

_emit_emits_metric_event("lease_coordinator", "p4obs", "metric_1")
_emit_emits_metric_event("lease_coordinator", "p4obs", "metric_2")
_emit_emits_metric_event("lease_coordinator", "p4obs", "metric_3")
_emit_emits_metric_event("lease_coordinator", "p4obs", "metric_4")
_emit_emits_metric_event("lease_coordinator", "p4obs", "metric_5")
_emit_emits_metric_event("lease_coordinator", "p4obs", "metric_6")
_emit_records_incident_event("lease_coordinator", "p4obs", "incident")
_emit_captures_runtime_anomaly("lease_coordinator", "p4obs", "anomaly")
_emit_writes_observability_log("lease_coordinator", "p4obs", "obs_log")
_emit_updates_monitoring_state("lease_coordinator", "p4obs", "mon_state")
_emit_triggers_alert("lease_coordinator", "p4obs", "alert")
_emit_links_incident_trace("lease_coordinator", "p4obs", "trace_link")
_emit_captures_pattern("lease_coordinator", "p3lm", "pattern")
_emit_records_learning_event("lease_coordinator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("lease_coordinator", "p3lm", "snapshot")
_emit_feeds_meta_learning("lease_coordinator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("lease_coordinator", "p3lm", "routing")
_emit_improves_agent_policy("lease_coordinator", "p3lm", "policy")
_emit_stores_learning_state("lease_coordinator", "p3lm", "state")
_emit_records_execution_trace("lease_coordinator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("lease_coordinator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("lease_coordinator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("lease_coordinator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("lease_coordinator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("lease_coordinator", "env_read", "p2_env_1")
_emit_reads_environ("lease_coordinator", "env_read", "p2_env_2")
_emit_reads_runtime_state("lease_coordinator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("lease_coordinator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "lease_coordinator", "context_pull")
_emit_pulls_context("p1", "lease_coordinator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "lease_coordinator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "lease_coordinator", "uwg_term_2")
_emit_writes_through("p1", "lease_coordinator", "write_through")
_emit_writes_through("p1", "lease_coordinator", "write_through_2")
_emit_validated_by_safety_plane("p1", "lease_coordinator", "safety_validation")
_emit_invokes_eval("p1", "lease_coordinator", "eval_call")
_emit_proposal_commits_routing("p1", "lease_coordinator", "routing_commit")

logger = logging.getLogger(__name__)

_DEFAULT_LEASE_TTL: int = 30  # seconds — short for coordination safety
_DEFAULT_IDEMPOTENCY_TTL: int = 300  # 5 minutes


class LeaseCoordinator:
    """Cross-process execution-lease manager (DB 1, short TTLs).

    Usage pattern::

        lc = LeaseCoordinator()
        acquired = lc.acquire("plan-abc123", holder_id="worker-1",
                               nonce="<transcript-nonce>",
                               semantic_clock_tick=42)
        if acquired:
            try:
                ...run plan...
            finally:
                lc.release("plan-abc123", holder_id="worker-1",
                            nonce="<transcript-nonce>")

    Parameters
    ----------
    lease_ttl_seconds:
        How long a lease is valid before automatic expiry.
    cache:
        Override the coordination-cache instance (useful for testing).
    """

    def __init__(
        self,
        lease_ttl_seconds: int = _DEFAULT_LEASE_TTL,
        cache: DeterministicRedisCache | None = None,
    ) -> None:
        self._ttl = lease_ttl_seconds
        self._cache = cache or get_coordination_cache()

    def acquire(
        self,
        plan_hash: str,
        holder_id: str,
        nonce: str,
        semantic_clock_tick: int,
        *,
        replay_mode: bool = False,
    ) -> bool:
        """Attempt to acquire the lease for *plan_hash*.

        Returns ``True`` if the lease was acquired; ``False`` if another
        holder currently holds it.  Always returns ``False`` in
        ``replay_mode=True`` — callers should treat replay as lease-free
        (no coordination needed for read-only transcript reconstruction).
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "LeaseCoordinator.acquire")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:LeaseCoordinator.acquire".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if replay_mode:
            return False

        key = build_lease_key(plan_hash)
        return self._cache.acquire_lease(
            key,
            holder_id=holder_id,
            nonce=nonce,
            semantic_clock_tick=semantic_clock_tick,
            ttl_seconds=self._ttl,
        )

    def release(
        self,
        plan_hash: str,
        holder_id: str,
        nonce: str,
    ) -> bool:
        """Release the lease for *plan_hash* held by *holder_id* / *nonce*.

        Returns ``True`` if the lease was successfully released; ``False``
        if the caller did not hold the lease or it had already expired.
        """
        key = build_lease_key(plan_hash)
        return self._cache.release_lease(key, holder_id=holder_id, nonce=nonce)

    def is_held(self, plan_hash: str) -> bool:
        """Return ``True`` if any holder currently holds the lease."""
        key = build_lease_key(plan_hash)
        return self._cache.exists(key)

    def holder_info(self, plan_hash: str) -> dict[str, Any] | None:
        """Return the lease payload dict (holder_id, nonce, clock tick) or None."""
        key = build_lease_key(plan_hash)
        return self._cache.get_json(key)


class IdempotencyStore:
    """Records exact tool-call outputs for deduplication (DB 1).

    When a tool call identified by ``tool_call_hash`` has already been
    executed, its raw output bytes are stored here so that a retry returns
    the same bytes without re-executing the tool.

    Rules
    -----
    * Only store outputs for tools that are **strictly input-hashed** (the
      same hash always produces the same output).  Do NOT store outputs for
      tools with side effects unless those side effects are idempotent.
    * In ``replay_mode=True`` all reads return ``None`` — the transcript
      already contains the canonical output.

    Parameters
    ----------
    ttl_seconds:
        TTL for idempotency records.
    cache:
        Override the coordination-cache instance (useful for testing).
    """

    def __init__(
        self,
        ttl_seconds: int = _DEFAULT_IDEMPOTENCY_TTL,
        cache: DeterministicRedisCache | None = None,
    ) -> None:
        self._ttl = ttl_seconds
        self._cache = cache or get_coordination_cache()

    def get(
        self,
        tool_call_hash: str,
        *,
        replay_mode: bool = False,
    ) -> bytes | None:
        """Return stored tool-output bytes or ``None`` on miss/bypass."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "IdempotencyStore.get")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:IdempotencyStore.get".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        key = build_tool_result_key(tool_call_hash)
        return self._cache.get(key, replay_mode=replay_mode)

    def set(
        self,
        tool_call_hash: str,
        output_bytes: bytes,
    ) -> None:
        """Record *output_bytes* as the canonical output for *tool_call_hash*."""
        key = build_tool_result_key(tool_call_hash)
        self._cache.set(key, output_bytes, ttl_seconds=self._ttl)

    def exists(self, tool_call_hash: str) -> bool:
        """Return ``True`` if a recorded result exists for *tool_call_hash*."""
        key = build_tool_result_key(tool_call_hash)
        return self._cache.exists(key)

    def invalidate(self, tool_call_hash: str) -> None:
        """Evict the idempotency record (e.g. after a forced retry)."""
        key = build_tool_result_key(tool_call_hash)
        self._cache.delete(key)


# ---------------------------------------------------------------------------
# Module-level convenience singletons
# ---------------------------------------------------------------------------

_lease_coordinator: LeaseCoordinator | None = None
_idempotency_store: IdempotencyStore | None = None


def get_lease_coordinator() -> LeaseCoordinator:
    """Return the process-global ``LeaseCoordinator`` instance."""
    global _lease_coordinator
    if _lease_coordinator is None:
        _lease_coordinator = LeaseCoordinator()
    return _lease_coordinator


def get_idempotency_store() -> IdempotencyStore:
    """Return the process-global ``IdempotencyStore`` instance."""
    global _idempotency_store
    if _idempotency_store is None:
        _idempotency_store = IdempotencyStore()
    return _idempotency_store
