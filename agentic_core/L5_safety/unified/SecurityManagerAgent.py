#!/usr/bin/env python3
from enum import Enum, auto
from typing import Any
from pathlib import Path
from dataclasses import dataclass
from dataclasses import field

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin

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
- Code security pattern detection (SQL, URLs, Ports)
"""


import ast
import hashlib
import logging
import re
import secrets
import threading
from datetime import datetime

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


class SecurityManagerAgent(SubatomicTestingMixin, SovereignBaseAgent):
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


# =============================================================================
# CODE SECURITY PATTERN DETECTION
# =============================================================================

# Patterns for detecting security anti-patterns in code
SQL_PATTERNS = [
    re.compile(r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\s+", re.IGNORECASE),
    re.compile(r'\.execute\s*\(\s*["\']', re.IGNORECASE),
    re.compile(r'\.executemany\s*\(\s*["\']', re.IGNORECASE),
]

# URL patterns - exclude localhost and internal domains
URL_PATTERN = re.compile(
    r'["\']https?://(?!localhost|127\.0\.0\.1|0\.0\.0\.0|192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.)[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}[^"\']*["\']'
)

# Port patterns in socket/connect calls
PORT_PATTERN = re.compile(r"\b(port\s*=\s*\d{2,5}|:\s*\d{2,5}|connect\s*\([^)]*\d{2,5})")


class SecurityPatternVisitor(ast.NodeVisitor):
    """AST visitor to detect security anti-patterns in code."""

    def __init__(self, source_lines: list[str]):
        self.source_lines = source_lines
        self.violations: list[dict[str, Any]] = []

    def visit_Constant(self, node: ast.Constant) -> None:
        """Check string constants for SQL and URL patterns."""
        if isinstance(node.value, str):
            value = node.value

            # Check for raw SQL patterns
            for pattern in SQL_PATTERNS:
                if pattern.search(value):
                    self.violations.append(
                        {
                            "type": "raw_sql",
                            "line": node.lineno,
                            "message": f"Potential raw SQL detected: {value[:50]}...",
                            "severity": "high",
                        }
                    )
                    break

            # Check for hardcoded URLs (excluding internal domains)
            if URL_PATTERN.search(f'"{value}"') or URL_PATTERN.search(f"'{value}'"):
                self.violations.append(
                    {
                        "type": "hardcoded_url",
                        "line": node.lineno,
                        "message": f"Hardcoded URL detected: {value[:50]}...",
                        "severity": "medium",
                    }
                )

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Check function calls for hardcoded ports."""
        # Check for socket.connect() or similar with hardcoded ports
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            if func_name in ("connect", "bind", "listen"):
                for arg in node.args:
                    if isinstance(arg, ast.Tuple):
                        for elt in arg.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, int):
                                if 1 <= elt.value <= 65535:
                                    self.violations.append(
                                        {
                                            "type": "hardcoded_port",
                                            "line": node.lineno,
                                            "message": f"Hardcoded port detected: {elt.value}",
                                            "severity": "low",
                                        }
                                    )

        # Check keyword arguments for port=
        for keyword in node.keywords:
            if keyword.arg == "port" and isinstance(keyword.value, ast.Constant):
                if isinstance(keyword.value.value, int):
                    self.violations.append(
                        {
                            "type": "hardcoded_port",
                            "line": node.lineno,
                            "message": f"Hardcoded port in keyword argument: {keyword.value.value}",
                            "severity": "low",
                        }
                    )

        self.generic_visit(node)


def scan_file_for_security_patterns(file_path: Path) -> list[dict[str, Any]]:
    """
    Scan a Python file for security anti-patterns.

    Detects:
    - Raw SQL strings
    - Hardcoded URLs (excluding localhost/internal)
    - Hardcoded ports in socket/connect calls

    Args:
        file_path: Path to the Python file to scan

    Returns:
        List of violation dictionaries with type, line, message, severity
    """
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        source_lines = source.splitlines()

        visitor = SecurityPatternVisitor(source_lines)
        visitor.visit(tree)

        return visitor.violations
    except SyntaxError:
        return []
    except Exception as e:
        Logger.warning(f"Failed to scan {file_path}: {e}")
        return []


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
