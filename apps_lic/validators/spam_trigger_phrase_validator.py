"""Spam-trigger phrase validator for outreach messages.

W3-P8 of the apps_lic LinkedIn response-rate maximization plan
(Notion page 35327693-f55c-81e2-9b58-debeeb48bb35).

Scans outreach message text for any of the curated spam-trigger phrases
defined in ``apps_lic.config.spam_trigger_phrases`` and produces a
structured validation result HOP6 can consume.

Matching rules:
    - Case-insensitive (input text is lowercased for comparison).
    - Word-boundary aware: "circle back" matches "I'll circle back."
      but NOT "circled back onto the path". Implementation uses
      pre-compiled regex with ``\\b`` boundaries.
    - Each phrase match produces a single violation regardless of
      occurrence count (dedup per phrase), but the total-hit count is
      reported in the result.

Severity ladder:
    - ``critical`` category (false_urgency) → is_valid=False hard gate
    - ``high`` category (pushy_cta) → is_valid=False hard gate
    - ``medium`` category (corporate_cliche, generic_opener) →
      is_valid=False soft gate (HOP6 regenerates but logs telemetry)

Callers that want purely-advisory mode (log but don't reject) should
consume the ``hits`` list from the result and ignore ``is_valid``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Final, List, Mapping, Optional

from apps_lic.config.spam_trigger_phrases import (
    ALL_PHRASES,
    CATEGORY_SEVERITY,
    category_for_phrase,
)

# Critical + high categories hard-reject. Medium categories soft-reject.
_HARD_REJECT_SEVERITIES: Final[frozenset[str]] = frozenset({"critical", "high"})


@dataclass(frozen=True)
class SpamTriggerHit:
    """One detected spam-trigger phrase match."""

    phrase: str
    category: str
    severity: str
    occurrence_count: int


@dataclass(frozen=True)
class SpamTriggerValidationResult:
    """Result of a single spam-trigger validation scan.

    Attributes:
        is_valid: True when no hard-reject-severity hits were found.
        hits: Every matched phrase with its category + occurrence count.
            Sorted by (severity rank desc, category asc, phrase asc) for
            deterministic operator-facing output.
        total_hit_count: Sum of ``occurrence_count`` across all hits.
        reason: Human-readable reason string. Empty when is_valid=True.
    """

    is_valid: bool
    hits: List[SpamTriggerHit] = field(default_factory=list)
    total_hit_count: int = 0
    reason: str = ""


# Severity ranking for deterministic sort.
_SEVERITY_RANK: Final[Mapping[str, int]] = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}

# Pre-compile one word-boundary regex per phrase. Compiled at import
# time (one-time cost) so runtime validation is O(N_phrases * |text|).
# Phrases containing non-word characters (hyphens, apostrophes) are
# escaped correctly via ``re.escape``.
_PHRASE_PATTERNS: Final[tuple[tuple[str, re.Pattern[str], str, str], ...]] = tuple(
    (
        phrase,
        re.compile(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", re.IGNORECASE),
        category,
        CATEGORY_SEVERITY.get(category, "medium"),
    )
    for phrase, category in ALL_PHRASES
)


def validate_message_for_spam_triggers(text: str) -> SpamTriggerValidationResult:
    """Pure-function spam-trigger scan.

    Args:
        text: The outreach message body. ``None`` and empty strings
            are treated as valid (nothing to scan).

    Returns:
        ``SpamTriggerValidationResult`` with every field populated.
        Never raises.
    """
    if not text:
        return SpamTriggerValidationResult(is_valid=True)

    hits: list[SpamTriggerHit] = []
    total = 0
    hard_reject = False
    for phrase, pattern, category, severity in _PHRASE_PATTERNS:
        matches = pattern.findall(text)
        if not matches:
            continue
        count = len(matches)
        hits.append(
            SpamTriggerHit(
                phrase=phrase,
                category=category,
                severity=severity,
                occurrence_count=count,
            )
        )
        total += count
        if severity in _HARD_REJECT_SEVERITIES:
            hard_reject = True

    hits.sort(key=_hit_sort_key)

    if not hits:
        return SpamTriggerValidationResult(is_valid=True)

    reason = _build_reason(hits, total, hard_reject)
    return SpamTriggerValidationResult(
        is_valid=not hard_reject,
        hits=hits,
        total_hit_count=total,
        reason=reason,
    )


class SpamTriggerPhraseValidator:
    """Stateful wrapper for HOP6 wiring with telemetry emission."""

    def __init__(self, telemetry_bus: Optional[object] = None) -> None:
        self._telemetry_bus = telemetry_bus

    def validate(self, text: str) -> SpamTriggerValidationResult:
        result = validate_message_for_spam_triggers(text)
        if result.hits and self._telemetry_bus is not None:
            try:
                self._telemetry_bus.record(
                    "spam_trigger_hits",
                    {
                        "is_valid": result.is_valid,
                        "total_hits": result.total_hit_count,
                        "categories": _aggregate_by_category(result.hits),
                    },
                )
            except (AttributeError, TypeError, RuntimeError, ValueError, OSError):  # guardian: allow-log-and-swallow -- telemetry must never break validation
                pass
        return result


# ----------------------------------------------------------------------
# Internals
# ----------------------------------------------------------------------


def _hit_sort_key(hit: SpamTriggerHit) -> tuple[int, str, str]:
    return (_SEVERITY_RANK.get(hit.severity, 99), hit.category, hit.phrase)


def _build_reason(hits: list[SpamTriggerHit], total: int, hard_reject: bool) -> str:
    verb = "rejected" if hard_reject else "flagged"
    top = hits[0]
    tail = f" (+ {len(hits) - 1} more)" if len(hits) > 1 else ""
    return (
        f"Message {verb}: {total} spam-trigger hit(s). "
        f"Top: {top.phrase!r} ({top.category}, {top.severity}){tail}."
    )


def _aggregate_by_category(hits: list[SpamTriggerHit]) -> dict[str, int]:
    agg: dict[str, int] = {}
    for hit in hits:
        agg[hit.category] = agg.get(hit.category, 0) + hit.occurrence_count
    return agg


__all__ = [
    "SpamTriggerHit",
    "SpamTriggerPhraseValidator",
    "SpamTriggerValidationResult",
    "validate_message_for_spam_triggers",
]
