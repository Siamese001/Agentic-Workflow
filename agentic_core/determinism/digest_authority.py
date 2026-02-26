from __future__ import annotations

import hashlib
import json
import threading
from typing import Any


class DuplicateDigestViolation(Exception):
    """Raised when a digest is emitted more than once in a single run."""

    pass


class _DigestAuthority:
    _LOCK: threading.Lock = threading.Lock()
    _INSTANCE: _DigestAuthority | None = None
    _emitted: bool = False

    def __init__(self) -> None:
        if self.__class__._INSTANCE is not None:
            raise RuntimeError("Cannot construct DigestAuthority directly. Use get_instance().")

    @classmethod
    def get_instance(cls) -> _DigestAuthority:
        with cls._LOCK:
            if cls._INSTANCE is None:
                cls._INSTANCE = cls()
        return cls._INSTANCE

    @classmethod
    def reset_for_testing(cls) -> None:
        """Resets the singleton state for isolated test runs."""
        with cls._LOCK:
            cls._INSTANCE = None
            cls._emitted = False

    def _canonical_json(self, data: Any) -> str:
        """Computes canonical JSON: sorted keys, UTF-8, no whitespace, 6dp floats."""

        class _FloatEncoder(json.JSONEncoder):
            def default(self, o: Any) -> Any:
                if isinstance(o, float):
                    return f"{o:.6f}"
                return super().default(o)

        return json.dumps(
            data,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
            cls=_FloatEncoder,
        )

    def compute_digest(
        self,
        *,
        trace_id: str,
        plan_hash: str,
        policy_hash: str,
        transcript_hash: str,
        config_surface_hash: str,
    ) -> str:
        """Computes the canonical SHA-256 digest from required components."""
        material = {
            "trace_id": trace_id,
            "plan_hash": plan_hash,
            "policy_hash": policy_hash,
            "transcript_hash": transcript_hash,
            "config_surface_hash": config_surface_hash,
        }
        canonical_string = self._canonical_json(material)
        return hashlib.sha256(canonical_string.encode("utf-8")).hexdigest()

    def emit_digest(self, digest: str, wave_number: int) -> str:
        """Emits the digest string, ensuring it happens only once per run."""
        with self._LOCK:
            if self._emitted:
                raise DuplicateDigestViolation(
                    "W<n>-DETERMINISM-DIGEST has already been emitted for this run."
                )
            self._emitted = True
            emission_string = f"W{wave_number}-DETERMINISM-DIGEST: {digest}"
            # In a real system, this would use a sovereign logger.
            # For now, printing to stdout is sufficient for evidence capture.
            print(emission_string)
            return emission_string


# Public API - singleton instance
digest_authority = _DigestAuthority.get_instance()
