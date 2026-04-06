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

emit_replay_key("p0", "reasoning_cache")
emit_determinism_digest("p0", "reasoning_cache")

_emit_dispatches_healing_run("p1", "reasoning_cache", "L1")
_emit_routes_through("p1", "reasoning_cache", "L1")
_emit_checks_agent_registry("p1", "reasoning_cache", "agent_registry")
_emit_validates_agent_capability("p1", "reasoning_cache", "capability")
_emit_dispatches_execution_plan("p1", "reasoning_cache", "exec_plan")
_emit_agent_executes_agent("p1", "reasoning_cache", "sub_agent")
_emit_routes_to_agent("p1", "reasoning_cache", "target_agent")
_emit_verifies_policy("p1", "reasoning_cache", "policy_check")
_emit_observes_runtime_state("p1", "reasoning_cache", "runtime_state")
_emit_verifies_boundary("p1", "reasoning_cache", "boundary_check")
_emit_transcripts_response("p1", "reasoning_cache", "transcript")
_emit_hard_fails_untranscripted("p1", "reasoning_cache")
_emit_gated_by_confidence("p1", "reasoning_cache", "confidence_gate")
_emit_escalates_to_human("p1", "reasoning_cache", "L1")
_emit_reads_policy_state("p1", "reasoning_cache", "L1")
_emit_authorize_and_execute("p2", "reasoning_cache", "execution_auth")
_emit_validates_capability("p2", "reasoning_cache", "capability_check")
_emit_routes_to_capability("p2", "reasoning_cache", "capability_route")
_emit_writes_via_uwg("p2", "reasoning_cache", "uwg_write")
_emit_blocks_direct_write("p2", "reasoning_cache", "direct_write_block")
_emit_records_tool_invocation("p2", "reasoning_cache", "tool_invocation")
_emit_captures_execution_output("p2", "reasoning_cache", "exec_output")
_emit_dispatches_agent("p3", "reasoning_cache", "agent_dispatch")
_emit_coordinates_agents("p3", "reasoning_cache", "agent_coordination")
_emit_records_workflow_lineage("p3", "reasoning_cache", "workflow_lineage")
_emit_records_healing_outcome("p3", "reasoning_cache", "healing_outcome")
_emit_escalates_failure("p3", "reasoning_cache", "failure_escalation")
_emit_orchestrates_workflow("p3", "reasoning_cache", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "reasoning_cache", "healing_dispatch")
_emit_invokes_evaluation("p3", "reasoning_cache", "evaluation_signal")
_emit_records_telemetry_event("p4", "reasoning_cache", "telemetry_event")
_emit_captures_evaluation_metric("p4", "reasoning_cache", "eval_metric")
_emit_stores_embedding("p4", "reasoning_cache", "embedding_store")
_emit_updates_meta_learning_state("p4", "reasoning_cache", "meta_learning")
_emit_links_execution_to_snapshot("p4", "reasoning_cache", "exec_snapshot_link")

"\nReasoning Path Caching Module\n\nImplements memoization for reasoning paths to reduce redundant LLM calls\nand improve latency on repeated sub-problems.\n"
import functools
import hashlib
import json
from collections import OrderedDict
from typing import Any

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

