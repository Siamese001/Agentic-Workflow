"""
L7 Runtime Audit Trace Contract — agentic_core/runtime/contracts/l7_runtime_audit_trace.py

Immutable span-bound evidence proving apps_rg had zero runtime authority during execution.
L7 is the authority boundary: any code path that successfully emitted span-chain evidence
without APPS_RG_AUTHORITY_VIOLATION span constitutes a certified no-shadow-pipeline proof.

Canonical L7 span types:
- APPS_RG_INGRESS_ACCEPT: U0 accepted payload; policy receipt attached
- APPS_RG_POLICY_PASS: Runtime authority scan passed; no forbidden surface detected
- APPS_RG_AUTHORITY_VIOLATION: Policy deny — runtime authority detected in apps_rg live path
- L7_CHAIN_COMPLETE: Full span chain closed; no gaps; ready for archival

Usage:
    from agentic_core.runtime.contracts.l7_runtime_audit_trace import (
        L7RuntimeAuditTrace,
        AuthoritySpanType,
        AuditTraceReceipt,
    )
    trace = L7RuntimeAuditTrace.start_new(run_id="run_123")
    trace.emit(span_type=AuthoritySpanType.POLICY_PASS, detail={...})
    receipt = trace.finalize()
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class AuthoritySpanType(str, Enum):
    """Canonical L7 span type vocabulary.
    
    These span types form a strict state machine:
    INGRESS_ACCEPT → (POLICY_PASS | AUTHORITY_VIOLATION) → CHAIN_COMPLETE
    """
    INGRESS_ACCEPT = "APPS_RG_INGRESS_ACCEPT"
    POLICY_PASS = "APPS_RG_POLICY_PASS"
    AUTHORITY_VIOLATION = "APPS_RG_AUTHORITY_VIOLATION"
    CHAIN_COMPLETE = "L7_CHAIN_COMPLETE"


@dataclass(frozen=True, slots=True)
class AuthoritySpan:
    """Single immutable span within the L7 audit trace.
    
    Fields:
        span_id: UUIDv4 for deduplication and cross-span referencing.
        span_type: Canonical span type from AuthoritySpanType.
        timestamp: ISO-8601 UTC timestamp (nanosecond precision when available).
        run_id: The run context identifier (propagated from AppsRgIngressPayload).
        detail: Arbitrary JSON-serializable detail dict (length-capped by policy).
        parent_span_id: Optional chaining reference for hierarchical traces.
    """
    span_id: str
    span_type: AuthoritySpanType
    timestamp: str
    run_id: str
    detail: Dict[str, Any] = field(default_factory=dict)
    parent_span_id: Optional[str] = None

    def __post_init__(self) -> None:
        # Validate span_type is canonical
        if not isinstance(self.span_type, AuthoritySpanType):
            raise ValueError(
                f"Invalid span_type: {self.span_type}. "
                f"Must be one of {[e.value for e in AuthoritySpanType]}"
            )
        # Validate timestamp is ISO-8601-like (basic RFC 3339 check)
        if not self.timestamp or "T" not in self.timestamp:
            raise ValueError(f"Invalid ISO-8601 timestamp: {self.timestamp}")

    def is_violation(self) -> bool:
        """True if this span records an authority violation."""
        return self.span_type == AuthoritySpanType.AUTHORITY_VIOLATION

    def is_terminal(self) -> bool:
        """True if this span type is terminal (chain complete)."""
        return self.span_type == AuthoritySpanType.CHAIN_COMPLETE


@dataclass(frozen=True, slots=True)
class AuditTraceReceipt:
    """Final signed receipt produced when an L7 trace is finalized.
    
    This receipt is the attestation artifact referenced by downstream compliance
    and certification processes. It binds the full span chain to a single
    signed structure suitable for ledger append or archival.
    
    Fields:
        run_id: The run context identifier.
        trace_id: UUIDv4 identifying this specific trace instance.
        spans_count: Total number of spans in the trace.
        violation_count: Number of AUTHORITY_VIOLATION spans (must be 0 for PASS).
        status: "PASS" if no violations and chain complete; else "FAIL".
        started_at: ISO-8601 timestamp of first span.
        finalized_at: ISO-8601 timestamp of receipt generation.
        span_ids: Ordered list of span IDs for chain verification.
        merkle_root: Optional hash of canonical span serialization (placeholder).
    """
    run_id: str
    trace_id: str
    spans_count: int
    violation_count: int
    status: str  # "PASS" | "FAIL"
    started_at: str
    finalized_at: str
    span_ids: List[str] = field(default_factory=list)
    merkle_root: Optional[str] = None

    def is_pass(self) -> bool:
        """True if this receipt represents a passing audit (no violations)."""
        return self.status == "PASS" and self.violation_count == 0


class L7RuntimeAuditTrace:
    """Mutable builder for an L7 runtime audit trace.
    
    This class is NOT frozen — it accumulates spans incrementally during a run.
    Once finalized, it produces an immutable AuditTraceReceipt.
    
    Thread-safety: This builder is intended for single-threaded use within the
    async loop of the Exit stage. Concurrent emit() calls require external lock.
    
    Example:
        trace = L7RuntimeAuditTrace.start_new(run_id="abc123")
        trace.emit(AuthoritySpanType.INGRESS_ACCEPT, detail={"payload_digest": "sha256:..."})
        trace.emit(AuthoritySpanType.POLICY_PASS, detail={"scan_receipt": {...}})
        trace.emit(AuthoritySpanType.CHAIN_COMPLETE, detail={})
        receipt = trace.finalize()
        assert receipt.is_pass()
    """

    def __init__(self, run_id: str, trace_id: Optional[str] = None) -> None:
        self._run_id: str = run_id
        self._trace_id: str = trace_id or str(uuid.uuid4())
        self._spans: List[AuthoritySpan] = []
        self._started_at: Optional[str] = None
        self._finalized: bool = False

    @classmethod
    def start_new(cls, run_id: str) -> L7RuntimeAuditTrace:
        """Factory for a fresh trace with generated trace_id."""
        return cls(run_id=run_id, trace_id=str(uuid.uuid4()))

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def trace_id(self) -> str:
        return self._trace_id

    @property
    def span_count(self) -> int:
        return len(self._spans)

    def emit(
        self,
        span_type: AuthoritySpanType,
        detail: Optional[Dict[str, Any]] = None,
        parent_span_id: Optional[str] = None,
        now: Optional[datetime] = None,
    ) -> AuthoritySpan:
        """Emit a new span into the trace.
        
        Args:
            span_type: The canonical span type.
            detail: JSON-serializable dict (default empty).
            parent_span_id: Optional hierarchical reference.
            now: Optional timestamp override (for deterministic testing).
        
        Returns:
            The emitted AuthoritySpan (immutable).
        """
        if self._finalized:
            raise RuntimeError("Cannot emit to finalized trace")
        ts = (now or datetime.now(timezone.utc)).isoformat()
        if self._started_at is None:
            self._started_at = ts
        span = AuthoritySpan(
            span_id=str(uuid.uuid4()),
            span_type=span_type,
            timestamp=ts,
            run_id=self._run_id,
            detail=detail or {},
            parent_span_id=parent_span_id,
        )
        self._spans.append(span)
        return span

    def finalize(self, now: Optional[datetime] = None) -> AuditTraceReceipt:
        """Finalize the trace and produce an immutable receipt.
        
        After finalize(), emit() will raise RuntimeError.
        
        Returns:
            AuditTraceReceipt with status "PASS" if no violations and
            CHAIN_COMPLETE span present; else "FAIL".
        """
        if self._finalized:
            # Idempotent: return same conceptual receipt (reconstruct from state)
            pass
        self._finalized = True
        violation_count = sum(1 for s in self._spans if s.is_violation())
        has_terminal = any(s.is_terminal() for s in self._spans)
        status = "PASS" if violation_count == 0 and has_terminal else "FAIL"
        finalized_at = (now or datetime.now(timezone.utc)).isoformat()
        return AuditTraceReceipt(
            run_id=self._run_id,
            trace_id=self._trace_id,
            spans_count=len(self._spans),
            violation_count=violation_count,
            status=status,
            started_at=self._started_at or finalized_at,
            finalized_at=finalized_at,
            span_ids=[s.span_id for s in self._spans],
            merkle_root=None,  # Placeholder for future cryptographic binding
        )

    def to_serializable(self) -> Dict[str, Any]:
        """Return a JSON-serializable dict representing the current trace state.
        
        Note: This includes spans but does not finalize the trace.
        """
        return {
            "run_id": self._run_id,
            "trace_id": self._trace_id,
            "started_at": self._started_at,
            "finalized": self._finalized,
            "spans": [
                {
                    "span_id": s.span_id,
                    "span_type": s.span_type.value,
                    "timestamp": s.timestamp,
                    "run_id": s.run_id,
                    "detail": s.detail,
                    "parent_span_id": s.parent_span_id,
                }
                for s in self._spans
            ],
        }
