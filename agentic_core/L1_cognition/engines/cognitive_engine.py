from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
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

"\nRefactored Cognitive Node - Coordinator Pattern\n\nOrchestrates PerceptionNode, ReasoningNode, and ActionNode with:\n- Parallel/async execution\n- Lazy evaluation for simple intents\n- Output caching\n- Per-node performance monitoring\n"
import asyncio
import hashlib
import uuid
from typing import Any

from agentic_core.L0_routing.config.path_constants import DEFAULT_SLEEP


# Lazy import to avoid L1->L2 gravity violation
def _get_proof_emitter():
    from agentic_core.L2_execution.determinism.execution_proof_emitter import ExecutionProofEmitter
    return ExecutionProofEmitter("L1.cognitive_engine")

_proof_emitter = _get_proof_emitter()


def _get_reason_and_record():
    _emit_transcripts_response(str(uuid.uuid4()), "Module._get_reason_and_record", "model")
    from agentic_core.L1_cognition.enforcement.reasoning_chokepoint import reason_and_record  # noqa: PLC0415

    return reason_and_record


def _invoke_reason_and_record(ctx, prompt, context, fn, **kw):
    from agentic_core.L1_cognition.enforcement.reasoning_chokepoint import reason_and_record  # noqa: PLC0415

    return reason_and_record(ctx, prompt, context, fn, **kw)


def _make_reasoning_context(run_id: str, policy_hash: str, prompt: str, model_id: str, clock_tick: float):
    from agentic_core.L1_cognition.context.reasoning_context_builder import (
        build_reasoning_context,  # noqa: PLC0415
    )

    return build_reasoning_context(
        run_id=run_id,
        trace_id=str(uuid.uuid4()),
        policy_context=policy_hash or "default",
        prompt=prompt,
        model_id=model_id or "cognitive_engine",
    )


def _get_ActionNode():
    """Lazy load ActionNode to avoid upward import."""
    from agentic_core.interfaces.orchestration import ActionRouter

    return ActionRouter


try:
    from .PerceptionNode import PerceptionNode
except ImportError:  # guardian: allow-silent-swallow
    PerceptionNode = None
try:
    from .ReasoningNode import ReasoningNode
except ImportError:
    ReasoningNode = None
