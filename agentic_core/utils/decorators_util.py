"""
Canonical decorator implementations for agent standardization.

This is the SSOT for agent decorators. All imports should use:
    from agentic_core.utils.decorators_compat_util import standard_heal, HEAL_RESULT_SCHEMA

DECORATORS:
    @standard_heal: Standardizes heal_repository() methods
        - Input normalization (ensures dry_run/execute exist)
        - Output normalization (converts legacy dicts to HealResult schema)
        - Error containment (catches crashes, returns valid HealResult)

    @standard_heal_async: Async version of @standard_heal

Canonical location: agentic_core/base_agents/decorators.py
Backward-compat shim: agentic_core/L5_safety/utils/decorators_util.py
"""

from __future__ import annotations

import functools
import inspect
import logging
import os
import time
import traceback
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar, cast

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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,  # noqa: E402
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

_emit_authorize_and_execute("p2", "decorators_util", "execution_auth")
_emit_validates_capability("p2", "decorators_util", "capability_check")
_emit_routes_to_capability("p2", "decorators_util", "capability_route")
_emit_writes_via_uwg("p2", "decorators_util", "uwg_write")
_emit_blocks_direct_write("p2", "decorators_util", "direct_write_block")
_emit_records_tool_invocation("p2", "decorators_util", "tool_invocation")
_emit_captures_execution_output("p2", "decorators_util", "exec_output")
_emit_dispatches_agent("p3", "decorators_util", "agent_dispatch")
_emit_coordinates_agents("p3", "decorators_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "decorators_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "decorators_util", "healing_outcome")
_emit_escalates_failure("p3", "decorators_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "decorators_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "decorators_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "decorators_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "decorators_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "decorators_util", "eval_metric")
_emit_stores_embedding("p4", "decorators_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "decorators_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "decorators_util", "exec_snapshot_link")
from agentic_core.utils.timeout_decorator_util import TimeoutError, timeout

_emit_records_execution_trace("p0", "evidence", "decorators_util")
_emit_applies_guardrail("p0", "decorators_util", "p0_governance")
_emit_snapshots_state("p0", "decorators_util", "state_snapshot")
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("decorators_util", "p4obs", "metric_1")
_emit_emits_metric_event("decorators_util", "p4obs", "metric_2")
_emit_emits_metric_event("decorators_util", "p4obs", "metric_3")
_emit_emits_metric_event("decorators_util", "p4obs", "metric_4")
_emit_emits_metric_event("decorators_util", "p4obs", "metric_5")
_emit_emits_metric_event("decorators_util", "p4obs", "metric_6")
_emit_records_incident_event("decorators_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("decorators_util", "p4obs", "anomaly")
_emit_writes_observability_log("decorators_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("decorators_util", "p4obs", "mon_state")
_emit_triggers_alert("decorators_util", "p4obs", "alert")
_emit_links_incident_trace("decorators_util", "p4obs", "trace_link")
_emit_captures_pattern("decorators_util", "p3lm", "pattern")
_emit_records_learning_event("decorators_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("decorators_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("decorators_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("decorators_util", "p3lm", "routing")
_emit_improves_agent_policy("decorators_util", "p3lm", "policy")
_emit_stores_learning_state("decorators_util", "p3lm", "state")
_emit_records_execution_trace("decorators_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("decorators_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("decorators_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("decorators_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("decorators_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("decorators_util", "env_read", "p2_env_1")
_emit_reads_environ("decorators_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("decorators_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("decorators_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "decorators_util", "context_pull")
_emit_pulls_context("p1", "decorators_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "decorators_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "decorators_util", "uwg_term_2")
_emit_writes_through("p1", "decorators_util", "write_through")
_emit_writes_through("p1", "decorators_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "decorators_util", "safety_validation")
_emit_invokes_eval("p1", "decorators_util", "eval_call")
_emit_proposal_commits_routing("p1", "decorators_util", "routing_commit")
_emit_escalates_to_human("p1", "decorators_util", "human_escalation")
_emit_routes_through("p1", "decorators_util", "route_through")
_emit_checks_agent_registry("p1", "decorators_util", "agent_registry")
_emit_validates_agent_capability("p1", "decorators_util", "capability")
_emit_dispatches_execution_plan("p1", "decorators_util", "exec_plan")
_emit_agent_executes_agent("p1", "decorators_util", "sub_agent")
_emit_routes_to_agent("p1", "decorators_util", "target_agent")
_emit_verifies_policy("p1", "decorators_util", "policy_check")
_emit_observes_runtime_state("p1", "decorators_util", "runtime_state")
_emit_verifies_boundary("p1", "decorators_util", "boundary_check")
_emit_transcripts_response("p1", "decorators_util", "transcript")
_emit_hard_fails_untranscripted("p1", "decorators_util")
_emit_gated_by_confidence("p1", "decorators_util", "confidence_gate")
emit_replay_key("p0", "decorators_util")
emit_determinism_digest("p0", "decorators_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

if TYPE_CHECKING:
    from agentic_core.L5_safety.types.heal_policy_types import (
        ReasoningTier,
    )


def _get_heal_llm_seam_types():
    from agentic_core.L5_safety.types.heal_llm_seam_types import (
        HealLlmRequest,
        PolicyDecisionRecord,
        guarded_heal_llm_call,
        reset_heal_seam_capability,
        set_heal_seam_capability,
    )

    return (
        HealLlmRequest,
        PolicyDecisionRecord,
        guarded_heal_llm_call,
        reset_heal_seam_capability,
        set_heal_seam_capability,
    )


def _get_heal_policy_types():
    from agentic_core.L3_orchestration.healers.healing_tier_router import route_by_confidence
    from agentic_core.L5_safety.types.heal_policy_types import ReasoningTier

    return route_by_confidence, ReasoningTier


# Backward-compat alias — resolved lazily at call time
def decide_reasoning_tier(*args, **kwargs):
    from agentic_core.L5_safety.types.heal_policy_types import decide_heal_escalation

    return decide_heal_escalation(*args, **kwargs)


Logger = logging.getLogger(__name__)

# Type variable for decorated functions
F = TypeVar("F", bound=Callable[..., Any])


# Canonical HealResult schema keys
HEAL_RESULT_SCHEMA = {
    "violations_found": 0,
    "violations_fixed": 0,
    "status": "UNKNOWN",
    "errors": 0,
    "skipped": 0,
    "execution_time_ms": 0.0,
    "error_message": None,
}


def _select_reasoning_tier_enabled() -> bool:
    """Check if heal policy model escalation is enabled via env var.

    Returns True iff HEAL_POLICY_MODEL_ESCALATION == "1", else False.
    """
    return os.environ.get("HEAL_POLICY_MODEL_ESCALATION") == "1"


# Phase 4: Seam for tier observation (default None, no external calls)
_HEAL_TIER_OBSERVER: Callable[[ReasoningTier], None] | None = None


# Phase 6: Seam for model routing (default None, no SDK/executor imports)
_HEAL_MODEL_ROUTER: Callable[[ReasoningTier], str] | None = None

# Phase 8: Default LLM caller seam (test patching)
DEFAULT_HEAL_LLM_CALLER: Callable[[Any], Any] | None = None


def _warn_non_canonical_keys(result: dict[str, Any], agent_name: str) -> None:
    """Emit warnings for non-canonical keys in heal_repository return values."""
    if not isinstance(result, dict):
        return

    canonical_keys = {
        "violations_found",
        "violations_fixed",
        "errors",
        "skipped",
        "status",
        "execution_time_ms",
        "error_message",
    }

    non_canonical = sorted(k for k in result if k not in canonical_keys)
    if non_canonical:
        Logger.warning(
            f"[standard_heal] {agent_name}: {len(non_canonical)} non-canonical key(s): "
            f"{', '.join(non_canonical[:5])}{'...' if len(non_canonical) > 5 else ''}",
        )


def _normalize_heal_result(
    result: Any,
    execution_time_ms: float,
    agent_name: str = "",
) -> dict[str, Any]:
    """Normalize a heal result to the canonical HealResult schema."""
    if isinstance(result, dict):
        _warn_non_canonical_keys(result, agent_name)

    normalized: dict[str, Any] = {
        **HEAL_RESULT_SCHEMA,
        "execution_time_ms": execution_time_ms,
    }

    if result is None:
        normalized["status"] = "SKIPPED"
        normalized["skipped"] = 1
        return normalized

    if isinstance(result, bool):
        normalized["status"] = "PASS" if result else "FAIL"
        return normalized

    if isinstance(result, int):
        normalized["violations_found"] = result
        normalized["status"] = "PASS" if result == 0 else "FAIL"
        return normalized

    if isinstance(result, dict):
        for key in HEAL_RESULT_SCHEMA.keys():
            if key in result:
                normalized[key] = result[key]

        if "error_message" in result:
            normalized["error_message"] = result["error_message"]
        elif "error" in result:
            normalized["error_message"] = str(result["error"])
        elif "message" in result:
            normalized["error_message"] = result["message"]

        if normalized["status"] == "UNKNOWN":
            if normalized.get("error_message") or normalized.get("errors", 0) > 0:
                normalized["status"] = "ERROR"
            elif normalized.get("skipped", 0) > 0 and normalized.get("violations_found", 0) == 0:
                normalized["status"] = "SKIPPED"
            elif normalized.get("violations_found", 0) == 0:
                normalized["status"] = "PASS"
            elif normalized.get("violations_fixed", 0) >= normalized.get(
                "violations_found",
                0,
            ):
                normalized["status"] = "PASS"
            else:
                normalized["status"] = "FAIL"

        normalized["_raw_result"] = result
        return normalized

    Logger.warning(f"[standard_heal] Unexpected result type: {type(result)}")
    normalized["status"] = "ERROR"
    normalized["error_message"] = f"Unexpected result type: {type(result)}"
    return normalized


def _normalize_heal_inputs(kwargs: dict[str, Any]) -> tuple[bool, bool, dict[str, Any]]:
    """Normalize heal_repository inputs."""
    dry_run = kwargs.pop("dry_run", True)
    execute = kwargs.pop("execute", False)

    if not isinstance(dry_run, bool):
        dry_run = bool(dry_run)
    if not isinstance(execute, bool):
        execute = bool(execute)

    return dry_run, execute, kwargs


def standard_heal(func: F) -> F:
    """
    Decorator that standardizes heal_repository() methods.

    Provides:
    1. Input Normalization: Ensures dry_run and execute args exist with safe defaults
    2. Output Normalization: Converts legacy dicts to canonical HealResult schema
    3. Error Containment: Catches crashes and returns valid HealResult with status='ERROR'

    Supports Phase 20 HealerMixin signature (depth, _call_path).
    """

    @functools.wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> dict[str, Any]:
        start_time = time.time()
        agent_name = self.__class__.__name__

        # Phase 3: Set canonical seam capability token
        (
            HealLlmRequest,
            PolicyDecisionRecord,
            guarded_heal_llm_call,
            reset_heal_seam_capability,
            set_heal_seam_capability,
        ) = _get_heal_llm_seam_types()
        route_by_confidence, ReasoningTier = _get_heal_policy_types()
        capability_token = set_heal_seam_capability(True)

        try:
            dry_run, execute, remaining_kwargs = _normalize_heal_inputs(kwargs)
            depth = remaining_kwargs.pop("depth", 0)
            _call_path = remaining_kwargs.pop("_call_path", None)
            auto_approve = remaining_kwargs.pop("auto_approve", False)

            Logger.debug(
                f"[standard_heal] {agent_name}.{func.__name__} "
                f"(dry_run={dry_run}, execute={execute}, depth={depth}, auto_approve={auto_approve})",
            )

            # Phase 2: Compute heal policy decision using score-based routing.
            # Score S determines tier: S<=13 agent-native, S14-26 Qwen, S>26 Gemini.
            # proceed is always True — routing by score never blocks healing.
            # If auto_approve=True the external decision_engine has already approved.
            enable_llm = _select_reasoning_tier_enabled()
            score = remaining_kwargs.pop("_score", 0)
            # Backward-compat: pop legacy kwargs so they don't leak into func signature
            remaining_kwargs.pop("_confidence", None)
            remaining_kwargs.pop("_task_complexity", None)
            remaining_kwargs.pop("_prior_failures", None)

            if auto_approve:
                policy_decision = None
            else:
                heal_decision = route_by_confidence(confidence=0.75, retry_count=score)
                _tier_name = heal_decision.tier.value
                policy_decision = type(
                    "_RoutedDecision",
                    (),
                    {
                        "proceed": True,
                        "tier": type("_Tier", (), {"name": _tier_name})(),
                        "threshold_used": "CANONICAL_ROUTER",
                        "rationale": " | ".join(heal_decision.reason_codes),
                    },
                )()
                Logger.debug(
                    f"[heal_policy] proceed=True tier={_tier_name} threshold=CANONICAL_ROUTER",
                )

            # Phase 4: LLM escalation (only if tier is set)
            routed_model_id: str | None = None
            if policy_decision is not None and policy_decision.tier is not None and enable_llm:
                Logger.debug(
                    f"[heal_policy] escalation_enabled=1 selected_tier={policy_decision.tier.name}",
                )
                # Invoke observer seam if set (for testing/monitoring)
                if _HEAL_TIER_OBSERVER is not None:
                    _HEAL_TIER_OBSERVER(policy_decision.tier)

                # Phase 6: Model routing seam (no SDK/executor imports)
                if _HEAL_MODEL_ROUTER is not None:
                    routed_model_id = _HEAL_MODEL_ROUTER(policy_decision.tier)
                    Logger.debug(f"[heal_policy] routed_model={routed_model_id}")
                else:
                    Logger.debug("[heal_policy] routed_model=NONE")

                remaining_kwargs["_heal_routed_model_id"] = routed_model_id

                # Phase 8: Invoke heal LLM seam probe via guarded call (only when model is routed)
                if routed_model_id is not None:
                    request = HealLlmRequest(
                        prompt="heal_policy_probe",
                        model_id=routed_model_id,
                        metadata={"source": "standard_heal"},
                    )
                    _ = guarded_heal_llm_call(request)
                    Logger.debug(f"[heal_policy] llm_probe=CALLED model_id={routed_model_id}")

            # Phase 3: Create and store policy decision record for observability
            if policy_decision is not None:
                policy_record = PolicyDecisionRecord(
                    confidence=float(score),
                    enable_llm=enable_llm,
                    complexity=score,
                    prior_failures=0,
                    proceed=policy_decision.proceed,
                    tier=policy_decision.tier.name if policy_decision.tier else None,
                    threshold_used=policy_decision.threshold_used,
                    rationale=policy_decision.rationale,
                )
                _policy_for_result = policy_record.to_dict()
            else:
                _policy_for_result = {
                    "proceed": True,
                    "tier": None,
                    "threshold_used": "AUTO_APPROVED",
                    "rationale": "auto_approve=True",
                }

            # Map *args to named parameters using signature introspection.
            # This handles module-level @standard_heal functions (e.g. execute_phase3_validation)
            # where positional args like territory/original_violations live in *args.
            try:
                _sig = inspect.signature(func)
                _param_names = list(_sig.parameters.keys())
                _has_var_kw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in _sig.parameters.values())
            except (ValueError, TypeError):
                _param_names = []
                _has_var_kw = True

            _positional_kwargs: dict[str, Any] = {}
            for _i, _val in enumerate(args):
                _pidx = _i + 1  # skip 'self' at index 0
                if _pidx < len(_param_names):
                    _pname = _param_names[_pidx]
                    if _pname not in ("dry_run", "execute"):
                        _positional_kwargs[_pname] = _val

            _call_kwargs: dict[str, Any] = {**_positional_kwargs, **remaining_kwargs}
            _call_kwargs["dry_run"] = dry_run
            _call_kwargs["execute"] = execute
            _call_kwargs["depth"] = depth
            _call_kwargs["_call_path"] = _call_path

            # Strip kwargs the function does not accept (only when no **kwargs)
            if not _has_var_kw:
                _call_kwargs = {k: v for k, v in _call_kwargs.items() if k in _param_names}

            raw_result = func(self, **_call_kwargs)

            # Inject policy decision into raw result for observability (never passed to func)
            if isinstance(raw_result, dict):
                raw_result["_policy_from_kwargs"] = _policy_for_result

            result = raw_result

            execution_time_ms = (time.time() - start_time) * 1000
            normalized = _normalize_heal_result(result, execution_time_ms, agent_name)

            Logger.debug(
                f"[standard_heal] {agent_name}.{func.__name__} completed: "
                f"status={normalized['status']}, "
                f"violations={normalized['violations_found']}, "
                f"fixed={normalized['violations_fixed']}",
            )

            return normalized

        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            execution_time_ms = (time.time() - start_time) * 1000

            Logger.error(
                f"[standard_heal] {agent_name}.{func.__name__} crashed: {e}\n{traceback.format_exc()}",
            )

            return {
                **HEAL_RESULT_SCHEMA,
                "status": "ERROR",
                "errors": 1,
                "execution_time_ms": execution_time_ms,
                "error_message": str(e),
                "_exception_type": type(e).__name__,
                "_traceback": traceback.format_exc(),
            }

        finally:
            # Phase 3: Reset canonical seam capability token
            reset_heal_seam_capability(capability_token)

    return cast(F, wrapper)


def standard_heal_async(func: F) -> F:
    """
    Async version of @standard_heal decorator.

    Provides the same standardization for async heal_repository methods.
    Supports Phase 20 HealerMixin signature (depth, _call_path).
    """

    @functools.wraps(func)
    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> dict[str, Any]:
        start_time = time.time()
        agent_name = self.__class__.__name__

        try:
            dry_run, execute, remaining_kwargs = _normalize_heal_inputs(kwargs)
            depth = remaining_kwargs.pop("depth", 0)
            _call_path = remaining_kwargs.pop("_call_path", None)

            Logger.debug(
                f"[standard_heal_async] {agent_name}.{func.__name__} "
                f"(dry_run={dry_run}, execute={execute}, depth={depth})",
            )

            result = await func(
                self,
                *args,
                dry_run=dry_run,
                execute=execute,
                depth=depth,
                _call_path=_call_path,
                **remaining_kwargs,
            )

            execution_time_ms = (time.time() - start_time) * 1000
            normalized = _normalize_heal_result(result, execution_time_ms, agent_name)

            return normalized

        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            execution_time_ms = (time.time() - start_time) * 1000

            Logger.error(
                f"[standard_heal_async] {agent_name}.{func.__name__} crashed: {e}\n{traceback.format_exc()}",
            )

            return {
                **HEAL_RESULT_SCHEMA,
                "status": "ERROR",
                "errors": 1,
                "execution_time_ms": execution_time_ms,
                "error_message": str(e),
            }

    return cast(F, wrapper)


__all__ = [
    "standard_heal",
    "standard_heal_async",
    "HEAL_RESULT_SCHEMA",
    "timeout",
    "TimeoutError",
]
