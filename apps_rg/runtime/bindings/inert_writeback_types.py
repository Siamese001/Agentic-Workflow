"""W8 identity, budget, L6 firewall, inert writeback types.

Per W8 requirements:
- AppsRgInertWritebackCandidate: potential writeback without UWG commitment
- Runtime summary distinguishes inert_writeback_candidates vs uwg_committed_writes
- durable_commit_occurred=false until UWG receipt
- L6 shadow handoff is future-run only
- Token/cost budget fields enforced
"""
from __future__ import annotations

import dataclasses
from datetime import datetime
from typing import Any, Optional


@dataclasses.dataclass(frozen=True)
class TokenBudget:
    """Token and cost budget for a resume generation run."""
    # Input tokens consumed
    input_tokens: int
    
    # Output tokens generated
    output_tokens: int
    
    # Total tokens (input + output)
    total_tokens: int
    
    # Estimated cost in USD
    estimated_cost_usd: float
    
    # Budget limits (enforced)
    input_token_limit: int = 8192
    output_token_limit: int = 4096
    cost_limit_usd: float = 0.50
    
    @property
    def within_budget(self) -> bool:
        """True if all budget constraints satisfied."""
        return (
            self.input_tokens <= self.input_token_limit
            and self.output_tokens <= self.output_token_limit
            and self.estimated_cost_usd <= self.cost_limit_usd
        )
    
    @property
    def overage(self) -> dict[str, float]:
        """Return overage amounts if any."""
        result: dict[str, float] = {}
        if self.input_tokens > self.input_token_limit:
            result["input_tokens"] = self.input_tokens - self.input_token_limit
        if self.output_tokens > self.output_token_limit:
            result["output_tokens"] = self.output_tokens - self.output_token_limit
        if self.estimated_cost_usd > self.cost_limit_usd:
            result["cost_usd"] = self.estimated_cost_usd - self.cost_limit_usd
        return result


@dataclasses.dataclass(frozen=True)
class CallerSessionBinding:
    """U0 caller/session binding that survives runtime.
    
    W8: Identity preservation across the pipeline.
    """
    # Caller identity (from U0)
    caller_id: str  # e.g., "apps_rg_cli", "apps_rg_wizard"
    session_id: str  # Unique session identifier
    
    # Ingress timestamp
    ingress_timestamp: datetime
    
    # Request metadata
    request_id: str
    trace_id: str
    
    # Original payload digest (for replay detection)
    payload_digest: str
    
    # Optional fields with defaults
    idempotency_key: Optional[str] = None
    
    # Caller context preserved through runtime
    caller_context: dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True)
class AppsRgInertWritebackCandidate:
    """Inert writeback candidate — not committed until UWG receipt.
    
    W8: Durable writes require Exit X3C + UWG receipt.
    This represents a potential writeback that is NOT yet committed.
    """
    # What would be written
    writeback_type: str  # "semantic_cache", "c0_chunk", "golden_state"
    
    # Content reference (not the actual content — that stays in run dir)
    content_path: str  # Path to content in run directory
    content_hash: str  # Hash of content
    
    # Provenance
    run_id: str
    request_id: str
    trace_id: str
    
    # Why this is a candidate (evidence)
    evidence_digest: str  # Digest of supporting evidence
    
    # Current status
    status: str = "CANDIDATE"  # "CANDIDATE", "SUBMITTED_TO_UWG", "COMMITTED", "REJECTED"
    
    # UWG receipt (only set after successful commit)
    uwg_receipt_ref: Optional[str] = None
    uwg_commit_timestamp: Optional[datetime] = None
    
    @property
    def is_committed(self) -> bool:
        """True only if UWG receipt present."""
        return self.status == "COMMITTED" and self.uwg_receipt_ref is not None
    
    @property
    def durable_commit_occurred(self) -> bool:
        """W8: False until UWG receipt proves durable commit."""
        return self.is_committed


@dataclasses.dataclass(frozen=True)
class L6ShadowHandoff:
    """L6 shadow learning handoff marker — future-run only.
    
    W8: L6 cannot mutate/rescue current run.
    This marks data for future L6 learning, NOT current-run intervention.
    """
    # Required field first (no default)
    trace_refs: list[str]  # References to traces for L6 to learn from
    
    # Fields with defaults
    handoff_type: str = "L6_SHADOW_FUTURE_RUN"
    applicable_run: str = "FUTURE_ONLY"
    can_mutate_current_run: bool = False
    can_rescue_current_run: bool = False
    handoff_timestamp: Optional[datetime] = None
    run_id: str = ""
    trace_id: str = ""
    
    def __post_init__(self) -> None:
        """Enforce L6 firewall invariants."""
        # These must always be False for current run
        if self.can_mutate_current_run or self.can_rescue_current_run:
            raise ValueError(
                "L6ShadowHandoff cannot mutate or rescue current run. "
                "L6 is future-run only."
            )


@dataclasses.dataclass(frozen=True)
class WritebackCommitStatus:
    """Overall writeback commit status for a run.
    
    W8: Runtime summary must distinguish inert vs committed.
    """
    # Inert candidates (not yet committed)
    inert_writeback_candidates: list[AppsRgInertWritebackCandidate]
    inert_candidate_count: int
    
    # UWG committed writes
    uwg_committed_writes: list[AppsRgInertWritebackCandidate]
    uwg_committed_count: int
    
    # Overall status
    durable_commit_occurred: bool  # True if any UWG commits succeeded
    
    # Pending (submitted to UWG but no receipt yet)
    pending_commit_count: int
    
    @property
    def total_candidates(self) -> int:
        """Total writeback candidates."""
        return self.inert_candidate_count + self.uwg_committed_count + self.pending_commit_count
    
    @property
    def commit_rate(self) -> float:
        """Fraction of candidates that were committed."""
        if self.total_candidates == 0:
            return 0.0
        return self.uwg_committed_count / self.total_candidates


# L6 firewall invariants (for test verification)
L6_FIREWALL_INVARIANTS = {
    "l6_cannot_mutate_current_run": True,
    "l6_cannot_rescue_current_run": True,
    "l6_is_future_run_only": True,
    "l6_shadow_handoff_readonly": True,
    "current_run_protected_from_l6": True,
}


__all__ = [
    "TokenBudget",
    "CallerSessionBinding",
    "AppsRgInertWritebackCandidate",
    "L6ShadowHandoff",
    "WritebackCommitStatus",
    "L6_FIREWALL_INVARIANTS",
]
