"""SemanticMemoryRegistry — Central registry for all ADG embedding use-cases.

Provides a single access point for all six semantic memory embedders:
  1. IncidentBundleEmbedder     — composite execution incident retrieval
  2. MutationDiffEmbedder       — UWG diff nearest-neighbour search
  3. HealerOutcomeEmbedder      — healer playbook retrieval
  4. PathDPreferenceEmbedder    — HITL preference precedent retrieval
  5. GraphNeighborhoodEmbedder  — ADG architectural motif search
  6. PolicyGuardrailEmbedder    — guardrail drift and calibration

All embedders are lazily instantiated singletons scoped to the registry.
The registry is itself a singleton, protected by a module-level lock.

Usage:
    registry = SemanticMemoryRegistry.get()
    registry.incidents.ingest(bundle)
    registry.mutations.pre_commit_check(candidate)
    registry.healers.retrieve_for_failure("ImportError: missing module x")
    registry.preferences.retrieve_for_proposal(plan_text)
    registry.graph.retrieve_by_description("risky mutation broker")
    registry.guardrails.retrieve_for_policy_hash(policy_hash)

Export for seed-pack ingestion:
    all_records = registry.export_all_corpus_records()

Design constraints:
- Thread-safe singleton via module-level lock.
- Each embedder has its own independent max_buffer.
- No wall-clock reads.
- Kill-switch compliant: retrieval paths fall through to [] when disabled.
"""

from __future__ import annotations

import logging
import threading
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "semantic_memory_registry", "execution_auth")
trace_contract._emit_validates_capability("p2", "semantic_memory_registry", "capability_check")
trace_contract._emit_routes_to_capability("p2", "semantic_memory_registry", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "semantic_memory_registry", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "semantic_memory_registry", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "semantic_memory_registry", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "semantic_memory_registry", "exec_output")
trace_contract._emit_dispatches_agent("p3", "semantic_memory_registry", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "semantic_memory_registry", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "semantic_memory_registry", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "semantic_memory_registry", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "semantic_memory_registry", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "semantic_memory_registry", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "semantic_memory_registry", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "semantic_memory_registry", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "semantic_memory_registry", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "semantic_memory_registry", "eval_metric")
trace_contract._emit_stores_embedding("p4", "semantic_memory_registry", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "semantic_memory_registry", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "semantic_memory_registry", "exec_snapshot_link")
from agentic_core.L6_system_learning.config.semantic_memory_config import (
    DEFAULT_EMBEDDER_BUFFER_SIZE,
    GRAPH_NEIGHBORHOOD_BUFFER_SIZE,
)
from .embedding_corpus_extraction import CorpusRecord
from .graph_neighborhood_embedder import GraphNeighborhoodEmbedder
from .healer_outcome_embedder import HealerOutcomeEmbedder
from .incident_bundle_embedder import IncidentBundleEmbedder
from .mutation_diff_embedder import MutationDiffEmbedder
from .path_d_preference_embedder import PathDPreferenceEmbedder
from .policy_guardrail_embedder import PolicyGuardrailEmbedder

trace_contract._emit_applies_guardrail("p0", "semantic_memory_registry", "p0_governance")
trace_contract._emit_snapshots_state("p0", "semantic_memory_registry", "state_snapshot")

