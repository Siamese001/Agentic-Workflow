from __future__ import annotations
'Types and models for agent_permissions.'
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
try:
    from agentic_core.L1_cognition.identity.spiffe_manager_types import AgentIdentity
except ImportError:
    AgentIdentity = type('AgentIdentity', (), {})
Logger: Any = logging.getLogger(__name__)

class PermissionScope(Enum):
    """Permission scopes."""
    TOOL_EXECUTION: Any = 'tool_execution'
    DATA_ACCESS: Any = 'data_access'
    AGENT_COMMUNICATION: Any = 'agent_communication'
    SYSTEM_CONFIGURATION: Any = 'system_configuration'
    CODE_EXECUTION: Any = 'code_execution'

class PermissionAction(Enum):
    """Permission actions."""
    READ: Any = 'read'
    WRITE: Any = 'write'
    EXECUTE: Any = 'execute'
    DELETE: Any = 'delete'
    ADMIN: Any = 'admin'

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
        scope_match: Any = self.scope == scope
        action_match: Any = self.action == action or self.action == PermissionAction.ADMIN
        resource_match: Any = self.resource == resource or self.resource == '*'
        return scope_match and action_match and resource_match

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {'scope': self.scope.value, 'action': self.action.value, 'resource': self.resource, 'conditions': self.conditions}

@dataclass
class PermissionCheck:
    """Result of Permission check."""
    allowed: bool
    identity: AgentIdentity
    Permission: Permission | None = None
    reason: str = ''
    safety_decision: Any | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {'allowed': self.allowed, 'identity': self.identity.to_dict(), 'Permission': self.Permission.to_dict() if self.Permission else None, 'reason': self.reason, 'safety_decision': self.safety_decision.to_dict() if self.safety_decision else None}
