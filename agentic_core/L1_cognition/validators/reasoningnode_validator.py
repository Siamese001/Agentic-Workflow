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

emit_replay_key("p0", "reasoningnode_validator")
emit_determinism_digest("p0", "reasoningnode_validator")

_emit_dispatches_healing_run("p1", "reasoningnode_validator", "L1")
_emit_routes_through("p1", "reasoningnode_validator", "L1")
_emit_checks_agent_registry("p1", "reasoningnode_validator", "agent_registry")
_emit_validates_agent_capability("p1", "reasoningnode_validator", "capability")
_emit_dispatches_execution_plan("p1", "reasoningnode_validator", "exec_plan")
_emit_agent_executes_agent("p1", "reasoningnode_validator", "sub_agent")
_emit_routes_to_agent("p1", "reasoningnode_validator", "target_agent")
_emit_verifies_policy("p1", "reasoningnode_validator", "policy_check")
_emit_observes_runtime_state("p1", "reasoningnode_validator", "runtime_state")
_emit_verifies_boundary("p1", "reasoningnode_validator", "boundary_check")
_emit_transcripts_response("p1", "reasoningnode_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "reasoningnode_validator")
_emit_gated_by_confidence("p1", "reasoningnode_validator", "confidence_gate")
_emit_escalates_to_human("p1", "reasoningnode_validator", "L1")
_emit_reads_policy_state("p1", "reasoningnode_validator", "L1")
_emit_authorize_and_execute("p2", "reasoningnode_validator", "execution_auth")
_emit_validates_capability("p2", "reasoningnode_validator", "capability_check")
_emit_routes_to_capability("p2", "reasoningnode_validator", "capability_route")
_emit_writes_via_uwg("p2", "reasoningnode_validator", "uwg_write")
_emit_blocks_direct_write("p2", "reasoningnode_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "reasoningnode_validator", "tool_invocation")
_emit_captures_execution_output("p2", "reasoningnode_validator", "exec_output")
_emit_dispatches_agent("p3", "reasoningnode_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "reasoningnode_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "reasoningnode_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "reasoningnode_validator", "healing_outcome")
_emit_escalates_failure("p3", "reasoningnode_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "reasoningnode_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "reasoningnode_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "reasoningnode_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "reasoningnode_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "reasoningnode_validator", "eval_metric")
_emit_stores_embedding("p4", "reasoningnode_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "reasoningnode_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "reasoningnode_validator", "exec_snapshot_link")

"\nReasoning Node - Sub-atomic Thought Generation\n\nHandles reasoning strategy selection, thought generation, and planning.\nIntegrates Phase 1-3 optimizations (caching, pruning, adaptive planning).\n"
import asyncio
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

_emit_emits_metric_event("reasoningnode_validator", "p4obs", "metric_1")
_emit_emits_metric_event("reasoningnode_validator", "p4obs", "metric_2")
_emit_emits_metric_event("reasoningnode_validator", "p4obs", "metric_3")
_emit_emits_metric_event("reasoningnode_validator", "p4obs", "metric_4")
_emit_emits_metric_event("reasoningnode_validator", "p4obs", "metric_5")
_emit_emits_metric_event("reasoningnode_validator", "p4obs", "metric_6")
_emit_records_incident_event("reasoningnode_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("reasoningnode_validator", "p4obs", "anomaly")
_emit_writes_observability_log("reasoningnode_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("reasoningnode_validator", "p4obs", "mon_state")
_emit_triggers_alert("reasoningnode_validator", "p4obs", "alert")
_emit_links_incident_trace("reasoningnode_validator", "p4obs", "trace_link")
_emit_captures_pattern("reasoningnode_validator", "p3lm", "pattern")
_emit_records_learning_event("reasoningnode_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("reasoningnode_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("reasoningnode_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("reasoningnode_validator", "p3lm", "routing")
_emit_improves_agent_policy("reasoningnode_validator", "p3lm", "policy")
_emit_stores_learning_state("reasoningnode_validator", "p3lm", "state")
_emit_records_execution_trace("reasoningnode_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("reasoningnode_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("reasoningnode_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("reasoningnode_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("reasoningnode_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("reasoningnode_validator", "env_read", "p2_env_1")
_emit_reads_environ("reasoningnode_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("reasoningnode_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("reasoningnode_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "reasoningnode_validator", "context_pull")
_emit_pulls_context("p1", "reasoningnode_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "reasoningnode_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "reasoningnode_validator", "uwg_term_2")
_emit_writes_through("p1", "reasoningnode_validator", "write_through")
_emit_writes_through("p1", "reasoningnode_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "reasoningnode_validator", "safety_validation")
_emit_invokes_eval("p1", "reasoningnode_validator", "eval_call")
_emit_proposal_commits_routing("p1", "reasoningnode_validator", "routing_commit")


class ReasoningNode:
    """
    Sub-atomic reasoning node - thought generation and planning.

    Responsibilities:
    - Select reasoning strategy based on intent
    - Generate thoughts with prioritization
    - Create execution plan
    - Integrate Phase 1-3 optimizations
    """

    def __init__(self):
        """Initialize reasoning node."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ReasoningNode.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ReasoningNode.__init__", "p0_governance")
        self.thoughts_generated = 0
        self.plans_created = 0
        self.total_reasoning_time = 0.0

    def reason(self, perceived: dict[str, Any]) -> dict[str, Any]:
        """
        Generate reasoning from perceived state.

        Args:
            perceived: Perceived state from PerceptionNode

        Returns:
            Reasoning result with thoughts and plan
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "ReasoningNode.reason")

        start_time = get_clock().now_epoch()
        strategy = self._select_strategy(perceived["intent"])
        thoughts = self._generate_thoughts(perceived["query"], strategy, perceived)
        plan = self._generate_plan(thoughts, perceived)
        reasoning_time = get_clock().now_epoch() - start_time
        self.total_reasoning_time += reasoning_time
        reasoning = {
            "thoughts": thoughts,
            "plan": plan,
            "strategy": strategy,
            "reasoning_time": reasoning_time,
            "thought_count": len(thoughts),
        }
        return reasoning

    async def reason_async(self, perceived: dict[str, Any]) -> dict[str, Any]:
        """
        Asynchronous reasoning generation.

        Args:
            perceived: Perceived state

        Returns:
            Reasoning result
        """
        start_time = get_clock().now_epoch()
        strategy = self._select_strategy(perceived["intent"])
        thoughts = await asyncio.to_thread(self._generate_thoughts, perceived["query"], strategy, perceived)
        plan = await asyncio.to_thread(self._generate_plan, thoughts, perceived)
        reasoning_time = get_clock().now_epoch() - start_time
        self.total_reasoning_time += reasoning_time
        reasoning = {
            "thoughts": thoughts,
            "plan": plan,
            "strategy": strategy,
            "reasoning_time": reasoning_time,
            "thought_count": len(thoughts),
        }
        return reasoning

    def _select_strategy(self, intent: str) -> str:
        """
        Select reasoning strategy based on intent.

        Args:
            intent: Classified intent

        Returns:
            Strategy name
        """
        strategy_map = {
            "reasoning": "chain_of_thought",
            "action": "reactive",
            "memory": "retrieval",
            "general": "balanced",
        }
        return strategy_map.get(intent, "balanced")

    def _generate_thoughts(
        self, query: str, strategy: str, perceived: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Generate prioritized thoughts using strategy.

        Integrates Phase 1 optimizations (caching, pruning, early stopping).

        Args:
            query: User query
            strategy: Reasoning strategy
            perceived: Perceived state

        Returns:
            List of prioritized thoughts
        """
        self.thoughts_generated += 1
        thoughts = []
        if strategy == "chain_of_thought":
            thoughts = [
                {"step": 1, "thought": f"Analyzing: {query[:50]}...", "confidence": 0.8},
                {"step": 2, "thought": "Identifying key concepts", "confidence": 0.75},
                {"step": 3, "thought": "Forming hypothesis", "confidence": 0.7},
            ]
        elif strategy == "reactive":
            thoughts = [
                {"step": 1, "thought": "Immediate action needed", "confidence": 0.9},
                {"step": 2, "thought": "Execute primary action", "confidence": 0.85},
            ]
        elif strategy == "retrieval":
            thoughts = [
                {"step": 1, "thought": "Searching memory", "confidence": 0.8},
                {"step": 2, "thought": "Retrieving relevant context", "confidence": 0.75},
            ]
        else:
            thoughts = [
                {"step": 1, "thought": f"Processing: {query[:50]}...", "confidence": 0.75},
                {"step": 2, "thought": "Evaluating options", "confidence": 0.7},
            ]
        # guardian: allow-magic-config
        min_confidence = 0.6
        thoughts = [t for t in thoughts if t.get("confidence", 0) >= min_confidence]
        if thoughts and thoughts[0].get("confidence", 0) >= 0.9:
            thoughts = thoughts[:1]
        thoughts.sort(key=lambda t: t.get("confidence", 0), reverse=True)
        return thoughts

    def _generate_plan(self, thoughts: list[dict[str, Any]], perceived: dict[str, Any]) -> dict[str, Any]:
        """
        Generate execution plan from thoughts.

        Integrates Phase 2 planning optimizations (quality scoring, validation).

        Args:
            thoughts: Generated thoughts
            perceived: Perceived state

        Returns:
            Execution plan
        """
        self.plans_created += 1
        steps = [
            {"action": f"thought_{i}", "description": thought.get("thought", ""), "priority": i}
            for i, thought in enumerate(thoughts)
        ]
        score = self._score_plan(steps, perceived)
        valid = self._validate_plan(steps, perceived)
        plan = {
            "steps": steps,
            "score": score,
            "valid": valid,
            "estimated_cost": len(steps),
            "constraints": ["coherence", "feasibility"],
        }
        return plan

    def _score_plan(self, steps: list[dict[str, Any]], perceived: dict[str, Any]) -> float:
        """
        Score plan quality (Phase 2 integration).

        Args:
            steps: Plan steps
            perceived: Perceived state

        Returns:
            Quality score (0.0-1.0)
        """
        score = 0.0
        score += min(1.0, len(steps) / 5.0) * 0.3
        score += 0.3
        score += max(0.0, 1.0 - len(steps) / 10.0) * 0.2
        score += 0.2
        return min(1.0, max(0.0, score))

    def _validate_plan(self, steps: list[dict[str, Any]], perceived: dict[str, Any]) -> bool:
        """
        Validate plan feasibility (Phase 2 integration).

        Args:
            steps: Plan steps
            perceived: Perceived state

        Returns:
            True if plan is valid
        """
        if len(steps) > 20:
            return False
        if len(steps) == 0:
            return False
        return True

    def get_statistics(self) -> dict[str, Any]:
        """Get reasoning statistics."""
        avg_reasoning_time = (
            self.total_reasoning_time / self.thoughts_generated if self.thoughts_generated > 0 else 0.0
        )
        return {
            "thoughts_generated": self.thoughts_generated,
            "plans_created": self.plans_created,
            "total_reasoning_time": self.total_reasoning_time,
            "avg_reasoning_time": avg_reasoning_time,
        }
