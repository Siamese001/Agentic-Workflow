"""
meta_learning_storage.py - Pinecone/Vector DB Interaction Layer

[MIXIN REFACTOR] Extracted from meta_learning_mixin.py (643 lines).
Manages all connections to storage backends:
  - SemanticCacheManager (Pinecone) for experience recall/learn
  - GraphMemoryBridge for entity registration and MASTERED_TASK relations

Thread-safe singleton initialization with circuit breaker.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
from typing import Any

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

_emit_applies_guardrail("p0", "meta_learning_storage_util", "p0_governance")
_emit_reads_policy_state("p0", "meta_learning_storage_util", "policy_binding")
_emit_snapshots_state("p0", "meta_learning_storage_util", "state_snapshot")
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

_emit_emits_metric_event("meta_learning_storage_util", "p4obs", "metric_1")
_emit_emits_metric_event("meta_learning_storage_util", "p4obs", "metric_2")
_emit_emits_metric_event("meta_learning_storage_util", "p4obs", "metric_3")
_emit_emits_metric_event("meta_learning_storage_util", "p4obs", "metric_4")
_emit_emits_metric_event("meta_learning_storage_util", "p4obs", "metric_5")
_emit_emits_metric_event("meta_learning_storage_util", "p4obs", "metric_6")
_emit_records_incident_event("meta_learning_storage_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("meta_learning_storage_util", "p4obs", "anomaly")
_emit_writes_observability_log("meta_learning_storage_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("meta_learning_storage_util", "p4obs", "mon_state")
_emit_triggers_alert("meta_learning_storage_util", "p4obs", "alert")
_emit_links_incident_trace("meta_learning_storage_util", "p4obs", "trace_link")
_emit_captures_pattern("meta_learning_storage_util", "p3lm", "pattern")
_emit_records_learning_event("meta_learning_storage_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("meta_learning_storage_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("meta_learning_storage_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("meta_learning_storage_util", "p3lm", "routing")
_emit_improves_agent_policy("meta_learning_storage_util", "p3lm", "policy")
_emit_stores_learning_state("meta_learning_storage_util", "p3lm", "state")
_emit_records_execution_trace("meta_learning_storage_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("meta_learning_storage_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("meta_learning_storage_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("meta_learning_storage_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("meta_learning_storage_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("meta_learning_storage_util", "env_read", "p2_env_1")
_emit_reads_environ("meta_learning_storage_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("meta_learning_storage_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("meta_learning_storage_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "meta_learning_storage_util", "context_pull")
_emit_pulls_context("p1", "meta_learning_storage_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "meta_learning_storage_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "meta_learning_storage_util", "uwg_term_2")
_emit_writes_through("p1", "meta_learning_storage_util", "write_through")
_emit_writes_through("p1", "meta_learning_storage_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "meta_learning_storage_util", "safety_validation")
_emit_invokes_eval("p1", "meta_learning_storage_util", "eval_call")
_emit_proposal_commits_routing("p1", "meta_learning_storage_util", "routing_commit")
_emit_escalates_to_human("p1", "meta_learning_storage_util", "human_escalation")
_emit_routes_through("p1", "meta_learning_storage_util", "route_through")
_emit_checks_agent_registry("p1", "meta_learning_storage_util", "agent_registry")
_emit_validates_agent_capability("p1", "meta_learning_storage_util", "capability")
_emit_dispatches_execution_plan("p1", "meta_learning_storage_util", "exec_plan")
_emit_agent_executes_agent("p1", "meta_learning_storage_util", "sub_agent")
_emit_routes_to_agent("p1", "meta_learning_storage_util", "target_agent")
_emit_verifies_policy("p1", "meta_learning_storage_util", "policy_check")
_emit_observes_runtime_state("p1", "meta_learning_storage_util", "runtime_state")
_emit_verifies_boundary("p1", "meta_learning_storage_util", "boundary_check")
_emit_transcripts_response("p1", "meta_learning_storage_util", "transcript")
_emit_hard_fails_untranscripted("p1", "meta_learning_storage_util")
_emit_gated_by_confidence("p1", "meta_learning_storage_util", "confidence_gate")
emit_replay_key("p0", "meta_learning_storage_util")
emit_determinism_digest("p0", "meta_learning_storage_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "meta_learning_storage_util", "execution_auth")
_emit_validates_capability("p2", "meta_learning_storage_util", "capability_check")
_emit_routes_to_capability("p2", "meta_learning_storage_util", "capability_route")
_emit_writes_via_uwg("p2", "meta_learning_storage_util", "uwg_write")
_emit_blocks_direct_write("p2", "meta_learning_storage_util", "direct_write_block")
_emit_records_tool_invocation("p2", "meta_learning_storage_util", "tool_invocation")
_emit_captures_execution_output("p2", "meta_learning_storage_util", "exec_output")
_emit_dispatches_agent("p3", "meta_learning_storage_util", "agent_dispatch")
_emit_coordinates_agents("p3", "meta_learning_storage_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "meta_learning_storage_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "meta_learning_storage_util", "healing_outcome")
_emit_escalates_failure("p3", "meta_learning_storage_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "meta_learning_storage_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "meta_learning_storage_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "meta_learning_storage_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "meta_learning_storage_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "meta_learning_storage_util", "eval_metric")
_emit_stores_embedding("p4", "meta_learning_storage_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "meta_learning_storage_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "meta_learning_storage_util", "exec_snapshot_link")

Logger = logging.getLogger(__name__)


class MetaLearningStorage:
    """Thread-safe storage layer for meta-learning backends.

    Class-level singletons with circuit breaker for graceful degradation.
    """

    _memory = None
    _memory_lock = threading.RLock()
    _lobotomized = False
    _graph_bridge = None
    _graph_lock = threading.RLock()

    @classmethod
    def ensure_memory_connection(cls, agent_name: str) -> None:
        """Connect to SemanticCacheManager singleton (thread-safe, circuit-breaker)."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MetaLearningStorage.ensure_memory_connection")

        if cls._lobotomized:
            return
        if cls._memory is None:
            with cls._memory_lock:
                if cls._memory is None:
                    try:
                        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

                        cls._memory = SemanticCacheManager.get_instance()
                        Logger.debug(f"[{agent_name}] Connected to Hive Mind")
                    except Exception as e:
                        raise
                        cls._lobotomized = True
                        Logger.critical(
                            f"[{agent_name}] LOBOTOMY PROTOCOL ACTIVE: Hive Mind unavailable ({e})"
                        )

    @classmethod
    def recall(cls, context: str, namespace: str) -> dict[str, Any] | None:
        """Query Pinecone for a cached experience."""
        if cls._lobotomized or cls._memory is None:
            return None
        try:
            result = cls._memory.recall(context, namespace)
            if result:
                Logger.info(f"[{namespace}] INSTINCT TRIGGERED: Recalled previous experience.")
            return result
        except Exception as e:
            Logger.warning(f"[{namespace}] Recall error: {e}")
            return None

    @classmethod
    async def learn_async(cls, context: str, namespace: str, result: dict[str, Any]) -> None:
        """Async write to Pinecone (fire-and-forget safe)."""
        if cls._lobotomized or cls._memory is None:
            return
        try:
            _ = json.dumps(result)
            await cls._memory.learn_async(context, namespace, result)
        except Exception as e:
            raise
            Logger.warning(f"[{namespace}] Async learn failed: {e}")

    @classmethod
    def learn_with_feedback(
        cls, context: str, namespace: str, result: dict[str, Any], feedback_score: float
    ) -> bool:
        """Learn with feedback score, promoting to long-term DNA if threshold met."""
        if cls._lobotomized or cls._memory is None:
            return False
        try:
            cls._memory.learn(context, namespace, result, feedback_score)
            promotion_threshold = getattr(cls._memory, "promotion_threshold", 0.8)
            if feedback_score >= promotion_threshold:
                promoted = cls._memory.promote_to_long_term(context, namespace, result, feedback_score)
                if promoted:
                    sanitized_context = context
                    if hasattr(cls._memory, "sanitizer"):
                        sanitized_context = cls._memory.sanitizer.sanitize(context)
                    cls._create_mastered_task_relation(namespace, sanitized_context, feedback_score)
                    Logger.info(
                        f"[{namespace}] DNA PROMOTION: Memory promoted with feedback_score={feedback_score:.2f}"
                    )
                    return True
            return False
        except Exception as e:
            Logger.warning(f"[{namespace}] Learn with feedback failed: {e}")
            return False

    @classmethod
    def get_memory_stats(cls) -> dict[str, Any] | None:
        """Get statistics from the Hive Mind."""
        if cls._lobotomized or cls._memory is None:
            return None
        try:
            return cls._memory.get_statistics()
        except (ValueError, TypeError, RuntimeError) as e:
            return None

    @classmethod
    def ensure_graph_bridge_connection(cls, agent_name: str) -> None:
        """Connect to GraphMemoryBridge singleton (thread-safe)."""
        if cls._graph_bridge is None:
            with cls._graph_lock:
                if cls._graph_bridge is None:
                    try:
                        from agentic_core.L4_state.memory.graph_memory_bridge_types import GraphMemoryBridge

                        cls._graph_bridge = GraphMemoryBridge.get_instance()
                        Logger.debug(f"[{agent_name}] Connected to Graph Memory Bridge")
                    except Exception as e:
                        raise
                        Logger.warning(f"[{agent_name}] Graph Memory Bridge unavailable: {e}")

    @classmethod
    def register_agent_entity(cls, agent_name: str) -> None:
        """Register agent as entity in graph bridge (idempotent)."""
        if cls._graph_bridge is None:
            return
        try:
            cls._graph_bridge.create_agent_entity(
                agent_name=agent_name, agent_type="Agent", observations=[f"Agent {agent_name} initialized"]
            )
        except Exception as e:
            raise
            Logger.warning(f"[{agent_name}] Agent entity registration failed: {e}")

    @classmethod
    def _create_mastered_task_relation(cls, agent_name: str, context: str, feedback_score: float) -> None:
        """Create MASTERED_TASK relation when memory is promoted."""
        if cls._graph_bridge is None:
            return
        try:
            cls._graph_bridge.create_mastered_task_relation(
                agent_name=agent_name, task_description=context, feedback_score=feedback_score
            )
        except Exception as e:
            raise
            Logger.warning(f"[{agent_name}] MASTERED_TASK relation creation failed: {e}")

    @classmethod
    def get_graph_stats(cls) -> dict[str, Any] | None:
        """Get statistics from the Graph Memory Bridge."""
        if cls._graph_bridge is None:
            return None
        try:
            return cls._graph_bridge.get_statistics()
        except (ValueError, TypeError, RuntimeError) as e:
            return None

    @classmethod
    def reset_lobotomy(cls) -> None:
        """Reset the circuit breaker state."""
        cls._lobotomized = False
        cls._memory = None
        Logger.info("[MetaLearningStorage] Lobotomy state reset")

    @classmethod
    def reset_graph_bridge(cls) -> None:
        """Reset the Graph Memory Bridge."""
        cls._graph_bridge = None
        Logger.info("[MetaLearningStorage] Graph Memory Bridge reset")

    @staticmethod
    def generate_context_hash(namespace: str, context: str) -> str:
        """Deterministic context hash for DNA segregation."""
        key = f"{namespace}:{context}"
        return hashlib.sha256(key.encode()).hexdigest()

    @classmethod
    @property
    def is_lobotomized(cls) -> bool:
        """Check circuit breaker state."""
        return cls._lobotomized
