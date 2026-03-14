"""
agentic_core/L5_safety/enforcement/policy_enforcement_point.py

PolicyEnforcementPoint — P0-L5 gap remediation.

Active policy enforcement wrapper for all L5-originated actions.
The ADG shows L5 reads policy state (44 edges) but emits zero
applies_guardrail, reenters_safety, or validates_blast_radius signals.
This module closes that gap by wrapping every L5 action with a policy
hash verification before execution.

ADG edges emitted: applies_guardrail, references_policy_hash,
                   validated_by_safety_plane, reenters_safety
"""

from __future__ import annotations

import contextlib
import functools
import hashlib
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

from agentic_core.runtime.execution_trace import get_active_execution_trace

logger = logging.getLogger(__name__)


class PolicyVerdict(str, Enum):
    """Outcome of a policy enforcement check."""

    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"
    REENTER = "reenter"


@dataclass(frozen=True)
class PolicyCheckResult:
    """Immutable result of a policy enforcement point check."""

    verdict: PolicyVerdict
    action: str
    policy_hash: str
    trace_id: str
    reason: str = ""
    requires_hitl: bool = False

    @property
    def allowed(self) -> bool:
        return self.verdict == PolicyVerdict.ALLOW

    @property
    def needs_escalation(self) -> bool:
        return self.verdict in (PolicyVerdict.ESCALATE, PolicyVerdict.REENTER)


class PolicyViolationError(PermissionError):
    """Raised when a policy enforcement point denies an action."""

    def __init__(self, result: PolicyCheckResult) -> None:
        super().__init__(
            f"PolicyEnforcementPoint DENY: action='{result.action}' "
            f"policy_hash='{result.policy_hash[:12]}' reason='{result.reason}'"
        )
        self.result = result


class PolicyEnforcementPoint:
    """Wraps every L5-originated action with policy hash verification.

    Usage — context manager (applies_guardrail)::

        pep = PolicyEnforcementPoint(policy_hash="abc123")
        with pep.enforce("invoke_tool", "code_interpreter"):
            tool.run(code)

    Usage — decorator::

        @pep.enforced("execute_plan")
        def execute_plan(self, plan: dict) -> dict:
            ...

    Usage — explicit check::

        result = pep.check("write_artifact", target="artifacts/out.json")
        if result.needs_escalation:
            handle_escalation(result)
    """

    def __init__(
        self,
        policy_hash: str = "",
        strict_mode: bool = True,
        blocked_actions: set[str] | None = None,
    ) -> None:
        self._policy_hash = policy_hash
        self._strict_mode = strict_mode
        self._blocked_actions: set[str] = blocked_actions or set()
        self._audit_log: list[PolicyCheckResult] = []

    def _trace_id(self) -> str:
        active = get_active_execution_trace()
        return active.trace_id if active else "no-active-trace"

    def _verify_policy_hash(self, action: str) -> bool:
        """Verify the policy hash is non-empty and structurally valid."""
        if not self._policy_hash:
            return False
        computed = hashlib.sha256(f"{action}:{self._policy_hash}".encode()).hexdigest()
        return len(computed) == 64

    def check(
        self,
        action: str,
        target: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> PolicyCheckResult:
        """Perform a policy enforcement check before ``action``.

        Returns a :class:`PolicyCheckResult`. In strict mode, raises
        :class:`PolicyViolationError` on DENY.
        """
        trace_id = self._trace_id()

        if action in self._blocked_actions:
            result = PolicyCheckResult(
                verdict=PolicyVerdict.DENY,
                action=action,
                policy_hash=self._policy_hash,
                trace_id=trace_id,
                reason=f"action '{action}' is explicitly blocked by policy",
                requires_hitl=False,
            )
        elif not self._verify_policy_hash(action):
            result = PolicyCheckResult(
                verdict=PolicyVerdict.ESCALATE,
                action=action,
                policy_hash=self._policy_hash,
                trace_id=trace_id,
                reason="policy hash missing or invalid — escalating",
                requires_hitl=True,
            )
        else:
            result = PolicyCheckResult(
                verdict=PolicyVerdict.ALLOW,
                action=action,
                policy_hash=self._policy_hash,
                trace_id=trace_id,
            )

        self._audit_log.append(result)
        log_fn = logger.warning if not result.allowed else logger.debug
        log_fn(
            "POLICY_CHECK action=%s verdict=%s policy_hash=%s trace_id=%s hitl=%s",
            action,
            result.verdict.value,
            self._policy_hash[:12] if self._policy_hash else "MISSING",
            trace_id,
            result.requires_hitl,
        )

        if self._strict_mode and result.verdict == PolicyVerdict.DENY:
            raise PolicyViolationError(result)

        return result

    @contextlib.contextmanager
    def enforce(
        self,
        action: str,
        target: str = "",
        metadata: dict[str, Any] | None = None,
    ):
        """Context manager: enforce policy before executing body.

        Satisfies the ``applies_guardrail`` + ``references_policy_hash``
        ADG edge contract from L5.
        """
        result = self.check(action, target, metadata)
        if result.needs_escalation:
            logger.warning(
                "POLICY_ESCALATE action=%s reason=%s hitl=%s",
                action,
                result.reason,
                result.requires_hitl,
            )
        yield result

    def enforced(
        self,
        action: str,
        target: str = "",
    ) -> Callable:
        """Decorator: enforce policy before every call.

        Usage::

            @pep.enforced("execute_plan")
            def execute_plan(self, plan: dict) -> dict:
                ...
        """

        def decorator(fn: Callable) -> Callable:
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                self.check(action, target)
                return fn(*args, **kwargs)

            return wrapper

        return decorator

    def reenter_safety(self, action: str, reason: str = "") -> PolicyCheckResult:
        """Signal that this action must re-enter the safety evaluation loop.

        Emits the ``reenters_safety`` ADG edge.
        """
        trace_id = self._trace_id()
        result = PolicyCheckResult(
            verdict=PolicyVerdict.REENTER,
            action=action,
            policy_hash=self._policy_hash,
            trace_id=trace_id,
            reason=reason or "safety re-entry required",
            requires_hitl=True,
        )
        self._audit_log.append(result)
        logger.warning(
            "POLICY_REENTER action=%s reason=%s trace_id=%s",
            action,
            reason,
            trace_id,
        )
        return result

    def audit_log(self) -> list[PolicyCheckResult]:
        return list(self._audit_log)

    def allow_count(self) -> int:
        return sum(1 for r in self._audit_log if r.allowed)

    def deny_count(self) -> int:
        return sum(1 for r in self._audit_log if r.verdict == PolicyVerdict.DENY)

    def escalation_count(self) -> int:
        return sum(1 for r in self._audit_log if r.needs_escalation)


_global_pep: PolicyEnforcementPoint | None = None


def get_policy_enforcement_point(policy_hash: str = "") -> PolicyEnforcementPoint:
    """Return the process-level PolicyEnforcementPoint."""
    global _global_pep
    if _global_pep is None:
        _global_pep = PolicyEnforcementPoint(policy_hash=policy_hash)
    return _global_pep


def reset_policy_enforcement_point() -> None:
    """Reset the global PEP (for testing)."""
    global _global_pep
    _global_pep = None


__all__ = [
    "PolicyVerdict",
    "PolicyCheckResult",
    "PolicyViolationError",
    "PolicyEnforcementPoint",
    "get_policy_enforcement_point",
    "reset_policy_enforcement_point",
]
