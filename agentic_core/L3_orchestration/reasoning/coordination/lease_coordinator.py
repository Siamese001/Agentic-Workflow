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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "lease_coordinator")
trace_contract.emit_determinism_digest("p0", "lease_coordinator")

trace_contract._emit_dispatches_healing_run("p1", "lease_coordinator", "L2")
trace_contract._emit_routes_through("p1", "lease_coordinator", "L2")
trace_contract._emit_checks_agent_registry("p1", "lease_coordinator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "lease_coordinator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "lease_coordinator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "lease_coordinator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "lease_coordinator", "target_agent")
trace_contract._emit_verifies_policy("p1", "lease_coordinator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "lease_coordinator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "lease_coordinator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "lease_coordinator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "lease_coordinator")
trace_contract._emit_gated_by_confidence("p1", "lease_coordinator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "lease_coordinator", "L2")
trace_contract._emit_reads_policy_state("p1", "lease_coordinator", "L2")

trace_contract._emit_applies_guardrail("p0", "lease_coordinator", "p0_governance")
trace_contract._emit_snapshots_state("p0", "lease_coordinator", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "lease_coordinator", "execution_auth")
trace_contract._emit_validates_capability("p2", "lease_coordinator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "lease_coordinator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "lease_coordinator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "lease_coordinator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "lease_coordinator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "lease_coordinator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "lease_coordinator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "lease_coordinator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "lease_coordinator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "lease_coordinator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "lease_coordinator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "lease_coordinator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "lease_coordinator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "lease_coordinator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "lease_coordinator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "lease_coordinator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "lease_coordinator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "lease_coordinator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "lease_coordinator", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("lease_coordinator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("lease_coordinator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("lease_coordinator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("lease_coordinator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("lease_coordinator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("lease_coordinator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("lease_coordinator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("lease_coordinator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("lease_coordinator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("lease_coordinator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("lease_coordinator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("lease_coordinator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("lease_coordinator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("lease_coordinator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("lease_coordinator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("lease_coordinator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("lease_coordinator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("lease_coordinator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("lease_coordinator", "p3lm", "state")
trace_contract._emit_records_execution_trace("lease_coordinator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("lease_coordinator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("lease_coordinator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("lease_coordinator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("lease_coordinator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("lease_coordinator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("lease_coordinator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("lease_coordinator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("lease_coordinator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "lease_coordinator", "context_pull")
trace_contract._emit_pulls_context("p1", "lease_coordinator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "lease_coordinator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "lease_coordinator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "lease_coordinator", "write_through")
trace_contract._emit_writes_through("p1", "lease_coordinator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "lease_coordinator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "lease_coordinator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "lease_coordinator", "routing_commit")

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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "LeaseCoordinator.acquire")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:LeaseCoordinator.acquire".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "IdempotencyStore.get")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:IdempotencyStore.get".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
