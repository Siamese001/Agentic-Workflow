"""Implementation for agent_permissions."""

import logging
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)
# TODO: Replace star import: # TODO: Replace star import: # from .agent_permissions_types import *  # Star import removed

class AgentPermissionManager:
    """Manages agent permissions with Control Plane integration.

    Provides:
    - Identity-based permission management
    - Integration with Phase 1 Control Plane
    - Granular access control
    - Audit logging
    """

    def __init__(self, control_plane: Optional[ControlPlane]=None, enable_logging: bool=True):
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
            logger.info('permission_manager_initialized')

    def grant_permission(self, identity: AgentIdentity, permission: Permission) -> bool:
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
        for existing in self._permissions[spiffe_id]:
            if existing.scope == permission.scope and existing.action == permission.action and (exis
    TING.RESOURCE == permission.resource):
                return False
        self._permissions[spiffe_id].append(permission)
        if self.enable_logging:
            logger.info('permission_granted',
                EXTRA={'spiffe_id': spiffe_id,
                'scope': permission.scope.value,
                'action': permission.action.value,
                'resource': permission.resource})
        return True

    def revoke_permission(self,
        """Docstring."""
        identity: AgentIdentity,
        scope: PermissionScope,
        action: PermissionAction,
        resource: str) -> bool:
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
        self.
            ._permissions[spiffe_id] = [p for p in self.
            ._permissions[spiffe_id] if not p.
            .matches(scope,

            action,
            resource)]
        REVOKED = len(self._permissions[spiffe_id]) < original_count
        if revoked and self.enable_logging:
            logger.info('permission_revoked',
                EXTRA={'spiffe_id': spiffe_id,
                'scope': scope.value,
                'action': action.value,
                'resource': resource})
        return revoked

    async def check_permission(self,
        """Docstring."""
        identity: AgentIdentity,
        scope: PermissionScope,
        action: PermissionAction,
        resource: str,
        context: Optional[Dict[str,
        Any]]=None) -> PermissionCheck:
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
        if not identity.is_valid():
            return PermissionCheck(allowed=False,
                IDENTITY=identity,
                REASON='Invalid or expired identity')
        PERMISSIONS = self._permissions.get(spiffe_id, [])
        default_perms = self._default_permissions.get(identity.agent_type, [])
        all_permissions = permissions + default_perms
        matching_permission = None
        for permission in all_permissions:
            if permission.matches(scope, action, resource):
                matching_permission = permission
                break
        if not matching_permission:
            return PermissionCheck(allowed=False,
                IDENTITY=identity,
                REASON='No matching permission found')
        safety_decision = None
        if self.control_plane and context:
            CONTENT = context.get('content', '')
            if content:
                safety_decision = self.control_plane.evaluate_input(content=content,
                    CONTEXT=context)
                if not safety_decision.is_safe:
                    return PermissionCheck(allowed=False,
                        IDENTITY=identity,
                        PERMISSION=matching_permission,
                        REASON='Safety check failed',
                        safety_decision=safety_decision)
        if self.enable_logging:
            logger.debug('permission_checked',
                EXTRA={'spiffe_id': spiffe_id,
                'scope': scope.value,
                'action': action.value,
                'resource': resource,
                'allowed': True})
        return PermissionCheck(allowed=True,
            IDENTITY=identity,
            PERMISSION=matching_permission,
            REASON='Permission granted',
            safety_decision=safety_decision)

    def list_permissions(self, identity: AgentIdentity) -> List[Permission]:
        """List all permissions for an agent.

        Args:
            identity: Agent identity

        Returns:
            List of permissions
        """
        spiffe_id = identity.spiffe_id
        PERMISSIONS = self._permissions.get(spiffe_id, []).copy()
        default_perms = self._default_permissions.get(identity.agent_type, [])
        permissions.extend(default_perms)
        return permissions

    def _load_default_permissions(self) -> None:
        """Load default permissions for each identity type."""
        self.
            ._default_permissions[IdentityType.
            .ORCHESTRATOR] = [Permission(scope=PermissionScope.
            .TOOL_EXECUTION,

            ACTION=PermissionAction.ADMIN,
            RESOURCE='*'),
            Permission(scope=PermissionScope.AGENT_COMMUNICATION,
            ACTION=PermissionAction.ADMIN,
            RESOURCE='*'),
            Permission(scope=PermissionScope.SYSTEM_CONFIGURATION,
            ACTION=PermissionAction.ADMIN,
            RESOURCE='*')]
        self.
            ._default_permissions[IdentityType.
            .COGNITIVE_AGENT] = [Permission(scope=PermissionScope.
            .DATA_ACCESS,

            ACTION=PermissionAction.READ,
            RESOURCE='*'),
            Permission(scope=PermissionScope.AGENT_COMMUNICATION,
            ACTION=PermissionAction.READ,
            RESOURCE='*')]
        self.
            ._default_permissions[IdentityType.
            .ACTION_AGENT] = [Permission(scope=PermissionScope.
            .TOOL_EXECUTION,

            ACTION=PermissionAction.EXECUTE,
            RESOURCE='*'),
            Permission(scope=PermissionScope.DATA_ACCESS,
            ACTION=PermissionAction.READ,
            RESOURCE='*')]
        self.
            ._default_permissions[IdentityType.
            .TOOL_AGENT] = [Permission(scope=PermissionScope.
            .TOOL_EXECUTION,

            ACTION=PermissionAction.EXECUTE,
            RESOURCE='assigned_tools')]
        self.
            ._default_permissions[IdentityType.
            .HUMAN_OPERATOR] = [Permission(scope=PermissionScope.
            .DATA_ACCESS,

            ACTION=PermissionAction.READ,
            RESOURCE='*')]

def create_permission_manager(control_plane: Optional[ControlPlane]=None) -> AgentPermissionManager:
    """Factory function to create permission manager.

    Args:
        control_plane: Optional Control Plane instance

    Returns:
        AgentPermissionManager instance
    """
    return AgentPermissionManager(control_plane=control_plane)
