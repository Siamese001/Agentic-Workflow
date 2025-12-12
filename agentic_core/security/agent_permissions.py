"""Agent Permission Management with Control Plane Integration.

Phase 3 - Pillar 2: Agent Boundaries (Identity & Discovery)
Integrates SPIFFE identity with Phase 1 Control Plane for policy enforcement.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from agentic_core.identity.spiffe_manager import AgentIdentity, IdentityType
from shared.safety import ControlPlane, SafetyPolicy, PolicyDecision

logger = logging.getLogger(__name__)


class PermissionScope(Enum):
    """Permission scopes."""
    TOOL_EXECUTION = "tool_execution"
    DATA_ACCESS = "data_access"
    AGENT_COMMUNICATION = "agent_communication"
    SYSTEM_CONFIGURATION = "system_configuration"
    CODE_EXECUTION = "code_execution"


class PermissionAction(Enum):
    """Permission actions."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    ADMIN = "admin"


@dataclass
class Permission:
    """Individual permission."""
    scope: PermissionScope
    action: PermissionAction
    resource: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    def matches(
        self,
        scope: PermissionScope,
        action: PermissionAction,
        resource: str,
    ) -> bool:
        """Check if permission matches request.
        
        Args:
            scope: Requested scope
            action: Requested action
            resource: Requested resource
            
        Returns:
            True if matches
        """
        # Exact match or wildcard
        scope_match = self.scope == scope
        action_match = self.action == action or self.action == PermissionAction.ADMIN
        resource_match = self.resource == resource or self.resource == "*"
        
        return scope_match and action_match and resource_match
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scope": self.scope.value,
            "action": self.action.value,
            "resource": self.resource,
            "conditions": self.conditions,
        }


@dataclass
class PermissionCheck:
    """Result of permission check."""
    allowed: bool
    identity: AgentIdentity
    permission: Optional[Permission] = None
    reason: str = ""
    safety_decision: Optional[PolicyDecision] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "allowed": self.allowed,
            "identity": self.identity.to_dict(),
            "permission": self.permission.to_dict() if self.permission else None,
            "reason": self.reason,
            "safety_decision": self.safety_decision.to_dict() if self.safety_decision else None,
        }


