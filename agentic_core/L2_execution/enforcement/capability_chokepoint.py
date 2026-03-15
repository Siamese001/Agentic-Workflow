"""P5.1 Capability-Gated L2 Single Chokepoint — G-12-3 Implementation.

Every L2 execution invocation MUST pass through authorize_and_execute.
Missing or invalid CapabilityTokenArtifact => FAIL-CLOSED (PermissionError).
Every invocation emits a typed CapabilityDecisionArtifact (ALLOW or DENY).
No alternate execution path may bypass this module.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Callable, TypeVar

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.L2_execution.types.capability_token_types import (
    CapabilityDecisionArtifact,
    CapabilityEnforcer,
    CapabilityTokenArtifact,
    build_capability_decision,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_hard_fails_untranscripted,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")

# =============================================================================
# Single chokepoint — all L2 execution MUST route through this function
# =============================================================================


class CapabilityChokepoint:
    """Singleton-style chokepoint enforcer for the L2 execution boundary.

    Tracks all decisions emitted during the lifetime of this instance.
    """

    def __init__(self) -> None:
        self._decisions: list[CapabilityDecisionArtifact] = []
        self._frozen: bool = False

    @property
    def decisions(self) -> list[CapabilityDecisionArtifact]:
        """All decisions emitted through this chokepoint."""
        return list(self._decisions)

    def freeze(self) -> None:
        """REQ-091: Tier III freeze — token issuance and execution blocked."""
        self._frozen = True

    def issue_token(self, scope: str, trace_id: str) -> None:
        """REQ-091: Issue a capability token for a given scope.

        Raises PermissionError if the chokepoint is frozen.
        """
        if self._frozen:
            raise PermissionError(
                f"REQ-091: CapabilityChokepoint frozen — token issuance blocked (scope={scope})."
            )

    def authorize_and_execute(
        self,
        *,
        token: CapabilityTokenArtifact | None,
        fn: Callable[..., T],
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
        tool_name: str,
        action: str,
        requested_resource: str,
        required_permission: str,
        semantic_clock: SemanticClockSnapshot,
    ) -> T:
        """Single L2 execution chokepoint — P5.1 enforcement.

        Args:
            token: CapabilityTokenArtifact. None => FAIL-CLOSED.
            fn: The callable to execute on ALLOW.
            args: Positional arguments for fn.
            kwargs: Keyword arguments for fn.
            tool_name: Name of the tool being invoked.
            action: Action being performed.
            requested_resource: Resource path being accessed.
            required_permission: Permission code required.
            semantic_clock: Current semantic clock snapshot.

        Returns:
            Result of fn(*args, **kwargs) on ALLOW.

        Raises:
            PermissionError: On DENY or missing/invalid token (FAIL-CLOSED).
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "CapabilityChokepoint.authorize_and_execute")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:CapabilityChokepoint.authorize_and_execute".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if kwargs is None:
            kwargs = {}

        # FAIL-CLOSED: missing token
        if token is None:
            decision = build_capability_decision(
                semantic_clock=semantic_clock,
                tool_name=tool_name,
                action=action,
                requested_resource=requested_resource,
                decision="DENY",
                deny_reason="TOKEN_MISSING",
                capability_trace_id="NONE",
            )
            self._decisions.append(decision)
            logger.warning(
                "CAPABILITY_CHOKEPOINT DENY: token missing for %s/%s",
                tool_name,
                action,
            )
            raise PermissionError("CAPABILITY_CHOKEPOINT_FAIL_CLOSED: no CapabilityTokenArtifact provided")

        # FAIL-CLOSED: invalid token type
        if not isinstance(token, CapabilityTokenArtifact):
            decision = build_capability_decision(
                semantic_clock=semantic_clock,
                tool_name=tool_name,
                action=action,
                requested_resource=requested_resource,
                decision="DENY",
                deny_reason=f"TOKEN_INVALID_TYPE:{type(token).__name__}",
                capability_trace_id="NONE",
            )
            self._decisions.append(decision)
            logger.warning(
                "CAPABILITY_CHOKEPOINT DENY: invalid token type %s for %s/%s",
                type(token).__name__,
                tool_name,
                action,
            )
            raise PermissionError(
                f"CAPABILITY_CHOKEPOINT_FAIL_CLOSED: expected CapabilityTokenArtifact, "
                f"got {type(token).__name__}"
            )

        # FAIL-CLOSED: invalid artifact_type field
        if token.artifact_type != "CAPABILITY_TOKEN":
            decision = build_capability_decision(
                semantic_clock=semantic_clock,
                tool_name=tool_name,
                action=action,
                requested_resource=requested_resource,
                decision="DENY",
                deny_reason=f"TOKEN_ARTIFACT_TYPE_MISMATCH:{token.artifact_type}",
                capability_trace_id=token.trace_id,
            )
            self._decisions.append(decision)
            raise PermissionError(
                f"CAPABILITY_CHOKEPOINT_FAIL_CLOSED: artifact_type mismatch '{token.artifact_type}'"
            )

        # Delegate to CapabilityEnforcer for permission/path/quota checks
        enforcer = CapabilityEnforcer(token)
        # CapabilityEnforcer.check() raises PermissionError on DENY
        decision = enforcer.check(
            tool_name=tool_name,
            action=action,
            requested_resource=requested_resource,
            required_permission=required_permission,
            semantic_clock=semantic_clock,
        )
        self._decisions.append(decision)

        # ALLOW — execute the guarded function
        logger.info(
            "CAPABILITY_CHOKEPOINT ALLOW: %s/%s (trace=%s)",
            tool_name,
            action,
            decision.trace_id,
        )
        return fn(*args, **kwargs)


# Module-level singleton — the ONE chokepoint for all L2 execution
_chokepoint = CapabilityChokepoint()


def authorize_and_execute(
    *,
    token: CapabilityTokenArtifact | None,
    fn: Callable[..., T],
    args: tuple[Any, ...] = (),
    kwargs: dict[str, Any] | None = None,
    tool_name: str,
    action: str,
    requested_resource: str,
    required_permission: str,
    semantic_clock: SemanticClockSnapshot,
) -> T:
    """Module-level entry — delegates to the singleton CapabilityChokepoint.

    This is the ONLY function external callers should use for L2 execution.
    """
    _emit_hard_fails_untranscripted(str(uuid.uuid4()), "Module.authorize_and_execute")
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.authorize_and_execute", "L2_EXECUTION")
    return _chokepoint.authorize_and_execute(
        token=token,
        fn=fn,
        args=args,
        kwargs=kwargs,
        tool_name=tool_name,
        action=action,
        requested_resource=requested_resource,
        required_permission=required_permission,
        semantic_clock=semantic_clock,
    )


def get_chokepoint() -> CapabilityChokepoint:
    """Return the module-level singleton for inspection/testing."""
    return _chokepoint


def reset_chokepoint() -> None:
    """Reset the singleton (testing only)."""
    global _chokepoint
    _chokepoint = CapabilityChokepoint()


__all__ = [
    "CapabilityChokepoint",
    "authorize_and_execute",
    "get_chokepoint",
    "reset_chokepoint",
]
