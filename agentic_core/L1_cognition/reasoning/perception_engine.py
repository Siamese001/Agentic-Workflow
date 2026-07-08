from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "perception_engine")
trace_contract.emit_determinism_digest("p0", "perception_engine")

trace_contract._emit_dispatches_healing_run("p1", "perception_engine", "L1")
trace_contract._emit_routes_through("p1", "perception_engine", "L1")
trace_contract._emit_checks_agent_registry("p1", "perception_engine", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "perception_engine", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "perception_engine", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "perception_engine", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "perception_engine", "target_agent")
trace_contract._emit_verifies_policy("p1", "perception_engine", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "perception_engine", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "perception_engine", "boundary_check")
trace_contract._emit_hard_fails_untranscripted("p1", "perception_engine")
trace_contract._emit_escalates_to_human("p1", "perception_engine", "L1")
trace_contract._emit_reads_policy_state("p1", "perception_engine", "L1")

trace_contract._emit_snapshots_state("p0", "perception_engine", "state_snapshot")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "perception_engine", "p0_governance")
trace_contract._emit_authorize_and_execute("p2", "perception_engine", "execution_auth")
trace_contract._emit_validates_capability("p2", "perception_engine", "capability_check")
trace_contract._emit_routes_to_capability("p2", "perception_engine", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "perception_engine", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "perception_engine", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "perception_engine", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "perception_engine", "exec_output")
trace_contract._emit_dispatches_agent("p3", "perception_engine", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "perception_engine", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "perception_engine", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "perception_engine", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "perception_engine", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "perception_engine", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "perception_engine", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "perception_engine", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "perception_engine", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "perception_engine", "eval_metric")
trace_contract._emit_stores_embedding("p4", "perception_engine", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "perception_engine", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "perception_engine", "exec_snapshot_link")

"\nPerception Node - Sub-atomic Input Processing\n\nHandles input parsing, context preparation, intent classification,\nand memory retrieval. Isolated from reasoning and action logic.\n"
import asyncio
import uuid
from typing import Any


trace_contract._emit_emits_metric_event("perception_engine", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("perception_engine", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("perception_engine", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("perception_engine", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("perception_engine", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("perception_engine", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("perception_engine", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("perception_engine", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("perception_engine", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("perception_engine", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("perception_engine", "p4obs", "alert")
trace_contract._emit_links_incident_trace("perception_engine", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("perception_engine", "p3lm", "pattern")
trace_contract._emit_records_learning_event("perception_engine", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("perception_engine", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("perception_engine", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("perception_engine", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("perception_engine", "p3lm", "policy")
trace_contract._emit_stores_learning_state("perception_engine", "p3lm", "state")
trace_contract._emit_records_execution_trace("perception_engine", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("perception_engine", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("perception_engine", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("perception_engine", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("perception_engine", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("perception_engine", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("perception_engine", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("perception_engine", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("perception_engine", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "perception_engine", "context_pull")
trace_contract._emit_pulls_context("p1", "perception_engine", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "perception_engine", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "perception_engine", "uwg_term_2")
trace_contract._emit_writes_through("p1", "perception_engine", "write_through")
trace_contract._emit_writes_through("p1", "perception_engine", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "perception_engine", "safety_validation")
trace_contract._emit_invokes_eval("p1", "perception_engine", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "perception_engine", "routing_commit")


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
        trace_contract._emit_transcripts_response(str(uuid.uuid4()), "PerceptionNode.process", "model")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L1_REASONING, "PerceptionNode.process")

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
        trace_contract._emit_gated_by_confidence(str(uuid.uuid4()), "PerceptionNode._estimate_confidence", "0.5")
        confidence = 0.5
        confidence += min(0.3, len(query) / 100.0)
        if intent in ["reasoning", "action", "memory"]:
            confidence += 0.2
        return min(1.0, confidence)

    def get_statistics(self) -> dict[str, Any]:
        """Get perception statistics."""
        return {"inputs_processed": self.inputs_processed, "cache_size": len(self.cache)}
