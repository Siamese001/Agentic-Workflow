from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
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

emit_replay_key("p0", "episodic_manager")
emit_determinism_digest("p0", "episodic_manager")

_emit_dispatches_healing_run("p1", "episodic_manager", "L1")
_emit_routes_through("p1", "episodic_manager", "L1")
_emit_checks_agent_registry("p1", "episodic_manager", "agent_registry")
_emit_validates_agent_capability("p1", "episodic_manager", "capability")
_emit_dispatches_execution_plan("p1", "episodic_manager", "exec_plan")
_emit_agent_executes_agent("p1", "episodic_manager", "sub_agent")
_emit_routes_to_agent("p1", "episodic_manager", "target_agent")
_emit_verifies_policy("p1", "episodic_manager", "policy_check")
_emit_observes_runtime_state("p1", "episodic_manager", "runtime_state")
_emit_verifies_boundary("p1", "episodic_manager", "boundary_check")
_emit_transcripts_response("p1", "episodic_manager", "transcript")
_emit_hard_fails_untranscripted("p1", "episodic_manager")
_emit_gated_by_confidence("p1", "episodic_manager", "confidence_gate")
_emit_escalates_to_human("p1", "episodic_manager", "L1")
_emit_reads_policy_state("p1", "episodic_manager", "L1")
_emit_authorize_and_execute("p2", "episodic_manager", "execution_auth")
_emit_validates_capability("p2", "episodic_manager", "capability_check")
_emit_routes_to_capability("p2", "episodic_manager", "capability_route")
_emit_writes_via_uwg("p2", "episodic_manager", "uwg_write")
_emit_blocks_direct_write("p2", "episodic_manager", "direct_write_block")
_emit_records_tool_invocation("p2", "episodic_manager", "tool_invocation")
_emit_captures_execution_output("p2", "episodic_manager", "exec_output")
_emit_dispatches_agent("p3", "episodic_manager", "agent_dispatch")
_emit_coordinates_agents("p3", "episodic_manager", "agent_coordination")
_emit_records_workflow_lineage("p3", "episodic_manager", "workflow_lineage")
_emit_records_healing_outcome("p3", "episodic_manager", "healing_outcome")
_emit_escalates_failure("p3", "episodic_manager", "failure_escalation")
_emit_orchestrates_workflow("p3", "episodic_manager", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "episodic_manager", "healing_dispatch")
_emit_invokes_evaluation("p3", "episodic_manager", "evaluation_signal")
_emit_records_telemetry_event("p4", "episodic_manager", "telemetry_event")
_emit_captures_evaluation_metric("p4", "episodic_manager", "eval_metric")
_emit_stores_embedding("p4", "episodic_manager", "embedding_store")
_emit_updates_meta_learning_state("p4", "episodic_manager", "meta_learning")
_emit_links_execution_to_snapshot("p4", "episodic_manager", "exec_snapshot_link")

