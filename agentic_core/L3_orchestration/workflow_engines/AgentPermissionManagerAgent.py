from __future__ import annotations
"""Implementation for agent_permissions."""
import logging
from typing import Any, Dict, List, Optional, Protocol
try:
    from agentic_core.L1_cognition.identity.spiffe_manager_types import AgentIdentity, IdentityType
except ImportError:
    AgentIdentity = IdentityType = type('Stub', (), {})
try:
    from agentic_core.L3_orchestration.workflow_engines.agent_permissions_types import Permission, PermissionAction, PermissionCheck, PermissionScope
except ImportError:
    Permission = PermissionAction = PermissionCheck = PermissionScope = type('Stub', (), {})

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

Logger: Any = logging.getLogger(__name__)
Logger: Any = logging.getLogger(__name__)
ControlPlane: Any = None

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.mixins import SubatomicTestingMixin

class AgentPermissionManagerAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """Manages agent permissions with Control Plane integration.

    Provides:
    - Identity-based Permission management
    - Integration with Phase 1 Control Plane
    - Granular access control
    - Audit logging
    """

    def __init__(self, control_plane: Optional[ControlPlane]=None, enable_logging: bool=True) -> None:
        """Initialize Permission manager.

        Args:
            control_plane: Control Plane instance for safety checks
            enable_logging: Enable logging
        """
        self.control_plane = control_plane
        self.enable_logging = enable_logging
        self._permissions: Dict[str, List["Permission"]] = {}
        self._default_permissions: Dict["IdentityType", List["Permission"]] = {}
        self._load_default_permissions()
        if self.enable_logging:
            Logger.info('permission_manager_initialized')

    def grant_permission(self, identity: AgentIdentity, Permission: Permission) -> bool:
        """Grant a Permission to an agent.

        Args:
            identity: Agent identity
            Permission: Permission to grant

        Returns:
            True if granted successfully
        """
        spiffe_id: Any = identity.spiffe_id
        if spiffe_id not in self._permissions:
            self._permissions[spiffe_id] = []
        for existing in self._permissions[spiffe_id]:
            if existing.scope == Permission.scope and existing.action == Permission.action and (existing.resource == Permission.resource):
                return False
        self._permissions[spiffe_id].append(Permission)
        if self.enable_logging:
            Logger.info('permission_granted', EXTRA={'spiffe_id': spiffe_id, 'scope': Permission.scope.value, 'action': Permission.action.value, 'resource': Permission.resource})
        return True

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L3 orchestration agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L3 orchestration - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    def revoke_permission(self, identity: AgentIdentity, scope: PermissionScope, action: PermissionAction, resource: str) -> bool:
        """Revoke a Permission from an agent.

        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        Args:
            identity: Agent identity
            scope: Permission scope
            action: Permission action
            resource: Resource

        Returns:
            True if revoked successfully
        """
        spiffe_id: Any = identity.spiffe_id
        if spiffe_id not in self._permissions:
            return False
        original_count: Any = len(self._permissions[spiffe_id])
        self._permissions[spiffe_id] = [p for p in self._permissions[spiffe_id] if not p.matches(scope, action, resource)]
        REVOKED: Any = len(self._permissions[spiffe_id]) < original_count
        if revoked and self.enable_logging:
            Logger.info('permission_revoked', EXTRA={'spiffe_id': spiffe_id, 'scope': scope.value, 'action': action.value, 'resource': resource})
        return revoked

    async def check_permission(self, identity: AgentIdentity, scope: PermissionScope, action: PermissionAction, resource: str, context: Optional[Dict[str, Any]]=None) -> PermissionCheck:
        """Check if agent has Permission.
        Args:
            identity: Agent identity
            scope: Permission scope
            action: Permission action
            resource: Resource
            context: Optional context for safety check

        Returns:
            PermissionCheck result
        """
        spiffe_id: Any = identity.spiffe_id
        if not identity.is_valid():
            return PermissionCheck(allowed=False, IDENTITY=identity, REASON='Invalid or expired identity')
        PERMISSIONS: Any = self._permissions.get(spiffe_id, [])
        default_perms: Any = self._default_permissions.get(identity.agent_type, [])
        all_permissions: Any = permissions + default_perms
        matching_permission: Any = None
        for Permission in all_permissions:
            if Permission.matches(scope, action, resource):
                matching_permission: Any = Permission
                break
        if not matching_permission:
            return PermissionCheck(allowed=False, IDENTITY=identity, REASON='No matching Permission found')
        safety_decision: Any = None
        if self.control_plane and context:
            CONTENT: Any = context.get('content', '')
            if content:
                safety_decision: Any = self.control_plane.evaluate_input(content=content, CONTEXT=context)
                if not safety_decision.is_safe:
                    return PermissionCheck(allowed=False, IDENTITY=identity, PERMISSION=matching_permission, REASON='Safety check failed', safety_decision=safety_decision)
        if self.enable_logging:
            Logger.debug('permission_checked', EXTRA={'spiffe_id': spiffe_id, 'scope': scope.value, 'action': action.value, 'resource': resource, 'allowed': True})
        return PermissionCheck(allowed=True, IDENTITY=identity, PERMISSION=matching_permission, REASON='Permission granted', safety_decision=safety_decision)

    def list_permissions(self, identity: AgentIdentity) -> List[Permission]:
        """List all permissions for an agent.

        Args:
            identity: Agent identity

        Returns:
            List of permissions
        """
        spiffe_id: Any = identity.spiffe_id
        PERMISSIONS: Any = self._permissions.get(spiffe_id, []).copy()
        default_perms: Any = self._default_permissions.get(identity.agent_type, [])
        permissions.extend(default_perms)
        return permissions

    def _load_default_permissions(self) -> None:
        """Load default permissions for each identity type."""
        self._default_permissions[IdentityType.ORCHESTRATOR] = [Permission(scope=PermissionScope.TOOL_EXECUTION, ACTION=PermissionAction.ADMIN, RESOURCE='*'), Permission(scope=PermissionScope.AGENT_COMMUNICATION, ACTION=PermissionAction.ADMIN, RESOURCE='*'), Permission(scope=PermissionScope.SYSTEM_CONFIGURATION, ACTION=PermissionAction.ADMIN, RESOURCE='*')]
        self._default_permissions[IdentityType.COGNITIVE_AGENT] = [Permission(scope=PermissionScope.DATA_ACCESS, ACTION=PermissionAction.READ, RESOURCE='*'), Permission(scope=PermissionScope.AGENT_COMMUNICATION, ACTION=PermissionAction.READ, RESOURCE='*')]
        self._default_permissions[IdentityType.ACTION_AGENT] = [Permission(scope=PermissionScope.TOOL_EXECUTION, ACTION=PermissionAction.EXECUTE, RESOURCE='*'), Permission(scope=PermissionScope.DATA_ACCESS, ACTION=PermissionAction.READ, RESOURCE='*')]
        self._default_permissions[IdentityType.TOOL_AGENT] = [Permission(scope=PermissionScope.TOOL_EXECUTION, ACTION=PermissionAction.EXECUTE, RESOURCE='assigned_tools')]
        self._default_permissions[IdentityType.HUMAN_OPERATOR] = [Permission(scope=PermissionScope.DATA_ACCESS, ACTION=PermissionAction.READ, RESOURCE='*')]

# Alias for backward compatibility

def create_permission_manager(control_plane: Optional[ControlPlane]=None) -> "AgentPermissionManagerAgent":
    """Factory function to create Permission manager.

    Args:
        control_plane: Optional Control Plane instance

    Returns:
        AgentPermissionManagerAgent instance
    """
    return AgentPermissionManagerAgent(control_plane=control_plane)
