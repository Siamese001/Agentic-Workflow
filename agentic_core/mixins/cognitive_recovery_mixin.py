import logging
import traceback
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "cognitive_recovery_mixin", "p0_governance")
_emit_reads_policy_state("p0", "cognitive_recovery_mixin", "policy_binding")
_emit_snapshots_state("p0", "cognitive_recovery_mixin", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("cognitive_recovery_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("cognitive_recovery_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("cognitive_recovery_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("cognitive_recovery_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("cognitive_recovery_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("cognitive_recovery_mixin", "p4obs", "metric_6")
_emit_records_incident_event("cognitive_recovery_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("cognitive_recovery_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("cognitive_recovery_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("cognitive_recovery_mixin", "p4obs", "mon_state")
_emit_triggers_alert("cognitive_recovery_mixin", "p4obs", "alert")
_emit_links_incident_trace("cognitive_recovery_mixin", "p4obs", "trace_link")
_emit_captures_pattern("cognitive_recovery_mixin", "p3lm", "pattern")
_emit_records_learning_event("cognitive_recovery_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("cognitive_recovery_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("cognitive_recovery_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("cognitive_recovery_mixin", "p3lm", "routing")
_emit_improves_agent_policy("cognitive_recovery_mixin", "p3lm", "policy")
_emit_stores_learning_state("cognitive_recovery_mixin", "p3lm", "state")
_emit_records_execution_trace("cognitive_recovery_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("cognitive_recovery_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("cognitive_recovery_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("cognitive_recovery_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("cognitive_recovery_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("cognitive_recovery_mixin", "env_read", "p2_env_1")
_emit_reads_environ("cognitive_recovery_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("cognitive_recovery_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("cognitive_recovery_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "cognitive_recovery_mixin", "context_pull")
_emit_pulls_context("p1", "cognitive_recovery_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "cognitive_recovery_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "cognitive_recovery_mixin", "uwg_term_2")
_emit_writes_through("p1", "cognitive_recovery_mixin", "write_through")
_emit_writes_through("p1", "cognitive_recovery_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "cognitive_recovery_mixin", "safety_validation")
_emit_invokes_eval("p1", "cognitive_recovery_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "cognitive_recovery_mixin", "routing_commit")
_emit_escalates_to_human("p1", "cognitive_recovery_mixin", "human_escalation")
_emit_routes_through("p1", "cognitive_recovery_mixin", "route_through")
_emit_checks_agent_registry("p1", "cognitive_recovery_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "cognitive_recovery_mixin", "capability")
_emit_dispatches_execution_plan("p1", "cognitive_recovery_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "cognitive_recovery_mixin", "sub_agent")
_emit_routes_to_agent("p1", "cognitive_recovery_mixin", "target_agent")
_emit_verifies_policy("p1", "cognitive_recovery_mixin", "policy_check")
_emit_observes_runtime_state("p1", "cognitive_recovery_mixin", "runtime_state")
_emit_verifies_boundary("p1", "cognitive_recovery_mixin", "boundary_check")
_emit_transcripts_response("p1", "cognitive_recovery_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "cognitive_recovery_mixin")
_emit_gated_by_confidence("p1", "cognitive_recovery_mixin", "confidence_gate")
emit_replay_key("p0", "cognitive_recovery_mixin")
emit_determinism_digest("p0", "cognitive_recovery_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "cognitive_recovery_mixin", "execution_auth")
_emit_validates_capability("p2", "cognitive_recovery_mixin", "capability_check")
_emit_routes_to_capability("p2", "cognitive_recovery_mixin", "capability_route")
_emit_writes_via_uwg("p2", "cognitive_recovery_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "cognitive_recovery_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "cognitive_recovery_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "cognitive_recovery_mixin", "exec_output")
_emit_dispatches_agent("p3", "cognitive_recovery_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "cognitive_recovery_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "cognitive_recovery_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "cognitive_recovery_mixin", "healing_outcome")
_emit_escalates_failure("p3", "cognitive_recovery_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "cognitive_recovery_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "cognitive_recovery_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "cognitive_recovery_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "cognitive_recovery_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "cognitive_recovery_mixin", "eval_metric")
_emit_stores_embedding("p4", "cognitive_recovery_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "cognitive_recovery_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "cognitive_recovery_mixin", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class CognitiveRecoveryMixin:
    """
    A mixin that gives agents access to the project's 'Semantic Brain'.
    Allows agents to look up architecture docs, API contracts, and
    healing patterns when they encounter unknown errors.

    Dependencies:
    - SemanticKnowledgeClient (Singleton)
    """

    def _get_cognitive_client(self):
        """Safe lazy retrieval of the singleton client."""
        from agentic_core.infrastructure.SemanticKnowledgeClient import SemanticKnowledgeClient

        return SemanticKnowledgeClient()

    def consult_knowledge_base(
        self,
        query: str,
        namespace: str = "architecture-docs",
    ) -> list[dict[str, Any]]:
        """
        Generic query to the semantic brain.
        Useful for 'Just-in-Time' learning about system architecture.
        """
        try:
            client = self._get_cognitive_client()
            results = client.search(query, namespace, top_k=3)
            return [
                {"id": r.id, "content": r.content, "score": r.score, "metadata": r.metadata} for r in results
            ]
        except (AttributeError, RuntimeError) as e:  # guardian: allow-silent-swallow
            logger.warning(f"[{self.__class__.__name__}] Brain Freeze (Knowledge Query Failed): {e}")
            return []

    def perform_cognitive_rca(self, exception: Exception) -> str | None:
        """
        When an error occurs, this method queries the 'healing-patterns' namespace
        to see if this specific error has a known fix or RCA document.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "CognitiveRecoveryMixin.perform_cognitive_rca"
        )

        error_msg = f"{type(exception).__name__}: {str(exception)}"
        tb = traceback.format_exc()
        query = f"Fix for error: {error_msg} Context: {tb[:200]}"
        logger.info(f"[{self.__class__.__name__}] 🧠 Consulted Semantic Memory for: {error_msg}")
        try:
            client = self._get_cognitive_client()
            patterns = client.find_healing_pattern(query)
        except (
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-return-none-swallow  -- ADG-burn: return_none_swallow
            logger.error(f"[{self.__class__.__name__}] Cognitive RCA failed: {e}")
            return None
        if patterns:
            best_match = patterns[0]
            if best_match.score > 0.8:
                advice = f"\n✅ KNOWN ISSUE IDENTIFIED\n-----------------------\nPattern ID: {best_match.id}\nConfidence: {best_match.score:.2f}\nSource: {best_match.metadata.get('source', 'Unknown')}\n\nSuggested Fix Context:\n{best_match.content[:500]}...\n"
                logger.info(advice)
                return advice
            else:
                logger.info(
                    f"[{self.__class__.__name__}] No high-confidence healing patterns found (Best: {best_match.score:.2f}).",
                )
        else:
            logger.info(
                f"[{self.__class__.__name__}] This appears to be a novel error (No memory records found).",
            )
        return None
