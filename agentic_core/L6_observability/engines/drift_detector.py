"""Drift Detector — Monitors C0 context hash for drift detection.

Alerts when C0 context changes between replays, indicating potential
drift in the embedding space that could affect decision consistency.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Dict, Optional, Tuple

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)


class DriftDetector:
    """Detects drift in C0 context hash between executions.

    Maintains a registry of C0 context hashes and alerts when
    the hash changes, indicating potential drift in the embedding space.
    """

    def __init__(self) -> None:
        """Initialize the drift detector."""
        # Registry of context hashes by key
        self._context_registry: Dict[str, str] = {}
        # Registry of drift alerts
        self._drift_alerts: Dict[str, Tuple[str, str]] = {}  # key -> (old_hash, new_hash)

    def register_context_hash(self, replay_key: str, c0_context_hash: str) -> bool:
        """Register a C0 context hash for a replay key.

        Args:
            replay_key: The replay key identifier.
            c0_context_hash: The C0 context hash.

        Returns:
            True if drift was detected, False otherwise.
        """
        if replay_key in self._context_registry:
            old_hash = self._context_registry[replay_key]
            if old_hash != c0_context_hash:
                # Drift detected
                self._drift_alerts[replay_key] = (old_hash, c0_context_hash)
                logger.warning(
                    f"C0 context drift detected for replay key {replay_key}: "
                    f"old_hash={old_hash[:8]}..., new_hash={c0_context_hash[:8]}..."
                )
                return True
        else:
            # First registration
            self._context_registry[replay_key] = c0_context_hash

        return False

    def get_drift_alert(self, replay_key: str) -> Optional[Tuple[str, str]]:
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

    def get_all_drift_alerts(self) -> Dict[str, Tuple[str, str]]:
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

    def get_context_hash(self, replay_key: str) -> Optional[str]:
        """Get the registered context hash for a replay key.

        Args:
            replay_key: The replay key identifier.

        Returns:
            The context hash if registered, None otherwise.
        """
        return self._context_registry.get(replay_key)


# Global instance for system-wide drift detection
_drift_detector: Optional[DriftDetector] = None


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
