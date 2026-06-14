"""Anthropic prompt-cache usage telemetry — closed-loop verification (P4).

Observability-only. Reads provider-reported prompt-cache usage from an
Anthropic ``usage`` object/dict and records per-call cache hit/miss so that
"caching is low" becomes a *measured, alarmed* signal instead of a guess.

This module is NEVER on a hot path that affects generation: extraction and
recording are best-effort and fail-soft; a telemetry failure must never change
a response. It mirrors the house pattern in
``agentic_core/L2_execution/enforcement/_thinking_token_ledger.py`` (thread-safe
in-process ledger, process-wide default instance, test-reset helper).

Anthropic ``usage`` fields consumed:
  - ``input_tokens``                  — non-cached input tokens
  - ``output_tokens``                 — generated tokens
  - ``cache_read_input_tokens``       — tokens served FROM cache (the win, ~10% cost)
  - ``cache_creation_input_tokens``   — tokens written TO cache (the cost, ~125%)

Two failure modes this layer makes visible:
  - *Silent invalidator* — an identical logical prefix that keeps paying cache
    writes but never yields a read (below-floor marker, TTL eviction, or a
    non-frozen prefix). Caught here via :meth:`CacheUsageLedger.is_silent_invalidator`.
  - *Prefix drift* — the cacheable prefix silently changing every call (a
    datetime/uuid leak). Caught by the sibling P5 guard in
    ``anthropic_cache_determinism.py`` (different fingerprint each call).

Reference:
  https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
"""

from __future__ import annotations

import hashlib
import logging
import threading
from dataclasses import dataclass
from typing import Any

Logger = logging.getLogger(__name__)

# Calls sharing an identical logical-prefix fingerprint after which a persistent
# ``cache_read == 0`` (despite cache writes) is treated as a silent invalidator.
# The first write is always a legitimate cold miss; ``3`` gives two subsequent
# calls that SHOULD have read the cache before we alarm.
DEFAULT_SILENT_INVALIDATOR_MIN_CALLS = 3

_FINGERPRINT_LEN = 32


def prefix_fingerprint(text: str) -> str:
    """Stable SHA-256 fingerprint (hex, truncated) of a logical-prefix string.

    Used as the ledger key so calls sharing an identical prefix collapse onto
    one history. Encoding is fixed UTF-8 so the fingerprint is reproducible.
    """
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:_FINGERPRINT_LEN]


@dataclass(frozen=True)
class CacheUsage:
    """Provider-reported prompt-cache token usage for a single response."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0

    @property
    def cacheable_input_tokens(self) -> int:
        """Tokens that touched the cache subsystem (read + freshly written)."""
        return self.cache_read_input_tokens + self.cache_creation_input_tokens

    @property
    def cache_hit_ratio(self) -> float:
        """Fraction of cacheable input tokens served from cache (0.0..1.0).

        Returns 0.0 when nothing was cacheable (denominator zero) — an honest
        "no signal", not a hit.
        """
        denom = self.cacheable_input_tokens
        if denom <= 0:
            return 0.0
        return self.cache_read_input_tokens / denom

    @property
    def is_read_hit(self) -> bool:
        return self.cache_read_input_tokens > 0

    @property
    def is_write_only(self) -> bool:
        """A write with no read — normal on the first call, suspicious if it persists."""
        return self.cache_creation_input_tokens > 0 and self.cache_read_input_tokens == 0


def _coerce_int(value: Any) -> int:
    """Coerce a possibly-None/str usage field to a non-negative int."""
    if value is None:
        return 0
    try:
        ivalue = int(value)
    except (TypeError, ValueError):
        return 0
    return ivalue if ivalue > 0 else 0


def extract_cache_usage(usage: Any) -> CacheUsage:
    """Duck-typed extraction of cache usage from an Anthropic ``usage`` object.

    Accepts the SDK ``Usage`` object (attribute access), a plain ``dict``, or
    ``None``. Missing/None/negative fields coerce to 0 so callers never crash on
    a provider that omits cache fields (e.g. OpenAI / stub responses).
    """
    if usage is None:
        return CacheUsage()

    def _get(name: str) -> Any:
        if isinstance(usage, dict):
            return usage.get(name)
        return getattr(usage, name, None)

    return CacheUsage(
        input_tokens=_coerce_int(_get("input_tokens")),
        output_tokens=_coerce_int(_get("output_tokens")),
        cache_read_input_tokens=_coerce_int(_get("cache_read_input_tokens")),
        cache_creation_input_tokens=_coerce_int(_get("cache_creation_input_tokens")),
    )


@dataclass(frozen=True)
class CacheUsageRecord:
    """A single recorded cache-usage observation, keyed by prefix fingerprint."""

    fingerprint: str
    usage: CacheUsage
    label: str = ""
    trace_id: str | None = None
    model: str | None = None


class CacheUsageLedger:
    """Thread-safe in-process ledger of per-call cache usage.

    Observability-only — never on a hot path where it would affect generation.
    A process-wide default instance is exposed via :func:`get_default_cache_ledger`
    but callers can construct their own for test isolation.
    """

    def __init__(self) -> None:
        self._records: list[CacheUsageRecord] = []
        self._lock = threading.Lock()

    def record(
        self,
        fingerprint: str,
        usage: CacheUsage,
        *,
        label: str = "",
        trace_id: str | None = None,
        model: str | None = None,
    ) -> CacheUsageRecord:
        """Append a single observation and return the stored record."""
        record = CacheUsageRecord(
            fingerprint=fingerprint,
            usage=usage,
            label=label,
            trace_id=trace_id,
            model=model,
        )
        with self._lock:
            self._records.append(record)
        return record

    def records_for(self, fingerprint: str) -> list[CacheUsageRecord]:
        with self._lock:
            return [r for r in self._records if r.fingerprint == fingerprint]

    def all_records(self) -> list[CacheUsageRecord]:
        with self._lock:
            return list(self._records)

    def is_silent_invalidator(
        self,
        fingerprint: str,
        *,
        min_calls: int = DEFAULT_SILENT_INVALIDATOR_MIN_CALLS,
    ) -> bool:
        """True when an identical-prefix history keeps writing but never reads.

        Fires only when ALL hold:
          - ``>= min_calls`` records share the fingerprint,
          - total ``cache_read_input_tokens == 0`` across them, and
          - total ``cache_creation_input_tokens > 0`` (a write DID happen, so a
            read should have followed — that is the silent invalidation).

        A single first-call write (read=0, creation>0) is NOT an alarm; that is
        a normal cold miss, which is why ``min_calls`` defaults to 3.
        """
        records = self.records_for(fingerprint)
        if len(records) < min_calls:
            return False
        total_read = sum(r.usage.cache_read_input_tokens for r in records)
        total_creation = sum(r.usage.cache_creation_input_tokens for r in records)
        return total_read == 0 and total_creation > 0

    def hit_ratio_for(self, fingerprint: str) -> float:
        """Aggregate ``cache_read / cacheable`` ratio across a fingerprint's history."""
        records = self.records_for(fingerprint)
        total_read = sum(r.usage.cache_read_input_tokens for r in records)
        total_cacheable = sum(r.usage.cacheable_input_tokens for r in records)
        if total_cacheable <= 0:
            return 0.0
        return total_read / total_cacheable

    def clear(self) -> None:
        """Drop all records. Intended for tests and long-running process resets."""
        with self._lock:
            self._records.clear()


