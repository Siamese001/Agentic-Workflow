"""RetrievalProfile Manager (W4-A)

Manages active RetrievalProfile pointer in L4.
Provides deterministic loading and activation.
"""

from __future__ import annotations

import json
from typing import Optional

from system_learning.engines.l4_state_writer import L4StateWriter
from system_learning.engines.retrieval_profile import RetrievalProfile


class RetrievalProfileManager:
    """Manages RetrievalProfile lifecycle in L4.
    
    W4-A: RetrievalProfile Authority (L4 Only)
    
    Handles:
    - Active profile pointer management
    - Profile loading from L4
    - Profile activation (pointer swap only)
    """
    
    # Active profile pointer key
    ACTIVE_POINTER_KEY = "ACTIVE_RETRIEVAL_PROFILE_ID"
    
    def __init__(self, l4_state_writer: Optional[L4StateWriter] = None):
        """Initialize with optional L4 state writer.
        
        Args:
            l4_state_writer: L4 state writer for persistence.
        """
        self._l4_state_writer = l4_state_writer
        self._active_profile_cache: Optional[RetrievalProfile] = None
    
    def get_active_profile_id(self) -> Optional[str]:
        """Get the active RetrievalProfile ID from L4.
        
        Returns:
            Active profile ID or None if not set.
        """
        # For now, return the default profile ID
        # In a full implementation, this would read from L4
        return "retrieval-profile-v1"
    
    def load_active_profile(self) -> RetrievalProfile:
        """Load the active RetrievalProfile.
        
        Returns:
            Active RetrievalProfile.
            
        Raises:
            ValueError: If no active profile is found.
        """
        if self._active_profile_cache is not None:
            return self._active_profile_cache
        
        # Get active profile ID
        profile_id = self.get_active_profile_id()
        if profile_id is None:
            raise ValueError("No active RetrievalProfile found")
        
        # For now, return the default profile
        # In a full implementation, this would load from L4
        profile = RetrievalProfile.create_default()
        
        # Cache the profile
        self._active_profile_cache = profile
        
        return profile
    
    def activate_profile(
        self, 
        profile: RetrievalProfile, 
        created_utc: int
    ) -> str:
        """Activate a RetrievalProfile (pointer swap only).
        
        Args:
            profile: The profile to activate.
            created_utc: Timestamp for the activation.
            
        Returns:
            Version ID of the activation.
        """
        # Serialize the profile
        profile_json = profile.to_canonical_json()
        profile_bytes = profile_json.encode('utf-8')
        
        # Write to L4 if available
        if self._l4_state_writer is not None:
            version_id = self._l4_state_writer.write_l4c_retrieval_profile(
                payload_bytes=profile_bytes,
                component_name="meta-learning",
                created_utc=created_utc,
            )
        else:
            version_id = f"noop_activation_{created_utc}"
        
        # Update active pointer (in a full implementation, this would be in L4)
        # For now, just update cache
        self._active_profile_cache = profile
        
        return version_id
    
    def clear_cache(self) -> None:
        """Clear the active profile cache."""
        self._active_profile_cache = None


# Global instance for backward compatibility
_default_manager: Optional[RetrievalProfileManager] = None


def get_retrieval_profile_manager(
    l4_state_writer: Optional[L4StateWriter] = None
) -> RetrievalProfileManager:
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


def get_active_retrieval_profile() -> RetrievalProfile:
    """Get the currently active RetrievalProfile.
    
    Returns:
        Active RetrievalProfile.
        
    Raises:
        ValueError: If no active profile is found.
    """
    manager = get_retrieval_profile_manager()
    return manager.load_active_profile()


# Export public interface
__all__ = [
    'RetrievalProfileManager',
    'get_retrieval_profile_manager',
    'get_active_retrieval_profile',
]
