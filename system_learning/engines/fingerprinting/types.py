"""FailureFingerprinter types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FailureEvent:
    exc_type: str
    error_code: str
    component: str
    symbols: list[str]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class FailureFingerprint:
    fingerprint_hex: str
    source_event: FailureEvent
    canonical_bytes: bytes = b""

    @property
    def fingerprint_sha256(self) -> str:
        return self.fingerprint_hex
