"""
L2 Deterministic Providers — Replay Mode Enforcement.

Provides structural overrides for nondeterministic modules (time, random, uuid)
during replay mode execution. All providers derive deterministic state from a
trace_id, ensuring byte-identical replay across runs.

Layer: L2 Execution
Authority: May only be activated by ReplayGuardMixin during replay mode.
Invariant: One trace_id per process. Re-patching with a different trace_id is
           a hard error to prevent cross-trace contamination.
"""

from __future__ import annotations

import hashlib
import random as _random_module
import time as _time_module
import uuid as _uuid_module
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ---------------------------------------------------------------------------
# Module-level sentinel — prevents accidental re-patching with different trace
# ---------------------------------------------------------------------------
_ACTIVE_TRACE_ID: str | None = None
_PATCHED: bool = False

# Store originals so we can restore in tests
_ORIGINAL_TIME: float = _time_module.time
_ORIGINAL_SLEEP = _time_module.sleep
_ORIGINAL_RANDOM = _random_module.random
_ORIGINAL_RANDINT = _random_module.randint
_ORIGINAL_CHOICE = _random_module.choice
_ORIGINAL_UUID4 = _uuid_module.uuid4


class DeterministicPatchError(Exception):
    """Raised when attempting to re-patch with a different trace_id."""


class FixedTimeProvider:
    """Deterministic time provider for replay mode.

    Derives a stable base timestamp from trace_id via SHA-256.
    Advances monotonically via sleep() and advance() calls.
    """

    def __init__(self, trace_id: str) -> None:
        seed_bytes = hashlib.sha256(trace_id.encode("utf-8")).digest()
        self._base_time: float = float(int.from_bytes(seed_bytes[:8], byteorder="big") % 1_000_000_000)
        self._offset: float = 0.0

    def time(self) -> float:
        """Return deterministic timestamp."""
        return self._base_time + self._offset

    def sleep(self, seconds: float) -> None:
        """Advance virtual clock instead of blocking."""
        if seconds < 0:
            raise ValueError("sleep duration must be non-negative")
        self._offset += seconds

    def advance(self, seconds: float) -> None:
        """Manually advance virtual clock."""
        if seconds < 0:
            raise ValueError("advance duration must be non-negative")
        self._offset += seconds

    @property
    def current_offset(self) -> float:
        """Return accumulated offset for inspection."""
        return self._offset


class DeterministicRandomSource:
    """Deterministic random source for replay mode.

    Derives seed from trace_id via SHA-256, producing identical sequences
    for identical trace_ids across runs.
    """

    def __init__(self, trace_id: str) -> None:
        seed_bytes = hashlib.sha256(trace_id.encode("utf-8")).digest()
        seed_int = int.from_bytes(seed_bytes[:8], byteorder="big")
        self._rng = _random_module.Random(seed_int)

    def random(self) -> float:
        """Return deterministic float in [0.0, 1.0)."""
        return self._rng.random()

    def randint(self, a: int, b: int) -> int:
        """Return deterministic integer in [a, b]."""
        return self._rng.randint(a, b)

    def choice(self, seq: Any) -> Any:
        """Return deterministic choice from sequence."""
        return self._rng.choice(seq)

    def shuffle(self, seq: list) -> list:
        """Shuffle sequence deterministically in-place and return it."""
        self._rng.shuffle(seq)
        return seq


class DeterministicUUIDProvider:
    """Deterministic UUID4 provider for replay mode.

    Produces a monotonically incrementing sequence of UUIDs derived from
    trace_id, ensuring identical UUID sequences across replays.
    """

    def __init__(self, trace_id: str) -> None:
        seed_bytes = hashlib.sha256(f"{trace_id}-uuid".encode()).digest()
        self._base_int = int.from_bytes(seed_bytes[:16], byteorder="big")
        self._counter = 0

    def uuid4(self) -> _uuid_module.UUID:
        """Return deterministic UUID."""
        raw = (self._base_int + self._counter) & ((1 << 128) - 1)
        self._counter += 1
        # Set version=4 and variant bits per RFC 4122
        raw = (raw & ~(0xF << 76)) | (4 << 76)  # version 4
        raw = (raw & ~(0x3 << 62)) | (0x2 << 62)  # variant 10
        return _uuid_module.UUID(int=raw)


# ---------------------------------------------------------------------------
# Patching / Unpatching API
# ---------------------------------------------------------------------------


def patch_deterministic(trace_id: str) -> dict[str, Any]:
    """Install deterministic providers for the given trace_id.

    Returns a dict of provider instances for direct use.

    Raises DeterministicPatchError if already patched with a different trace_id.
    """
    global _ACTIVE_TRACE_ID, _PATCHED

    if _PATCHED:
        if _ACTIVE_TRACE_ID != trace_id:
            raise DeterministicPatchError(
                f"Already patched with trace_id={_ACTIVE_TRACE_ID!r}, "
                f"cannot re-patch with trace_id={trace_id!r}. "
                "One trace per process."
            )
        # Already patched with same trace_id — idempotent
        return _get_active_providers()

    time_provider = FixedTimeProvider(trace_id)
    random_source = DeterministicRandomSource(trace_id)
    uuid_provider = DeterministicUUIDProvider(trace_id)

    # Patch modules
    _time_module.time = time_provider.time  # type: ignore[assignment]
    _time_module.sleep = time_provider.sleep  # type: ignore[assignment]
    _random_module.random = random_source.random  # type: ignore[assignment]
    _random_module.randint = random_source.randint  # type: ignore[assignment]
    _random_module.choice = random_source.choice  # type: ignore[assignment]
    _uuid_module.uuid4 = uuid_provider.uuid4  # type: ignore[assignment]

    _ACTIVE_TRACE_ID = trace_id
    _PATCHED = True

    return {
        "time_provider": time_provider,
        "random_source": random_source,
        "uuid_provider": uuid_provider,
    }


def unpatch_deterministic() -> None:
    """Restore original nondeterministic modules.

    Safe to call even if not patched (no-op).
    Primarily used in tests.
    """
    global _ACTIVE_TRACE_ID, _PATCHED

    _time_module.time = _ORIGINAL_TIME  # type: ignore[assignment]
    _time_module.sleep = _ORIGINAL_SLEEP  # type: ignore[assignment]
    _random_module.random = _ORIGINAL_RANDOM  # type: ignore[assignment]
    _random_module.randint = _ORIGINAL_RANDINT  # type: ignore[assignment]
    _random_module.choice = _ORIGINAL_CHOICE  # type: ignore[assignment]
    _uuid_module.uuid4 = _ORIGINAL_UUID4  # type: ignore[assignment]

    _ACTIVE_TRACE_ID = None
    _PATCHED = False


def is_patched() -> bool:
    """Return True if deterministic providers are currently active."""
    return _PATCHED


def get_active_trace_id() -> str | None:
    """Return the trace_id of the active patch, or None."""
    return _ACTIVE_TRACE_ID


def _get_active_providers() -> dict[str, Any]:
    """Return dict of current provider instances (internal helper)."""
    return {
        "time_provider": _time_module.time,
        "random_source": _random_module.random,
        "uuid_provider": _uuid_module.uuid4,
    }