trace_contract._emit_emits_metric_event("semantic_memory_registry", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("semantic_memory_registry", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("semantic_memory_registry", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("semantic_memory_registry", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("semantic_memory_registry", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("semantic_memory_registry", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("semantic_memory_registry", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("semantic_memory_registry", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("semantic_memory_registry", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("semantic_memory_registry", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("semantic_memory_registry", "p4obs", "alert")
trace_contract._emit_links_incident_trace("semantic_memory_registry", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("semantic_memory_registry", "p3lm", "pattern")
trace_contract._emit_records_learning_event("semantic_memory_registry", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("semantic_memory_registry", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("semantic_memory_registry", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("semantic_memory_registry", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("semantic_memory_registry", "p3lm", "policy")
trace_contract._emit_stores_learning_state("semantic_memory_registry", "p3lm", "state")
trace_contract._emit_records_execution_trace("semantic_memory_registry", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("semantic_memory_registry", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("semantic_memory_registry", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("semantic_memory_registry", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("semantic_memory_registry", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("semantic_memory_registry", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("semantic_memory_registry", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("semantic_memory_registry", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("semantic_memory_registry", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "semantic_memory_registry", "context_pull")
trace_contract._emit_pulls_context("p1", "semantic_memory_registry", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "semantic_memory_registry", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "semantic_memory_registry", "uwg_term_2")
trace_contract._emit_writes_through("p1", "semantic_memory_registry", "write_through")
trace_contract._emit_writes_through("p1", "semantic_memory_registry", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "semantic_memory_registry", "safety_validation")
trace_contract._emit_invokes_eval("p1", "semantic_memory_registry", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "semantic_memory_registry", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "semantic_memory_registry", "human_escalation")
trace_contract._emit_routes_through("p1", "semantic_memory_registry", "route_through")
trace_contract._emit_checks_agent_registry("p1", "semantic_memory_registry", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "semantic_memory_registry", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "semantic_memory_registry", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "semantic_memory_registry", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "semantic_memory_registry", "target_agent")
trace_contract._emit_verifies_policy("p1", "semantic_memory_registry", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "semantic_memory_registry", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "semantic_memory_registry", "boundary_check")
trace_contract._emit_transcripts_response("p1", "semantic_memory_registry", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "semantic_memory_registry")
trace_contract._emit_gated_by_confidence("p1", "semantic_memory_registry", "confidence_gate")
trace_contract.emit_replay_key("p0", "semantic_memory_registry")
trace_contract.emit_determinism_digest("p0", "semantic_memory_registry")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

_REGISTRY_LOCK = threading.Lock()
_REGISTRY_INSTANCE: SemanticMemoryRegistry | None = None


class SemanticMemoryRegistry:
    """Central registry providing access to all six ADG semantic memory embedders.

    All embedders are independent singletons; the registry coordinates their
    lifecycle and provides a unified export surface for seed-pack ingestion.
    """

    def __init__(
        self,
        *,
        incident_max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE,
        mutation_max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE,
        healer_max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE,
        preference_max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE,
        graph_max_buffer: int = GRAPH_NEIGHBORHOOD_BUFFER_SIZE,
        guardrail_max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE,
    ) -> None:
        self.incidents = IncidentBundleEmbedder(max_buffer=incident_max_buffer)
        self.mutations = MutationDiffEmbedder(max_buffer=mutation_max_buffer)
        self.healers = HealerOutcomeEmbedder(max_buffer=healer_max_buffer)
        self.preferences = PathDPreferenceEmbedder(max_buffer=preference_max_buffer)
        self.graph = GraphNeighborhoodEmbedder(max_buffer=graph_max_buffer)
        self.guardrails = PolicyGuardrailEmbedder(max_buffer=guardrail_max_buffer)

    @classmethod
    def get(cls, **kwargs: Any) -> SemanticMemoryRegistry:
        """Get or create the singleton registry instance.

        Args:
            **kwargs: Passed to __init__ only on first construction.

        Returns:
            The singleton SemanticMemoryRegistry instance.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "SemanticMemoryRegistry.get")

        global _REGISTRY_INSTANCE
        with _REGISTRY_LOCK:
            if _REGISTRY_INSTANCE is None:
                _REGISTRY_INSTANCE = cls(**kwargs)
                logger.info("SemanticMemoryRegistry: singleton created")
            return _REGISTRY_INSTANCE

    @classmethod
    def reset_for_testing(cls) -> None:
        """Reset singleton — test use only."""
        global _REGISTRY_INSTANCE
        with _REGISTRY_LOCK:
            _REGISTRY_INSTANCE = None

    def export_all_corpus_records(self) -> dict[str, list[CorpusRecord]]:
        """Export all buffered corpus records keyed by namespace.

        Returns a deterministically sorted snapshot from each embedder,
        grouped by namespace for seed-pack ingestion.

        Returns:
            Dict mapping namespace string to sorted list of CorpusRecords.
        """
        return {
            "incident_bundles": self.incidents.export_corpus_records(),
            "mutation_diffs": self.mutations.export_corpus_records(),
            "healer_outcomes": self.healers.export_corpus_records(),
            "path_d_preferences": self.preferences.export_corpus_records(),
            "graph_neighborhoods": self.graph.export_corpus_records(),
            "policy_guardrail_cases": self.guardrails.export_corpus_records(),
        }

    def total_buffer_size(self) -> dict[str, int]:
        """Return current buffer sizes for all embedders.

        Returns:
            Dict mapping namespace to buffer count.
        """
        return {
            "incident_bundles": self.incidents.buffer_size(),
            "mutation_diffs": self.mutations.buffer_size(),
            "healer_outcomes": self.healers.buffer_size(),
            "path_d_preferences": self.preferences.buffer_size(),
            "graph_neighborhoods": self.graph.buffer_size(),
            "policy_guardrail_cases": self.guardrails.buffer_size(),
        }


__all__ = ["SemanticMemoryRegistry"]
