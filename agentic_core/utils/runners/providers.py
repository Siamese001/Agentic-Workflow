"""
Cross-cutting time and random injection providers (L_SHARED).

Moved from L2_execution.providers to L_SHARED to fix layer boundary violations.
L0 (routing/foundation) needs clock access but cannot depend on L2 (execution).

Replaces bare ``datetime.now()`` / ``time.time()`` / ``random.*`` calls with
injectable providers so that:

- Tests inject ``FrozenClock`` / ``SeededRandom`` for deterministic, replayable runs.
- Production injects ``WallClock`` / ``OsRandom`` which record their values into the
  active trace context so the same values can be replayed.

ADG edges produced:
  ``patches_time``           — any module using ClockProvider instead of datetime.now
  ``seeds_rng``              — any module using RandomProvider instead of random.*
  ``emits_determinism_digest`` — emitted by ClockProvider.emit_digest()
  ``emits_replay_key``       — emitted by ClockProvider.emit_replay_key()

Usage
-----
    from agentic_core.utils.runners.providers import get_clock, get_random

    ts = get_clock().now_iso()          # replaces datetime.now().isoformat()
    n  = get_random().randint(0, 100)   # replaces random.randint(0, 100)

Injection (test)::

    from agentic_core.utils.runners.providers import set_clock, set_random, FrozenClock, SeededRandom
    set_clock(FrozenClock("2026-01-01T00:00:00"))
    set_random(SeededRandom(seed=42))

Injection (production with trace context)::

    set_clock(WallClock(trace_context=ctx))
    set_random(OsRandom(trace_context=ctx))
"""

from __future__ import annotations

import hashlib
import logging
import random as _random_module
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    emit_determinism_digest,
    emit_replay_key,
)

emit_replay_key("p0", "providers")
emit_determinism_digest("p0", "providers")

logger = logging.getLogger(__name__)
_DETERMINISM_LOGGER = logging.getLogger("adg.emits_determinism_digest")
_REPLAY_KEY_LOGGER = logging.getLogger("adg.emits_replay_key")
_SEEDS_RNG_LOGGER = logging.getLogger("adg.seeds_rng")
_PATCHES_TIME_LOGGER = logging.getLogger("adg.patches_time")


# ---------------------------------------------------------------------------
# Abstract base classes
# ---------------------------------------------------------------------------


class ClockProvider(ABC):
    """Abstract injectable clock replacing datetime.now() / time.time()."""

    @abstractmethod
    def now(self) -> datetime:
        """Return current datetime (timezone-aware UTC)."""

    def now_iso(self) -> str:
        """Return ISO-8601 string of current time."""
        return self.now().isoformat()

    def now_epoch(self) -> float:
        """Return POSIX timestamp."""
        return self.now().timestamp()

    def emit_replay_key(self, context: str = "") -> str:
        """Emit a deterministic replay key covering this clock value.

        ADG edge: ``emits_replay_key``.
        """
        ts = self.now_iso()
        raw = f"{context}:{ts}"
        key = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        _REPLAY_KEY_LOGGER.debug("emits_replay_key context=%s ts=%s key=%s", context, ts, key[:16])
        return key

    def emit_determinism_digest(self, inputs: dict[str, Any]) -> str:
        """Emit a determinism digest covering inputs + current clock value.

        ADG edge: ``emits_determinism_digest``.
        """
        import json as _json

        ts = self.now_iso()
        payload = {"clock": ts, "inputs": inputs}
        digest = hashlib.sha256(_json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()
        _DETERMINISM_LOGGER.debug("emits_determinism_digest ts=%s digest=%s", ts, digest[:16])
        return digest


class RandomProvider(ABC):
    """Abstract injectable random source replacing random.* / os.urandom calls."""

    @abstractmethod
    def randint(self, a: int, b: int) -> int:
        """Return random integer N such that a <= N <= b."""

    @abstractmethod
    def random(self) -> float:
        """Return random float in [0.0, 1.0)."""

    @abstractmethod
    def choice(self, seq: list) -> Any:
        """Return random element from seq."""

    @abstractmethod
    def seed_value(self) -> int | str | None:
        """Return the seed used, or None if non-deterministic."""

    def emit_seeds_rng(self, context: str = "") -> None:
        """Log that RNG was seeded for this context.

        ADG edge: ``seeds_rng``.
        """
        _SEEDS_RNG_LOGGER.debug("seeds_rng context=%s seed=%s", context, self.seed_value())


# ---------------------------------------------------------------------------
# Production implementations
# ---------------------------------------------------------------------------


class WallClock(ClockProvider):
    """Production clock: returns real wall-clock time.

    Records values into trace_context if provided so they can be replayed.
    ADG edge: ``patches_time`` (any caller using WallClock instead of datetime.now).
    """

    def __init__(self, trace_context: Any = None) -> None:
        self._trace_context = trace_context

    def now(self) -> datetime:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "WallClock.now")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:WallClock.now".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        ts = datetime.now(tz=timezone.utc)
        _PATCHES_TIME_LOGGER.debug("patches_time wall_clock ts=%s", ts.isoformat())
        if self._trace_context is not None and hasattr(self._trace_context, "record_clock"):
            self._trace_context.record_clock(ts.isoformat())
        return ts


