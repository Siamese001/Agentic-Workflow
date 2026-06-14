"""Tier-1 prefix determinism guard (P5).

The cacheable Tier-1 block (tools + system prompt) MUST be byte-identical for a
given logical-input key, or every call silently writes a fresh cache entry and
never reads it — the cache "works" yet ``cache_read`` stays 0. This guard hashes
the Tier-1 block per logical key and warns when the hash drifts across identical
logical inputs, mechanically catching ``datetime.now()`` / ``uuid`` / session-id
interpolation leaking into what should be a frozen prefix.

Complement to the P4 telemetry in ``anthropic_cache_telemetry.py``: P4 catches
"identical prefix but no reads" (eviction / below-floor marker); P5 catches
"prefix silently changes" (a determinism leak), which P4 alone cannot see
because a drifting prefix produces a different fingerprint every call.

Observability-only and fail-soft — never raises into a render/generation path.
"""

from __future__ import annotations

import logging
import re
import threading

from agentic_core.knowledge.retrieval.anthropic_cache_telemetry import prefix_fingerprint

Logger = logging.getLogger(__name__)

# Patterns that, in a would-be-frozen Tier-1 prefix, almost certainly mean a
# non-deterministic value leaked in (and will silently invalidate the cache).
_VOLATILE_PATTERNS: tuple[tuple[str, "re.Pattern[str]"], ...] = (
    ("iso_timestamp", re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")),
    (
        "uuid",
        re.compile(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
        ),
    ),
    ("epoch_seconds", re.compile(r"\b1[0-9]{9}\b")),
    ("session_id", re.compile(r"session[_-]?id\s*[=:]", re.IGNORECASE)),
)


def find_nondeterministic_tokens(text: str) -> list[str]:
    """Return labels of volatile patterns found in a would-be-frozen prefix.

    A static belt-and-suspenders check: a clean Tier-1 block returns ``[]``. It
    does not replace the hash-drift guard (which catches values the regex set
    misses) — it makes determinism violations legible in logs and tests.
    """
    if not text:
        return []
    return [label for label, pattern in _VOLATILE_PATTERNS if pattern.search(text)]


class DeterminismGuard:
    """Detects when a Tier-1 prefix changes across identical logical inputs.

    Remembers the first fingerprint seen per logical key and warns when a later
    call presents a different fingerprint for the same key. Thread-safe;
    observability-only (never raises into a render/generation path).
    """

    def __init__(self) -> None:
        self._seen: dict[str, str] = {}
        self._lock = threading.Lock()

    def check(self, logical_key: str, tier1_text: str) -> bool:
        """Record/compare the Tier-1 fingerprint for ``logical_key``.

        Returns ``True`` when the prefix is stable (first sighting, or identical
        to the prior sighting). Returns ``False`` and logs a WARNING when the
        prefix drifted for an identical logical key — the silent-invalidation
        signal.
        """
        fingerprint = prefix_fingerprint(tier1_text)
        with self._lock:
            prior = self._seen.get(logical_key)
            if prior is None:
                self._seen[logical_key] = fingerprint
                return True
            if prior == fingerprint:
                return True
            # Drift: keep the first (canonical) fingerprint; report the change.
            drift_tokens = find_nondeterministic_tokens(tier1_text)
        Logger.warning(
            "TIER1_PREFIX_DRIFT logical_key=%s: cacheable prefix changed across "
            "identical logical inputs (was %s, now %s)%s. The system/tools prefix "
            "is not frozen — every call silently rewrites the cache and never reads it.",
            logical_key,
            prior,
            fingerprint,
            f"; volatile tokens: {drift_tokens}" if drift_tokens else "",
        )
        return False

    def fingerprint_for(self, logical_key: str) -> str | None:
        with self._lock:
            return self._seen.get(logical_key)

    def clear(self) -> None:
        with self._lock:
            self._seen.clear()


_DEFAULT_GUARD: DeterminismGuard | None = None


def get_default_determinism_guard() -> DeterminismGuard:
    """Return the process-wide determinism guard (lazily instantiated)."""
    global _DEFAULT_GUARD
    if _DEFAULT_GUARD is None:
        _DEFAULT_GUARD = DeterminismGuard()
    return _DEFAULT_GUARD


def reset_default_determinism_guard() -> None:
    """Test helper — replace the default guard with a fresh empty one."""
    global _DEFAULT_GUARD
    _DEFAULT_GUARD = DeterminismGuard()


__all__ = [
    "DeterminismGuard",
    "find_nondeterministic_tokens",
    "get_default_determinism_guard",
    "prefix_fingerprint",
    "reset_default_determinism_guard",
]
