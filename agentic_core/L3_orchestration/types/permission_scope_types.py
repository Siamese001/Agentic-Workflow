from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "permission_scope_types")
emit_determinism_digest("p0", "permission_scope_types")

_emit_dispatches_healing_run("p1", "permission_scope_types", "L3")
_emit_routes_through("p1", "permission_scope_types", "L3")
_emit_escalates_to_human("p1", "permission_scope_types", "L3")
_emit_reads_policy_state("p1", "permission_scope_types", "L3")

"Types and models for agent_permissions."
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

try:
    from agentic_core.L1_cognition.identity.spiffe_manager_types import AgentIdentity
except ImportError:
    AgentIdentity = type("AgentIdentity", (), {})
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

Logger: Any = logging.getLogger(__name__)


class PermissionScope(Enum):
    """Permission scopes."""

    TOOL_EXECUTION: Any = "tool_execution"
    DATA_ACCESS: Any = "data_access"
    AGENT_COMMUNICATION: Any = "agent_communication"
    SYSTEM_CONFIGURATION: Any = "system_configuration"
    CODE_EXECUTION: Any = "code_execution"


class PermissionAction(Enum):
    """Permission actions."""

    READ: Any = "read"
    WRITE: Any = "write"
    EXECUTE: Any = "execute"
    DELETE: Any = "delete"
    ADMIN: Any = "admin"


@dataclass
class Permission:
    """Individual Permission."""

    scope: PermissionScope
    action: PermissionAction
    resource: str
    conditions: dict[str, Any] = field(default_factory=dict)

    def matches(self, scope: PermissionScope, action: PermissionAction, resource: str) -> bool:
        """Check if Permission matches request.

        Args:
            scope: Requested scope
            action: Requested action
            resource: Requested resource

        Returns:
            True if matches
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "Permission.matches", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "Permission.matches", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "Permission.matches")

        scope_match: Any = self.scope == scope
        action_match: Any = self.action == action or self.action == PermissionAction.ADMIN
        resource_match: Any = self.resource == resource or self.resource == "*"
        return scope_match and action_match and resource_match

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scope": self.scope.value,
            "action": self.action.value,
            "resource": self.resource,
            "conditions": self.conditions,
        }


@dataclass
class PermissionCheck:
    """Result of Permission check."""

    allowed: bool
    identity: AgentIdentity
    Permission: Permission | None = None
    reason: str = ""
    safety_decision: Any | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "allowed": self.allowed,
            "identity": self.identity.to_dict(),
            "Permission": self.Permission.to_dict() if self.Permission else None,
            "reason": self.reason,
            "safety_decision": self.safety_decision.to_dict() if self.safety_decision else None,
        }
