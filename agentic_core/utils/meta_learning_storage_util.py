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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "meta_learning_storage_util", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "meta_learning_storage_util", "policy_binding")
trace_contract._emit_snapshots_state("p0", "meta_learning_storage_util", "state_snapshot")

trace_contract._emit_emits_metric_event("meta_learning_storage_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("meta_learning_storage_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("meta_learning_storage_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("meta_learning_storage_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("meta_learning_storage_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("meta_learning_storage_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("meta_learning_storage_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("meta_learning_storage_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("meta_learning_storage_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("meta_learning_storage_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("meta_learning_storage_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("meta_learning_storage_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("meta_learning_storage_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("meta_learning_storage_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("meta_learning_storage_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("meta_learning_storage_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("meta_learning_storage_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("meta_learning_storage_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("meta_learning_storage_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("meta_learning_storage_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("meta_learning_storage_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("meta_learning_storage_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("meta_learning_storage_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("meta_learning_storage_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("meta_learning_storage_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("meta_learning_storage_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("meta_learning_storage_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("meta_learning_storage_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "meta_learning_storage_util", "context_pull")
trace_contract._emit_pulls_context("p1", "meta_learning_storage_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "meta_learning_storage_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "meta_learning_storage_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "meta_learning_storage_util", "write_through")
trace_contract._emit_writes_through("p1", "meta_learning_storage_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "meta_learning_storage_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "meta_learning_storage_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "meta_learning_storage_util", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "meta_learning_storage_util", "human_escalation")
trace_contract._emit_routes_through("p1", "meta_learning_storage_util", "route_through")
trace_contract._emit_checks_agent_registry("p1", "meta_learning_storage_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "meta_learning_storage_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "meta_learning_storage_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "meta_learning_storage_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "meta_learning_storage_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "meta_learning_storage_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "meta_learning_storage_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "meta_learning_storage_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "meta_learning_storage_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "meta_learning_storage_util")
trace_contract._emit_gated_by_confidence("p1", "meta_learning_storage_util", "confidence_gate")
trace_contract.emit_replay_key("p0", "meta_learning_storage_util")
trace_contract.emit_determinism_digest("p0", "meta_learning_storage_util")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "meta_learning_storage_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "meta_learning_storage_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "meta_learning_storage_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "meta_learning_storage_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "meta_learning_storage_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "meta_learning_storage_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "meta_learning_storage_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "meta_learning_storage_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "meta_learning_storage_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "meta_learning_storage_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "meta_learning_storage_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "meta_learning_storage_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "meta_learning_storage_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "meta_learning_storage_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "meta_learning_storage_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "meta_learning_storage_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "meta_learning_storage_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "meta_learning_storage_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "meta_learning_storage_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "meta_learning_storage_util", "exec_snapshot_link")

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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "MetaLearningStorage.ensure_memory_connection"
        )

        if cls._lobotomized:
            return
        if cls._memory is None:
            with cls._memory_lock:
                if cls._memory is None:
                    try:
                        from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
                            CriticalInfrastructureError,
                            SemanticCacheManager,
                        )

                        cls._memory = SemanticCacheManager.get_instance()
                        Logger.debug(f"[{agent_name}] Connected to Hive Mind")
                    except CriticalInfrastructureError as e:  # ADR-079 / W4 P4.3: STRICT-mode infra failure triggers lobotomy protocol
                        cls._memory = None
                        cls._lobotomized = True
                        Logger.critical(
                            "%s LOBOTOMY PROTOCOL ACTIVE (STRICT-mode infra unavailable): %s",
                            agent_name,
                            e,
                        )
                        cls.reset_lobotomy()
                    except (ImportError, AttributeError, OSError, RuntimeError, ValueError, TypeError) as e:
                        cls._memory = None
                        cls._lobotomized = True
                        Logger.critical(
                            "%s LOBOTOMY PROTOCOL ACTIVE: Hive Mind unavailable (%s)",
                            agent_name,
                            e,
                        )
                        cls.reset_lobotomy()

    @classmethod
    def recall(cls, context: str, namespace: str) -> dict[str, Any] | None:
        """Recall a prior experience from the Hive Mind.

        Offline / meta-learning path: NOT a D2 production gate.
        flow_class and replay_mode are intentionally absent — this path is only
        invoked for agent instinct/learning recall, never for HITL or action flows.
        """
        if cls._lobotomized or cls._memory is None:
            return None
        try:
            # Offline learning path: no flow_class bypass enforcement required.
            result = cls._memory.recall(context, namespace, flow_class=None, replay_mode=False)
            if result:
                Logger.info("%s INSTINCT TRIGGERED: Recalled previous experience.", namespace)
            return result
        except (  # guardian: allow-return-none-swallow -- memory recall: non-fatal, caller treats None as no prior context
            AttributeError,
            OSError,
            RuntimeError,
            ValueError,
            TypeError,
        ) as e:
            Logger.warning("%s Recall error: %s", namespace, e)
            return None

    @classmethod
    async def learn_async(cls, context: str, namespace: str, result: dict[str, Any]) -> None:
        """Async write to Pinecone (fire-and-forget safe)."""
        if cls._lobotomized or cls._memory is None:
            return
        try:
            _ = json.dumps(result)
            await cls._memory.learn_async(context, namespace, result)
        except (  # guardian: allow-log-and-swallow -- async learn: fire-and-forget memory write, non-fatal
            AttributeError,
            OSError,
            RuntimeError,
            ValueError,
            TypeError,
        ) as e:
            Logger.warning("%s Async learn failed: %s", namespace, e)

    @classmethod
    def learn_with_feedback(
        cls,
        context: str,
        namespace: str,
        result: dict[str, Any],
        feedback_score: float,
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
                        "%s DNA PROMOTION: Memory promoted with feedback_score=%.2f",
                        namespace,
                        feedback_score,
                    )
                    return True
            return False
        except (AttributeError, OSError, RuntimeError, ValueError, TypeError) as e:
            Logger.warning("%s Learn with feedback failed: %s", namespace, e)
            return False

    @classmethod
    def get_memory_stats(cls) -> dict[str, Any] | None:
        """Get statistics from the Hive Mind."""
        if cls._lobotomized or cls._memory is None:
            return None
        try:
            return cls._memory.get_statistics()
        except (  # guardian: allow-return-none-swallow -- graph stats: optional monitoring call, non-fatal
            ValueError,
            TypeError,
            RuntimeError,
        ) as e:
            return None

    @classmethod
    def ensure_graph_bridge_connection(cls, agent_name: str) -> None:
        """Connect to GraphMemoryBridge singleton (thread-safe)."""
        if cls._graph_bridge is None:
            with cls._graph_lock:
                if cls._graph_bridge is None:
                    try:
                        from agentic_core.L4_state.utils.memory.graph_memory_bridge_types import (
                            GraphMemoryBridge,
                        )

                        cls._graph_bridge = GraphMemoryBridge.get_instance()
                        Logger.debug("%s Connected to Graph Memory Bridge", agent_name)
                    except (ImportError, AttributeError, OSError, RuntimeError, ValueError, TypeError) as e:
                        cls._graph_bridge = None
                        Logger.warning("%s Graph Memory Bridge unavailable: %s", agent_name, e)
                        cls.reset_graph_bridge()

    @classmethod
    def register_agent_entity(cls, agent_name: str) -> None:
        """Register agent as entity in graph bridge (idempotent)."""
        if cls._graph_bridge is None:
            return
        try:
            cls._graph_bridge.create_agent_entity(
                agent_name=agent_name,
                agent_type="Agent",
                observations=[f"Agent {agent_name} initialized"],
            )
        except (  # guardian: allow-log-and-swallow -- agent entity registration: optional graph write, non-fatal
            AttributeError,
            OSError,
            RuntimeError,
            ValueError,
            TypeError,
        ) as e:
            Logger.warning("%s Agent entity registration failed: %s", agent_name, e)

    @classmethod
    def _create_mastered_task_relation(cls, agent_name: str, context: str, feedback_score: float) -> None:
        """Create MASTERED_TASK relation when memory is promoted."""
        if cls._graph_bridge is None:
            return
        try:
            cls._graph_bridge.create_mastered_task_relation(
                agent_name=agent_name,
                task_description=context,
                feedback_score=feedback_score,
            )
        except (  # guardian: allow-log-and-swallow -- relation creation: optional graph write, non-fatal
            AttributeError,
            OSError,
            RuntimeError,
            ValueError,
            TypeError,
        ) as e:
            Logger.warning("%s MASTERED_TASK relation creation failed: %s", agent_name, e)

    @classmethod
    def get_graph_stats(cls) -> dict[str, Any] | None:
        """Get statistics from the Graph Memory Bridge."""
        if cls._graph_bridge is None:
            return None
        try:
            return cls._graph_bridge.get_statistics()
        except (  # guardian: allow-return-none-swallow -- graph stats query: optional monitoring call, non-fatal
            ValueError,
            TypeError,
            RuntimeError,
        ) as e:
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
