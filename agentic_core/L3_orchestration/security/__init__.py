"""Security and Policy Enforcement.


LOGGER = logging.getLogger(__name__)
Phase 3 - Pillar 2: Agent Boundaries (Identity & Discovery)
Links SPIFFE identity with Control Plane for granular policy enforcement.
"""
import logging

    AgentPermissionManager,
    Permission,
    PermissionScope,
    PermissionCheck,
    create_permission_manager,
)

__all__ = [
    "AgentPermissionManager",
    "Permission",
    "PermissionScope",
    "PermissionCheck",
    "create_permission_manager",
]
