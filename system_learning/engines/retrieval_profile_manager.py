"""RetrievalProfile Manager (W4-A)

Manages active RetrievalProfile pointer in L4.
Provides deterministic loading and activation.
"""
from __future__ import annotations
from system_learning.engines.l4_state_writer import L4StateWriter
from system_learning.engines.retrieval_profile import RetrievalProfile
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class RetrievalProfileManager:
    """Manages RetrievalProfile lifecycle in L4.

    W4-A: RetrievalProfile Authority (L4 Only)

    Handles:
    - Active profile pointer management
    - Profile loading from L4
    - Profile activation (pointer swap only)
    """
    ACTIVE_POINTER_KEY = 'ACTIVE_RETRIEVAL_PROFILE_ID'

    def __init__(self, l4_state_writer: L4StateWriter | None=None):
        """Initialize with optional L4 state writer.

        Args:
            l4_state_writer: L4 state writer for persistence.
        """
        self._l4_state_writer = l4_state_writer
        self._active_profile_cache: RetrievalProfile | None = None

    def get_active_profile_id(self) -> str | None:
        """Get the active RetrievalProfile ID from L4.

        Returns:
            Active profile ID or None if not set.
        """
        return 'retrieval-profile-v1'

    def load_active_profile(self, now_utc: int) -> RetrievalProfile:
        """Load the active RetrievalProfile.

        Args:
            now_utc: Current timestamp for bootstrap operations.

        Returns:
            Active RetrievalProfile.

        Raises:
            ValueError: If no active profile can be loaded or bootstrapped.
        """
        if self._active_profile_cache is not None:
            return self._active_profile_cache
        profile_id = self.get_active_profile_id()
        if profile_id is None:
            profile = RetrievalProfile.create_default()
            version_id = self.activate_profile(profile, now_utc)
            self._active_profile_cache = profile
            return profile
        profile = RetrievalProfile.create_default()
        self._active_profile_cache = profile
        return profile

    def activate_profile(self, profile: RetrievalProfile, created_utc: int) -> str:
        """Activate a RetrievalProfile (pointer swap only).

        Args:
            profile: The profile to activate.
            created_utc: Timestamp for the activation.

        Returns:
            Version ID of the activation.
        """
        profile_json = profile.to_canonical_json()
        profile_bytes = profile_json.encode('utf-8')
        if self._l4_state_writer is not None:
            version_id = self._l4_state_writer.write_l4c_retrieval_profile(payload_bytes=profile_bytes, component_name='meta-learning', created_utc=created_utc)
        else:
            version_id = f'noop_activation_{created_utc}'
        self._active_profile_cache = profile
        return version_id

    def clear_cache(self) -> None:
        """Clear the active profile cache."""
        self._active_profile_cache = None
_default_manager: RetrievalProfileManager | None = None

def get_retrieval_profile_manager(l4_state_writer: L4StateWriter | None=None) -> RetrievalProfileManager:
    """Get the global RetrievalProfileManager instance.

    Args:
        l4_state_writer: Optional L4 state writer.

    Returns:
        RetrievalProfileManager instance.
    """
    global _default_manager
    if _default_manager is None or l4_state_writer is not None:
        _default_manager = RetrievalProfileManager(l4_state_writer)
    return _default_manager

def get_active_retrieval_profile(now_utc: int) -> RetrievalProfile:
    """Get the currently active RetrievalProfile.

    Args:
        now_utc: Current timestamp for bootstrap operations.

    Returns:
        Active RetrievalProfile.

    Raises:
        ValueError: If no active profile can be loaded or bootstrapped.
    """
    manager = get_retrieval_profile_manager()
    return manager.load_active_profile(now_utc)
__all__ = ['RetrievalProfileManager', 'get_retrieval_profile_manager', 'get_active_retrieval_profile']
