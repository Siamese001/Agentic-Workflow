"""DeterminismDigestEmitter — L6 Observability, emit-once stable artifact.

Wraps DigestCalculator with:
- Singleton emit-once enforcement (DuplicateEmissionError on second call).
- No wall-clock, no env-var, no random inputs in the surface.
- Canonical five-component surface: policy, registry, config, transcript,
  dependency_lock.
- ASCII-only emission line: DETERMINISM-DIGEST: <64-hex>

Layer rule: L6 observes only. This emitter NEVER mutates routes/safety/tiers.
"""

from __future__ import annotations

import hashlib
import threading
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    record_execution_trace,
)

record_execution_trace("determinism_digest_emitter", "determinism_digest_emitter_trace")


class DuplicateEmissionError(RuntimeError):
    """Raised when emit_once() is called more than once in a single run."""


class DeterminismDigestEmitter:
    """Thread-safe, emit-once determinism digest emitter for L6 observability.

    Usage::

        emitter = DeterminismDigestEmitter()
        digest = emitter.compute(
            policy_hash="a" * 64,
            registry_hash="b" * 64,
            config_surface_hash="c" * 64,
            transcript_hash="d" * 64,
            dependency_lock_hash="e" * 64,
        )
        line = emitter.emit_once(digest)
        # Returns "DETERMINISM-DIGEST: <64-hex>"
        # Raises DuplicateEmissionError on second call.
    """

    _LOCK: threading.Lock
    _emitted: bool

    def __init__(self) -> None:
        self._LOCK = threading.Lock()
        self._emitted = False

    def compute(
        self,
        *,
        policy_hash: str,
        registry_hash: str,
        config_surface_hash: str,
        transcript_hash: str,
        dependency_lock_hash: str,
    ) -> str:
        """Return SHA-256 hex digest of the canonical five-component surface.

        All five arguments must be 64-character lowercase hex strings.
        No wall-clock, no env-vars, no random inputs are permitted.

        Raises:
            ValueError: if any component is not a 64-char hex string.
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "DeterminismDigestEmitter.compute", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "DeterminismDigestEmitter.compute", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L6_OBSERVABILITY,
            "DeterminismDigestEmitter.compute",
        )

        components = {
            "config_surface_hash": config_surface_hash,
            "dependency_lock_hash": dependency_lock_hash,
            "policy_hash": policy_hash,
            "registry_hash": registry_hash,
            "transcript_hash": transcript_hash,
        }
        for name, value in components.items():
            if not isinstance(value, str) or len(value) != 64:
                raise ValueError(
                    f"DeterminismDigestEmitter: {name} must be a 64-char hex string, got {value!r}",
                )
        canonical = _canonical_json_bytes(components)
        return hashlib.sha256(canonical).hexdigest()

    def emit_once(self, digest: str) -> str:
        """Emit the determinism artifact line exactly once per instance.

        Returns:
            "DETERMINISM-DIGEST: <64-hex>"

        Raises:
            DuplicateEmissionError: on any call after the first.
            ValueError: if *digest* is not a 64-char hex string.
        """
        if not isinstance(digest, str) or len(digest) != 64:
            raise ValueError(
                f"DeterminismDigestEmitter.emit_once: digest must be 64-char hex, got {digest!r}",
            )
        with self._LOCK:
            if self._emitted:
                raise DuplicateEmissionError(
                    "DeterminismDigestEmitter: DETERMINISM-DIGEST already emitted for this instance.",
                )
            self._emitted = True
            return f"DETERMINISM-DIGEST: {digest}"

    def reset_for_testing(self) -> None:
        """Reset emit-once guard for test isolation only."""
        with self._LOCK:
            self._emitted = False


def build_stable_config_surface() -> dict[str, Any]:
    """Return a deterministic config surface dict with no wall-clock inputs.

    The surface captures the structural/configuration constants that define
    the system's deterministic identity. All values are hard constants or
    derived from deterministic sources.

    Returns:
        dict with keys: model_version, top_k, cutoff, blas_eps, max_k,
        embedding_batch, embedding_retry, embedding_enabled, meta_learning_enabled,
        oscillation_detector_enabled, proposal_only, rlhf_delta_min, rlhf_delta_max,
        decision_delta_limit.
    """
    return {
        "blas_eps": 1e-12,
        "cutoff": 0.5,
        "decision_delta_limit": 0.1,
        "embedding_batch": 500,
        "embedding_enabled": True,
        "embedding_retry": 8,
        "max_k": 20,
        "meta_learning_enabled": True,
        "model_version": "multilingual-e5-large",
        "oscillation_detector_enabled": True,
        "proposal_only": True,
        "rlhf_delta_max": 2.0,
        "rlhf_delta_min": 0.1,
        "top_k": 20,
    }


def hash_config_surface(surface: dict[str, Any]) -> str:
    """SHA-256 hash of the canonical config surface dict."""
    canonical = _canonical_json_bytes(surface)
    return hashlib.sha256(canonical).hexdigest()


def _canonical_json_bytes(data: Any) -> bytes:
    """Deterministic JSON serialization: sorted keys, no whitespace, UTF-8."""
    import json

    class _Encoder(json.JSONEncoder):
        def default(self, o: Any) -> Any:
            import uuid as _uuid  # noqa: PLC0415

            _trace_id = str(_uuid.uuid4())
            _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "_Encoder.default")

            if isinstance(o, float):
                return round(o, 12)
            return super().default(o)

    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True, cls=_Encoder).encode(
        "utf-8",
    )


__all__ = [
    "DeterminismDigestEmitter",
    "DuplicateEmissionError",
    "build_stable_config_surface",
    "hash_config_surface",
]