_DEFAULT_LEDGER: CacheUsageLedger | None = None


def get_default_cache_ledger() -> CacheUsageLedger:
    """Return the process-wide cache-usage ledger (lazily instantiated)."""
    global _DEFAULT_LEDGER
    if _DEFAULT_LEDGER is None:
        _DEFAULT_LEDGER = CacheUsageLedger()
    return _DEFAULT_LEDGER


def reset_default_cache_ledger() -> None:
    """Test helper — replace the default ledger with a fresh empty one."""
    global _DEFAULT_LEDGER
    _DEFAULT_LEDGER = CacheUsageLedger()


def record_cache_usage(
    usage: Any,
    *,
    fingerprint: str,
    label: str = "",
    trace_id: str | None = None,
    model: str | None = None,
    ledger: CacheUsageLedger | None = None,
    alarm: bool = True,
    min_calls: int = DEFAULT_SILENT_INVALIDATOR_MIN_CALLS,
) -> CacheUsage:
    """Extract, record, and (optionally) alarm on cache usage for one response.

    Returns the extracted :class:`CacheUsage`. ``usage`` may be an SDK object, a
    dict, a pre-extracted :class:`CacheUsage`, or ``None``. Per-call telemetry is
    emitted at DEBUG; a silent-invalidator alarm is emitted at WARNING when the
    fingerprint's history trips :meth:`CacheUsageLedger.is_silent_invalidator`.
    """
    cache_usage = usage if isinstance(usage, CacheUsage) else extract_cache_usage(usage)
    target = ledger or get_default_cache_ledger()
    target.record(fingerprint, cache_usage, label=label, trace_id=trace_id, model=model)

    Logger.debug(
        "cache_usage label=%s fp=%s read=%d creation=%d input=%d hit_ratio=%.3f",
        label,
        fingerprint,
        cache_usage.cache_read_input_tokens,
        cache_usage.cache_creation_input_tokens,
        cache_usage.input_tokens,
        cache_usage.cache_hit_ratio,
    )

    if alarm and target.is_silent_invalidator(fingerprint, min_calls=min_calls):
        Logger.warning(
            "SILENT_CACHE_INVALIDATOR label=%s fp=%s: %d calls share this prefix, "
            "cache_read stayed 0 while cache_creation kept billing — the cached "
            "prefix is written every call but never read (below-floor marker, TTL "
            "eviction, or a non-frozen prefix). Investigate before trusting cache savings.",
            label,
            fingerprint,
            len(target.records_for(fingerprint)),
        )

    return cache_usage


__all__ = [
    "CacheUsage",
    "CacheUsageLedger",
    "CacheUsageRecord",
    "DEFAULT_SILENT_INVALIDATOR_MIN_CALLS",
    "extract_cache_usage",
    "get_default_cache_ledger",
    "prefix_fingerprint",
    "record_cache_usage",
    "reset_default_cache_ledger",
]
