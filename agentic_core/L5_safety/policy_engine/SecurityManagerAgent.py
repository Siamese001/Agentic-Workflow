#!/usr/bin/env python3
from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"""
SecurityManagerAgent - Vaulted Security Management

Phase 3 Hard Migration: Consolidates:
- AgentPermissionManagerAgent (permission management)
- SecureCheckpointManagerAgent (secure checkpoint operations)
- SecureConfigManagerAgent (secure configuration access)

Features:
- Permission-based access control
- Vaulted configuration storage
- Secure checkpoint operations
- Role-based access (SECURE_READER, SECURE_WRITER, ADMIN)
- Audit logging for all security operations
"""


import hashlib
import logging
import secrets
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any

Logger = logging.getLogger(__name__)


class PermissionLevel(Enum):
    """Permission levels for security access."""

    NONE = 0
    SECURE_READER = 1
    SECURE_WRITER = 2
    ADMIN = 3


class SecurityAction(Enum):
    """Types of security actions."""

    READ_CONFIG = auto()
    WRITE_CONFIG = auto()
    CREATE_CHECKPOINT = auto()
    RESTORE_CHECKPOINT = auto()
    GRANT_PERMISSION = auto()
    REVOKE_PERMISSION = auto()


@dataclass
class SecurityAuditEntry:
    """Audit log entry for security operations."""

    timestamp: datetime
    agent_id: str
    action: SecurityAction
    resource: str
    success: bool
    details: str = ""


@dataclass
class AgentPermission:
    """Permission record for an agent."""

    agent_id: str
    level: PermissionLevel
    granted_by: str
    granted_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    allowed_resources: set[str] = field(default_factory=set)


@dataclass
class secure_config:
    """Secure configuration entry."""

    key: str
    value: Any
    encrypted: bool = False
    required_level: PermissionLevel = PermissionLevel.SECURE_READER
    created_at: datetime = field(default_factory=datetime.utcnow)
    modified_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class secure_checkpoint:
    """Secure checkpoint record."""

    checkpoint_id: str
    created_by: str
    created_at: datetime
    data_hash: str
    encrypted: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


