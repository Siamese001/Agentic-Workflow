"""Prod → golden curation adapter (W2.3).

Closes the "virtuous feedback loop" called out by Google Cloud: production
failures / novel interactions are anonymized, annotated with an expected
outcome, and added to ``data/eval/golden/``.

Invariants:
  - Observer posture only; never mutates production data.
  - Every emitted candidate has ``gold_outcome: "pending"`` and ``gold_score:
    null`` until a human rater annotates.
  - Deterministic anonymization: same input trace → same redacted output.
  - Content-addressed item IDs so duplicates are rejected by the queue.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Deny-list patterns for deterministic anonymization. Expanded in follow-up
# work; kept intentionally conservative here to avoid false-negative PII leaks.
_REDACTION_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"sk-[A-Za-z0-9]{16,}"), "<API_KEY>"),
    (re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]+"), "Bearer <TOKEN>"),
    (re.compile(r"\b[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}\b"), "<EMAIL>"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "<SSN>"),
    (re.compile(r"\b(?:\d[ -]*?){13,19}\b"), "<CARD>"),
)


@dataclass(frozen=True, slots=True)
class CurationCandidate:
    item_id: str
    source_trace_id: str
    rubric_family: str          # rag | governance | security
    rubric_id: str
    query: str
    context: str
    answer: str | None
    gold_score: None
    gold_outcome: str
    created_at: str
    notes: str = ""


def _redact(text: str) -> str:
    out = text
    for pattern, replacement in _REDACTION_PATTERNS:
        out = pattern.sub(replacement, out)
    return out


def _deterministic_id(trace_id: str, rubric_id: str) -> str:
    digest = hashlib.sha256(f"{trace_id}|{rubric_id}".encode("utf-8")).hexdigest()[:12]
    return f"curated-{rubric_id}-{digest}"


def curate_trace(
    trace: dict[str, Any],
    rubric_family: str,
    rubric_id: str,
    now_iso: str,
    notes: str = "",
) -> CurationCandidate:
    """Build a pending golden-dataset candidate from a single execution trace."""
    trace_id = str(trace.get("trace_id", "unknown"))
    return CurationCandidate(
        item_id=_deterministic_id(trace_id, rubric_id),
        source_trace_id=trace_id,
        rubric_family=rubric_family,
        rubric_id=rubric_id,
        query=_redact(str(trace.get("query", ""))),
        context=_redact(str(trace.get("context", ""))),
        answer=_redact(str(trace.get("answer", ""))) if trace.get("answer") is not None else None,
        gold_score=None,
        gold_outcome="pending",
        created_at=now_iso,
        notes=notes,
    )


def write_candidate(candidate: CurationCandidate, golden_root: Path) -> Path:
    """Write the candidate to ``<golden_root>/<family>/<rubric>/<item>.json``.

    Idempotent: re-writing the same candidate produces the same bytes.
    """
    target_dir = golden_root / candidate.rubric_family / candidate.rubric_id
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{candidate.item_id}.json"
    payload = {
        "item_id": candidate.item_id,
        "source_trace_id": candidate.source_trace_id,
        "rubric_id": candidate.rubric_id,
        "query": candidate.query,
        "context": candidate.context,
        "answer": candidate.answer,
        "human_labels": [],
        "gold_score": candidate.gold_score,
        "gold_outcome": candidate.gold_outcome,
        "created_at": candidate.created_at,
        "notes": candidate.notes,
    }
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
    logger.info("curated candidate written: %s", path)
    return path
