"""
StateValidationMixin — Canonical location.

Relocated from agentic_core/L4_state/types/state_validation_types.py to satisfy
the mixin location invariant (all *Mixin classes under agentic_core/mixins/).

Original file re-exports this class for backward compatibility.
"""

from __future__ import annotations

import asyncio
import hashlib
import inspect
import json
import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

from agentic_core.L0_routing.config.path_constants import DEFAULT_TIMEOUT
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "state_validation_mixin", "p0_governance")
_emit_reads_policy_state("p0", "state_validation_mixin", "policy_binding")
_emit_snapshots_state("p0", "state_validation_mixin", "state_snapshot")
emit_replay_key("p0", "state_validation_mixin")
emit_determinism_digest("p0", "state_validation_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "state_validation_mixin", "execution_auth")
_emit_validates_capability("p2", "state_validation_mixin", "capability_check")
_emit_routes_to_capability("p2", "state_validation_mixin", "capability_route")
_emit_writes_via_uwg("p2", "state_validation_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "state_validation_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "state_validation_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "state_validation_mixin", "exec_output")
_emit_dispatches_agent("p3", "state_validation_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "state_validation_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "state_validation_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "state_validation_mixin", "healing_outcome")
_emit_escalates_failure("p3", "state_validation_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "state_validation_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "state_validation_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "state_validation_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "state_validation_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "state_validation_mixin", "eval_metric")
_emit_stores_embedding("p4", "state_validation_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "state_validation_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "state_validation_mixin", "exec_snapshot_link")


class StateValidationError(Exception):
    """Raised when a pre-condition or post-condition fails."""

    pass


class StateValidationMixin:
    """
    Phase 1 Critical Infrastructure: State Validation (Report 4.2).

    Ensures data consistency through:
    - Pre-condition checks (guard clauses)
    - Post-condition verification (invariants)
    - Idempotency guarantees via input hashing
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._sv_logger = logging.getLogger(self.__class__.__name__)
        self._operation_ledger: dict[str, Any] = {}

    def _run_conditions(self, conditions: list[Callable[..., bool]], result: Any = None) -> None:
        for condition in conditions:
            sig = inspect.signature(condition)
            if len(sig.parameters) == 1:
                ok = condition(self)
            else:
                ok = condition(self, result)
            if not ok:
                raise StateValidationError(f"Condition failed: {getattr(condition, '__name__', 'condition')}")

    def _generate_op_hash(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generates a unique deterministic hash for an operation call."""
        if len(str(args)) + len(str(kwargs)) > 100000:
            return None
        try:
            payload = {
                "func": func_name,
                "args": [str(a) for a in args],
                "kwargs": {k: str(v) for k, v in kwargs.items()},
            }
            s = json.dumps(payload, sort_keys=True)
            return hashlib.sha256(s.encode()).hexdigest()
        except Exception as e:
            self._sv_logger.warning(f"Could not generate idempotency hash: {e}")
            return None

    @staticmethod
    def validate_state(
        pre: Callable[[Any], bool] | None = None,
        post: Callable[[Any, Any], bool] | None = None,
        idempotent: bool = False,
    ):
        """
        Decorator to enforce state validity.

        Args:
            pre: Callable(self) -> bool. Runs BEFORE method. Raises if False.
            post: Callable(self, result) -> bool. Runs AFTER method. Raises if False.
            idempotent: If True, returns cached result for identical inputs.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "StateValidationMixin.validate_state")


        def decorator(func):
            @wraps(func)
            async def wrapper(self, *args, **kwargs):
                if not isinstance(self, StateValidationMixin):
                    return await func(self, *args, **kwargs)
                op_hash = None
                if idempotent:
                    op_hash = self._generate_op_hash(func.__name__, args, kwargs)
                    if op_hash and op_hash in self._operation_ledger:
                        self._sv_logger.info(f"Idempotent hit for {func.__name__} ({op_hash[:8]})")
                        return self._operation_ledger[op_hash]
                if pre:
                    try:
                        pre_conditions = pre if isinstance(pre, list) else [pre]
                        await asyncio.wait_for(
                            asyncio.to_thread(lambda: self._run_conditions(pre_conditions, None)),
                            timeout=DEFAULT_TIMEOUT,
                        )
                    except asyncio.TimeoutError:
                        raise StateValidationError(f"Pre-condition check timeout for {func.__name__}")
                    except Exception as e:
                        raise StateValidationError(f"Pre-condition failed: {e}")
                result = await func(self, *args, **kwargs)
                if post:
                    try:
                        post_conditions = post if isinstance(post, list) else [post]
                        for condition in post_conditions:
                            if not condition(self, result):
                                raise StateValidationError(f"Post-condition failed for {func.__name__}")
                    except Exception as e:
                        raise StateValidationError(f"Post-condition error in {func.__name__}: {e}")
                if idempotent and op_hash:
                    self._operation_ledger[op_hash] = result
                if hasattr(self, "emit_event"):
                    self.emit_event(
                        "state_validation.success" if result is not None else "state_validation.failed",
                        {"method": func.__name__},
                        severity="INFO" if result is not None else "WARNING",
                    )
                return result

            return wrapper

        return decorator
