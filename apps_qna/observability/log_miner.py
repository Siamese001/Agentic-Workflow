"""Production-log mining with PII redaction — D3.1.

Provides a deterministic log analysis pipeline for apps_qna run logs:

1. PII redaction: strips email, phone, SSN, credit-card-like, and
   custom-pattern matches before any log record is stored or emitted.
2. Log mining: extracts structured run metrics (pack slug, route_id,
   card_count, evidence_sufficiency, dim_scores, latency_ms) from raw
   log dicts produced by the spine pipeline.
3. Aggregation: summarises a batch of run records into pass/fail/abstain
   counts and per-dim score distributions.

All operations are deterministic and pure — no I/O, no side effects.
The caller is responsible for feeding log dicts and persisting output.

Plan: .windsurf/plans/apps-qna-spine-deferred-e9c5b3.md D3.1
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# PII redaction patterns
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.ASCII,
)
_PHONE_RE = re.compile(
    r"\b(?:\+?1[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}\b",
)
_SSN_RE = re.compile(
    r"\b\d{3}[- ]\d{2}[- ]\d{4}\b",
)
_CARD_RE = re.compile(
    r"\b(?:4\d{3}|5[1-5]\d{2}|3[47]\d{2}|6011)[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
)

_PII_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (_EMAIL_RE, "[REDACTED_EMAIL]"),
    (_PHONE_RE, "[REDACTED_PHONE]"),
    (_SSN_RE, "[REDACTED_SSN]"),
    (_CARD_RE, "[REDACTED_CARD]"),
]


def redact_pii(text: str, extra_patterns: list[tuple[str, str]] | None = None) -> str:
    """Redact PII from a string.

    Applies canonical PII patterns (email, phone, SSN, card) and any
    caller-supplied extra patterns. Patterns are applied left-to-right;
    each pass operates on the result of the previous.

    Args:
        text: Raw string that may contain PII.
        extra_patterns: Optional list of (regex_pattern, replacement) tuples
            for app-specific PII fields (e.g. employee IDs, internal codes).

    Returns:
        String with all recognised PII replaced by sentinel tokens.
    """
    result = text
    for pattern, replacement in _PII_PATTERNS:
        result = pattern.sub(replacement, result)
    if extra_patterns:
        for raw_pattern, replacement in extra_patterns:
            result = re.sub(raw_pattern, replacement, result)
    return result


def _redact_value(value: Any, extra_patterns: list[tuple[str, str]] | None) -> Any:
    """Recursively redact PII from a value (str, dict, list, or primitive)."""
    if isinstance(value, str):
        return redact_pii(value, extra_patterns)
    if isinstance(value, dict):
        return {k: _redact_value(v, extra_patterns) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        redacted = [_redact_value(v, extra_patterns) for v in value]
        return type(value)(redacted)
    return value


def redact_log_record(
    record: dict[str, Any],
    extra_patterns: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    """Redact PII from every string-valued field in a log record dict.

    Args:
        record: Raw log record dict (may be deeply nested).
        extra_patterns: Optional app-specific PII patterns.

    Returns:
        New dict with all string values PII-redacted.
    """
    return {k: _redact_value(v, extra_patterns) for k, v in record.items()}


# ---------------------------------------------------------------------------
# Log mining — structured metric extraction
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RunMetrics:
    """Structured metrics extracted from a single apps_qna run log record.

    Attributes:
        interview_slug: Pack slug for this run.
        route_id: Selected route.
        card_count: Number of cards rendered.
        evidence_sufficiency: Evidence sufficiency label.
        x3_disposition: Exit disposition (ALLOW_FINISH / SAFE_ABSTAIN / …).
        latency_ms: End-to-end build latency in milliseconds (0 if absent).
        dim_scores: Mapping of dim_id → float score from the evaluator.
        reason_codes: Reason codes from the exit packet.
        pii_redacted: True when PII redaction was applied before mining.
        raw_producer: Producer field from the evidence contract.
    """

    interview_slug: str = ""
    route_id: str = ""
    card_count: int = 0
    evidence_sufficiency: str = "empty"
    x3_disposition: str = ""
    latency_ms: int = 0
    dim_scores: dict[str, float] = field(default_factory=dict)
    reason_codes: tuple[str, ...] = ()
    pii_redacted: bool = False
    raw_producer: str = ""


def mine_run_log(
    record: dict[str, Any],
    *,
    redact: bool = True,
    extra_patterns: list[tuple[str, str]] | None = None,
) -> RunMetrics:
    """Extract structured RunMetrics from a raw spine run log record.

    The function is defensive — missing keys produce safe defaults.
    PII redaction is applied to string fields before value extraction
    when redact=True (default).

    Expected record shape (all keys optional):
        {
            "interview_slug": str,
            "route_id": str,
            "manifest": {"cards": [...], "interview_slug": str},
            "evidence_contract": {"evidence_sufficiency": str, "producer": str},
            "exit_packet": {"x3_disposition": str, "reason_codes": [str]},
            "dim_scores": {dim_id: float},
            "latency_ms": int,
        }

    Args:
        record: Raw log record dict from the spine pipeline.
        redact: Apply PII redaction before mining (default True).
        extra_patterns: App-specific extra PII patterns.

    Returns:
        RunMetrics with extracted values and pii_redacted flag.
    """
    if redact:
        record = redact_log_record(record, extra_patterns)

    manifest = record.get("manifest") or {}
    evidence = record.get("evidence_contract") or {}
    exit_pkt = record.get("exit_packet") or {}
    dim_scores_raw = record.get("dim_scores") or {}

    slug = (
        record.get("interview_slug")
        or manifest.get("interview_slug")
        or ""
    )
    route_id = record.get("route_id") or ""
    cards = manifest.get("cards") or []
    card_count = len(cards) if isinstance(cards, (list, tuple)) else 0
    evidence_sufficiency = evidence.get("evidence_sufficiency") or "empty"
    x3 = exit_pkt.get("x3_disposition") or record.get("x3_disposition") or ""
    latency = int(record.get("latency_ms") or 0)
    reason_codes_raw = exit_pkt.get("reason_codes") or record.get("reason_codes") or []
    reason_codes = tuple(str(r) for r in reason_codes_raw if r)
    producer = evidence.get("producer") or ""

    dim_scores: dict[str, float] = {}
    for dim_id, score in dim_scores_raw.items():
        try:
            dim_scores[str(dim_id)] = float(score)
        except (TypeError, ValueError):  # guardian: allow-silent-swallow -- dim score parsing fail-soft; malformed scores are silently dropped
            pass

    return RunMetrics(
        interview_slug=str(slug),
        route_id=str(route_id),
        card_count=card_count,
        evidence_sufficiency=str(evidence_sufficiency),
        x3_disposition=str(x3),
        latency_ms=latency,
        dim_scores=dim_scores,
        reason_codes=reason_codes,
        pii_redacted=redact,
        raw_producer=str(producer),
    )


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RunBatchSummary:
    """Summary of a batch of RunMetrics records.

    Attributes:
        total: Total number of records.
        allow_finish_count: Runs that exited ALLOW_FINISH.
        abstain_count: Runs that exited SAFE_ABSTAIN or other non-finish.
        avg_card_count: Average cards per run.
        avg_latency_ms: Average latency in ms.
        dim_score_means: Mapping of dim_id → mean score across all runs
            that reported a score for that dim.
        evidence_sufficiency_counts: Mapping of label → count.
    """

    total: int = 0
    allow_finish_count: int = 0
    abstain_count: int = 0
    avg_card_count: float = 0.0
    avg_latency_ms: float = 0.0
    dim_score_means: dict[str, float] = field(default_factory=dict)
    evidence_sufficiency_counts: dict[str, int] = field(default_factory=dict)


class LogMiner:
    """Stateful log miner that accumulates RunMetrics and produces summaries.

    Usage:
        miner = LogMiner()
        for raw in log_records:
            miner.ingest(raw)
        summary = miner.summarise()
    """

    def __init__(
        self,
        *,
        redact: bool = True,
        extra_patterns: list[tuple[str, str]] | None = None,
    ) -> None:
        self._redact = redact
        self._extra_patterns = extra_patterns
        self._records: list[RunMetrics] = []

    def ingest(self, record: dict[str, Any]) -> RunMetrics:
        """Mine and accumulate a single raw log record.

        Args:
            record: Raw spine run log dict.

        Returns:
            The extracted RunMetrics (also stored internally).
        """
        metrics = mine_run_log(
            record, redact=self._redact, extra_patterns=self._extra_patterns
        )
        self._records.append(metrics)
        return metrics

    def ingest_batch(self, records: list[dict[str, Any]]) -> list[RunMetrics]:
        """Mine and accumulate a batch of raw log records."""
        return [self.ingest(r) for r in records]

    @property
    def records(self) -> list[RunMetrics]:
        """All accumulated RunMetrics records."""
        return list(self._records)

    def summarise(self) -> RunBatchSummary:
        """Compute a RunBatchSummary over all accumulated records."""
        if not self._records:
            return RunBatchSummary()

        allow_count = sum(
            1 for r in self._records if r.x3_disposition == "ALLOW_FINISH"
        )
        abstain_count = len(self._records) - allow_count
        avg_cards = sum(r.card_count for r in self._records) / len(self._records)
        avg_latency = sum(r.latency_ms for r in self._records) / len(self._records)

        dim_sums: dict[str, list[float]] = {}
        for rec in self._records:
            for dim_id, score in rec.dim_scores.items():
                dim_sums.setdefault(dim_id, []).append(score)
        dim_means = {
            dim_id: sum(scores) / len(scores)
            for dim_id, scores in dim_sums.items()
        }

        sufficiency_counts: dict[str, int] = {}
        for rec in self._records:
            label = rec.evidence_sufficiency
            sufficiency_counts[label] = sufficiency_counts.get(label, 0) + 1

        return RunBatchSummary(
            total=len(self._records),
            allow_finish_count=allow_count,
            abstain_count=abstain_count,
            avg_card_count=avg_cards,
            avg_latency_ms=avg_latency,
            dim_score_means=dim_means,
            evidence_sufficiency_counts=sufficiency_counts,
        )


__all__ = [
    "LogMiner",
    "RunBatchSummary",
    "RunMetrics",
    "mine_run_log",
    "redact_log_record",
    "redact_pii",
]
