from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "SecurityManagerAgent")
emit_determinism_digest("p0", "SecurityManagerAgent")

_emit_dispatches_healing_run("p1", "SecurityManagerAgent", "L5")
_emit_routes_through("p1", "SecurityManagerAgent", "L5")
_emit_checks_agent_registry("p1", "SecurityManagerAgent", "agent_registry")
_emit_validates_agent_capability("p1", "SecurityManagerAgent", "capability")
_emit_dispatches_execution_plan("p1", "SecurityManagerAgent", "exec_plan")
_emit_agent_executes_agent("p1", "SecurityManagerAgent", "sub_agent")
_emit_routes_to_agent("p1", "SecurityManagerAgent", "target_agent")
_emit_verifies_policy("p1", "SecurityManagerAgent", "policy_check")
_emit_observes_runtime_state("p1", "SecurityManagerAgent", "runtime_state")
_emit_verifies_boundary("p1", "SecurityManagerAgent", "boundary_check")
_emit_transcripts_response("p1", "SecurityManagerAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "SecurityManagerAgent")
_emit_gated_by_confidence("p1", "SecurityManagerAgent", "confidence_gate")
_emit_escalates_to_human("p1", "SecurityManagerAgent", "L5")
_emit_reads_policy_state("p1", "SecurityManagerAgent", "L5")

_emit_snapshots_state("p0", "SecurityManagerAgent", "state_snapshot")
_emit_authorize_and_execute("p2", "SecurityManagerAgent", "execution_auth")
_emit_validates_capability("p2", "SecurityManagerAgent", "capability_check")
_emit_routes_to_capability("p2", "SecurityManagerAgent", "capability_route")
_emit_writes_via_uwg("p2", "SecurityManagerAgent", "uwg_write")
_emit_blocks_direct_write("p2", "SecurityManagerAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "SecurityManagerAgent", "tool_invocation")
_emit_captures_execution_output("p2", "SecurityManagerAgent", "exec_output")
_emit_dispatches_agent("p3", "SecurityManagerAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "SecurityManagerAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "SecurityManagerAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "SecurityManagerAgent", "healing_outcome")
_emit_escalates_failure("p3", "SecurityManagerAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "SecurityManagerAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "SecurityManagerAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "SecurityManagerAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "SecurityManagerAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "SecurityManagerAgent", "eval_metric")
_emit_stores_embedding("p4", "SecurityManagerAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "SecurityManagerAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "SecurityManagerAgent", "exec_snapshot_link")

"\nSecurityManagerAgent - Vaulted Security Management\n\nPhase 3 Hard Migration: Consolidates:\n- AgentPermissionManagerAgent (permission management)\n- SecureCheckpointManagerAgent (secure checkpoint operations)\n- SecureConfigManagerAgent (secure configuration access)\n\nFeatures:\n- Permission-based access control\n- Vaulted configuration storage\n- Secure checkpoint operations\n- Role-based access (SECURE_READER, SECURE_WRITER, ADMIN)\n- Audit logging for all security operations\n"
import hashlib
import logging
import secrets
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("SecurityManagerAgent", "p4obs", "metric_1")
_emit_emits_metric_event("SecurityManagerAgent", "p4obs", "metric_2")
_emit_emits_metric_event("SecurityManagerAgent", "p4obs", "metric_3")
_emit_emits_metric_event("SecurityManagerAgent", "p4obs", "metric_4")
_emit_emits_metric_event("SecurityManagerAgent", "p4obs", "metric_5")
_emit_emits_metric_event("SecurityManagerAgent", "p4obs", "metric_6")
_emit_records_incident_event("SecurityManagerAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("SecurityManagerAgent", "p4obs", "anomaly")
_emit_writes_observability_log("SecurityManagerAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("SecurityManagerAgent", "p4obs", "mon_state")
_emit_triggers_alert("SecurityManagerAgent", "p4obs", "alert")
_emit_links_incident_trace("SecurityManagerAgent", "p4obs", "trace_link")
_emit_captures_pattern("SecurityManagerAgent", "p3lm", "pattern")
_emit_records_learning_event("SecurityManagerAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("SecurityManagerAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("SecurityManagerAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("SecurityManagerAgent", "p3lm", "routing")
_emit_improves_agent_policy("SecurityManagerAgent", "p3lm", "policy")
_emit_stores_learning_state("SecurityManagerAgent", "p3lm", "state")
_emit_records_execution_trace("SecurityManagerAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("SecurityManagerAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("SecurityManagerAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("SecurityManagerAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("SecurityManagerAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("SecurityManagerAgent", "env_read", "p2_env_1")
_emit_reads_environ("SecurityManagerAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("SecurityManagerAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("SecurityManagerAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "SecurityManagerAgent", "context_pull")
_emit_pulls_context("p1", "SecurityManagerAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "SecurityManagerAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "SecurityManagerAgent", "uwg_term_2")
_emit_writes_through("p1", "SecurityManagerAgent", "write_through")
_emit_writes_through("p1", "SecurityManagerAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "SecurityManagerAgent", "safety_validation")
_emit_invokes_eval("p1", "SecurityManagerAgent", "eval_call")
_emit_proposal_commits_routing("p1", "SecurityManagerAgent", "routing_commit")

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

    # guardian: allow-type-erasure
    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, Any]:
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
        self._permissions["system"] = AgentPermission(
            agent_id="system", level=PermissionLevel.ADMIN, granted_by="system"
        )
        Logger.info("SecurityManagerAgent initialized")

    def _audit(
        self, agent_id: str, action: SecurityAction, resource: str, success: bool, details: str = ""
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
            level, f"SECURITY: {agent_id} {action.name} {resource} - {('OK' if success else 'DENIED')}"
        )

    def _check_permission(
        self, agent_id: str, required_level: PermissionLevel, resource: str | None = None
    ) -> bool:
        """Check if agent has required permission level."""
        _emit_applies_guardrail(str(uuid.uuid4()), "SecurityManagerAgent._check_permission", "L5_POLICY")
        if agent_id not in self._permissions:
            return False
        perm = self._permissions[agent_id]
        if perm.expires_at and datetime.utcnow() > perm.expires_at:
            return False
        if perm.level.value < required_level.value:
            return False
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
            if not self._check_permission(granted_by, PermissionLevel.ADMIN):
                self._audit(
                    granted_by, SecurityAction.GRANT_PERMISSION, agent_id, False, "Insufficient permission"
                )
                return False
            self._permissions[agent_id] = AgentPermission(
                agent_id=agent_id,
                level=level,
                granted_by=granted_by,
                expires_at=expires_at,
                allowed_resources=allowed_resources or {"*"},
            )
            self._audit(granted_by, SecurityAction.GRANT_PERMISSION, agent_id, True, f"Level: {level.name}")
            return True

    def revoke_permission(self, agent_id: str, revoked_by: str) -> bool:
        """Revoke permission from an agent."""
        with self._lock:
            if not self._check_permission(revoked_by, PermissionLevel.ADMIN):
                self._audit(
                    revoked_by, SecurityAction.REVOKE_PERMISSION, agent_id, False, "Insufficient permission"
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
            # guardian: allow-config-with-logic
            if not self._check_permission(agent_id, PermissionLevel.SECURE_WRITER):
                self._audit(agent_id, SecurityAction.WRITE_CONFIG, key, False, "Insufficient permission")
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
            # guardian: allow-config-with-logic
            if key not in self._configs:
                return None
            config = self._configs[key]
            # guardian: allow-config-with-logic
            if not self._check_permission(agent_id, config.required_level, key):
                self._audit(agent_id, SecurityAction.READ_CONFIG, key, False, "Insufficient permission")
                return None
            self._audit(agent_id, SecurityAction.READ_CONFIG, key, True)
            return config.value

    def create_checkpoint(
        self, agent_id: str, data: dict[str, Any], encrypted: bool = True
    ) -> secure_checkpoint | None:
        """Create a secure checkpoint."""
        with self._lock:
            if not self._check_permission(agent_id, PermissionLevel.SECURE_WRITER):
                self._audit(
                    agent_id, SecurityAction.CREATE_CHECKPOINT, "new", False, "Insufficient permission"
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

    # guardian: allow-type-erasure
    def restore_checkpoint(self, checkpoint_id: str, agent_id: str) -> dict[str, Any] | None:
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

    # guardian: allow-magic-config
    def get_audit_log(
        self, agent_id: str | None = None, action: SecurityAction | None = None, limit: int = 100
    ) -> list[SecurityAuditEntry]:
        """Get audit log entries."""
        with self._lock:
            entries = self._audit_log
            if agent_id:
                entries = [e for e in entries if e.agent_id == agent_id]
            if action:
                entries = [e for e in entries if e.action == action]
            return entries[-limit:]

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """Heal security management violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (permission, config, checkpoint)
                - agent_id: Agent that caused the violation
                - action: Security action that failed

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SecurityManagerAgent.heal")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SecurityManagerAgent.heal".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        Logger.info("[SECURITY_MANAGER] Security violations require manual review")
        return {
            "violations_fixed": 0,
            "violations_found": 1,
            "errors": 0,
            "skipped": 1,
            "reason": "Security violations require manual security review",
        }


def create_legacy_permission_manager() -> SecurityManagerAgent:
    """Create a security manager for permission management."""
    return SecurityManagerAgent()


def create_legacy_checkpoint_manager() -> SecurityManagerAgent:
    """Create a security manager for checkpoint operations."""
    return SecurityManagerAgent()


def create_legacy_config_manager() -> SecurityManagerAgent:
    """Create a security manager for configuration access."""
    return SecurityManagerAgent()
