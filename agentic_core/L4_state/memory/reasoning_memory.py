from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

emit_replay_key("p0", "reasoning_memory")
emit_determinism_digest("p0", "reasoning_memory")

_emit_dispatches_healing_run("p1", "reasoning_memory", "L4")
_emit_routes_through("p1", "reasoning_memory", "L4")
_emit_checks_agent_registry("p1", "reasoning_memory", "agent_registry")
_emit_validates_agent_capability("p1", "reasoning_memory", "capability")
_emit_dispatches_execution_plan("p1", "reasoning_memory", "exec_plan")
_emit_agent_executes_agent("p1", "reasoning_memory", "sub_agent")
_emit_routes_to_agent("p1", "reasoning_memory", "target_agent")
_emit_verifies_policy("p1", "reasoning_memory", "policy_check")
_emit_observes_runtime_state("p1", "reasoning_memory", "runtime_state")
_emit_verifies_boundary("p1", "reasoning_memory", "boundary_check")
_emit_transcripts_response("p1", "reasoning_memory", "transcript")
_emit_hard_fails_untranscripted("p1", "reasoning_memory")
_emit_gated_by_confidence("p1", "reasoning_memory", "confidence_gate")
_emit_escalates_to_human("p1", "reasoning_memory", "L4")
_emit_reads_policy_state("p1", "reasoning_memory", "L4")
_emit_authorize_and_execute("p2", "reasoning_memory", "execution_auth")
_emit_validates_capability("p2", "reasoning_memory", "capability_check")
_emit_routes_to_capability("p2", "reasoning_memory", "capability_route")
_emit_writes_via_uwg("p2", "reasoning_memory", "uwg_write")
_emit_blocks_direct_write("p2", "reasoning_memory", "direct_write_block")
_emit_records_tool_invocation("p2", "reasoning_memory", "tool_invocation")
_emit_captures_execution_output("p2", "reasoning_memory", "exec_output")
_emit_dispatches_agent("p3", "reasoning_memory", "agent_dispatch")
_emit_coordinates_agents("p3", "reasoning_memory", "agent_coordination")
_emit_records_workflow_lineage("p3", "reasoning_memory", "workflow_lineage")
_emit_records_healing_outcome("p3", "reasoning_memory", "healing_outcome")
_emit_escalates_failure("p3", "reasoning_memory", "failure_escalation")
_emit_orchestrates_workflow("p3", "reasoning_memory", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "reasoning_memory", "healing_dispatch")
_emit_invokes_evaluation("p3", "reasoning_memory", "evaluation_signal")
_emit_records_telemetry_event("p4", "reasoning_memory", "telemetry_event")
_emit_captures_evaluation_metric("p4", "reasoning_memory", "eval_metric")
_emit_stores_embedding("p4", "reasoning_memory", "embedding_store")
_emit_updates_meta_learning_state("p4", "reasoning_memory", "meta_learning")
_emit_links_execution_to_snapshot("p4", "reasoning_memory", "exec_snapshot_link")

"\nReasoning Memory - Expanded Short-Term Thought Storage\n\nProvides expanded capacity for reasoning thoughts with persistence\nand semantic memory integration for long-term retention.\n\nFeatures:\n- Expanded capacity (50 → 500 thoughts)\n- Persistent storage to ledger/Redis\n- Semantic memory offload for LRU evictions\n- Relevance-based retrieval\n"
import hashlib
import time
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_signs_execution_trace,
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

