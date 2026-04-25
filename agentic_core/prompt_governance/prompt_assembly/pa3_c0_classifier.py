"""PA.3 C0 Retrieved-Content Classifier.

Implements the four classifier actions from the spec — PASS, STRIP,
QUARANTINE, REJECT — with a per-chunk record carrying detected patterns,
disposition, safe-residue hash, and quarantine reason.

Retrieved content is **data, never instruction**. Hidden directives must be
either stripped (when factual residue can survive) or quarantined (when the
chunk is too poisoned to keep).
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping, Sequence


class C0Disposition(str, Enum):
    """One of four dispositions per spec §PA.3."""

    PASS = "PASS"
    STRIP = "STRIP"
    QUARANTINE = "QUARANTINE"
    REJECT = "REJECT"


# Pattern → category map. Patterns are case-insensitive substrings or regexes
# applied to the lowercased chunk text. The presence of any high-severity
# pattern (e.g. fake system header, embedded tool-use instruction) escalates
# disposition from STRIP to QUARANTINE.
_HIGH_SEVERITY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("FAKE_SYSTEM_HEADER", re.compile(r"^\s*system\s*:", re.IGNORECASE | re.MULTILINE)),
    ("FAKE_DEVELOPER_HEADER", re.compile(r"^\s*developer\s*:", re.IGNORECASE | re.MULTILINE)),
    ("HIDDEN_HTML_INSTRUCTION", re.compile(r"<!--\s*(?:system|instruction|prompt)\b", re.IGNORECASE)),
    ("EMBEDDED_TOOL_USE", re.compile(r"\b(?:use|invoke|call)\s+tool\s+[a-z_]+", re.IGNORECASE)),
    ("CREDENTIAL_HARVEST", re.compile(r"(?:use|reveal)\s+(?:any|the)\s+credentials", re.IGNORECASE)),
    ("MALICIOUS_URL", re.compile(r"https?://[^\s]+(?:\.onion|\.exec|/\.\./)", re.IGNORECASE)),
)

_MEDIUM_SEVERITY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "IGNORE_INSTRUCTIONS",
        re.compile(r"\b(?:ignore|disregard|forget|override)\s+(?:\w+\s+){0,3}instructions\b", re.IGNORECASE),
    ),
    ("ROLE_OVERRIDE", re.compile(r"you\s+are\s+now\s+(?:an?\s+)?unfiltered", re.IGNORECASE)),
    ("POLICY_OVERRIDE", re.compile(r"(?:bypass|disregard)\s+(?:the\s+)?policy", re.IGNORECASE)),
    ("PROMPT_LEAK", re.compile(r"repeat\s+(?:the\s+)?(?:words|text|prompt)\s+above", re.IGNORECASE)),
    (
        "TREAT_AS_SYSTEM",
        re.compile(r"treat\s+this\s+(?:retrieved\s+)?(?:page|content)\s+as\s+system", re.IGNORECASE),
    ),
)


@dataclass(frozen=True)
class C0ChunkRecord:
    """Per-chunk classifier record (spec §PA.3 'Security record')."""

    source_id: str
    span_id: str
    detected_patterns: tuple[str, ...]
    disposition: C0Disposition
    safe_residue_hash: str
    quarantine_reason: str = ""
    safe_residue: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "span_id": self.span_id,
            "detected_patterns": list(self.detected_patterns),
            "disposition": self.disposition.value,
            "safe_residue_hash": self.safe_residue_hash,
            "quarantine_reason": self.quarantine_reason,
        }


@dataclass(frozen=True)
class C0ClassifierResult:
    """Aggregated classifier output across all C0 chunks."""

    records: tuple[C0ChunkRecord, ...]
    pass_count: int
    strip_count: int
    quarantine_count: int
    reject_count: int
    safe_chunks: tuple[C0ChunkRecord, ...] = field(default_factory=tuple)

    @property
    def total(self) -> int:
        return self.pass_count + self.strip_count + self.quarantine_count + self.reject_count


def _hash_residue(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _detect(text: str, patterns: Iterable[tuple[str, re.Pattern[str]]]) -> list[str]:
    hits: list[str] = []
    for name, regex in patterns:
        if regex.search(text):
            hits.append(name)
    return hits


def _strip(text: str, patterns: Iterable[tuple[str, re.Pattern[str]]]) -> str:
    out = text
    for _name, regex in patterns:
        out = regex.sub("", out)
    return out.strip()


def classify_c0_chunk(
    *,
    source_id: str,
    span_id: str,
    text: str,
    safe_min_chars: int = 16,
) -> C0ChunkRecord:
    """Classify a single retrieved chunk.

    Decision tree:
      * No patterns detected → ``PASS``.
      * Only medium-severity patterns → ``STRIP`` (sanitize, keep residue).
      * Any high-severity pattern → ``QUARANTINE``.
      * After STRIP, if residue is shorter than ``safe_min_chars`` → ``REJECT``
        (the chunk was almost entirely instruction).
    """
    high_hits = _detect(text, _HIGH_SEVERITY_PATTERNS)
    medium_hits = _detect(text, _MEDIUM_SEVERITY_PATTERNS)

    all_hits = tuple(sorted(set(high_hits + medium_hits)))

    if not all_hits:
        residue = text.strip()
        return C0ChunkRecord(
            source_id=source_id,
            span_id=span_id,
            detected_patterns=(),
            disposition=C0Disposition.PASS,
            safe_residue=residue,
            safe_residue_hash=_hash_residue(residue),
        )

    if high_hits:
        return C0ChunkRecord(
            source_id=source_id,
            span_id=span_id,
            detected_patterns=all_hits,
            disposition=C0Disposition.QUARANTINE,
            safe_residue="",
            safe_residue_hash=_hash_residue(""),
            quarantine_reason="high_severity_pattern:" + ",".join(high_hits),
        )

    # Medium-only → STRIP and re-evaluate residue length.
    residue = _strip(text, _MEDIUM_SEVERITY_PATTERNS)
    if len(residue) < safe_min_chars:
        return C0ChunkRecord(
            source_id=source_id,
            span_id=span_id,
            detected_patterns=all_hits,
            disposition=C0Disposition.REJECT,
            safe_residue="",
            safe_residue_hash=_hash_residue(""),
            quarantine_reason="post_strip_residue_below_min_chars",
        )
    return C0ChunkRecord(
        source_id=source_id,
        span_id=span_id,
        detected_patterns=all_hits,
        disposition=C0Disposition.STRIP,
        safe_residue=residue,
        safe_residue_hash=_hash_residue(residue),
    )


def classify_c0_chunks(chunks: Sequence[Mapping[str, str]]) -> C0ClassifierResult:
    """Classify a sequence of chunks.

    Each item must provide ``source_id``, ``span_id`` and ``text``.
    """
    records: list[C0ChunkRecord] = []
    for chunk in chunks:
        records.append(
            classify_c0_chunk(
                source_id=str(chunk.get("source_id", "")),
                span_id=str(chunk.get("span_id", "")),
                text=str(chunk.get("text", "")),
            )
        )
    pass_count = sum(1 for r in records if r.disposition is C0Disposition.PASS)
    strip_count = sum(1 for r in records if r.disposition is C0Disposition.STRIP)
    quarantine_count = sum(1 for r in records if r.disposition is C0Disposition.QUARANTINE)
    reject_count = sum(1 for r in records if r.disposition is C0Disposition.REJECT)
    safe = tuple(r for r in records if r.disposition in {C0Disposition.PASS, C0Disposition.STRIP})
    return C0ClassifierResult(
        records=tuple(records),
        pass_count=pass_count,
        strip_count=strip_count,
        quarantine_count=quarantine_count,
        reject_count=reject_count,
        safe_chunks=safe,
    )


__all__ = [
    "C0ChunkRecord",
    "C0ClassifierResult",
    "C0Disposition",
    "classify_c0_chunk",
    "classify_c0_chunks",
]
