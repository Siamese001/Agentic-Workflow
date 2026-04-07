"""
HITLMixin - Phase 3 Critical Infrastructure: Human-in-the-Loop Integration

Provides defined interrupt points for high-stakes operations, approval workflows,
and human escalation paths.

Features:
- Configurable approval requirements for sensitive operations
- Human escalation paths for critical decisions
- Approval workflow management
- Audit trail for human interventions
- Timeout handling for pending approvals

SSOT PRINCIPLE:
    All agents requiring human oversight should inherit from this mixin.
    This ensures consistent HITL patterns across the agent ecosystem.
"""
from __future__ import annotations

# Configuration constants
DEFAULT_HITL_TIMEOUT = 300.0
MAX_PENDING_APPROVALS = 100
DEFAULT_HISTORY_LIMIT = 100

import logging
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

Logger = logging.getLogger(__name__)

class ApprovalStatus(Enum):
    """Status of an approval request."""
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    TIMEOUT = 'timeout'
    ESCALATED = 'escalated'

class RiskLevel(Enum):
    """Risk levels for operations."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ApprovalRequest:
    """Represents a request for human approval."""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    operation_name: str = ''
    description: str = ''
    risk_level: RiskLevel = RiskLevel.MEDIUM
    context: dict[str, Any] = field(default_factory=dict)
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: float = field(default_factory=time.time)
    resolved_at: float | None = None
    resolved_by: str | None = None
    resolution_notes: str | None = None
    timeout_seconds: float = DEFAULT_HITL_TIMEOUT
    escalation_chain: list[str] = field(default_factory=list)
    current_escalation_level: int = 0

    def is_expired(self) -> bool:
        """Check if request has timed out."""
        return time.time() - self.created_at > self.timeout_seconds

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {'request_id': self.request_id, 'operation_name': self.operation_name, 'description': self.description, 'risk_level': self.risk_level.name, 'context': self.context, 'status': self.status.value, 'created_at': self.created_at, 'resolved_at': self.resolved_at, 'resolved_by': self.resolved_by, 'resolution_notes': self.resolution_notes, 'timeout_seconds': self.timeout_seconds, 'is_expired': self.is_expired()}

@dataclass
class HITLConfig:
    """Configuration for HITL behavior."""
    enabled: bool = True
    default_timeout_seconds: float = DEFAULT_HITL_TIMEOUT
    auto_approve_low_risk: bool = True
    require_notes_on_rejection: bool = True
    escalation_timeout_seconds: float = 600.0
    max_escalation_levels: int = 3
    default_escalation_chain: list[str] = field(default_factory=lambda: ['team_lead', 'manager', 'director'])
    max_pending_approvals: int = MAX_PENDING_APPROVALS
    max_history_size: int = 10000

class ApprovalRequiredError(Exception):
    """Raised when an operation requires approval."""

    def __init__(self, request: ApprovalRequest):
        self.request = request
        super().__init__(f"Approval required for '{request.operation_name}' (Risk: {request.risk_level.name}, ID: {request.request_id})")

class ApprovalRejectedError(Exception):
    """Raised when an operation is rejected."""

    def __init__(self, request: ApprovalRequest):
        self.request = request
        super().__init__(f"Operation '{request.operation_name}' rejected by {request.resolved_by}: {request.resolution_notes}")

class ApprovalTimeoutError(Exception):
    """Raised when approval times out."""

    def __init__(self, request: ApprovalRequest):
        self.request = request
        super().__init__(f"Approval timeout for '{request.operation_name}' after {request.timeout_seconds}s")

class HITLMixin:
    """
    Mixin providing Human-in-the-Loop capabilities for agents.

    Phase 3 Critical Infrastructure:
    - Approval workflows for high-stakes operations
    - Human escalation paths
    - Audit trail for interventions
    - Configurable risk levels

    Usage:
        class MyAgent(HITLMixin, SovereignBaseAgent):
            def __init__(self):
                super().__init__()
                self.configure_hitl(default_timeout_seconds=600)
                self.register_sensitive_operation(
                    "delete_files",
                    RiskLevel.HIGH,
                    "Permanently deletes files from repository"
                )

            async def delete_files(self, files: list[str]):
                # This will require approval
                await self.require_approval(
                    "delete_files",
                    context={"files": files, "count": len(files)}
                )
                # Proceed with deletion after approval
                ...
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize HITL state."""
        super().__init__(**kwargs)
        self._hitl_config: HITLConfig = HITLConfig()
        self._pending_approvals: dict[str, ApprovalRequest] = {}
        self._approval_history: list[ApprovalRequest] = []
        self._sensitive_operations: dict[str, dict[str, Any]] = {}
        self._approval_callbacks: dict[str, Callable] = {}
        self._hitl_lock = threading.RLock()
        self._hitl_initialized = True
        Logger.debug(f'[HITL] {self.__class__.__name__} HITL initialized')

    def configure_hitl(self, enabled: bool | None=None, default_timeout_seconds: float | None=None, auto_approve_low_risk: bool | None=None, require_notes_on_rejection: bool | None=None, escalation_timeout_seconds: float | None=None, max_escalation_levels: int | None=None, default_escalation_chain: list[str] | None=None, max_pending_approvals: int | None=None, max_history_size: int | None=None) -> None:
        """
        Configure HITL behavior.

        Args:
            enabled: Whether HITL is enabled
            default_timeout_seconds: Default timeout for approvals
            auto_approve_low_risk: Auto-approve LOW risk operations
            require_notes_on_rejection: Require notes when rejecting
            escalation_timeout_seconds: Timeout before escalation
            max_escalation_levels: Maximum escalation levels
            default_escalation_chain: Default escalation chain
            max_pending_approvals: Maximum pending approval requests
            max_history_size: Maximum approval history entries

        Raises:
            ValueError: If any parameter is invalid
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "HITLMixin.configure_hitl")
        if default_timeout_seconds is not None and default_timeout_seconds <= 0:
            raise ValueError('default_timeout_seconds must be positive')
        if escalation_timeout_seconds is not None and escalation_timeout_seconds <= 0:
            raise ValueError('escalation_timeout_seconds must be positive')
        if max_escalation_levels is not None and max_escalation_levels <= 0:
            raise ValueError('max_escalation_levels must be positive')
        if max_pending_approvals is not None and max_pending_approvals <= 0:
            raise ValueError('max_pending_approvals must be positive')
        if max_history_size is not None and max_history_size <= 0:
            raise ValueError('max_history_size must be positive')
        with self._hitl_lock:
            if enabled is not None:
                self._hitl_config.enabled = enabled
            if default_timeout_seconds is not None:
                self._hitl_config.default_timeout_seconds = default_timeout_seconds
            if auto_approve_low_risk is not None:
                self._hitl_config.auto_approve_low_risk = auto_approve_low_risk
            if require_notes_on_rejection is not None:
                self._hitl_config.require_notes_on_rejection = require_notes_on_rejection
            if escalation_timeout_seconds is not None:
                self._hitl_config.escalation_timeout_seconds = escalation_timeout_seconds
            if max_escalation_levels is not None:
                self._hitl_config.max_escalation_levels = max_escalation_levels
            if default_escalation_chain is not None:
                self._hitl_config.default_escalation_chain = default_escalation_chain
            if max_pending_approvals is not None:
                self._hitl_config.max_pending_approvals = max_pending_approvals
            if max_history_size is not None:
                self._hitl_config.max_history_size = max_history_size
        Logger.info(f'[HITL] Configuration updated: {self._hitl_config}')

    def register_sensitive_operation(self, operation_name: str, risk_level: RiskLevel, description: str='', escalation_chain: list[str] | None=None, timeout_seconds: float | None=None) -> None:
        """
        Register a sensitive operation requiring approval.

        Args:
            operation_name: Name of the operation
            risk_level: Risk level for the operation
            description: Human-readable description
            escalation_chain: Custom escalation chain
            timeout_seconds: Custom timeout
        """
        with self._hitl_lock:
            self._sensitive_operations[operation_name] = {'risk_level': risk_level, 'description': description, 'escalation_chain': escalation_chain or self._hitl_config.default_escalation_chain, 'timeout_seconds': timeout_seconds or self._hitl_config.default_timeout_seconds}
        Logger.info(f'[HITL] Registered sensitive operation: {operation_name} (Risk: {risk_level.name})')

    def create_approval_request(self, operation_name: str, context: dict[str, Any] | None=None, description: str | None=None) -> ApprovalRequest:
        """
        Create an approval request for an operation.

        Args:
            operation_name: Name of the operation
            context: Additional context for the approver
            description: Override description

        Returns:
            ApprovalRequest object
        """
        op_config = self._sensitive_operations.get(operation_name, {})
        request = ApprovalRequest(operation_name=operation_name, description=description or op_config.get('description', ''), risk_level=op_config.get('risk_level', RiskLevel.MEDIUM), context=context or {}, timeout_seconds=op_config.get('timeout_seconds', self._hitl_config.default_timeout_seconds), escalation_chain=op_config.get('escalation_chain', self._hitl_config.default_escalation_chain))
        with self._hitl_lock:
            if len(self._pending_approvals) >= self._hitl_config.max_pending_approvals:
                oldest_id = min(self._pending_approvals.keys(), key=lambda k: self._pending_approvals[k].created_at)
                oldest = self._pending_approvals.pop(oldest_id)
                oldest.status = ApprovalStatus.TIMEOUT
                oldest.resolved_at = time.time()
                self._approval_history.append(oldest)
                Logger.warning(f'[HITL] Evicted oldest pending request {oldest_id} due to limit')
            self._pending_approvals[request.request_id] = request
        Logger.info(f"[HITL] Created approval request: {request.request_id} for '{operation_name}'")
        return request

    def requires_human_review(self, operation_name: str) -> bool:
        """Check if an operation requires human review (ADG: requires_human_review edge)."""
        return self.check_approval_required(operation_name)

    def check_approval_required(self, operation_name: str) -> bool:
        """
        Check if an operation requires approval.

        Args:
            operation_name: Name of the operation

        Returns:
            True if approval is required
        """
        if not self._hitl_config.enabled:
            return False
        op_config = self._sensitive_operations.get(operation_name)
        if not op_config:
            return False
        risk_level = op_config.get('risk_level', RiskLevel.LOW)
        if risk_level == RiskLevel.LOW and self._hitl_config.auto_approve_low_risk:
            return False
        return risk_level.value >= RiskLevel.MEDIUM.value

    def require_approval(self, operation_name: str, context: dict[str, Any] | None=None, blocking: bool=True) -> ApprovalRequest:
        """
        Require approval for an operation.

        Args:
            operation_name: Name of the operation
            context: Additional context for the approver
            blocking: If True, raises exception requiring approval

        Returns:
            ApprovalRequest object

        Raises:
            ApprovalRequiredError: If blocking and approval required
        """
        if not self.check_approval_required(operation_name):
            request = self.create_approval_request(operation_name, context)
            self.approve(request.request_id, 'system', 'Auto-approved (low risk)')
            return request
        request = self.create_approval_request(operation_name, context)
        if blocking:
            raise ApprovalRequiredError(request)
        return request

    def approve(self, request_id: str, approved_by: str, notes: str='') -> ApprovalRequest:
        """
        Approve a pending request.

        Args:
            request_id: ID of the request to approve
            approved_by: Identifier of the approver
            notes: Optional approval notes

        Returns:
            Updated ApprovalRequest

        Raises:
            ValueError: If request not found or already resolved
        """
        with self._hitl_lock:
            request = self._pending_approvals.get(request_id)
            if not request:
                raise ValueError(f'Approval request not found: {request_id}')
            if request.status != ApprovalStatus.PENDING:
                raise ValueError(f'Request already resolved: {request.status.value}')
            request.status = ApprovalStatus.APPROVED
            request.resolved_at = time.time()
            request.resolved_by = approved_by
            request.resolution_notes = notes
            del self._pending_approvals[request_id]
            self._approval_history.append(request)
            self._trim_history_if_needed()
        Logger.info(f'[HITL] Request {request_id} APPROVED by {approved_by}')
        self._trigger_approval_callback(request)
        return request

    def reject(self, request_id: str, rejected_by: str, notes: str='') -> ApprovalRequest:
        """
        Reject a pending request.

        Args:
            request_id: ID of the request to reject
            rejected_by: Identifier of the rejector
            notes: Rejection reason (required if configured)

        Returns:
            Updated ApprovalRequest

        Raises:
            ValueError: If request not found, already resolved, or notes required
        """
        with self._hitl_lock:
            request = self._pending_approvals.get(request_id)
            if not request:
                raise ValueError(f'Approval request not found: {request_id}')
            if request.status != ApprovalStatus.PENDING:
                raise ValueError(f'Request already resolved: {request.status.value}')
            if self._hitl_config.require_notes_on_rejection and (not notes):
                raise ValueError('Rejection notes are required')
            request.status = ApprovalStatus.REJECTED
            request.resolved_at = time.time()
            request.resolved_by = rejected_by
            request.resolution_notes = notes
            del self._pending_approvals[request_id]
            self._approval_history.append(request)
            self._trim_history_if_needed()
        Logger.info(f'[HITL] Request {request_id} REJECTED by {rejected_by}: {notes}')
        return request

    def escalate(self, request_id: str) -> ApprovalRequest:
        """
        Escalate a pending request to the next level.

        Args:
            request_id: ID of the request to escalate

        Returns:
            Updated ApprovalRequest

        Raises:
            ValueError: If request not found or max escalation reached
        """
        with self._hitl_lock:
            request = self._pending_approvals.get(request_id)
            if not request:
                raise ValueError(f'Approval request not found: {request_id}')
            if request.current_escalation_level >= len(request.escalation_chain) - 1:
                raise ValueError('Maximum escalation level reached')
            request.current_escalation_level += 1
            request.status = ApprovalStatus.ESCALATED
            current_approver = request.escalation_chain[request.current_escalation_level]
        Logger.warning(f'[HITL] Request {request_id} ESCALATED to level {request.current_escalation_level}: {current_approver}')
        return request

    def get_pending_approvals(self) -> list[dict[str, Any]]:
        """
        Get all pending approval requests.

        Returns:
            List of pending requests as dictionaries
        """
        with self._hitl_lock:
            expired = []
            for req_id, request in self._pending_approvals.items():
                if request.is_expired():
                    request.status = ApprovalStatus.TIMEOUT
                    expired.append(req_id)
            for req_id in expired:
                request = self._pending_approvals.pop(req_id)
                request.resolved_at = time.time()
                self._approval_history.append(request)
                Logger.warning(f'[HITL] Request {req_id} TIMEOUT')
            return [req.to_dict() for req in self._pending_approvals.values()]

    def get_approval_history(self, limit: int=DEFAULT_HISTORY_LIMIT, operation_name: str | None=None) -> list[dict[str, Any]]:
        """
        Get approval history.

        Args:
            limit: Maximum number of records to return
            operation_name: Filter by operation name

        Returns:
            List of historical requests as dictionaries
        """
        with self._hitl_lock:
            history = self._approval_history
            if operation_name:
                history = [r for r in history if r.operation_name == operation_name]
            return [r.to_dict() for r in reversed(history[-limit:])]

    def register_approval_callback(self, operation_name: str, callback: Callable[[ApprovalRequest], None]) -> None:
        """
        Register a callback for when an operation is approved.

        Args:
            operation_name: Name of the operation
            callback: Callback function receiving the ApprovalRequest
        """
        self._approval_callbacks[operation_name] = callback
        Logger.debug(f"[HITL] Registered callback for '{operation_name}'")

    def _trigger_approval_callback(self, request: ApprovalRequest) -> None:
        """Trigger registered callback for approved request."""
        callback = self._approval_callbacks.get(request.operation_name)
        if callback and request.status == ApprovalStatus.APPROVED:
            try:
                callback(request)
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
                Logger.error(f"[HITL] Callback error for '{request.operation_name}': {e}")

    def _trim_history_if_needed(self) -> None:
        """[HARDENING] Trim approval history if it exceeds the configured limit."""
        if len(self._approval_history) > self._hitl_config.max_history_size:
            excess = len(self._approval_history) - self._hitl_config.max_history_size
            self._approval_history = self._approval_history[excess:]
            Logger.debug(f'[HITL] Trimmed {excess} old history entries')

    def get_hitl_status(self) -> dict[str, Any]:
        """
        Get current HITL status.

        Returns:
            Dictionary with HITL status information
        """
        with self._hitl_lock:
            return {'enabled': self._hitl_config.enabled, 'pending_count': len(self._pending_approvals), 'history_count': len(self._approval_history), 'registered_operations': list(self._sensitive_operations.keys()), 'default_timeout': self._hitl_config.default_timeout_seconds, 'auto_approve_low_risk': self._hitl_config.auto_approve_low_risk}
__all__ = ['HITLMixin', 'HITLConfig', 'ApprovalRequest', 'ApprovalStatus', 'RiskLevel', 'ApprovalRequiredError', 'ApprovalRejectedError', 'ApprovalTimeoutError']
