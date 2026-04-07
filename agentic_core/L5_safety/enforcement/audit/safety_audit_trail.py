"""
agentic_core/L5_safety/audit/safety_audit_trail.py

SafetyAuditTrail — P2-L5 gap remediation.

Immutable append-only audit log capturing every guardrail check,
policy enforcement, tool safety gate, and HITL decision from L5.
Closes the gap: 608 L5 modules with 0 produces_audit_trail edges
in the ADG.

ADG edges emitted: produces_audit_trail, validated_by_safety_plane,
                   references_policy_hash
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
)

logger = logging.getLogger(__name__)

_DEFAULT_TRAIL_PATH = Path("artifacts/safety/audit_trail.jsonl")


class AuditEventKind(str, Enum):
    """Classification of a safety audit event."""

    GUARDRAIL_CHECK = "guardrail_check"
    POLICY_ENFORCEMENT = "policy_enforcement"
    TOOL_SAFETY_GATE = "tool_safety_gate"
    HITL_DECISION = "hitl_decision"
    GUARDRAIL_VIOLATION = "guardrail_violation"
    POLICY_VIOLATION = "policy_violation"
    SANDBOX_ENTRY = "sandbox_entry"
    REENTER_SAFETY = "reenter_safety"


@dataclass
class SafetyAuditEvent:
    """Single safety audit event record."""

    event_id: str
    kind: AuditEventKind
    module: str
    operation: str
    verdict: str
    policy_hash: str
    trace_id: str
    timestamp: float
    allowed: bool
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=True)


class SafetyAuditTrail:
    """Immutable append-only audit trail for all L5 safety events.

    Usage::

        trail = SafetyAuditTrail()
        trail.record_guardrail_check(
            module="airlock_guardrail",
            operation="write_file",
            verdict="allow",
            policy_hash="abc123",
            trace_id=trace_id,
            allowed=True,
        )
        trail.flush()
    """

    def __init__(self, trail_path: Path | None = None) -> None:
        self._path = trail_path or _DEFAULT_TRAIL_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._records: list[SafetyAuditEvent] = []
        self._lock = threading.Lock()
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        ts = time.monotonic()
        payload = f"{self._counter}:{ts:.6f}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def _record(self, event: SafetyAuditEvent) -> SafetyAuditEvent:
        with self._lock:
            self._records.append(event)
        log_fn = logger.debug if event.allowed else logger.warning
        log_fn(
            "SAFETY_AUDIT produces_audit_trail validated_by_safety_plane "
            "kind=%s module=%s op=%s verdict=%s allowed=%s trace=%s",
            event.kind.value,
            event.module,
            event.operation,
            event.verdict,
            event.allowed,
            event.trace_id,
        )
        return event

    def record_guardrail_check(
        self,
        module: str,
        operation: str,
        verdict: str,
        policy_hash: str,
        trace_id: str,
        allowed: bool,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> SafetyAuditEvent:
        return self._record(
            SafetyAuditEvent(
                event_id=self._next_id(),
                kind=AuditEventKind.GUARDRAIL_CHECK,
                module=module,
                operation=operation,
                verdict=verdict,
                policy_hash=policy_hash,
                trace_id=trace_id,
                timestamp=time.monotonic(),
                allowed=allowed,
                reason=reason,
                metadata=metadata or {},
            ),
        )

    def record_policy_enforcement(
        self,
        module: str,
        action: str,
        verdict: str,
        policy_hash: str,
        trace_id: str,
        allowed: bool,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> SafetyAuditEvent:
        return self._record(
            SafetyAuditEvent(
                event_id=self._next_id(),
                kind=AuditEventKind.POLICY_ENFORCEMENT,
                module=module,
                operation=action,
                verdict=verdict,
                policy_hash=policy_hash,
                trace_id=trace_id,
                timestamp=time.monotonic(),
                allowed=allowed,
                reason=reason,
                metadata=metadata or {},
            ),
        )

    def record_tool_gate(
        self,
        module: str,
        tool_name: str,
        risk_level: str,
        policy_hash: str,
        trace_id: str,
        allowed: bool,
        sandboxed: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> SafetyAuditEvent:
        return self._record(
            SafetyAuditEvent(
                event_id=self._next_id(),
                kind=AuditEventKind.TOOL_SAFETY_GATE,
                module=module,
                operation=f"tool:{tool_name}",
                verdict="allow" if allowed else "deny",
                policy_hash=policy_hash,
                trace_id=trace_id,
                timestamp=time.monotonic(),
                allowed=allowed,
                metadata={**(metadata or {}), "sandboxed": sandboxed, "risk_level": risk_level},
            ),
        )

    def record_hitl_decision(
        self,
        module: str,
        decision: str,
        trace_id: str,
        policy_hash: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> SafetyAuditEvent:
        return self._record(
            SafetyAuditEvent(
                event_id=self._next_id(),
                kind=AuditEventKind.HITL_DECISION,
                module=module,
                operation="hitl_decision",
                verdict=decision,
                policy_hash=policy_hash,
                trace_id=trace_id,
                timestamp=time.monotonic(),
                allowed=decision in ("approve", "allow"),
                metadata=metadata or {},
            ),
        )

    def flush(self) -> int:
        """Write all buffered records to the JSONL trail file.

        Returns count of records written.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SafetyAuditTrail.flush")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SafetyAuditTrail.flush".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        with self._lock:
            records = list(self._records)
        count = 0
        try:
            with open(self._path, "a", encoding="utf-8") as f:
                for rec in records:
                    f.write(rec.to_jsonl() + "\n")
                    count += 1
        except OSError as exc:    # guardian: Add error context logging
            logger.warning("SafetyAuditTrail flush failed: %s", exc)
        return count

    def all_records(self) -> list[SafetyAuditEvent]:
        with self._lock:
            return list(self._records)

    def violations(self) -> list[SafetyAuditEvent]:
        with self._lock:
            return [r for r in self._records if not r.allowed]

    def count(self) -> int:
        with self._lock:
            return len(self._records)


_global_trail: SafetyAuditTrail | None = None


def get_safety_audit_trail(path: Path | None = None) -> SafetyAuditTrail:
    global _global_trail
    if _global_trail is None:
        _global_trail = SafetyAuditTrail(trail_path=path)
    return _global_trail


def reset_safety_audit_trail() -> None:
    global _global_trail
    _global_trail = None


__all__ = [
    "AuditEventKind",
    "SafetyAuditEvent",
    "SafetyAuditTrail",
    "get_safety_audit_trail",
    "reset_safety_audit_trail",
]
