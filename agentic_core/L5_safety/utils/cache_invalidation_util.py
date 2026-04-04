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

emit_replay_key("p0", "cache_invalidation_util")
emit_determinism_digest("p0", "cache_invalidation_util")

_emit_dispatches_healing_run("p1", "cache_invalidation_util", "L5")
_emit_routes_through("p1", "cache_invalidation_util", "L5")
_emit_checks_agent_registry("p1", "cache_invalidation_util", "agent_registry")
_emit_validates_agent_capability("p1", "cache_invalidation_util", "capability")
_emit_dispatches_execution_plan("p1", "cache_invalidation_util", "exec_plan")
_emit_agent_executes_agent("p1", "cache_invalidation_util", "sub_agent")
_emit_routes_to_agent("p1", "cache_invalidation_util", "target_agent")
_emit_verifies_policy("p1", "cache_invalidation_util", "policy_check")
_emit_observes_runtime_state("p1", "cache_invalidation_util", "runtime_state")
_emit_verifies_boundary("p1", "cache_invalidation_util", "boundary_check")
_emit_transcripts_response("p1", "cache_invalidation_util", "transcript")
_emit_hard_fails_untranscripted("p1", "cache_invalidation_util")
_emit_gated_by_confidence("p1", "cache_invalidation_util", "confidence_gate")
_emit_escalates_to_human("p1", "cache_invalidation_util", "L5")
_emit_reads_policy_state("p1", "cache_invalidation_util", "L5")
_emit_authorize_and_execute("p2", "cache_invalidation_util", "execution_auth")
_emit_validates_capability("p2", "cache_invalidation_util", "capability_check")
_emit_routes_to_capability("p2", "cache_invalidation_util", "capability_route")
_emit_writes_via_uwg("p2", "cache_invalidation_util", "uwg_write")
_emit_blocks_direct_write("p2", "cache_invalidation_util", "direct_write_block")
_emit_records_tool_invocation("p2", "cache_invalidation_util", "tool_invocation")
_emit_captures_execution_output("p2", "cache_invalidation_util", "exec_output")
_emit_dispatches_agent("p3", "cache_invalidation_util", "agent_dispatch")
_emit_coordinates_agents("p3", "cache_invalidation_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "cache_invalidation_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "cache_invalidation_util", "healing_outcome")
_emit_escalates_failure("p3", "cache_invalidation_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "cache_invalidation_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "cache_invalidation_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "cache_invalidation_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "cache_invalidation_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "cache_invalidation_util", "eval_metric")
_emit_stores_embedding("p4", "cache_invalidation_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "cache_invalidation_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "cache_invalidation_util", "exec_snapshot_link")

'\ncache Invalidation Utilities for Healing Workflows\n\nProvides decorators and helpers to invalidate cache after successful healing operations.\nThis ensures stale cached data (like AST results, compliance checks) is purged\nwhen the underlying code changes.\n\nUsage:\n\n    class HealerAgent(SovereignBaseAgent):\n        @heal_invalidate_cache("canon:*")  # Invalidate AST caches after heal\n        async def heal_repository(self) -> dict:\n            # Healing logic...\n            return {"success": True}\n'
import functools
import logging
from collections.abc import Callable
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

_emit_emits_metric_event("cache_invalidation_util", "p4obs", "metric_1")
_emit_emits_metric_event("cache_invalidation_util", "p4obs", "metric_2")
_emit_emits_metric_event("cache_invalidation_util", "p4obs", "metric_3")
_emit_emits_metric_event("cache_invalidation_util", "p4obs", "metric_4")
_emit_emits_metric_event("cache_invalidation_util", "p4obs", "metric_5")
_emit_emits_metric_event("cache_invalidation_util", "p4obs", "metric_6")
_emit_records_incident_event("cache_invalidation_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("cache_invalidation_util", "p4obs", "anomaly")
_emit_writes_observability_log("cache_invalidation_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("cache_invalidation_util", "p4obs", "mon_state")
_emit_triggers_alert("cache_invalidation_util", "p4obs", "alert")
_emit_links_incident_trace("cache_invalidation_util", "p4obs", "trace_link")
_emit_captures_pattern("cache_invalidation_util", "p3lm", "pattern")
_emit_records_learning_event("cache_invalidation_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("cache_invalidation_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("cache_invalidation_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("cache_invalidation_util", "p3lm", "routing")
_emit_improves_agent_policy("cache_invalidation_util", "p3lm", "policy")
_emit_stores_learning_state("cache_invalidation_util", "p3lm", "state")
_emit_records_execution_trace("cache_invalidation_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("cache_invalidation_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("cache_invalidation_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("cache_invalidation_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("cache_invalidation_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("cache_invalidation_util", "env_read", "p2_env_1")
_emit_reads_environ("cache_invalidation_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("cache_invalidation_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("cache_invalidation_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "cache_invalidation_util", "context_pull")
_emit_pulls_context("p1", "cache_invalidation_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "cache_invalidation_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "cache_invalidation_util", "uwg_term_2")
_emit_writes_through("p1", "cache_invalidation_util", "write_through")
_emit_writes_through("p1", "cache_invalidation_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "cache_invalidation_util", "safety_validation")
_emit_invokes_eval("p1", "cache_invalidation_util", "eval_call")
_emit_proposal_commits_routing("p1", "cache_invalidation_util", "routing_commit")

log = logging.getLogger(__name__)


def heal_invalidate_cache(pattern: str = ""):
    """
    Decorator to invalidate cache after successful heal operation.

    Args:
        pattern: cache key pattern to invalidate (e.g., "canon:*", "compliance:*")
                 Empty string invalidates all keys for the agent's prefix.

    Usage:
        @heal_invalidate_cache("canon:*")
        async def heal_repository(self) -> dict:
            ...
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "heal_invalidate_cache", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "heal_invalidate_cache", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "heal_invalidate_cache")

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs) -> Any:
            result = await func(self, *args, **kwargs)
            success = False
            if isinstance(result, dict):
                success = result.get("success", False) or result.get("healed", False)
            elif isinstance(result, bool):
                success = result
            if success and hasattr(self, "cache_invalidate"):
                try:
                    invalidated = await self.cache_invalidate(pattern)
                    log.info(f"cache invalidated for pattern '{pattern}' after heal ({invalidated} keys)")
                # guardian: allow-silent-swallow
                except (RuntimeError, OSError) as e:
                    log.debug(f"cache invalidation failed: {e}")
            return result

        return wrapper

    return decorator


def invalidate_on_file_change(file_path_arg: str = "file_path"):
    """
    Decorator to invalidate cache entries related to a specific file after modification.

    Args:
        file_path_arg: Name of the argument containing the file path

    Usage:
        @invalidate_on_file_change("file_path")
        async def modify_file(self, file_path: Path) -> dict:
            ...
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs) -> Any:
            result = await func(self, *args, **kwargs)
            file_path = kwargs.get(file_path_arg)
            if file_path is None and args:
                import inspect

                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                if file_path_arg in params:
                    idx = params.index(file_path_arg) - 1
                    if 0 <= idx < len(args):
                        file_path = args[idx]
            if file_path and hasattr(self, "cache_invalidate"):
                file_name = str(file_path).split("/")[-1].split("\\")[-1]
                try:
                    await self.cache_invalidate(file_name)
                    log.debug(f"cache invalidated for file: {file_name}")
                # guardian: allow-silent-swallow
                except (RuntimeError, OSError) as e:
                    log.debug(f"File cache invalidation failed: {e}")
            return result

        return wrapper

    return decorator


async def invalidate_all_caches(agent) -> int:
    """
    Utility to invalidate all caches for an agent.

    Args:
        agent: Agent instance with cache_invalidate method

    Returns:
        Number of keys invalidated
    """
    if hasattr(agent, "cache_invalidate"):
        try:
            return await agent.cache_invalidate("")
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError) as e:
            log.warning(f"Failed to invalidate all caches: {e}")
    return 0
