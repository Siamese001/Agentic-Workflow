"""Drift Detector — Monitors C0 context hash for drift detection.

Alerts when C0 context changes between replays, indicating potential
drift in the embedding space that could affect decision consistency.

# guardian: allow-direct-prompt-compilation
"""

from __future__ import annotations

import hashlib
import logging

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    record_execution_trace,
)

record_execution_trace("drift_detector", "drift_detector_trace")


logger = logging.getLogger(__name__)


class DriftDetector:
    """Detects drift in C0 context hash between executions.

    Maintains a registry of C0 context hashes and alerts when
    the hash changes, indicating potential drift in the embedding space.
    """

    def __init__(self) -> None:
        """Initialize the drift detector."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "DriftDetector.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "DriftDetector.__init__", "p0_governance")
        self._context_registry: dict[str, str] = {}
        self._drift_alerts: dict[str, tuple[str, str]] = {}

    def register_context_hash(self, replay_key: str, c0_context_hash: str) -> bool:
        """Register a C0 context hash for a replay key.

        Args:
            replay_key: The replay key identifier.
            c0_context_hash: The C0 context hash.

        Returns:
            True if drift was detected, False otherwise.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L6_OBSERVABILITY,
            "DriftDetector.register_context_hash",
        )

        if replay_key in self._context_registry:
            old_hash = self._context_registry[replay_key]
            if old_hash != c0_context_hash:
                self._drift_alerts[replay_key] = (old_hash, c0_context_hash)
                _adg_score: float = 0.5
                try:
                    from pathlib import Path as _Path

                    from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile as _gbp

                    _root = _Path(__file__).resolve().parents[4]
                    _adg_score = _gbp(_Path(__file__).resolve(), _root).behavioral_score
                except (
                    ImportError,
                    AttributeError,
                    OSError,
                    RuntimeError,
                    TypeError,
                    ValueError,
                ) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
                    import logging

                    logging.getLogger(__name__).debug("drift_detector: Exception swallowed at L82: %s", e)
                # guardian: allow-direct-prompt-compilation
                logger.warning(
                    "C0 context drift detected for replay key %s: old_hash=%s..., "
                    "new_hash=%s... adg_behavioral_score=%.3f",
                    replay_key,
                    old_hash[:8],
                    c0_context_hash[:8],
                    _adg_score,
                )
                return True
        else:
            self._context_registry[replay_key] = c0_context_hash
        return False

    def get_drift_alert(self, replay_key: str) -> tuple[str, str] | None:
        """Get drift alert for a replay key.

        Args:
            replay_key: The replay key identifier.

        Returns:
            Tuple of (old_hash, new_hash) if drift detected, None otherwise.
        """
        return self._drift_alerts.get(replay_key)

    def has_drift(self, replay_key: str) -> bool:
        """Check if drift was detected for a replay key.

        Args:
            replay_key: The replay key identifier.

        Returns:
            True if drift detected, False otherwise.
        """
        return replay_key in self._drift_alerts

    def clear_drift_alert(self, replay_key: str) -> None:
        """Clear drift alert for a replay key.

        Args:
            replay_key: The replay key identifier.
        """
        self._drift_alerts.pop(replay_key, None)

    def get_all_drift_alerts(self) -> dict[str, tuple[str, str]]:
        """Get all drift alerts.

        Returns:
            Dictionary mapping replay keys to (old_hash, new_hash) tuples.
        """
        return self._drift_alerts.copy()

    def reset(self) -> None:
        """Reset the drift detector (for testing)."""
        self._context_registry.clear()
        self._drift_alerts.clear()

    def compute_c0_context_hash(self, c0_context: str) -> str:
        """Compute hash for C0 context.

        Args:
            c0_context: The C0 context string.

        Returns:
            SHA-256 hash of the C0 context.
        """
        return hashlib.sha256(c0_context.encode("utf-8", errors="replace")).hexdigest()

    def get_context_hash(self, replay_key: str) -> str | None:
        """Get the registered context hash for a replay key.

        Args:
            replay_key: The replay key identifier.

        Returns:
            The context hash if registered, None otherwise.
        """
        return self._context_registry.get(replay_key)


_drift_detector: DriftDetector | None = None


def get_drift_detector() -> DriftDetector:
    """Get the global drift detector instance.

    Returns:
        The global DriftDetector instance.
    """
    global _drift_detector
    if _drift_detector is None:
        _drift_detector = DriftDetector()
    return _drift_detector


def reset_drift_detector() -> None:
    """Reset the global drift detector (for testing)."""
    global _drift_detector
    if _drift_detector is not None:
        _drift_detector.reset()