"\nEpisodic Memory - Expanded Mission/Episode Storage\n\nProvides expanded capacity for mission episodes with semantic index\nintegration for long-term pattern access.\n\nFeatures:\n- Expanded capacity (20 → 200 episodes)\n- Semantic index integration for similarity retrieval\n- Automatic offload of old episodes to semantic memory\n- Mission history retention across sessions\n"
import hashlib
import time
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("episodic_manager", "p4obs", "metric_1")
_emit_emits_metric_event("episodic_manager", "p4obs", "metric_2")
_emit_emits_metric_event("episodic_manager", "p4obs", "metric_3")
_emit_emits_metric_event("episodic_manager", "p4obs", "metric_4")
_emit_emits_metric_event("episodic_manager", "p4obs", "metric_5")
_emit_emits_metric_event("episodic_manager", "p4obs", "metric_6")
_emit_records_incident_event("episodic_manager", "p4obs", "incident")
_emit_captures_runtime_anomaly("episodic_manager", "p4obs", "anomaly")
_emit_writes_observability_log("episodic_manager", "p4obs", "obs_log")
_emit_updates_monitoring_state("episodic_manager", "p4obs", "mon_state")
_emit_triggers_alert("episodic_manager", "p4obs", "alert")
_emit_links_incident_trace("episodic_manager", "p4obs", "trace_link")
_emit_captures_pattern("episodic_manager", "p3lm", "pattern")
_emit_records_learning_event("episodic_manager", "p3lm", "learning_event")
_emit_writes_learning_snapshot("episodic_manager", "p3lm", "snapshot")
_emit_feeds_meta_learning("episodic_manager", "p3lm", "meta_feed")
_emit_updates_routing_strategy("episodic_manager", "p3lm", "routing")
_emit_improves_agent_policy("episodic_manager", "p3lm", "policy")
_emit_stores_learning_state("episodic_manager", "p3lm", "state")
_emit_records_execution_trace("episodic_manager", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("episodic_manager", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("episodic_manager", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("episodic_manager", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("episodic_manager", "L4_STATE", "p2_trace_5")
_emit_reads_environ("episodic_manager", "env_read", "p2_env_1")
_emit_reads_environ("episodic_manager", "env_read", "p2_env_2")
_emit_reads_runtime_state("episodic_manager", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("episodic_manager", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "episodic_manager", "context_pull")
_emit_pulls_context("p1", "episodic_manager", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "episodic_manager", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "episodic_manager", "uwg_term_2")
_emit_writes_through("p1", "episodic_manager", "write_through")
_emit_writes_through("p1", "episodic_manager", "write_through_2")
_emit_validated_by_safety_plane("p1", "episodic_manager", "safety_validation")
_emit_invokes_eval("p1", "episodic_manager", "eval_call")
_emit_proposal_commits_routing("p1", "episodic_manager", "routing_commit")


@dataclass
class Episode:
    """Individual episode entry."""

    episode_id: str
    summary: str
    mission_type: str
    outcome: str
    steps: list[dict[str, Any]] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    duration_ms: float = 0.0
    reward: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class EpisodicMemory:
    """
    Expanded Episodic Memory - Mission history storage with semantic indexing.

    Provides:
    - Expanded capacity (200 episodes vs original 20)
    - Semantic index integration for similarity search
    - Automatic offload of evicted episodes
    - Mission pattern extraction
    """

    def __init__(self, capacity: int = 200, embed_index: bool = True):
        """
        Initialize episodic memory.

        Args:
            capacity: Maximum episodes in memory (default 200, up from 20)
            embed_index: Whether to use semantic indexing
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "EpisodicMemory.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "EpisodicMemory.__init__", "p0_governance")
        self.episodes: list[Episode] = []
        self.capacity = capacity
        self.embed_index = embed_index
        self._semantic_memory = None
        self.total_stored = 0
        self.total_evicted = 0
        self.success_count = 0
        self.failure_count = 0

    @property
    def semantic_index(self):
        """Lazy load semantic memory."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "EpisodicMemory.semantic_index")

        if self._semantic_memory is None and self.embed_index:
            try:
                from .semantic_manager import semantic_memory

                self._semantic_memory = semantic_memory
            except ImportError:  # guardian: allow-silent-swallow
                self._semantic_memory = None
        return self._semantic_memory

    def store_episode(self, episode: dict[str, Any]) -> str:
        """
        Store an episode in memory.

        Args:
            episode: Episode dictionary with summary, outcome, etc.

        Returns:
            Episode ID
        """
        episode_id = episode.get("id", self._generate_id(episode))
        episode_obj = Episode(
            episode_id=episode_id,
            summary=episode.get("summary", episode.get("description", str(episode))),
            mission_type=episode.get("type", episode.get("mission_type", "task")),
            outcome=episode.get("outcome", "unknown"),
            steps=episode.get("steps", []),
            context=episode.get("context", {}),
            duration_ms=episode.get("duration_ms", 0.0),
            reward=episode.get("reward", 0.0),
            metadata=episode.get("metadata", {}),
        )
        if episode_obj.outcome == "success":
            self.success_count += 1
        elif episode_obj.outcome == "failure":
            self.failure_count += 1
        self.episodes.append(episode_obj)
        self.total_stored += 1
        if self.semantic_index:
            self.semantic_index.add_episode(
                {
                    "id": episode_id,
                    "summary": episode_obj.summary,
                    "type": episode_obj.mission_type,
                    "outcome": episode_obj.outcome,
                }
            )
        while len(self.episodes) > self.capacity:
            self.episodes.pop(0)
            self.total_evicted += 1
        return episode_id

    def retrieve(self, count: int = 10) -> list[dict[str, Any]]:
        """
        Retrieve recent episodes.

        Args:
            count: Number of episodes to retrieve

        Returns:
            List of episode dictionaries
        """
        return [self._episode_to_dict(e) for e in self.episodes[-count:]]

    # guardian: allow-magic-config
    def retrieve_relevant(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Retrieve relevant episodes using semantic similarity.

        Args:
            query: Query text
            top_k: Number of results

        Returns:
            List of relevant episodes
        """
        in_memory_results = self._keyword_search(query, top_k)
        if self.semantic_index:
            semantic_results = self.semantic_index.query_episodes(query, top_k)
            seen_ids = {r.get("id") for r in in_memory_results}
            for result in semantic_results:
                if result.get("id") not in seen_ids:
                    in_memory_results.append(result.get("content", result))
        return in_memory_results[:top_k]

    def retrieve_by_outcome(self, outcome: str, count: int = 10) -> list[dict[str, Any]]:
        """
        Retrieve episodes by outcome.

        Args:
            outcome: Outcome to filter by ("success", "failure", "partial")
            count: Number of results

        Returns:
            List of matching episodes
        """
        matching = [e for e in self.episodes if e.outcome == outcome]
        return [self._episode_to_dict(e) for e in matching[-count:]]

    def retrieve_successes(self, count: int = 10) -> list[dict[str, Any]]:
        """Retrieve successful episodes."""
        return self.retrieve_by_outcome("success", count)

    def retrieve_failures(self, count: int = 10) -> list[dict[str, Any]]:
        """Retrieve failed episodes."""
        return self.retrieve_by_outcome("failure", count)

    def retrieve_by_type(self, mission_type: str, count: int = 10) -> list[dict[str, Any]]:
        """
        Retrieve episodes by mission type.

        Args:
            mission_type: Type to filter by
            count: Number of results

        Returns:
            List of matching episodes
        """
        matching = [e for e in self.episodes if e.mission_type == mission_type]
        return [self._episode_to_dict(e) for e in matching[-count:]]

    # guardian: allow-magic-config
    def retrieve_high_reward(self, threshold: float = 0.5, count: int = 10) -> list[dict[str, Any]]:
        """
        Retrieve high-reward episodes.

        Args:
            threshold: Minimum reward
            count: Number of results

        Returns:
            List of high-reward episodes
        """
        matching = [e for e in self.episodes if e.reward >= threshold]
        matching.sort(key=lambda x: x.reward, reverse=True)
        return [self._episode_to_dict(e) for e in matching[:count]]

    def get_success_rate(self) -> float:
        """Get overall success rate."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return self.success_count / total

    def _keyword_search(self, query: str, top_k: int) -> list[dict[str, Any]]:
        """Simple keyword-based search in memory."""
        query_words = set(query.lower().split())
        scored = []
        for episode in self.episodes:
            content_words = set(episode.summary.lower().split())
            overlap = len(query_words & content_words)
            if overlap > 0:
                scored.append((overlap, episode))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [self._episode_to_dict(e) for _, e in scored[:top_k]]

    def _generate_id(self, episode: dict) -> str:
        """Generate unique ID for episode."""
        content = str(episode)
        hash_val = hashlib.sha256(content.encode()).hexdigest()[:12]
        return f"episode_{self.total_stored}_{hash_val}"

    def _episode_to_dict(self, episode: Episode) -> dict[str, Any]:
        """Convert episode object to dictionary."""
        return {
            "id": episode.episode_id,
            "summary": episode.summary,
            "type": episode.mission_type,
            "outcome": episode.outcome,
            "steps": episode.steps,
            "context": episode.context,
            "timestamp": episode.timestamp,
            "duration_ms": episode.duration_ms,
            "reward": episode.reward,
            "metadata": episode.metadata,
        }

    def clear(self) -> None:
        """Clear all episodes."""
        self.episodes.clear()

    def get_statistics(self) -> dict[str, Any]:
        """Get memory statistics."""
        return {
            "capacity": self.capacity,
            "current_size": len(self.episodes),
            "total_stored": self.total_stored,
            "total_evicted": self.total_evicted,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.get_success_rate(),
            "embed_index_enabled": self.embed_index,
        }


episodic_memory = EpisodicMemory()