class AgentPermissionManager:
    """Manages agent permissions with Control Plane integration.
    
    Provides:
    - Identity-based permission management
    - Integration with Phase 1 Control Plane
    - Granular access control
    - Audit logging
    """
    
    def __init__(
        self,
        control_plane: Optional[ControlPlane] = None,
        enable_logging: bool = True,
    ):
        """Initialize permission manager.
        
        Args:
            control_plane: Control Plane instance for safety checks
            enable_logging: Enable logging
        """
        self.control_plane = control_plane
        self.enable_logging = enable_logging
        
        self._permissions: Dict[str, List[Permission]] = {}
        self._default_permissions: Dict[IdentityType, List[Permission]] = {}
        
        self._load_default_permissions()
        
        if self.enable_logging:
            logger.info("permission_manager_initialized")
    
    def grant_permission(
        self,
        identity: AgentIdentity,
        permission: Permission,
    ) -> bool:
        """Grant a permission to an agent.
        
        Args:
            identity: Agent identity
            permission: Permission to grant
            
        Returns:
            True if granted successfully
        """
        spiffe_id = identity.spiffe_id
        
        if spiffe_id not in self._permissions:
            self._permissions[spiffe_id] = []
        
        # Check if already granted
        for existing in self._permissions[spiffe_id]:
            if (existing.scope == permission.scope and
                existing.action == permission.action and
                existing.resource == permission.resource):
                return False
        
        self._permissions[spiffe_id].append(permission)
        
        if self.enable_logging:
            logger.info(
                "permission_granted",
                extra={
                    "spiffe_id": spiffe_id,
                    "scope": permission.scope.value,
                    "action": permission.action.value,
                    "resource": permission.resource,
                }
            )
        
        return True
    
    def revoke_permission(
        self,
        identity: AgentIdentity,
        scope: PermissionScope,
        action: PermissionAction,
        resource: str,
    ) -> bool:
        """Revoke a permission from an agent.
        
        Args:
            identity: Agent identity
            scope: Permission scope
            action: Permission action
            resource: Resource
            
        Returns:
            True if revoked successfully
        """
        spiffe_id = identity.spiffe_id
        
        if spiffe_id not in self._permissions:
            return False
        
        original_count = len(self._permissions[spiffe_id])
        
        self._permissions[spiffe_id] = [
            p for p in self._permissions[spiffe_id]
            if not p.matches(scope, action, resource)
        ]
        
        revoked = len(self._permissions[spiffe_id]) < original_count
        
        if revoked and self.enable_logging:
            logger.info(
                "permission_revoked",
                extra={
                    "spiffe_id": spiffe_id,
                    "scope": scope.value,
                    "action": action.value,
                    "resource": resource,
                }
            )
        
        return revoked
    
    async def check_permission(
        self,
        identity: AgentIdentity,
        scope: PermissionScope,
        action: PermissionAction,
        resource: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> PermissionCheck:
        """Check if agent has permission.
        
        Args:
            identity: Agent identity
            scope: Permission scope
            action: Permission action
            resource: Resource
            context: Optional context for safety check
            
        Returns:
            PermissionCheck result
        """
        spiffe_id = identity.spiffe_id
        
        # Check if identity is valid
        if not identity.is_valid():
            return PermissionCheck(
                allowed=False,
                identity=identity,
                reason="Invalid or expired identity",
            )
        
        # Get permissions (agent-specific + defaults)
        permissions = self._permissions.get(spiffe_id, [])
        default_perms = self._default_permissions.get(identity.agent_type, [])
        all_permissions = permissions + default_perms
        
        # Find matching permission
        matching_permission = None
        for permission in all_permissions:
            if permission.matches(scope, action, resource):
                matching_permission = permission
                break
        
        if not matching_permission:
            return PermissionCheck(
                allowed=False,
                identity=identity,
                reason="No matching permission found",
            )
        
        # Run safety check if Control Plane available
        safety_decision = None
        if self.control_plane and context:
            content = context.get("content", "")
            if content:
                safety_decision = self.control_plane.evaluate_input(
                    content=content,
                    context=context,
                )
                
                if not safety_decision.is_safe:
                    return PermissionCheck(
                        allowed=False,
                        identity=identity,
                        permission=matching_permission,
                        reason="Safety check failed",
                        safety_decision=safety_decision,
                    )
        
        if self.enable_logging:
            logger.debug(
                "permission_checked",
                extra={
                    "spiffe_id": spiffe_id,
                    "scope": scope.value,
                    "action": action.value,
                    "resource": resource,
                    "allowed": True,
                }
            )
        
        return PermissionCheck(
            allowed=True,
            identity=identity,
            permission=matching_permission,
            reason="Permission granted",
            safety_decision=safety_decision,
        )
    
    def list_permissions(
        self,
        identity: AgentIdentity,
    ) -> List[Permission]:
        """List all permissions for an agent.
        
        Args:
            identity: Agent identity
            
        Returns:
            List of permissions
        """
        spiffe_id = identity.spiffe_id
        permissions = self._permissions.get(spiffe_id, []).copy()
        default_perms = self._default_permissions.get(identity.agent_type, [])
        permissions.extend(default_perms)
        return permissions
    
    def _load_default_permissions(self) -> None:
        """Load default permissions for each identity type."""
        # Orchestrator - full permissions
        self._default_permissions[IdentityType.ORCHESTRATOR] = [
            Permission(
                scope=PermissionScope.TOOL_EXECUTION,
                action=PermissionAction.ADMIN,
                resource="*",
            ),
            Permission(
                scope=PermissionScope.AGENT_COMMUNICATION,
                action=PermissionAction.ADMIN,
                resource="*",
            ),
            Permission(
                scope=PermissionScope.SYSTEM_CONFIGURATION,
                action=PermissionAction.ADMIN,
                resource="*",
            ),
        ]
        
        # Cognitive Agent - planning and reasoning
        self._default_permissions[IdentityType.COGNITIVE_AGENT] = [
            Permission(
                scope=PermissionScope.DATA_ACCESS,
                action=PermissionAction.READ,
                resource="*",
            ),
            Permission(
                scope=PermissionScope.AGENT_COMMUNICATION,
                action=PermissionAction.READ,
                resource="*",
            ),
        ]
        
        # Action Agent - tool execution
        self._default_permissions[IdentityType.ACTION_AGENT] = [
            Permission(
                scope=PermissionScope.TOOL_EXECUTION,
                action=PermissionAction.EXECUTE,
                resource="*",
            ),
            Permission(
                scope=PermissionScope.DATA_ACCESS,
                action=PermissionAction.READ,
                resource="*",
            ),
        ]
        
        # Tool Agent - specific tool access
        self._default_permissions[IdentityType.TOOL_AGENT] = [
            Permission(
                scope=PermissionScope.TOOL_EXECUTION,
                action=PermissionAction.EXECUTE,
                resource="assigned_tools",
            ),
        ]
        
        # Human Operator - read-only by default
        self._default_permissions[IdentityType.HUMAN_OPERATOR] = [
            Permission(
                scope=PermissionScope.DATA_ACCESS,
                action=PermissionAction.READ,
                resource="*",
            ),
        ]


def create_permission_manager(
    control_plane: Optional[ControlPlane] = None,
) -> AgentPermissionManager:
    """Factory function to create permission manager.
    
    Args:
        control_plane: Optional Control Plane instance
        
    Returns:
        AgentPermissionManager instance
    """
    return AgentPermissionManager(control_plane=control_plane)
