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
from typing import Any, TypeVar, cast

from agentic_core.L5_safety.types.heal_llm_seam_types import (
    HealLlmRequest,
    PolicyDecisionRecord,
    guarded_heal_llm_call,
    reset_heal_seam_capability,
    set_heal_seam_capability,
)
from agentic_core.L5_safety.types.heal_policy_types import (
    HealEscalationInputs,
    ReasoningTier,
    decide_heal_escalation,
)
from agentic_core.utils.timeout_decorator_util import TimeoutError, timeout

# Backward-compat alias for tests that patch decide_reasoning_tier
decide_reasoning_tier = decide_heal_escalation

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

    for key in result:
        if key not in canonical_keys:
            Logger.warning(
                f"[standard_heal] {agent_name}: Non-canonical key '{key}' detected. "
                f"Consider using canonical keys for better schema compliance.",
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
                policy_inputs = HealEscalationInputs(
                    score=score,
                    enable_llm=enable_llm,
                )
                policy_decision = decide_heal_escalation(policy_inputs)
                Logger.debug(
                    f"[heal_policy] proceed={policy_decision.proceed} "
                    f"tier={policy_decision.tier.name if policy_decision.tier else 'NONE'} "
                    f"threshold={policy_decision.threshold_used}",
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
                    "proceed": True, "tier": None,
                    "threshold_used": "AUTO_APPROVED", "rationale": "auto_approve=True",
                }

            # Map *args to named parameters using signature introspection.
            # This handles module-level @standard_heal functions (e.g. execute_phase3_validation)
            # where positional args like territory/original_violations live in *args.
            try:
                _sig = inspect.signature(func)
                _param_names = list(_sig.parameters.keys())
                _has_var_kw = any(
                    p.kind == inspect.Parameter.VAR_KEYWORD
                    for p in _sig.parameters.values()
                )
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

        except Exception as e:
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

        except Exception as e:
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
