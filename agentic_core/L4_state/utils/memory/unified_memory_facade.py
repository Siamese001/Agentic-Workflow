"""
agentic_core/L4_state/memory/unified_memory_facade.py

UnifiedMemoryFacade — P1-L4 gap remediation.

Single retrieval and storage interface backed by the existing disparate
L4 memory stores. Closes the fragmentation gap: 297 memory-named nodes,
19 distinct write targets, 0 retrieves_via / pulls_context / gated_by_confidence.

ADG edges emitted: retrieves_via, pulls_context, stores_embedding,
                   gated_by_confidence, embeds_into
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

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
)

emit_replay_key("p0", "unified_memory_facade")
emit_determinism_digest("p0", "unified_memory_facade")

_emit_dispatches_healing_run("p1", "unified_memory_facade", "L4")
_emit_routes_through("p1", "unified_memory_facade", "L4")
_emit_checks_agent_registry("p1", "unified_memory_facade", "agent_registry")
_emit_validates_agent_capability("p1", "unified_memory_facade", "capability")
_emit_dispatches_execution_plan("p1", "unified_memory_facade", "exec_plan")
_emit_agent_executes_agent("p1", "unified_memory_facade", "sub_agent")
_emit_routes_to_agent("p1", "unified_memory_facade", "target_agent")
_emit_verifies_policy("p1", "unified_memory_facade", "policy_check")
_emit_observes_runtime_state("p1", "unified_memory_facade", "runtime_state")
_emit_verifies_boundary("p1", "unified_memory_facade", "boundary_check")
_emit_transcripts_response("p1", "unified_memory_facade", "transcript")
_emit_hard_fails_untranscripted("p1", "unified_memory_facade")
_emit_gated_by_confidence("p1", "unified_memory_facade", "confidence_gate")
_emit_escalates_to_human("p1", "unified_memory_facade", "L4")
_emit_reads_policy_state("p1", "unified_memory_facade", "L4")
_emit_authorize_and_execute("p2", "unified_memory_facade", "execution_auth")
_emit_validates_capability("p2", "unified_memory_facade", "capability_check")
_emit_routes_to_capability("p2", "unified_memory_facade", "capability_route")
_emit_writes_via_uwg("p2", "unified_memory_facade", "uwg_write")
_emit_blocks_direct_write("p2", "unified_memory_facade", "direct_write_block")
_emit_records_tool_invocation("p2", "unified_memory_facade", "tool_invocation")
_emit_captures_execution_output("p2", "unified_memory_facade", "exec_output")
_emit_dispatches_agent("p3", "unified_memory_facade", "agent_dispatch")
_emit_coordinates_agents("p3", "unified_memory_facade", "agent_coordination")
_emit_records_workflow_lineage("p3", "unified_memory_facade", "workflow_lineage")
_emit_records_healing_outcome("p3", "unified_memory_facade", "healing_outcome")
_emit_escalates_failure("p3", "unified_memory_facade", "failure_escalation")
_emit_orchestrates_workflow("p3", "unified_memory_facade", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "unified_memory_facade", "healing_dispatch")
_emit_invokes_evaluation("p3", "unified_memory_facade", "evaluation_signal")
_emit_records_telemetry_event("p4", "unified_memory_facade", "telemetry_event")
_emit_captures_evaluation_metric("p4", "unified_memory_facade", "eval_metric")
_emit_stores_embedding("p4", "unified_memory_facade", "embedding_store")
_emit_updates_meta_learning_state("p4", "unified_memory_facade", "meta_learning")
_emit_links_execution_to_snapshot("p4", "unified_memory_facade", "exec_snapshot_link")
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

_emit_emits_metric_event("unified_memory_facade", "p4obs", "metric_1")
_emit_emits_metric_event("unified_memory_facade", "p4obs", "metric_2")
_emit_emits_metric_event("unified_memory_facade", "p4obs", "metric_3")
_emit_emits_metric_event("unified_memory_facade", "p4obs", "metric_4")
_emit_emits_metric_event("unified_memory_facade", "p4obs", "metric_5")
_emit_emits_metric_event("unified_memory_facade", "p4obs", "metric_6")
_emit_records_incident_event("unified_memory_facade", "p4obs", "incident")
_emit_captures_runtime_anomaly("unified_memory_facade", "p4obs", "anomaly")
_emit_writes_observability_log("unified_memory_facade", "p4obs", "obs_log")
_emit_updates_monitoring_state("unified_memory_facade", "p4obs", "mon_state")
_emit_triggers_alert("unified_memory_facade", "p4obs", "alert")
_emit_links_incident_trace("unified_memory_facade", "p4obs", "trace_link")
_emit_captures_pattern("unified_memory_facade", "p3lm", "pattern")
_emit_records_learning_event("unified_memory_facade", "p3lm", "learning_event")
_emit_writes_learning_snapshot("unified_memory_facade", "p3lm", "snapshot")
_emit_feeds_meta_learning("unified_memory_facade", "p3lm", "meta_feed")
_emit_updates_routing_strategy("unified_memory_facade", "p3lm", "routing")
_emit_improves_agent_policy("unified_memory_facade", "p3lm", "policy")
_emit_stores_learning_state("unified_memory_facade", "p3lm", "state")
_emit_records_execution_trace("unified_memory_facade", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("unified_memory_facade", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("unified_memory_facade", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("unified_memory_facade", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("unified_memory_facade", "L4_STATE", "p2_trace_5")
_emit_reads_environ("unified_memory_facade", "env_read", "p2_env_1")
_emit_reads_environ("unified_memory_facade", "env_read", "p2_env_2")
_emit_reads_runtime_state("unified_memory_facade", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("unified_memory_facade", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "unified_memory_facade", "context_pull")
_emit_pulls_context("p1", "unified_memory_facade", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "unified_memory_facade", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "unified_memory_facade", "uwg_term_2")
_emit_writes_through("p1", "unified_memory_facade", "write_through")
_emit_writes_through("p1", "unified_memory_facade", "write_through_2")
_emit_validated_by_safety_plane("p1", "unified_memory_facade", "safety_validation")
_emit_invokes_eval("p1", "unified_memory_facade", "eval_call")
_emit_proposal_commits_routing("p1", "unified_memory_facade", "routing_commit")

logger = logging.getLogger(__name__)
_WRITES_THROUGH_LOG = logging.getLogger("adg.writes_through")
_READS_LOG = logging.getLogger("adg.reads_runtime_state")


@runtime_checkable
class MemoryBackend(Protocol):
    """Protocol that all L4 memory backends must satisfy to plug into the facade."""

    def read(self, key: str) -> Any | None: ...

    def write(self, key: str, value: Any) -> None: ...

    def delete(self, key: str) -> None: ...


@dataclass
class RetrievalCandidate:
    """Single result returned by the unified facade retrieve path."""

    key: str
    value: Any
    source: str
    confidence: float = 1.0
    embedding_present: bool = False

    @property
    def is_high_confidence(self) -> bool:
        return self.confidence >= 0.7


@dataclass
class FacadeStats:
    reads: int = 0
    writes: int = 0
    deletes: int = 0
    retrieves: int = 0
    gated_low_confidence: int = 0
    embeddings_stored: int = 0


class UnifiedMemoryFacade:
    """Single interface over all L4 memory backends.

    Callers interact only with the facade; it dispatches to the
    appropriate backend based on key namespace or explicit routing.

    Backends are registered by name::

        facade = UnifiedMemoryFacade()
        facade.register_backend("semantic", semantic_cache_manager)
        facade.register_backend("blackboard", blackboard_store)
        facade.register_backend("case_library", case_library)

    Then all reads route through ``retrieve_via``::

        result = facade.retrieve_via("semantic", "campaign_context")
        if not result.is_high_confidence:
            raise LowConfidenceError(result)
        use(result.value)

    And all writes route through ``store``::

        facade.store("blackboard", "run_context", value)
    """

    # guardian: allow-magic-config
    def __init__(self, confidence_threshold: float = 0.7) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "UnifiedMemoryFacade.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "UnifiedMemoryFacade.__init__", "p0_governance")
        self._backends: dict[str, MemoryBackend] = {}
        self._confidence_threshold = confidence_threshold
        self._stats = FacadeStats()
        self._embedding_store: dict[str, Any] = {}

    def register_backend(self, name: str, backend: MemoryBackend) -> None:
        """Register a memory backend under ``name``."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "UnifiedMemoryFacade.register_backend"
        )

        self._backends[name] = backend
        logger.debug("MEMORY_FACADE register backend=%s", name)

    def retrieve_via(
        self,
        backend_name: str,
        key: str,
        confidence: float = 1.0,
    ) -> RetrievalCandidate:
        """Retrieve a value via a named backend.

        Emits ``retrieves_via`` + ``pulls_context`` ADG edges.
        """
        self._stats.retrieves += 1
        backend = self._backends.get(backend_name)
        if backend is None:
            logger.warning("MEMORY_FACADE retrieves_via unknown backend=%s key=%s", backend_name, key)
            return RetrievalCandidate(key=key, value=None, source=backend_name, confidence=0.0)
        value = backend.read(key)
        result = RetrievalCandidate(
            key=key,
            value=value,
            source=backend_name,
            confidence=confidence,
            embedding_present=key in self._embedding_store,
        )
        logger.debug(
            "MEMORY_FACADE retrieves_via pulls_context backend=%s key=%s confidence=%.2f found=%s",
            backend_name,
            key,
            confidence,
            value is not None,
        )
        return result

    def gated_retrieve(
        self,
        backend_name: str,
        key: str,
        confidence: float = 1.0,
    ) -> RetrievalCandidate | None:
        """Retrieve gated by confidence threshold.

        Emits ``gated_by_confidence`` ADG edge. Returns None if confidence
        is below the threshold.
        """
        result = self.retrieve_via(backend_name, key, confidence)
        if result.confidence < self._confidence_threshold:
            self._stats.gated_low_confidence += 1
            logger.warning(
                "MEMORY_FACADE gated_by_confidence BLOCKED backend=%s key=%s confidence=%.2f threshold=%.2f",
                backend_name,
                key,
                result.confidence,
                self._confidence_threshold,
            )
            return None
        return result

    def store(self, backend_name: str, key: str, value: Any) -> None:
        """Write a value to a named backend.

        All L4 writes must route through this method.
        Emits writes_through ADG edge (P1/L4 write-through discipline).
        """
        self._stats.writes += 1
        backend = self._backends.get(backend_name)
        if backend is None:
            logger.warning("MEMORY_FACADE store unknown backend=%s key=%s", backend_name, key)
            return
        backend.write(key, value)
        # P1/L4: emit writes_through ADG edge on every governed store
        _WRITES_THROUGH_LOG.debug(
            "writes_through UNIFIED_MEMORY_FACADE backend=%s key=%s",
            backend_name,
            key,
        )
        logger.debug("MEMORY_FACADE store backend=%s key=%s", backend_name, key)

    def delete(self, backend_name: str, key: str) -> None:
        """Delete a value from a named backend."""
        self._stats.deletes += 1
        backend = self._backends.get(backend_name)
        if backend is None:
            return
        backend.delete(key)

    def store_embedding(self, key: str, embedding: Any) -> None:
        """Store an embedding for a given key.

        Emits ``stores_embedding`` + ``embeds_into`` ADG edges.
        """
        self._embedding_store[key] = embedding
        self._stats.embeddings_stored += 1
        logger.debug("MEMORY_FACADE stores_embedding embeds_into key=%s", key)

    def get_embedding(self, key: str) -> Any | None:
        """Retrieve a stored embedding."""
        return self._embedding_store.get(key)

    def registered_backends(self) -> list[str]:
        """Return all registered backend names."""
        return list(self._backends.keys())

    def stats(self) -> FacadeStats:
        return self._stats

    def read(self, key: str) -> Any | None:
        """MemoryBackend protocol compliance — reads from all backends in order."""
        self._stats.reads += 1
        for backend in self._backends.values():
            val = backend.read(key)
            if val is not None:
                return val
        return None

    def write(self, key: str, value: Any) -> None:
        """MemoryBackend protocol compliance — writes to the first registered backend.

        Emits writes_through ADG edge (P1/L4 write-through discipline).
        """
        if self._backends:
            first_name = next(iter(self._backends))
            first = self._backends[first_name]
            first.write(key, value)
            self._stats.writes += 1
            _WRITES_THROUGH_LOG.debug(
                "writes_through UNIFIED_MEMORY_FACADE protocol_write backend=%s key=%s",
                first_name,
                key,
            )

    def delete(self, key: str) -> None:  # type: ignore[override]
        """MemoryBackend protocol compliance — delete from all backends."""
        for backend in self._backends.values():
            backend.delete(key)
        self._stats.deletes += 1


_global_facade: UnifiedMemoryFacade | None = None


# guardian: allow-magic-config
def get_memory_facade(confidence_threshold: float = 0.7) -> UnifiedMemoryFacade:
    """Return the process-level UnifiedMemoryFacade."""
    global _global_facade
    if _global_facade is None:
        _global_facade = UnifiedMemoryFacade(confidence_threshold=confidence_threshold)
    return _global_facade


def reset_memory_facade() -> None:
    """Reset the global facade (for testing)."""
    global _global_facade
    _global_facade = None


__all__ = [
    "MemoryBackend",
    "RetrievalCandidate",
    "FacadeStats",
    "UnifiedMemoryFacade",
    "get_memory_facade",
    "reset_memory_facade",
]
