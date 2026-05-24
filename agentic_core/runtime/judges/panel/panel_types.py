"""Types for multi-provider judge panel harness (app-agnostic)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TransportReceipt:
    """Observed provider transport fields for parity audit."""

    provider_key: str
    contract_hash: str
    max_output_tokens: int
    temperature: float | None
    json_output_lock: str
    finish_or_stop_reason: str | None
    parse_status: str
    attempt: int = 1


@dataclass(frozen=True)
class PanelJudgeOutcome:
    """Normalized outcome from one provider after parse + score law."""

    provider_key: str
    contract_hash: str
    input_hash: str
    evaluator_mode: str
    provider_status: str
    score: float | None
    score_scale: str
    threshold: float
    pass_: bool
    decisive_failure: bool
    findings: tuple[str, ...] = field(default_factory=tuple)
    cited_sentence_indexes: tuple[int, ...] = field(default_factory=tuple)
    remediation_suggestions: tuple[str, ...] = field(default_factory=tuple)
    transport_receipt: TransportReceipt | None = None
    raw_body: dict[str, Any] | None = None


@dataclass(frozen=True)
class ReconciliationReceipt:
    """Audit trail for gate-closure reconcile."""

    policy_version: str
    original_score: float
    original_pass: bool
    final_score: float
    final_pass: bool
    suppressed_findings: tuple[str, ...]
    preserved_findings: tuple[str, ...]


@dataclass(frozen=True)
class TransportParityViolation:
    code: str
    detail: str
    provider_key: str = ""


__all__ = [
    "PanelJudgeOutcome",
    "ReconciliationReceipt",
    "TransportParityViolation",
    "TransportReceipt",
]