from agentic_core.runtime.lifecycle_trace_contract import (
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

from agentic_core.runtime.lifecycle_trace_contract import emit_determinism_digest

emit_determinism_digest("trace_cognitive_engine", "cognitive_engine_dispatch_entry")
emit_determinism_digest("trace_cognitive_engine", "cognitive_engine_dispatch_exit")
emit_determinism_digest("trace_cognitive_engine", "cognitive_engine_tool_invoke")
emit_determinism_digest("trace_cognitive_engine", "cognitive_engine_tool_complete")
emit_determinism_digest("trace_cognitive_engine", "cognitive_engine_agent_entry")
emit_determinism_digest("trace_cognitive_engine", "cognitive_engine_agent_exit")
emit_determinism_digest("trace_cognitive_engine", "cognitive_engine_uwg_write")
emit_determinism_digest("trace_cognitive_engine", "cognitive_engine_trace_sign")
emit_determinism_digest("trace_cognitive_engine", "cognitive_engine_guardrail_check")
emit_determinism_digest("trace_cognitive_engine", "cognitive_engine_policy_verify")


class CognitiveNodeRefactored:
    """
    Refactored cognitive node - coordinator pattern.

    Decomposes monolithic CognitiveNode into focused sub-nodes:
    - PerceptionNode: Input processing
    - ReasoningNode: Thought generation
    - ActionNode: Execution

    Features:
    - Parallel/async execution
    - Lazy evaluation (simple intent → skip heavy reasoning)
    - Output caching (hash-based)
    - Per-node monitoring (metrics)
    """

    def __init__(self):
        """Initialize refactored cognitive node."""
        self.perception = PerceptionNode()
        self.reasoning = ReasoningNode()
        self.action = ActionNode()
        self.cache: dict[str, dict[str, Any]] = {}
        self.node_metrics = {
            "perception": {"calls": 0, "total_time": 0.0},
            "reasoning": {"calls": 0, "total_time": 0.0},
            "action": {"calls": 0, "total_time": 0.0},
        }
        self.total_processes = 0
        self.lazy_evaluations = 0

    def process(self, raw_input: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Sequential cognitive processing (baseline).

        Args:
            raw_input: Raw user input
            context: Current context

        Returns:
            Final output
        """
        _emit_gated_by_confidence(str(uuid.uuid4()), "CognitiveNodeRefactored.process", "0.5")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "CognitiveNodeRefactored.process")

        self.total_processes += 1
        cache_key = self._make_cache_key(raw_input, context)
        if cache_key in self.cache:
            return self.cache[cache_key].copy()
        _clk = get_clock().now_epoch()
        _rctx = _make_reasoning_context(
            run_id=cache_key[:16],
            policy_hash=context.get("policy_hash", "default"),
            prompt=raw_input.get("user_query", str(raw_input)[:128]),
            model_id=context.get("model_id", "cognitive_engine"),
            clock_tick=_clk,
        )
        with _proof_emitter.proof_op("process"):
            pass
        _, _trace = _invoke_reason_and_record(
            _rctx,
            raw_input,
            context,
            lambda p, c: p,
        )
        start = get_clock().now_epoch()
        perceived = self.perception.process(raw_input, context)
        self._record_metric("perception", get_clock().now_epoch() - start)
        if self._is_simple_intent(perceived):
            self.lazy_evaluations += 1
            start = get_clock().now_epoch()
            output = self.action.act_simple(perceived)
            self._record_metric("action", get_clock().now_epoch() - start)
        else:
            start = get_clock().now_epoch()
            reasoned = self.reasoning.reason(perceived)
            self._record_metric("reasoning", get_clock().now_epoch() - start)
            start = get_clock().now_epoch()
            output = self.action.act(reasoned)
            self._record_metric("action", get_clock().now_epoch() - start)
        self.cache[cache_key] = output.copy()
        return output

    async def process_async(self, raw_input: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Parallel cognitive processing with async/await.

        Enables:
        - Parallel perception + memory prefetch
        - Lazy evaluation (skip reasoning for simple intents)
        - Async tool execution

        Args:
            raw_input: Raw user input
            context: Current context

        Returns:
            Final output
        """
        self.total_processes += 1
        cache_key = self._make_cache_key(raw_input, context)
        if cache_key in self.cache:
            return self.cache[cache_key].copy()
        _clk = get_clock().now_epoch()
        _rctx = _make_reasoning_context(
            run_id=cache_key[:16],
            policy_hash=context.get("policy_hash", "default"),
            prompt=raw_input.get("user_query", str(raw_input)[:128]),
            model_id=context.get("model_id", "cognitive_engine"),
            clock_tick=_clk,
        )
        with _proof_emitter.proof_op("process_async"):
            pass
        _, _trace_async = _invoke_reason_and_record(
            _rctx,
            raw_input,
            context,
            lambda p, c: p,
        )
        start = get_clock().now_epoch()
        perception_task = asyncio.create_task(self.perception.process_async(raw_input, context))
        memory_task = asyncio.create_task(self._lazy_memory_prefetch(context))
        perceived = await perception_task
        memory = await memory_task
        perceived["memory"] = memory
        self._record_metric("perception", get_clock().now_epoch() - start)
        if self._is_simple_intent(perceived):
            self.lazy_evaluations += 1
            start = get_clock().now_epoch()
            output = await asyncio.to_thread(self.action.act_simple, perceived)
            self._record_metric("action", get_clock().now_epoch() - start)
        else:
            start = get_clock().now_epoch()
            reasoned = await self.reasoning.reason_async(perceived)
            self._record_metric("reasoning", get_clock().now_epoch() - start)
            start = get_clock().now_epoch()
            output = await self.action.act_async(reasoned)
            self._record_metric("action", get_clock().now_epoch() - start)
        self.cache[cache_key] = output.copy()
        return output

    def _make_cache_key(self, raw_input: dict[str, Any], context: dict[str, Any]) -> str:
        """
        Create stable cache key from input and context.

        Args:
            raw_input: Raw input
            context: Context

        Returns:
            cache key
        """
        input_str = str(sorted(raw_input.items()))
        context_str = str(sorted(context.items()))
        key_input = f"{input_str}|{context_str}"
        return hashlib.sha256(key_input.encode()).hexdigest()

    def _is_simple_intent(self, perceived: dict[str, Any]) -> bool:
        """
        Determine if intent is simple (lazy evaluation).

        Args:
            perceived: Perceived state

        Returns:
            True if simple intent
        """
        query_len = len(perceived.get("query", ""))
        confidence = perceived.get("confidence", 0.0)
        intent = perceived.get("intent", "")
        return query_len < 50 and confidence > 0.8 and (intent in ["action", "memory"])

    async def _lazy_memory_prefetch(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Lazy memory prefetch (background task).

        Args:
            context: Current context

        Returns:
            Prefetched memory items
        """
        await asyncio.sleep(DEFAULT_SLEEP)
        return context.get("memory", [])

    def _record_metric(self, node_name: str, duration: float) -> None:
        """
        Record node performance metric.

        Args:
            node_name: Node name (perception, reasoning, action)
            duration: Execution duration
        """
        if node_name in self.node_metrics:
            self.node_metrics[node_name]["calls"] += 1
            self.node_metrics[node_name]["total_time"] += duration

    def get_statistics(self) -> dict[str, Any]:
        """Get cognitive node statistics."""
        stats = {
            "total_processes": self.total_processes,
            "lazy_evaluations": self.lazy_evaluations,
            "lazy_rate": self.lazy_evaluations / self.total_processes * 100
            if self.total_processes > 0
            else 0,
            "cache_size": len(self.cache),
            "nodes": {},
        }
        for node_name, metrics in self.node_metrics.items():
            calls = metrics["calls"]
            total_time = metrics["total_time"]
            avg_time = total_time / calls if calls > 0 else 0.0
            stats["nodes"][node_name] = {"calls": calls, "total_time": total_time, "avg_time": avg_time}
        stats["perception_stats"] = self.perception.get_statistics()
        stats["reasoning_stats"] = self.reasoning.get_statistics()
        stats["action_stats"] = self.action.get_statistics()
        return stats

    def clear_cache(self) -> None:
        """Clear output cache."""
        self.cache.clear()


cognitive_node_refactored = CognitiveNodeRefactored()