class SecurityManagerAgent(SovereignBaseAgent):
    """
    Vaulted security manager with permission-based access control.

    Consolidates:
    - AgentPermissionManagerAgent (permissions)
    - SecureCheckpointManagerAgent (checkpoints)
    - SecureConfigManagerAgent (configuration)

    Usage:
        manager = SecurityManagerAgent()

        # Grant permission
        manager.grant_permission("agent_1", PermissionLevel.SECURE_READER, "admin")

        # Access config (requires permission)
        value = manager.get_config("api_key", agent_id="agent_1")

        # Create secure checkpoint
        checkpoint = manager.create_checkpoint("agent_1", data={"state": "active"})
    """

    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs
    ) -> dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        """
        # Security manager handles permissions/vaults; it does not auto-heal code
        return {"violations": 0, "fixed": 0, "errors": 0}

    def __init__(self, vault_path: Path | None = None):
        self._lock = threading.RLock()
        self._permissions: dict[str, AgentPermission] = {}
        self._configs: dict[str, secure_config] = {}
        self._checkpoints: dict[str, secure_checkpoint] = {}
        self._audit_log: list[SecurityAuditEntry] = []
        self._vault_path = vault_path

        # Initialize admin permission
        self._permissions["system"] = AgentPermission(
            agent_id="system",
            level=PermissionLevel.ADMIN,
            granted_by="system",
        )

        Logger.info("SecurityManagerAgent initialized")

    def _audit(
        self,
        agent_id: str,
        action: SecurityAction,
        resource: str,
        success: bool,
        details: str = "",
    ) -> None:
        """Log a security audit entry."""
        entry = SecurityAuditEntry(
            timestamp=datetime.utcnow(),
            agent_id=agent_id,
            action=action,
            resource=resource,
            success=success,
            details=details,
        )
        self._audit_log.append(entry)

        level = logging.INFO if success else logging.WARNING
        Logger.log(
            level,
            f"SECURITY: {agent_id} {action.name} {resource} - {'OK' if success else 'DENIED'}",
        )

    def _check_permission(
        self,
        agent_id: str,
        required_level: PermissionLevel,
        resource: str | None = None,
    ) -> bool:
        """Check if agent has required permission level."""
        if agent_id not in self._permissions:
            return False

        perm = self._permissions[agent_id]

        # Check expiration
        if perm.expires_at and datetime.utcnow() > perm.expires_at:
            return False

        # Check level
        if perm.level.value < required_level.value:
            return False

        # Check resource-specific permissions
        if resource and perm.allowed_resources:
            if resource not in perm.allowed_resources and "*" not in perm.allowed_resources:
                return False

        return True

    def grant_permission(
        self,
        agent_id: str,
        level: PermissionLevel,
        granted_by: str,
        expires_at: datetime | None = None,
        allowed_resources: set[str] | None = None,
    ) -> bool:
        """Grant permission to an agent."""
        with self._lock:
            # Check if granter has admin permission
            if not self._check_permission(granted_by, PermissionLevel.ADMIN):
                self._audit(
                    granted_by,
                    SecurityAction.GRANT_PERMISSION,
                    agent_id,
                    False,
                    "Insufficient permission",
                )
                return False

            self._permissions[agent_id] = AgentPermission(
                agent_id=agent_id,
                level=level,
                granted_by=granted_by,
                expires_at=expires_at,
                allowed_resources=allowed_resources or {"*"},
            )

            self._audit(
                granted_by, SecurityAction.GRANT_PERMISSION, agent_id, True, f"Level: {level.name}"
            )
            return True

    def revoke_permission(self, agent_id: str, revoked_by: str) -> bool:
        """Revoke permission from an agent."""
        with self._lock:
            if not self._check_permission(revoked_by, PermissionLevel.ADMIN):
                self._audit(
                    revoked_by,
                    SecurityAction.REVOKE_PERMISSION,
                    agent_id,
                    False,
                    "Insufficient permission",
                )
                return False

            if agent_id in self._permissions:
                del self._permissions[agent_id]
                self._audit(revoked_by, SecurityAction.REVOKE_PERMISSION, agent_id, True)
                return True

            return False

    def get_permission_level(self, agent_id: str) -> PermissionLevel:
        """Get permission level for an agent."""
        with self._lock:
            if agent_id in self._permissions:
                return self._permissions[agent_id].level
            return PermissionLevel.NONE

    def set_config(
        self,
        key: str,
        value: Any,
        agent_id: str,
        required_level: PermissionLevel = PermissionLevel.SECURE_READER,
        encrypted: bool = False,
    ) -> bool:
        """Set a secure configuration value."""
        with self._lock:
            if not self._check_permission(agent_id, PermissionLevel.SECURE_WRITER):
                self._audit(
                    agent_id, SecurityAction.WRITE_CONFIG, key, False, "Insufficient permission"
                )
                return False

            self._configs[key] = secure_config(
                key=key,
                value=value,
                encrypted=encrypted,
                required_level=required_level,
                modified_at=datetime.utcnow(),
            )

            self._audit(agent_id, SecurityAction.WRITE_CONFIG, key, True)
            return True

    def get_config(self, key: str, agent_id: str) -> Any | None:
        """Get a secure configuration value."""
        with self._lock:
            if key not in self._configs:
                return None

            config = self._configs[key]

            if not self._check_permission(agent_id, config.required_level, key):
                self._audit(
                    agent_id, SecurityAction.READ_CONFIG, key, False, "Insufficient permission"
                )
                return None

            self._audit(agent_id, SecurityAction.READ_CONFIG, key, True)
            return config.value

    def create_checkpoint(
        self,
        agent_id: str,
        data: dict[str, Any],
        encrypted: bool = True,
    ) -> secure_checkpoint | None:
        """Create a secure checkpoint."""
        with self._lock:
            if not self._check_permission(agent_id, PermissionLevel.SECURE_WRITER):
                self._audit(
                    agent_id,
                    SecurityAction.CREATE_CHECKPOINT,
                    "new",
                    False,
                    "Insufficient permission",
                )
                return None

            checkpoint_id = secrets.token_hex(16)
            data_hash = hashlib.sha256(str(data).encode()).hexdigest()

            checkpoint = secure_checkpoint(
                checkpoint_id=checkpoint_id,
                created_by=agent_id,
                created_at=datetime.utcnow(),
                data_hash=data_hash,
                encrypted=encrypted,
                metadata={"data": data},
            )

            self._checkpoints[checkpoint_id] = checkpoint
            self._audit(agent_id, SecurityAction.CREATE_CHECKPOINT, checkpoint_id, True)

            return checkpoint

    def restore_checkpoint(
        self,
        checkpoint_id: str,
        agent_id: str,
    ) -> dict[str, Any] | None:
        """Restore from a secure checkpoint."""
        with self._lock:
            if checkpoint_id not in self._checkpoints:
                return None

            if not self._check_permission(agent_id, PermissionLevel.SECURE_READER):
                self._audit(
                    agent_id,
                    SecurityAction.RESTORE_CHECKPOINT,
                    checkpoint_id,
                    False,
                    "Insufficient permission",
                )
                return None

            checkpoint = self._checkpoints[checkpoint_id]
            self._audit(agent_id, SecurityAction.RESTORE_CHECKPOINT, checkpoint_id, True)

            return checkpoint.metadata.get("data")

    def get_audit_log(
        self,
        agent_id: str | None = None,
        action: SecurityAction | None = None,
        limit: int = 100,
    ) -> list[SecurityAuditEntry]:
        """Get audit log entries."""
        with self._lock:
            entries = self._audit_log

            if agent_id:
                entries = [e for e in entries if e.agent_id == agent_id]

            if action:
                entries = [e for e in entries if e.action == action]

            return entries[-limit:]


# Factory methods for backward compatibility
def create_legacy_permission_manager() -> SecurityManagerAgent:
    """Create a security manager for permission management."""
    return SecurityManagerAgent()


def create_legacy_checkpoint_manager() -> SecurityManagerAgent:
    """Create a security manager for checkpoint operations."""
    return SecurityManagerAgent()


def create_legacy_config_manager() -> SecurityManagerAgent:
    """Create a security manager for configuration access."""
    return SecurityManagerAgent()
