"""Surface Isolation Validator — Enforces single-surface mutation per activation window.

Ensures that only one surface can be mutated within a given activation window
to prevent cross-surface contamination and maintain isolation guarantees.
"""

from __future__ import annotations

import time
from typing import Dict, Optional, Set


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class SurfaceIsolationValidator:
    """Enforces single-surface mutation per activation window.

    Tracks active mutation surfaces and enforces that only one surface
    can be mutated within a given activation window. This prevents
    cross-surface contamination and maintains isolation guarantees.
    """

    # Activation window duration in seconds (default: 5 minutes)
    ACTIVATION_WINDOW_SECONDS = 300

    def __init__(self) -> None:
        """Initialize the surface isolation validator."""
        # Track active surfaces: surface_id -> activation_time
        self._active_surfaces: Dict[str, float] = {}
        # Track completed surfaces: surface_id -> completion_time (separate from active)
        self._completion_timestamps: Dict[str, float] = {}
        # Track surfaces that have been completed in current window (set for O(1) lookup)
        self._completed_surfaces: Set[str] = set()
        # Last window cleanup time
        self._last_cleanup = time.time()

    def can_mutate_surface(self, target_surface: str, authority_sensitivity: str = "MEDIUM") -> tuple[bool, str]:
        """Check if a surface can be mutated.

        Args:
            target_surface: The target surface identifier.
            authority_sensitivity: Authority sensitivity level (LOW/MEDIUM/HIGH).

        Returns:
            (can_mutate, reason) tuple
        """
        current_time = time.time()

        # Clean up expired windows
        self._cleanup_expired_windows(current_time)

        # Completed check is ALWAYS enforced — even HIGH authority cannot re-mutate a
        # surface already completed in the current activation window.
        if target_surface in self._completed_surfaces:
            return False, f"Surface {target_surface} already completed in current activation window"

        # HIGH authority sensitivity bypasses the single-active-surface constraint
        # (system-level changes that must proceed regardless of other active surfaces)
        if authority_sensitivity == "HIGH":
            if target_surface not in self._active_surfaces:
                self._active_surfaces[target_surface] = current_time
            return True, "HIGH authority sensitivity allows mutation"

        # If no active surfaces, allow mutation and track it
        if not self._active_surfaces:
            self._active_surfaces[target_surface] = current_time
            return True, "No active surfaces, mutation allowed"

        # Check if surface is already active in this window
        if target_surface in self._active_surfaces:
            return True, "Surface already active in current window"

        # Another surface is active — deny isolation violation
        active_surface = next(iter(self._active_surfaces))
        return False, f"Cannot mutate {target_surface}: surface {active_surface} is active in current window"

    def mark_surface_completed(self, target_surface: str) -> None:
        """Mark a surface as completed for the current activation window.

        Args:
            target_surface: The target surface identifier.
        """
        current_time = time.time()

        # Remove from active surfaces
        self._active_surfaces.pop(target_surface, None)

        # Record completion time for window expiry cleanup (separate dict)
        self._completion_timestamps[target_surface] = current_time

        # Mark as completed for this window
        self._completed_surfaces.add(target_surface)

    def reset_window(self) -> None:
        """Reset the activation window (for testing or manual override)."""
        self._active_surfaces.clear()
        self._completed_surfaces.clear()
        self._completion_timestamps.clear()
        self._last_cleanup = time.time()

    def get_active_surfaces(self) -> Set[str]:
        """Get the set of currently active surfaces.

        Returns:
            Set of active surface identifiers (excludes completion tracking keys).
        """
        self._cleanup_expired_windows(time.time())
        return set(self._active_surfaces.keys())

    def get_completed_surfaces(self) -> Set[str]:
        """Get the set of completed surfaces in current window.

        Returns:
            Set of completed surface identifiers.
        """
        self._cleanup_expired_windows(time.time())
        return self._completed_surfaces.copy()

    def _cleanup_expired_windows(self, current_time: float) -> None:
        """Clean up expired activation windows.

        Args:
            current_time: Current timestamp.
        """
        # Only cleanup if enough time has passed (avoid too frequent cleanup)
        if current_time - self._last_cleanup < 60:  # Cleanup at most once per minute
            return

        window_start = current_time - self.ACTIVATION_WINDOW_SECONDS

        # Expire stale active surfaces
        expired_active = [s for s, ts in self._active_surfaces.items() if ts < window_start]
        for s in expired_active:
            del self._active_surfaces[s]

        # Expire stale completed surfaces
        expired_completed = [s for s, ts in self._completion_timestamps.items() if ts < window_start]
        for s in expired_completed:
            del self._completion_timestamps[s]
            self._completed_surfaces.discard(s)

        self._last_cleanup = current_time

    def get_window_status(self) -> Dict[str, any]:
        """Get the current window status for debugging.

        Returns:
            Dictionary with window status information.
        """
        current_time = time.time()
        self._cleanup_expired_windows(current_time)

        return {
            "current_time": current_time,
            "active_surfaces": dict(self._active_surfaces),
            "completed_surfaces": list(self._completed_surfaces),
            "window_duration_seconds": self.ACTIVATION_WINDOW_SECONDS,
            "last_cleanup": self._last_cleanup,
        }


# Global instance for system-wide surface isolation
_surface_isolation_validator: Optional[SurfaceIsolationValidator] = None


def get_surface_isolation_validator() -> SurfaceIsolationValidator:
    """Get the global surface isolation validator instance.

    Returns:
        The global SurfaceIsolationValidator instance.
    """
    global _surface_isolation_validator
    if _surface_isolation_validator is None:
        _surface_isolation_validator = SurfaceIsolationValidator()
    return _surface_isolation_validator


def reset_surface_isolation_validator() -> None:
    """Reset the global surface isolation validator (for testing)."""
    global _surface_isolation_validator
    if _surface_isolation_validator is not None:
        _surface_isolation_validator.reset_window()
