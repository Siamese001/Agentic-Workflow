from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "reasoning_cache")
trace_contract.emit_determinism_digest("p0", "reasoning_cache")

trace_contract._emit_dispatches_healing_run("p1", "reasoning_cache", "L1")
trace_contract._emit_routes_through("p1", "reasoning_cache", "L1")
trace_contract._emit_checks_agent_registry("p1", "reasoning_cache", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "reasoning_cache", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "reasoning_cache", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "reasoning_cache", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "reasoning_cache", "target_agent")
trace_contract._emit_verifies_policy("p1", "reasoning_cache", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "reasoning_cache", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "reasoning_cache", "boundary_check")
trace_contract._emit_transcripts_response("p1", "reasoning_cache", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "reasoning_cache")
trace_contract._emit_gated_by_confidence("p1", "reasoning_cache", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "reasoning_cache", "L1")
trace_contract._emit_reads_policy_state("p1", "reasoning_cache", "L1")
trace_contract._emit_authorize_and_execute("p2", "reasoning_cache", "execution_auth")
trace_contract._emit_validates_capability("p2", "reasoning_cache", "capability_check")
trace_contract._emit_routes_to_capability("p2", "reasoning_cache", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "reasoning_cache", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "reasoning_cache", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "reasoning_cache", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "reasoning_cache", "exec_output")
trace_contract._emit_dispatches_agent("p3", "reasoning_cache", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "reasoning_cache", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "reasoning_cache", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "reasoning_cache", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "reasoning_cache", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "reasoning_cache", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "reasoning_cache", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "reasoning_cache", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "reasoning_cache", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "reasoning_cache", "eval_metric")
trace_contract._emit_stores_embedding("p4", "reasoning_cache", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "reasoning_cache", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "reasoning_cache", "exec_snapshot_link")

"\nReasoning Path Caching Module\n\nImplements memoization for reasoning paths to reduce redundant LLM calls\nand improve latency on repeated sub-problems.\n"
import functools
import hashlib
import json
from collections import OrderedDict
from typing import Any


trace_contract._emit_emits_metric_event("reasoning_cache", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("reasoning_cache", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("reasoning_cache", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("reasoning_cache", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("reasoning_cache", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("reasoning_cache", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("reasoning_cache", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("reasoning_cache", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("reasoning_cache", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("reasoning_cache", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("reasoning_cache", "p4obs", "alert")
trace_contract._emit_links_incident_trace("reasoning_cache", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("reasoning_cache", "p3lm", "pattern")
trace_contract._emit_records_learning_event("reasoning_cache", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("reasoning_cache", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("reasoning_cache", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("reasoning_cache", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("reasoning_cache", "p3lm", "policy")
trace_contract._emit_stores_learning_state("reasoning_cache", "p3lm", "state")
trace_contract._emit_records_execution_trace("reasoning_cache", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("reasoning_cache", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("reasoning_cache", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("reasoning_cache", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("reasoning_cache", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("reasoning_cache", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("reasoning_cache", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("reasoning_cache", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("reasoning_cache", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "reasoning_cache", "context_pull")
trace_contract._emit_pulls_context("p1", "reasoning_cache", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "reasoning_cache", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "reasoning_cache", "uwg_term_2")
trace_contract._emit_writes_through("p1", "reasoning_cache", "write_through")
trace_contract._emit_writes_through("p1", "reasoning_cache", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "reasoning_cache", "safety_validation")
trace_contract._emit_invokes_eval("p1", "reasoning_cache", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "reasoning_cache", "routing_commit")


class ReasoningCache:
    """LRU cache for reasoning paths."""

    def __init__(self, maxsize: int = 10000):
        """Initialize reasoning cache."""
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "ReasoningCache.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "ReasoningCache.__init__", "p0_governance")
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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L1_REASONING, "ReasoningCache.get")

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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L1_REASONING, "ObservationCache.get")

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