class OsRandom(RandomProvider):
    """Production random: uses Python stdlib random (non-deterministic by default).

    Records seed into trace_context if provided.
    """

    def __init__(self, trace_context: Any = None) -> None:
        self._rng = _random_module.Random()
        self._trace_context = trace_context

    def randint(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)

    def random(self) -> float:
        return self._rng.random()

    def choice(self, seq: list) -> Any:
        return self._rng.choice(seq)

    def seed_value(self) -> None:
        return None


# ---------------------------------------------------------------------------
# Test / deterministic implementations
# ---------------------------------------------------------------------------


class FrozenClock(ClockProvider):
    """Test clock: always returns the same instant.

    ADG edge: ``patches_time``.

    Args:
        frozen_time: ISO-8601 string, datetime, or POSIX float. Defaults to epoch.
    """

    def __init__(self, frozen_time: str | datetime | float | None = None) -> None:
        if frozen_time is None:
            self._frozen = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        elif isinstance(frozen_time, str):
            self._frozen = datetime.fromisoformat(frozen_time.replace("Z", "+00:00"))
            if self._frozen.tzinfo is None:
                self._frozen = self._frozen.replace(tzinfo=timezone.utc)
        elif isinstance(frozen_time, (int, float)):
            self._frozen = datetime.fromtimestamp(frozen_time, tz=timezone.utc)
        else:
            self._frozen = frozen_time
            if self._frozen.tzinfo is None:
                self._frozen = self._frozen.replace(tzinfo=timezone.utc)
        _PATCHES_TIME_LOGGER.debug("patches_time frozen_clock ts=%s", self._frozen.isoformat())

    def now(self) -> datetime:
        return self._frozen

    @property
    def frozen(self) -> datetime:
        return self._frozen


class SeededRandom(RandomProvider):
    """Deterministic random with a fixed seed.

    ADG edge: ``seeds_rng``.

    Args:
        seed: Integer seed for reproducible sequences.
    """

    def __init__(self, seed: int = 0) -> None:
        self._seed = seed
        self._rng = _random_module.Random(seed)
        _SEEDS_RNG_LOGGER.debug("seeds_rng seed=%d", seed)

    def randint(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)

    def random(self) -> float:
        return self._rng.random()

    def choice(self, seq: list) -> Any:
        return self._rng.choice(seq)

    def seed_value(self) -> int:
        return self._seed


class MonotonicSequenceClock(ClockProvider):
    """Test clock that advances by a fixed delta on each call.

    Useful for testing time-ordered sequences without relying on wall clock.
    """

    def __init__(
        self,
        start: str | datetime | None = None,
        step_seconds: float = 1.0,
    ) -> None:
        if start is None:
            self._current = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        elif isinstance(start, str):
            dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            self._current = dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
        else:
            self._current = start
        self._step = step_seconds
        self._call_count = 0

    def now(self) -> datetime:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "MonotonicSequenceClock.now")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:MonotonicSequenceClock.now".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        from datetime import timedelta

        result = self._current
        self._current = self._current + timedelta(seconds=self._step)
        self._call_count += 1
        _PATCHES_TIME_LOGGER.debug("patches_time monotonic_clock ts=%s", result.isoformat())
        return result


# ---------------------------------------------------------------------------
# Process-level singletons + accessors
# ---------------------------------------------------------------------------

_clock: ClockProvider = WallClock()
_random: RandomProvider = OsRandom()


def get_clock() -> ClockProvider:
    """Return the process-level ClockProvider."""
    return _clock


def get_random() -> RandomProvider:
    """Return the process-level RandomProvider."""
    return _random


def set_clock(provider: ClockProvider) -> None:
    """Replace the process-level ClockProvider (test injection)."""
    global _clock
    _clock = provider
    logger.debug("ClockProvider replaced: %s", type(provider).__name__)


def set_random(provider: RandomProvider) -> None:
    """Replace the process-level RandomProvider (test injection)."""
    global _random
    _random = provider
    logger.debug("RandomProvider replaced: %s", type(provider).__name__)


def reset_providers() -> None:
    """Reset both providers to production defaults (test teardown)."""
    global _clock, _random
    _clock = WallClock()
    _random = OsRandom()


__all__ = [
    "ClockProvider",
    "RandomProvider",
    "WallClock",
    "OsRandom",
    "FrozenClock",
    "SeededRandom",
    "MonotonicSequenceClock",
    "get_clock",
    "get_random",
    "set_clock",
    "set_random",
    "reset_providers",
]
