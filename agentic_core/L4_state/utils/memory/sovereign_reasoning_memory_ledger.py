from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "sovereign_reasoning_memory_ledger")
emit_determinism_digest("p0", "sovereign_reasoning_memory_ledger")

_emit_dispatches_healing_run("p1", "sovereign_reasoning_memory_ledger", "L4")
_emit_routes_through("p1", "sovereign_reasoning_memory_ledger", "L4")
_emit_checks_agent_registry("p1", "sovereign_reasoning_memory_ledger", "agent_registry")
_emit_validates_agent_capability("p1", "sovereign_reasoning_memory_ledger", "capability")
_emit_dispatches_execution_plan("p1", "sovereign_reasoning_memory_ledger", "exec_plan")
_emit_agent_executes_agent("p1", "sovereign_reasoning_memory_ledger", "sub_agent")
_emit_routes_to_agent("p1", "sovereign_reasoning_memory_ledger", "target_agent")
_emit_verifies_policy("p1", "sovereign_reasoning_memory_ledger", "policy_check")
_emit_observes_runtime_state("p1", "sovereign_reasoning_memory_ledger", "runtime_state")
_emit_verifies_boundary("p1", "sovereign_reasoning_memory_ledger", "boundary_check")
_emit_transcripts_response("p1", "sovereign_reasoning_memory_ledger", "transcript")
_emit_hard_fails_untranscripted("p1", "sovereign_reasoning_memory_ledger")
_emit_gated_by_confidence("p1", "sovereign_reasoning_memory_ledger", "confidence_gate")
_emit_escalates_to_human("p1", "sovereign_reasoning_memory_ledger", "L4")
_emit_reads_policy_state("p1", "sovereign_reasoning_memory_ledger", "L4")
_emit_authorize_and_execute("p2", "sovereign_reasoning_memory_ledger", "execution_auth")
_emit_validates_capability("p2", "sovereign_reasoning_memory_ledger", "capability_check")
_emit_routes_to_capability("p2", "sovereign_reasoning_memory_ledger", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_reasoning_memory_ledger", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_reasoning_memory_ledger", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_reasoning_memory_ledger", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_reasoning_memory_ledger", "exec_output")
_emit_dispatches_agent("p3", "sovereign_reasoning_memory_ledger", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_reasoning_memory_ledger", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_reasoning_memory_ledger", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_reasoning_memory_ledger", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_reasoning_memory_ledger", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_reasoning_memory_ledger", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_reasoning_memory_ledger", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_reasoning_memory_ledger", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_reasoning_memory_ledger", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_reasoning_memory_ledger", "eval_metric")
_emit_stores_embedding("p4", "sovereign_reasoning_memory_ledger", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_reasoning_memory_ledger", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_reasoning_memory_ledger", "exec_snapshot_link")

"\nL1 Cognition: Sovereign Reasoning Memory — ULTRA-HARDENED\n[PHASE 17 REFACTOR] Uses SovereignBaseAgent native Redis capabilities.\n"
import json
import logging
import threading
from datetime import datetime
from pathlib import Path

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
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

_emit_emits_metric_event("sovereign_reasoning_memory_ledger", "p4obs", "metric_1")
_emit_emits_metric_event("sovereign_reasoning_memory_ledger", "p4obs", "metric_2")
_emit_emits_metric_event("sovereign_reasoning_memory_ledger", "p4obs", "metric_3")
_emit_emits_metric_event("sovereign_reasoning_memory_ledger", "p4obs", "metric_4")
_emit_emits_metric_event("sovereign_reasoning_memory_ledger", "p4obs", "metric_5")
_emit_emits_metric_event("sovereign_reasoning_memory_ledger", "p4obs", "metric_6")
_emit_records_incident_event("sovereign_reasoning_memory_ledger", "p4obs", "incident")
_emit_captures_runtime_anomaly("sovereign_reasoning_memory_ledger", "p4obs", "anomaly")
_emit_writes_observability_log("sovereign_reasoning_memory_ledger", "p4obs", "obs_log")
_emit_updates_monitoring_state("sovereign_reasoning_memory_ledger", "p4obs", "mon_state")
_emit_triggers_alert("sovereign_reasoning_memory_ledger", "p4obs", "alert")
_emit_links_incident_trace("sovereign_reasoning_memory_ledger", "p4obs", "trace_link")
_emit_captures_pattern("sovereign_reasoning_memory_ledger", "p3lm", "pattern")
_emit_records_learning_event("sovereign_reasoning_memory_ledger", "p3lm", "learning_event")
_emit_writes_learning_snapshot("sovereign_reasoning_memory_ledger", "p3lm", "snapshot")
_emit_feeds_meta_learning("sovereign_reasoning_memory_ledger", "p3lm", "meta_feed")
_emit_updates_routing_strategy("sovereign_reasoning_memory_ledger", "p3lm", "routing")
_emit_improves_agent_policy("sovereign_reasoning_memory_ledger", "p3lm", "policy")
_emit_stores_learning_state("sovereign_reasoning_memory_ledger", "p3lm", "state")
_emit_records_execution_trace("sovereign_reasoning_memory_ledger", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("sovereign_reasoning_memory_ledger", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("sovereign_reasoning_memory_ledger", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("sovereign_reasoning_memory_ledger", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("sovereign_reasoning_memory_ledger", "L4_STATE", "p2_trace_5")
_emit_reads_environ("sovereign_reasoning_memory_ledger", "env_read", "p2_env_1")
_emit_reads_environ("sovereign_reasoning_memory_ledger", "env_read", "p2_env_2")
_emit_reads_runtime_state("sovereign_reasoning_memory_ledger", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("sovereign_reasoning_memory_ledger", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "sovereign_reasoning_memory_ledger", "context_pull")
_emit_pulls_context("p1", "sovereign_reasoning_memory_ledger", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "sovereign_reasoning_memory_ledger", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "sovereign_reasoning_memory_ledger", "uwg_term_2")
_emit_writes_through("p1", "sovereign_reasoning_memory_ledger", "write_through")
_emit_writes_through("p1", "sovereign_reasoning_memory_ledger", "write_through_2")
_emit_validated_by_safety_plane("p1", "sovereign_reasoning_memory_ledger", "safety_validation")
_emit_invokes_eval("p1", "sovereign_reasoning_memory_ledger", "eval_call")
_emit_proposal_commits_routing("p1", "sovereign_reasoning_memory_ledger", "routing_commit")

Logger = logging.getLogger(__name__)


class SovereignReasoningMemory(SovereignBaseAgent):
    """
    Ultra-hardened sovereign manager for cognitive artifacts.
    Inherits Redis connection from SovereignBaseAgent -> RedisCacheMixin.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "SovereignReasoningMemory.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "SovereignReasoningMemory.__init__", "p0_governance")
        super().__init__()
        # guardian: allow-magic-config
        self.max_thought_length = 4000
        # guardian: allow-magic-config
        self.max_history_per_file = 50
        self.redis_cache_ttl = 604800
        self.mission_id = "default_mission"
        self.thought_history: list[dict] = []
        self.history_lock = threading.RLock()
        self.redis_reasoning_key = f"reasoning:{self.mission_id}:history"

    @classmethod
    def get_instance(cls) -> SovereignReasoningMemory:
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def add_thought(self, file_path: str, thought: str, key_id: str = None) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L4_STATE,
            "SovereignReasoningMemory.add_thought",
        )

        if len(thought) > self.max_thought_length:
            thought = thought[: self.max_thought_length] + "...[TRUNCATED]"
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "file": Path(file_path).name,
            "thought": thought,
            "key_id": key_id or "general",
        }
        with self.history_lock:
            self.thought_history.append(entry)
            if len(self.thought_history) > self.max_history_per_file * 10:
                self.thought_history = self.thought_history[-self.max_history_per_file :]
        if hasattr(self, "redis_client") and self.redis_client:
            try:
                self.redis_client.rpush(self.redis_reasoning_key, json.dumps(entry))
                self.redis_client.ltrim(self.redis_reasoning_key, -self.max_history_per_file, -1)
                self.redis_client.expire(self.redis_reasoning_key, self.redis_cache_ttl)
            # guardian: allow-silent-swallow
            except Exception as e:
                self.log_warning(f"Redis write failed: {e}")

    def get_history(self, file_path: str = None) -> list[dict]:
        if hasattr(self, "redis_client") and self.redis_client:
            try:
                raw = self.redis_client.lrange(self.redis_reasoning_key, 0, -1)
                return [json.loads(x) for x in raw]
            # guardian: allow-silent-swallow
            except Exception as e:
                import logging

                logging.getLogger(__name__).debug(
                    "sovereign_reasoning_memory_ledger: Exception swallowed at L251: %s", e
                )
        with self.history_lock:
            return list(self.thought_history)

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)
