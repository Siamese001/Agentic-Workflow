"""FailureFingerprinter — deterministic hex digest for failure events."""

from __future__ import annotations

import hashlib
import json
import re

from system_learning.engines.fingerprinting.types import FailureEvent, FailureFingerprint

_LINE_NUM_RE = re.compile(r":\d+$")
_PATH_SEP_RE = re.compile(r"[\\/]+")


def _normalize_symbol(sym: str) -> str:
    """Strip line numbers and normalize path separators."""
    sym = _LINE_NUM_RE.sub("", sym)
    sym = _PATH_SEP_RE.sub("/", sym)
    return sym


def _normalize_component(component: str) -> str:
    """Strip absolute path prefix and line numbers from component."""
    component = _PATH_SEP_RE.sub("/", component)
    parts = component.split("/")
    return parts[-1] if parts else component


class FailureFingerprinter:
    """Produces a deterministic fingerprint_hex for each FailureEvent."""

    def fingerprint(self, event: FailureEvent) -> FailureFingerprint:
        if event is None or not isinstance(event, FailureEvent):
            raise TypeError(f"event must be FailureEvent, got {type(event).__name__}")
        if not event.exc_type:
            raise ValueError("event.exc_type must not be empty")

        normalized_symbols = sorted(_normalize_symbol(s) for s in event.symbols)
        normalized_component = _normalize_component(event.component)

        canonical = json.dumps(
            {
                "component": normalized_component,
                "error_code": event.error_code,
                "exc_type": event.exc_type,
                "symbols": normalized_symbols,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        canonical_bytes = canonical.encode("ascii")
        hex_digest = hashlib.sha256(canonical_bytes).hexdigest()
        return FailureFingerprint(
            fingerprint_hex=hex_digest, source_event=event, canonical_bytes=canonical_bytes
        )
