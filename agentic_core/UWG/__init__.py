"""Universal Write Gateway (UWG) — Package-Driven Write Admission

W11 Implementation: Sole durable admission path for apps_research writeback.

Hard Rules:
1. UWG is the ONLY path to L4 durable writes
2. L4 accepts writes only from UWG
3. L6 emits inert proposals only (FutureRunPromotionRequest)
4. No direct writes from L2, Exit, L6, tools, or apps_research
5. Every write has audit receipt and rollback reference
6. Prohibited terminal-cache payloads are blocked
"""
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto


class WriteStatus(Enum):
    """Status of write admission attempt."""
    ADMITTED = auto()
    BLOCKED = auto()
    PENDING_REVIEW = auto()
    ROLLBACK_SCHEDULED = auto()


class BlockReason(Enum):
    """Reasons for blocking a write."""
    MISSING_PROOF_REPLAY = auto()
    MISSING_PROOF_REGRESSION = auto()
    MISSING_PROOF_SAFETY = auto()
    MISSING_PROOF_CALIBRATION = auto()
    MISSING_ROLLBACK_PLAN = auto()
    MISSING_POLICY_HASH = auto()
    MISSING_REGISTRY_DIGEST = auto()
    INVALID_L4_NAMESPACE = auto()
    PROHIBITED_TERMINAL_CACHE_PAYLOAD = auto()
    FAILED_PROVENANCE_CHECK = auto()
    FAILED_INJECTION_SCAN = auto()
    DIRECT_WRITE_ATTEMPT_BLOCKED = auto()


@dataclass(frozen=True)
class CommitRequest:
    """Request to commit state to L4 via UWG.
    
    Immutable request with full provenance chain.
    """
    request_id: str
    run_id: str
    source_promotion_request: str  # Reference to FutureRunPromotionRequest
    
    # Write payload
    write_type: str  # research_substrate_record_promotion, etc.
    payload: Dict[str, Any] = field(default_factory=dict)
    target_l4_namespace: str = ""
    
    # Provenance
    replay_proof_ref: str = ""
    regression_proof_ref: str = ""
    safety_proof_ref: str = ""
    calibration_proof_ref: str = ""
    rollback_plan_ref: str = ""
    
    # Policy compliance
    write_policy_hash: str = ""
    registry_digest: str = ""
    
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class StateDiffValidationResult:
    """Result of validating state diff before commit."""
    valid: bool
    diff_summary: Dict[str, Any] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    state_hash_before: str = ""
    state_hash_after: str = ""


@dataclass(frozen=True)
class StateCommitReceipt:
    """Receipt for admitted L4 write.
    
    Produced only when UWG admits write.
    """
    receipt_id: str
    commit_request_id: str
    run_id: str
    status: WriteStatus = WriteStatus.ADMITTED
    
    l4_namespace: str = ""
    commit_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    state_diff_validation: Optional[StateDiffValidationResult] = None
    
    # Audit trail
    audit_ledger_ref: str = ""
    rollback_ref: str = ""
    read_surface_refresh_ref: str = ""
    
    evidence_digest: str = ""


@dataclass(frozen=True)
class BlockedWriteReceipt:
    """Receipt for blocked write attempt.
    
    Produced when UWG blocks a write.
    """
    receipt_id: str
    commit_request_id: str
    run_id: str
    status: WriteStatus = WriteStatus.BLOCKED
    
    block_reasons: Tuple[BlockReason, ...] = ()
    block_details: List[str] = field(default_factory=list)
    
    blocked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    audit_ledger_ref: str = ""
    
    evidence_digest: str = ""


@dataclass(frozen=True)
class AuditAppendReceipt:
    """Receipt for audit ledger append.
    
    Required for every write attempt (admit or block).
    """
    append_id: str
    commit_request_id: str
    run_id: str
    appended_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    ledger_sequence: int = 0
    merkle_root: str = ""


@dataclass(frozen=True)
class ReadSurfaceRefreshReceipt:
    """Receipt for read-surface refresh after commit.
    
    Makes committed writes visible to reads.
    """
    refresh_id: str
    commit_receipt_id: str
    l4_namespace: str = ""
    refreshed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    affected_indices: Tuple[str, ...] = ()
    refresh_proof: str = ""


__all__ = [
    "WriteStatus",
    "BlockReason",
    "CommitRequest",
    "StateDiffValidationResult",
    "StateCommitReceipt",
    "BlockedWriteReceipt",
    "AuditAppendReceipt",
    "ReadSurfaceRefreshReceipt",
]