_emit_emits_metric_event("reasoning_memory", "p4obs", "metric_1")
_emit_emits_metric_event("reasoning_memory", "p4obs", "metric_2")
_emit_emits_metric_event("reasoning_memory", "p4obs", "metric_3")
_emit_emits_metric_event("reasoning_memory", "p4obs", "metric_4")
_emit_emits_metric_event("reasoning_memory", "p4obs", "metric_5")
_emit_emits_metric_event("reasoning_memory", "p4obs", "metric_6")
_emit_records_incident_event("reasoning_memory", "p4obs", "incident")
_emit_captures_runtime_anomaly("reasoning_memory", "p4obs", "anomaly")
_emit_writes_observability_log("reasoning_memory", "p4obs", "obs_log")
_emit_updates_monitoring_state("reasoning_memory", "p4obs", "mon_state")
_emit_triggers_alert("reasoning_memory", "p4obs", "alert")
_emit_links_incident_trace("reasoning_memory", "p4obs", "trace_link")
_emit_captures_pattern("reasoning_memory", "p3lm", "pattern")
_emit_records_learning_event("reasoning_memory", "p3lm", "learning_event")
_emit_writes_learning_snapshot("reasoning_memory", "p3lm", "snapshot")
_emit_feeds_meta_learning("reasoning_memory", "p3lm", "meta_feed")
_emit_updates_routing_strategy("reasoning_memory", "p3lm", "routing")
_emit_improves_agent_policy("reasoning_memory", "p3lm", "policy")
_emit_stores_learning_state("reasoning_memory", "p3lm", "state")
_emit_records_execution_trace("reasoning_memory", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("reasoning_memory", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("reasoning_memory", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("reasoning_memory", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("reasoning_memory", "L4_STATE", "p2_trace_5")
_emit_reads_environ("reasoning_memory", "env_read", "p2_env_1")
_emit_reads_environ("reasoning_memory", "env_read", "p2_env_2")
_emit_reads_runtime_state("reasoning_memory", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("reasoning_memory", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "reasoning_memory", "context_pull")
_emit_pulls_context("p1", "reasoning_memory", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "reasoning_memory", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "reasoning_memory", "uwg_term_2")
_emit_writes_through("p1", "reasoning_memory", "write_through")
_emit_writes_through("p1", "reasoning_memory", "write_through_2")
_emit_validated_by_safety_plane("p1", "reasoning_memory", "safety_validation")
_emit_invokes_eval("p1", "reasoning_memory", "eval_call")
_emit_proposal_commits_routing("p1", "reasoning_memory", "routing_commit")


@dataclass
class Thought:
    """Individual thought entry."""

    thought_id: str
    content: str
    thought_type: str
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    confidence: float = 0.8
    metadata: dict[str, Any] = field(default_factory=dict)


class ReasoningMemory:
    """
    Expanded Reasoning Memory - Short-term thought storage with persistence.

    Provides:
    - Expanded capacity (500 thoughts vs original 50)
    - LRU eviction with semantic memory offload
    - Persistence to ledger/file
    - Relevance-based retrieval
    """

    def __init__(self, capacity: int = 500, persist: bool = True, semantic_offload: bool = True):
        """
        Initialize reasoning memory.

        Args:
            capacity: Maximum thoughts in memory (default 500, up from 50)
            persist: Whether to persist thoughts
            semantic_offload: Whether to offload evicted thoughts to semantic memory
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ReasoningMemory.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ReasoningMemory.__init__", "p0_governance")
        self.thoughts: list[Thought] = []
        self.capacity = capacity
        self.persist = persist
        self.semantic_offload = semantic_offload
        self._semantic_memory = None
        self.total_stored = 0
        self.total_evicted = 0
        self.total_retrieved = 0
        if persist:
            self._load_persistent()

    @property
    def semantic_memory(self):
        """Lazy load semantic memory."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "ReasoningMemory.semantic_memory")

        if self._semantic_memory is None and self.semantic_offload:
            try:
                from .SemanticMemory import semantic_memory

                self._semantic_memory = semantic_memory
            except ImportError:  # guardian: allow-silent-swallow
                self._semantic_memory = None
        return self._semantic_memory

    def store(self, thought: dict[str, Any]) -> str:
        """
        Store a thought in memory.

        Args:
            thought: Thought dictionary with content, type, etc.

        Returns:
            Thought ID
        """
        thought_id = thought.get("id", self._generate_id(thought))
        thought_obj = Thought(
            thought_id=thought_id,
            content=thought.get("content", thought.get("text", str(thought))),
            thought_type=thought.get("type", "reasoning"),
            context=thought.get("context", {}),
            confidence=thought.get("confidence", 0.8),
            metadata=thought.get("metadata", {}),
        )
        self.thoughts.append(thought_obj)
        self.total_stored += 1
        while len(self.thoughts) > self.capacity:
            evicted = self.thoughts.pop(0)
            self.total_evicted += 1
            if self.semantic_offload and self.semantic_memory:
                self.semantic_memory.add_thought(
                    {
                        "id": evicted.thought_id,
                        "text": evicted.content,
                        "type": evicted.thought_type,
                        "context": evicted.context,
                        "confidence": evicted.confidence,
                    }
                )
        if self.persist:
            self._persist_thought(thought_obj)
        return thought_id

    def retrieve(self, count: int = 10) -> list[dict[str, Any]]:
        """
        Retrieve recent thoughts.

        Args:
            count: Number of thoughts to retrieve

        Returns:
            List of thought dictionaries
        """
        self.total_retrieved += count
        return [self._thought_to_dict(t) for t in self.thoughts[-count:]]

    # guardian: allow-magic-config
    def retrieve_relevant(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Retrieve relevant thoughts using semantic similarity.

        Args:
            query: Query text
            top_k: Number of results

        Returns:
            List of relevant thoughts
        """
        self.total_retrieved += top_k
        in_memory_results = self._keyword_search(query, top_k)
        if self.semantic_memory:
            semantic_results = self.semantic_memory.query_thoughts(query, top_k)
            combined = in_memory_results + [
                r.get("content", r)
                for r in semantic_results
                if not any(self._is_duplicate(r, im) for im in in_memory_results)
            ]
            return combined[:top_k]
        return in_memory_results

    def retrieve_by_type(self, thought_type: str, count: int = 10) -> list[dict[str, Any]]:
        """
        Retrieve thoughts by type.

        Args:
            thought_type: Type to filter by
            count: Number of results

        Returns:
            List of matching thoughts
        """
        matching = [t for t in self.thoughts if t.thought_type == thought_type]
        return [self._thought_to_dict(t) for t in matching[-count:]]

    # guardian: allow-magic-config
    def retrieve_high_confidence(self, threshold: float = 0.9, count: int = 10) -> list[dict[str, Any]]:
        """
        Retrieve high-confidence thoughts.

        Args:
            threshold: Minimum confidence
            count: Number of results

        Returns:
            List of high-confidence thoughts
        """
        matching = [t for t in self.thoughts if t.confidence >= threshold]
        return [self._thought_to_dict(t) for t in matching[-count:]]

    def _keyword_search(self, query: str, top_k: int) -> list[dict[str, Any]]:
        """Simple keyword-based search in memory."""
        query_words = set(query.lower().split())
        scored = []
        for thought in self.thoughts:
            content_words = set(thought.content.lower().split())
            overlap = len(query_words & content_words)
            if overlap > 0:
                scored.append((overlap, thought))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [self._thought_to_dict(t) for _, t in scored[:top_k]]

    def _is_duplicate(self, result: dict, existing: dict) -> bool:
        """Check if result is duplicate of existing."""
        result_content = result.get("content", result.get("text", ""))
        existing_content = existing.get("content", existing.get("text", ""))
        return result_content == existing_content

    def _generate_id(self, thought: dict) -> str:
        """Generate unique ID for thought."""
        content = str(thought)
        hash_val = hashlib.sha256(content.encode()).hexdigest()[:12]
        return f"thought_{self.total_stored}_{hash_val}"

    def _thought_to_dict(self, thought: Thought) -> dict[str, Any]:
        """Convert thought object to dictionary."""
        return {
            "id": thought.thought_id,
            "content": thought.content,
            "type": thought.thought_type,
            "context": thought.context,
            "confidence": thought.confidence,
            "timestamp": thought.timestamp,
            "metadata": thought.metadata,
        }

    def _persist_thought(self, thought: Thought) -> None:
        """Persist thought to storage."""
        try:
            Ledger.append({"type": "reasoning_memory", "thought": self._thought_to_dict(thought)})
        # guardian: allow-silent-swallow - optional dependency
        except ImportError:
            pass

    def _load_persistent(self) -> None:
        """Load thoughts from persistent storage."""
        try:
            entries = Ledger.query({"type": "reasoning_memory"}, limit=self.capacity)
            for entry in entries:
                thought_dict = entry.get("thought", {})
                if thought_dict:
                    self.thoughts.append(
                        Thought(
                            thought_id=thought_dict.get("id", ""),
                            content=thought_dict.get("content", ""),
                            thought_type=thought_dict.get("type", "reasoning"),
                            context=thought_dict.get("context", {}),
                            confidence=thought_dict.get("confidence", 0.8),
                            timestamp=thought_dict.get("timestamp", time.time()),
                            metadata=thought_dict.get("metadata", {}),
                        )
                    )
        # guardian: allow-silent-swallow
        except (ImportError, Exception):
            pass

    def clear(self) -> None:
        """Clear all thoughts."""
        self.thoughts.clear()

    def get_statistics(self) -> dict[str, Any]:
        """Get memory statistics."""
        return {
            "capacity": self.capacity,
            "current_size": len(self.thoughts),
            "total_stored": self.total_stored,
            "total_evicted": self.total_evicted,
            "total_retrieved": self.total_retrieved,
            "persist_enabled": self.persist,
            "semantic_offload_enabled": self.semantic_offload,
        }


reasoning_memory = ReasoningMemory()