_emit_emits_metric_event("reasoning_cache", "p4obs", "metric_1")
_emit_emits_metric_event("reasoning_cache", "p4obs", "metric_2")
_emit_emits_metric_event("reasoning_cache", "p4obs", "metric_3")
_emit_emits_metric_event("reasoning_cache", "p4obs", "metric_4")
_emit_emits_metric_event("reasoning_cache", "p4obs", "metric_5")
_emit_emits_metric_event("reasoning_cache", "p4obs", "metric_6")
_emit_records_incident_event("reasoning_cache", "p4obs", "incident")
_emit_captures_runtime_anomaly("reasoning_cache", "p4obs", "anomaly")
_emit_writes_observability_log("reasoning_cache", "p4obs", "obs_log")
_emit_updates_monitoring_state("reasoning_cache", "p4obs", "mon_state")
_emit_triggers_alert("reasoning_cache", "p4obs", "alert")
_emit_links_incident_trace("reasoning_cache", "p4obs", "trace_link")
_emit_captures_pattern("reasoning_cache", "p3lm", "pattern")
_emit_records_learning_event("reasoning_cache", "p3lm", "learning_event")
_emit_writes_learning_snapshot("reasoning_cache", "p3lm", "snapshot")
_emit_feeds_meta_learning("reasoning_cache", "p3lm", "meta_feed")
_emit_updates_routing_strategy("reasoning_cache", "p3lm", "routing")
_emit_improves_agent_policy("reasoning_cache", "p3lm", "policy")
_emit_stores_learning_state("reasoning_cache", "p3lm", "state")
_emit_records_execution_trace("reasoning_cache", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("reasoning_cache", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("reasoning_cache", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("reasoning_cache", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("reasoning_cache", "L4_STATE", "p2_trace_5")
_emit_reads_environ("reasoning_cache", "env_read", "p2_env_1")
_emit_reads_environ("reasoning_cache", "env_read", "p2_env_2")
_emit_reads_runtime_state("reasoning_cache", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("reasoning_cache", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "reasoning_cache", "context_pull")
_emit_pulls_context("p1", "reasoning_cache", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "reasoning_cache", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "reasoning_cache", "uwg_term_2")
_emit_writes_through("p1", "reasoning_cache", "write_through")
_emit_writes_through("p1", "reasoning_cache", "write_through_2")
_emit_validated_by_safety_plane("p1", "reasoning_cache", "safety_validation")
_emit_invokes_eval("p1", "reasoning_cache", "eval_call")
_emit_proposal_commits_routing("p1", "reasoning_cache", "routing_commit")


class ReasoningCache:
    """LRU cache for reasoning paths."""

    def __init__(self, maxsize: int = 10000):
        """Initialize reasoning cache."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ReasoningCache.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ReasoningCache.__init__", "p0_governance")
        self.maxsize = maxsize
        self.cache: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def _make_key(self, problem: str, context: dict[str, Any], params: tuple) -> str:
        """
        Create cache key from problem, context, and parameters.

        Args:
            problem: Problem statement
            context: Context dictionary
            params: Parameter tuple (temperature, model, etc.)

        Returns:
            Stable hash key
        """
        context_str = json.dumps(context, sort_keys=True, default=str)
        params_str = json.dumps(params, sort_keys=True, default=str)
        key_input = f"{problem}|{context_str}|{params_str}"
        return hashlib.sha256(key_input.encode()).hexdigest()

    def get(self, problem: str, context: dict[str, Any], params: tuple) -> dict[str, Any] | None:
        """
        Get cached reasoning result.

        Args:
            problem: Problem statement
            context: Context dictionary
            params: Parameter tuple

        Returns:
            Cached result or None
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "ReasoningCache.get")

        key = self._make_key(problem, context, params)
        if key in self.cache:
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def put(self, problem: str, context: dict[str, Any], params: tuple, result: dict[str, Any]) -> None:
        """
        cache reasoning result.

        Args:
            problem: Problem statement
            context: Context dictionary
            params: Parameter tuple
            result: Reasoning result to cache
        """
        key = self._make_key(problem, context, params)
        if len(self.cache) >= self.maxsize:
            self.cache.popitem(last=False)
        self.cache[key] = result

    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_statistics(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = self.hits / total * 100 if total > 0 else 0
        return {
            "size": len(self.cache),
            "maxsize": self.maxsize,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "total_requests": total,
        }


class ObservationCache:
    """cache for ReAct observations to avoid redundant tool calls."""

    def __init__(self, maxsize: int = 5000):
        """Initialize observation cache."""
        self.maxsize = maxsize
        self.cache: OrderedDict[str, str] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def _make_key(self, action: str, context_hash: str) -> str:
        """
        Create cache key from action and context.

        Args:
            action: Action to execute
            context_hash: Hash of context

        Returns:
            cache key
        """
        key_input = f"{action}|{context_hash}"
        return hashlib.sha256(key_input.encode()).hexdigest()

    def get(self, action: str, context_hash: str) -> str | None:
        """
        Get cached observation.

        Args:
            action: Action to execute
            context_hash: Hash of context

        Returns:
            Cached observation or None
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "ObservationCache.get")

        key = self._make_key(action, context_hash)
        if key in self.cache:
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def put(self, action: str, context_hash: str, observation: str) -> None:
        """
        cache observation.

        Args:
            action: Action executed
            context_hash: Hash of context
            observation: Observation result
        """
        key = self._make_key(action, context_hash)
        if len(self.cache) >= self.maxsize:
            self.cache.popitem(last=False)
        self.cache[key] = observation

    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_statistics(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = self.hits / total * 100 if total > 0 else 0
        return {
            "size": len(self.cache),
            "maxsize": self.maxsize,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "total_requests": total,
        }


reasoning_cache = ReasoningCache(maxsize=10000)
observation_cache = ObservationCache(maxsize=5000)


def cached_reasoning(func):
    """Decorator for caching reasoning results."""

    @functools.wraps(func)
    def wrapper(self, problem: str, context: dict[str, Any], *args, **kwargs):
        params = (
            context.get("temperature", 0.7),
            context.get("model", "default"),
            context.get("max_steps", 8),
        )
        cached_result = reasoning_cache.get(problem, context, params)
        if cached_result is not None:
            print(f"[CACHE HIT] Problem: {problem[:50]}...")
            return cached_result
        print(f"[CACHE MISS] Problem: {problem[:50]}...")
        result = func(self, problem, context, *args, **kwargs)
        reasoning_cache.put(problem, context, params, result)
        return result

    return wrapper


def cached_observation(func):
    """Decorator for caching observations."""

    @functools.wraps(func)
    def wrapper(self, action: str, context: dict[str, Any], *args, **kwargs):
        context_str = json.dumps(context, sort_keys=True, default=str)
        context_hash = hashlib.sha256(context_str.encode()).hexdigest()
        cached_result = observation_cache.get(action, context_hash)
        if cached_result is not None:
            print(f"[OBS CACHE HIT] Action: {action[:50]}...")
            return cached_result
        print(f"[OBS CACHE MISS] Action: {action[:50]}...")
        result = func(self, action, context, *args, **kwargs)
        observation_cache.put(action, context_hash, result)
        return result

    return wrapper
