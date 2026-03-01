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
import logging
import os
import time
import traceback
from collections.abc import Callable
from typing import Any, TypeVar, cast

from agentic_core.L5_safety.types.heal_llm_seam import (
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

            # Phase 2: Compute heal policy decision using canonical escalation
            # If auto_approve=True the external decision_engine has already approved — skip gate.
            enable_llm = _select_reasoning_tier_enabled()
            confidence_value = remaining_kwargs.pop("_confidence", 0.75)
            task_complexity = remaining_kwargs.pop("_task_complexity", 5)
            prior_failures = remaining_kwargs.pop("_prior_failures", 0)

            if auto_approve:
                policy_decision = None
            else:
                policy_inputs = HealEscalationInputs(
                    confidence_value=confidence_value,
                    enable_llm=enable_llm,
                    task_complexity=task_complexity,
                    prior_failures=prior_failures,
                )
                policy_decision = decide_heal_escalation(policy_inputs)
                Logger.debug(
                    f"[heal_policy] proceed={policy_decision.proceed} "
                    f"tier={policy_decision.tier.name if policy_decision.tier else 'NONE'} "
                    f"threshold={policy_decision.threshold_used}",
                )

            # Hard gate: If proceed=False, return deterministic refusal (no LLM)
            if policy_decision is not None and not policy_decision.proceed:
                execution_time_ms = (time.time() - start_time) * 1000
                return {
                    **HEAL_RESULT_SCHEMA,
                    "status": "BLOCKED",
                    "violations_found": 0,
                    "violations_fixed": 0,
                    "execution_time_ms": execution_time_ms,
                    "error_message": policy_decision.rationale,
                    "_policy_decision": {
                        "proceed": False,
                        "tier": None,
                        "threshold_used": policy_decision.threshold_used,
                        "rationale": policy_decision.rationale,
                    },
                }

            # Phase 4: LLM escalation (only if proceed=True AND tier is set)
            routed_model_id: str | None = None
            if policy_decision.tier is not None and enable_llm:
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
                    confidence=confidence_value,
                    enable_llm=enable_llm,
                    complexity=task_complexity,
                    prior_failures=prior_failures,
                    proceed=policy_decision.proceed,
                    tier=policy_decision.tier.name if policy_decision.tier else None,
                    threshold_used=policy_decision.threshold_used,
                    rationale=policy_decision.rationale,
                )
                remaining_kwargs["_policy_decision"] = policy_record.to_dict()
            else:
                remaining_kwargs["_policy_decision"] = {
                    "proceed": True, "tier": None,
                    "threshold_used": "AUTO_APPROVED", "rationale": "auto_approve=True",
                }

            result = func(
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
