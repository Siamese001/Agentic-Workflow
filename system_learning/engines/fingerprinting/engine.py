"""FailureFingerprinter — deterministic hex digest for failure events."""

from __future__ import annotations

import hashlib
import json

from system_learning.engines.fingerprinting.types import FailureEvent, FailureFingerprint


class FailureFingerprinter:
    """Produces a deterministic fingerprint_hex for each FailureEvent."""

    def fingerprint(self, event: FailureEvent) -> FailureFingerprint:
        canonical = json.dumps(
            {
                "component": event.component,
                "error_code": event.error_code,
                "exc_type": event.exc_type,
                "symbols": sorted(event.symbols),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        hex_digest = hashlib.sha256(canonical.encode("ascii")).hexdigest()
        return FailureFingerprint(fingerprint_hex=hex_digest, source_event=event)
