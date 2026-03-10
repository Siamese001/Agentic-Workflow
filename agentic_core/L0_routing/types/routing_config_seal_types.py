"""
Wave 5.3: Immutable Routing Config Seal.

Prevents mid-run routing config mutation by sealing the config
at run start with a canonical hash.  Any attempt to mutate the
config during execution raises RoutingConfigSealViolation.

Lives in L0 (routing types) — config is read at routing time.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

from agentic_core.utils.canonical_serializer_util import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    canonical_bytes,
)


class RoutingConfigSealViolation(RuntimeError):
    """Raised when routing config is mutated after sealing."""


@dataclass(frozen=True)
class RoutingConfigSeal:
    """Immutable seal over a routing configuration snapshot.

    Once sealed, the config hash must remain constant for the
    duration of the run.  Verification re-derives the hash and
    compares.
    """

    canonical_hash: str
    version: str
    sealed_at: str

    @staticmethod
    def create(
        *,
        config: dict,
        version: str,
    ) -> RoutingConfigSeal:
        """Seal a routing config snapshot."""
        sealed_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        ch = hashlib.sha256(canonical_bytes(config)).hexdigest()
        return RoutingConfigSeal(
            canonical_hash=ch,
            version=version,
            sealed_at=sealed_at,
        )

    def verify(self, config: dict) -> bool:
        """Verify config has not changed since sealing."""
        current = hashlib.sha256(canonical_bytes(config)).hexdigest()
        return current == self.canonical_hash


class SealedRoutingContext:
    """Context manager that enforces routing config immutability.

    Usage::

        ctx = SealedRoutingContext(config, version="1.0")
        ctx.verify_or_raise(config)  # ok
        config["new_key"] = "value"
        ctx.verify_or_raise(config)  # raises
    """

    def __init__(self, config: dict, *, version: str) -> None:
        self._seal = RoutingConfigSeal.create(config=config, version=version)

    @property
    def seal(self) -> RoutingConfigSeal:
        return self._seal

    def verify_or_raise(self, config: dict) -> None:
        """Raise if config has been mutated since sealing."""
        if not self._seal.verify(config):
            raise RoutingConfigSealViolation(
                "Routing config mutated after sealing. "
                f"Expected hash: "
                f"{self._seal.canonical_hash[:16]}... "
                f"Sealed at: {self._seal.sealed_at}"
            )
