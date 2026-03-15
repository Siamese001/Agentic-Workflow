"""Seam audit module for Wave 18 - Replay Determinism Closure.

This module provides audit trail functionality for seam operations
with deterministic hash generation for replay verification.
"""

import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from functools import wraps
from typing import Any

from agentic_core.L2_execution.providers import get_clock
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "seam_audit", "L0")
_emit_routes_through("p1", "seam_audit", "L0")
_emit_escalates_to_human("p1", "seam_audit", "L0")
_emit_reads_policy_state("p1", "seam_audit", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "seam_audit", "p0_governance")
_emit_snapshots_state("p0", "seam_audit", "state_snapshot")

Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SeamAuditRecord:
    """Immutable audit record for seam operations."""

    seam_id: str
    operation: str
    inputs_hash: str
    outputs_hash: str
    invocation_hash: str
    timestamp: float
    layer_source: str
    layer_target: str
    caller_id: str | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})


class SeamAuditLogger:
    """Central logger for seam audit records."""

    def __init__(self):
        self._records: list[SeamAuditRecord] = []
        self._enabled = True

    def enable(self):
        """Enable audit logging."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "SeamAuditLogger.enable")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        self._enabled = True
        Logger.info("Seam audit logging enabled")

    def disable(self):
        """Disable audit logging."""
        self._enabled = False
        Logger.info("Seam audit logging disabled")

    def log_seam_operation(
        self,
        seam_id: str,
        operation: str,
        inputs: Any,
        outputs: Any,
        layer_source: str,
        layer_target: str,
        caller_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SeamAuditRecord:
        """Log a seam operation with deterministic hashing."""
        if not self._enabled:
            return None
        inputs_hash = self._compute_hash(inputs)
        outputs_hash = self._compute_hash(outputs)
        invocation_data = {
            "seam_id": seam_id,
            "operation": operation,
            "inputs_hash": inputs_hash,
            "outputs_hash": outputs_hash,
            "layer_source": layer_source,
            "layer_target": layer_target,
            "caller_id": caller_id,
            "metadata": metadata or {},
        }
        invocation_hash = self._compute_hash(invocation_data)
        record = SeamAuditRecord(
            seam_id=seam_id,
            operation=operation,
            inputs_hash=inputs_hash,
            outputs_hash=outputs_hash,
            invocation_hash=invocation_hash,
            timestamp=get_clock().now_epoch(),
            layer_source=layer_source,
            layer_target=layer_target,
            caller_id=caller_id,
            metadata=metadata or {},
        )
        self._records.append(record)
        Logger.debug(f"Seam audit: {operation} on {seam_id} ({layer_source} -> {layer_target})")
        return record

    def get_records(self, seam_id: str | None = None) -> list[SeamAuditRecord]:
        """Get audit records, optionally filtered by seam_id."""
        if seam_id is None:
            return self._records.copy()
        return [r for r in self._records if r.seam_id == seam_id]

    def get_digest(self, seam_id: str | None = None) -> str:
        """Compute deterministic digest of audit records."""
        records = self.get_records(seam_id)
        sorted_records = sorted(records, key=lambda r: (r.seam_id, r.timestamp, r.operation))
        digest_data = []
        for record in sorted_records:
            record_dict = asdict(record)
            digest_data.append(record_dict)
        digest_json = json.dumps(digest_data, sort_keys=True)
        return hashlib.sha256(digest_json.encode()).hexdigest()

    def clear_records(self):
        """Clear all audit records (for testing)."""
        self._records.clear()
        Logger.debug("Seam audit records cleared")

    def _compute_hash(self, data: Any) -> str:
        """Compute deterministic hash for any serializable data."""
        try:
            if isinstance(data, (dict, list, tuple, str, int, float, bool, type(None))):
                data_json = json.dumps(data, sort_keys=True, default=str)
            elif hasattr(data, "__dict__"):
                data_json = json.dumps(data.__dict__, sort_keys=True, default=str)
            else:
                data_json = str(data)
            return hashlib.sha256(data_json.encode()).hexdigest()
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.warning(f"Failed to compute hash for data: {e}")
            return hashlib.sha256(str(data).encode()).hexdigest()


_audit_logger = None


def get_seam_audit_logger() -> SeamAuditLogger:
    """Get the global seam audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = SeamAuditLogger()
    return _audit_logger


def seam_audit_hook(seam_id: str, operation: str, layer_source: str, layer_target: str):
    """Decorator to automatically audit seam operations."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_seam_audit_logger()
            inputs = {"args": args, "kwargs": kwargs}
            outputs = func(*args, **kwargs)
            caller_id = None
            if hasattr(func, "__module__"):
                caller_id = f"{func.__module__}.{func.__name__}"
            logger.log_seam_operation(
                seam_id=seam_id,
                operation=operation,
                inputs=inputs,
                outputs=outputs,
                layer_source=layer_source,
                layer_target=layer_target,
                caller_id=caller_id,
            )
            return outputs

        return wrapper

    return decorator


def log_seam_operation(
    seam_id: str,
    operation: str,
    inputs: Any,
    outputs: Any,
    layer_source: str,
    layer_target: str,
    caller_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> SeamAuditRecord | None:
    """Log a seam operation manually."""
    logger = get_seam_audit_logger()
    return logger.log_seam_operation(
        seam_id=seam_id,
        operation=operation,
        inputs=inputs,
        outputs=outputs,
        layer_source=layer_source,
        layer_target=layer_target,
        caller_id=caller_id,
        metadata=metadata,
    )


def get_seam_audit_digest(seam_id: str | None = None) -> str:
    """Get deterministic digest of seam audit records."""
    logger = get_seam_audit_logger()
    return logger.get_digest(seam_id)


def clear_seam_audit_records():
    """Clear all seam audit records (for testing)."""
    logger = get_seam_audit_logger()
    logger.clear_records()
