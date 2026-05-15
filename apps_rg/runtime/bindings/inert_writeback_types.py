"""apps_rg inert writeback types — W8 UWG-gated write candidates."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

__all__ = [
    "AppsRgInertWritebackCandidate",
    "TokenBudget",
    "CallerSessionBinding",
    "L6ShadowHandoff",
    "L6_FIREWALL_INVARIANTS",
    "WritebackCommitStatus",
]

L6_FIREWALL_INVARIANTS: dict[str, bool] = {
    "l6_cannot_mutate_current_run": True,
    "l6_cannot_rescue_current_run": True,
    "l6_is_future_run_only": True,
    "current_run_protected_from_l6": True,
}

@dataclass
class WritebackCommitStatus:
    """Tracks inert vs. UWG-committed writebacks for a single run."""

    inert_writeback_candidates: list[Any] = field(default_factory=list)
    inert_candidate_count: int = 0
    uwg_committed_writes: list[Any] = field(default_factory=list)
    uwg_committed_count: int = 0
    durable_commit_occurred: bool = False
    pending_commit_count: int = 0

    @property
    def total_candidates(self) -> int:
        return (
            self.inert_candidate_count
            + self.uwg_committed_count
            + self.pending_commit_count
        )

    @property
    def commit_rate(self) -> float:
        total = self.total_candidates
        if total == 0:
            return 0.0
        return round(self.uwg_committed_count / total, 4)


@dataclass
class AppsRgInertWritebackCandidate:
    """Non-durable writeback proposal — inert until UWG receipt."""

    writeback_type: str
    content_path: str
    content_hash: str
    run_id: str
    request_id: str
    trace_id: str
    evidence_digest: str
    status: str = "CANDIDATE"
    uwg_receipt_ref: Optional[str] = None
    uwg_commit_timestamp: Optional[datetime] = None

    @property
    def is_committed(self) -> bool:
        return self.status == "COMMITTED" and self.uwg_receipt_ref is not None

    @property
    def durable_commit_occurred(self) -> bool:
        return (
            self.status == "COMMITTED"
            and self.uwg_receipt_ref is not None
            and self.uwg_commit_timestamp is not None
        )


@dataclass(frozen=True)
class TokenBudget:
    """Token budget snapshot for a run."""

    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    _input_limit: int = field(default=8192, repr=False, compare=False)
    _output_limit: int = field(default=4096, repr=False, compare=False)
    _cost_limit_usd: float = field(default=0.50, repr=False, compare=False)

    @property
    def within_budget(self) -> bool:
        return (
            self.input_tokens <= self._input_limit
            and self.output_tokens <= self._output_limit
            and self.estimated_cost_usd <= self._cost_limit_usd
        )

    @property
    def overage(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.input_tokens > self._input_limit:
            result["input_tokens"] = self.input_tokens - self._input_limit
        if self.output_tokens > self._output_limit:
            result["output_tokens"] = self.output_tokens - self._output_limit
        if self.estimated_cost_usd > self._cost_limit_usd:
            result["cost_usd"] = round(self.estimated_cost_usd - self._cost_limit_usd, 4)
        return result


@dataclass
class CallerSessionBinding:
    """U0 caller and session identity binding."""

    caller_id: str
    session_id: str
    ingress_timestamp: datetime
    request_id: str
    trace_id: str
    payload_digest: str
    idempotency_key: str = ""
    caller_context: dict[str, Any] = field(default_factory=dict)


@dataclass
class L6ShadowHandoff:
    """Inert L6 shadow handoff record — future-run only.

    Raises ValueError if can_mutate_current_run or can_rescue_current_run
    is True — the L6 firewall forbids both unconditionally.
    """

    handoff_type: str
    trace_refs: list[str] = field(default_factory=list)
    applicable_run: str = "FUTURE_ONLY"
    can_mutate_current_run: bool = False
    can_rescue_current_run: bool = False
    handoff_timestamp: Optional[datetime] = None
    run_id: str = ""
    trace_id: str = ""
    payload_digest: str = ""
    is_shadow: bool = True
    is_future_run_only: bool = True

    def __post_init__(self) -> None:
        if self.can_mutate_current_run:
            raise ValueError(
                "L6ShadowHandoff: can_mutate_current_run=True violates the L6 firewall invariant. "
                "L6 shadow handoffs are future-run only."
            )
        if self.can_rescue_current_run:
            raise ValueError(
                "L6ShadowHandoff: can_rescue_current_run=True violates the L6 firewall invariant. "
                "L6 shadow handoffs are future-run only."
            )
