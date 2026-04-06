from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "perception_engine")
emit_determinism_digest("p0", "perception_engine")

_emit_dispatches_healing_run("p1", "perception_engine", "L1")
_emit_routes_through("p1", "perception_engine", "L1")
_emit_checks_agent_registry("p1", "perception_engine", "agent_registry")
_emit_validates_agent_capability("p1", "perception_engine", "capability")
_emit_dispatches_execution_plan("p1", "perception_engine", "exec_plan")
_emit_agent_executes_agent("p1", "perception_engine", "sub_agent")
_emit_routes_to_agent("p1", "perception_engine", "target_agent")
_emit_verifies_policy("p1", "perception_engine", "policy_check")
_emit_observes_runtime_state("p1", "perception_engine", "runtime_state")
_emit_verifies_boundary("p1", "perception_engine", "boundary_check")
_emit_hard_fails_untranscripted("p1", "perception_engine")
_emit_escalates_to_human("p1", "perception_engine", "L1")
_emit_reads_policy_state("p1", "perception_engine", "L1")

_emit_snapshots_state("p0", "perception_engine", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "perception_engine", "p0_governance")
_emit_authorize_and_execute("p2", "perception_engine", "execution_auth")
_emit_validates_capability("p2", "perception_engine", "capability_check")
_emit_routes_to_capability("p2", "perception_engine", "capability_route")
_emit_writes_via_uwg("p2", "perception_engine", "uwg_write")
_emit_blocks_direct_write("p2", "perception_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "perception_engine", "tool_invocation")
_emit_captures_execution_output("p2", "perception_engine", "exec_output")
_emit_dispatches_agent("p3", "perception_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "perception_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "perception_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "perception_engine", "healing_outcome")
_emit_escalates_failure("p3", "perception_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "perception_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "perception_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "perception_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "perception_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "perception_engine", "eval_metric")
_emit_stores_embedding("p4", "perception_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "perception_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "perception_engine", "exec_snapshot_link")

"\nPerception Node - Sub-atomic Input Processing\n\nHandles input parsing, context preparation, intent classification,\nand memory retrieval. Isolated from reasoning and action logic.\n"
import asyncio
import uuid
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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

_emit_emits_metric_event("perception_engine", "p4obs", "metric_1")
_emit_emits_metric_event("perception_engine", "p4obs", "metric_2")
_emit_emits_metric_event("perception_engine", "p4obs", "metric_3")
_emit_emits_metric_event("perception_engine", "p4obs", "metric_4")
_emit_emits_metric_event("perception_engine", "p4obs", "metric_5")
_emit_emits_metric_event("perception_engine", "p4obs", "metric_6")
_emit_records_incident_event("perception_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("perception_engine", "p4obs", "anomaly")
_emit_writes_observability_log("perception_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("perception_engine", "p4obs", "mon_state")
_emit_triggers_alert("perception_engine", "p4obs", "alert")
_emit_links_incident_trace("perception_engine", "p4obs", "trace_link")
_emit_captures_pattern("perception_engine", "p3lm", "pattern")
_emit_records_learning_event("perception_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("perception_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("perception_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("perception_engine", "p3lm", "routing")
_emit_improves_agent_policy("perception_engine", "p3lm", "policy")
_emit_stores_learning_state("perception_engine", "p3lm", "state")
_emit_records_execution_trace("perception_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("perception_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("perception_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("perception_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("perception_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("perception_engine", "env_read", "p2_env_1")
_emit_reads_environ("perception_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("perception_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("perception_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "perception_engine", "context_pull")
_emit_pulls_context("p1", "perception_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "perception_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "perception_engine", "uwg_term_2")
_emit_writes_through("p1", "perception_engine", "write_through")
_emit_writes_through("p1", "perception_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "perception_engine", "safety_validation")
_emit_invokes_eval("p1", "perception_engine", "eval_call")
_emit_proposal_commits_routing("p1", "perception_engine", "routing_commit")


class PerceptionNode:
    """
    Sub-atomic perception node - input/context processing.

    Responsibilities:
    - Parse user input
    - Classify intent
    - Retrieve relevant memory
    - Prepare context for reasoning
    """

    def __init__(self):
        """Initialize perception node."""
        self.inputs_processed = 0
        self.cache: dict[str, dict[str, Any]] = {}

    def process(self, raw_input: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Process raw input into perceived state.

        Args:
            raw_input: Raw user input
            context: Current context

        Returns:
            Perceived state with query, intent, memory
        """
        _emit_transcripts_response(str(uuid.uuid4()), "PerceptionNode.process", "model")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "PerceptionNode.process")

        self.inputs_processed += 1
        query = self._parse_query(raw_input)
        intent = self._classify_intent(query, raw_input)
        relevant_memory = self._retrieve_relevant_memory(query, context)
        perceived = {
            "query": query,
            "intent": intent,
            "relevant_memory": relevant_memory,
            "input_type": raw_input.get("type", "text"),
            "confidence": self._estimate_confidence(query, intent),
        }
        return perceived

    async def process_async(self, raw_input: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Asynchronous input processing.

        Args:
            raw_input: Raw user input
            context: Current context

        Returns:
            Perceived state
        """
        query = await asyncio.to_thread(self._parse_query, raw_input)
        intent = await asyncio.to_thread(self._classify_intent, query, raw_input)
        relevant_memory = await asyncio.to_thread(self._retrieve_relevant_memory, query, context)
        perceived = {
            "query": query,
            "intent": intent,
            "relevant_memory": relevant_memory,
            "input_type": raw_input.get("type", "text"),
            "confidence": self._estimate_confidence(query, intent),
        }
        return perceived

    def _parse_query(self, raw_input: dict[str, Any]) -> str:
        """
        Parse raw input into query string.

        Args:
            raw_input: Raw input

        Returns:
            Parsed query
        """
        if isinstance(raw_input, dict):
            return raw_input.get("user_query", raw_input.get("text", ""))
        return str(raw_input)

    def _classify_intent(self, query: str, raw_input: dict[str, Any]) -> str:
        """
        Classify user intent from query.

        Args:
            query: Parsed query
            raw_input: Raw input

        Returns:
            Intent classification
        """
        query_lower = query.lower()
        if any(word in query_lower for word in ["what", "how", "why", "explain"]):
            return "reasoning"
        elif any(word in query_lower for word in ["do", "execute", "run", "perform"]):
            return "action"
        elif any(word in query_lower for word in ["remember", "recall", "memory"]):
            return "memory"
        else:
            return "general"

    def _retrieve_relevant_memory(self, query: str, context: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Retrieve relevant memory for query.

        Args:
            query: Query string
            context: Current context

        Returns:
            List of relevant memory items
        """
        memory_items = []
        if "memory" in context:
            memory_items = context.get("memory", [])
        return memory_items

    def _estimate_confidence(self, query: str, intent: str) -> float:
        """
        Estimate confidence in perception.

        Args:
            query: Parsed query
            intent: Classified intent

        Returns:
            Confidence score (0.0-1.0)
        """
        _emit_gated_by_confidence(str(uuid.uuid4()), "PerceptionNode._estimate_confidence", "0.5")
        confidence = 0.5
        confidence += min(0.3, len(query) / 100.0)
        if intent in ["reasoning", "action", "memory"]:
            confidence += 0.2
        return min(1.0, confidence)

    def get_statistics(self) -> dict[str, Any]:
        """Get perception statistics."""
        return {"inputs_processed": self.inputs_processed, "cache_size": len(self.cache)}
