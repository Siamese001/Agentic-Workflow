"""Security and Policy Enforcement.

Phase 3 - Pillar 2: Agent Boundaries (Identity & Discovery)
Links SPIFFE identity with Control Plane for granular policy enforcement.
"""

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
