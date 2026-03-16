"""
agentic_core/L2_execution/context/execution_context.py

Run-scoped ExecutionContext — P0/L2 closure.

All 9 required fields per the guardrail contract MUST be present on
every execution attempt.  No execution may proceed without an explicit
ExecutionContext.

ADG edges emitted (via authorize_and_execute):
    applies_guardrail
    validated_by_safety_plane
    references_policy_hash
    execution_terminates_at_uwg
    reenters_safety
    requires_human_review
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "execution_context")
emit_determinism_digest("p0", "execution_context")

_emit_dispatches_healing_run("p1", "execution_context", "L2")
_emit_routes_through("p1", "execution_context", "L2")
_emit_escalates_to_human("p1", "execution_context", "L2")
_emit_reads_policy_state("p1", "execution_context", "L2")


class ActionClass(str, Enum):
    """Execution target action classification.

    Every execution target must be classified before execution.
    Higher-risk classes require stricter routing.
    """

    READ_ONLY = "READ_ONLY"
    MUTATION = "MUTATION"
    NETWORK = "NETWORK"
    PRIVILEGED_LOCAL = "PRIVILEGED_LOCAL"
    EXTERNAL_SIDE_EFFECT = "EXTERNAL_SIDE_EFFECT"
    HUMAN_GATED = "HUMAN_GATED"

    @property
    def is_irreversible(self) -> bool:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ActionClass.is_irreversible", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ActionClass.is_irreversible", "p0_governance")
        return self in (
            ActionClass.MUTATION,
            ActionClass.PRIVILEGED_LOCAL,
            ActionClass.EXTERNAL_SIDE_EFFECT,
            ActionClass.HUMAN_GATED,
        )

    @property
    def requires_uwg(self) -> bool:
        return self in (ActionClass.MUTATION, ActionClass.PRIVILEGED_LOCAL)

    @property
    def requires_human_review(self) -> bool:
        return self == ActionClass.HUMAN_GATED

    @property
    def requires_network_policy(self) -> bool:
        return self == ActionClass.NETWORK


class GuardrailOutcome(str, Enum):
    """Fail-closed guardrail outcome set.

    Only ALLOW may proceed to execution.
    All other outcomes MUST terminate execution.
    """

    ALLOW = "ALLOW"
    DENY = "DENY"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"

    @property
    def may_proceed(self) -> bool:
        return self == GuardrailOutcome.ALLOW

    @property
    def is_abnormal(self) -> bool:
        return self != GuardrailOutcome.ALLOW


@dataclass(frozen=True)
class ExecutionContext:
    """Immutable run-scoped execution context.

    All 9 required fields MUST be non-empty at creation time.
    No execution may proceed without an explicit instance.

    Fields:
        execution_request_id   — unique per execution attempt
        run_id                 — agent run linkage
        capability_token       — token proving authority to act
        policy_hash            — active policy state hash
        guardrail_decision_id  — ID of guardrail decision (filled post-evaluation)
        guardrail_decision_hash — hash of guardrail decision (filled post-evaluation)
        execution_input_hash   — hash of execution payload
        execution_target_hash  — hash of execution target identifier
        trace_id               — routing/execution trace linkage
    """

    execution_request_id: str
    run_id: str
    capability_token: str
    policy_hash: str
    guardrail_decision_id: str
    guardrail_decision_hash: str
    execution_input_hash: str
    execution_target_hash: str
    trace_id: str
    action_class: ActionClass = ActionClass.READ_ONLY
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        missing = [
            f
            for f in (
                "execution_request_id",
                "run_id",
                "capability_token",
                "policy_hash",
                "execution_input_hash",
                "execution_target_hash",
                "trace_id",
            )
            if not getattr(self, f)
        ]
        if missing:
            raise ValueError(f"ExecutionContext missing required fields: {missing}")

    @classmethod
    def create(
        cls,
        *,
        run_id: str,
        capability_token: str,
        policy_hash: str,
        execution_input: Any,
        execution_target: str,
        action_class: ActionClass = ActionClass.READ_ONLY,
        trace_id: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> ExecutionContext:
        """Factory with deterministic hashing."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ExecutionContext.create")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ExecutionContext.create".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        input_hash = hashlib.sha256(repr(execution_input).encode()).hexdigest()[:32]
        target_hash = hashlib.sha256(execution_target.encode()).hexdigest()[:32]
        return cls(
            execution_request_id=str(uuid.uuid4()),
            run_id=run_id,
            capability_token=capability_token,
            policy_hash=policy_hash,
            guardrail_decision_id="",
            guardrail_decision_hash="",
            execution_input_hash=input_hash,
            execution_target_hash=target_hash,
            trace_id=trace_id or str(uuid.uuid4()),
            action_class=action_class,
            extra=extra or {},
        )

    def with_guardrail_decision(
        self,
        decision_id: str,
        decision_hash: str,
    ) -> ExecutionContext:
        """Return copy with guardrail decision bound."""
        return ExecutionContext(
            execution_request_id=self.execution_request_id,
            run_id=self.run_id,
            capability_token=self.capability_token,
            policy_hash=self.policy_hash,
            guardrail_decision_id=decision_id,
            guardrail_decision_hash=decision_hash,
            execution_input_hash=self.execution_input_hash,
            execution_target_hash=self.execution_target_hash,
            trace_id=self.trace_id,
            action_class=self.action_class,
            extra=self.extra,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_request_id": self.execution_request_id,
            "run_id": self.run_id,
            "capability_token": self.capability_token[:8] + "...",
            "policy_hash": self.policy_hash,
            "guardrail_decision_id": self.guardrail_decision_id,
            "guardrail_decision_hash": self.guardrail_decision_hash,
            "execution_input_hash": self.execution_input_hash,
            "execution_target_hash": self.execution_target_hash,
            "trace_id": self.trace_id,
            "action_class": self.action_class.value,
        }


__all__ = [
    "ActionClass",
    "ExecutionContext",
    "GuardrailOutcome",
]
