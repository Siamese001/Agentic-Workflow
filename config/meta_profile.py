"""
Config meta profile module.

Provides user profile management, configuration snapshots, and meta-profile
functionality for the agentic system including user preferences, capabilities,
and contextual information.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
import logging
import json
import uuid

logger = logging.getLogger(__name__)


class ProfileType(str, Enum):
    """Types of user profiles."""

    INDIVIDUAL = "individual"
    ORGANIZATION = "organization"
    SYSTEM = "system"
    GUEST = "guest"


class CapabilityLevel(str, Enum):
    """User capability levels."""

    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    ADMIN = "admin"


@dataclass
class UserPreferences:
    """User preferences and settings."""

    preferred_models: List[str] = field(default_factory=list)
    language: str = "en"
    timezone: str = "UTC"
    notification_settings: Dict[str, bool] = field(default_factory=dict)
    privacy_settings: Dict[str, bool] = field(default_factory=dict)
    ui_preferences: Dict[str, Any] = field(default_factory=dict)
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserProfile:
    """Comprehensive user profile."""

    user_id: str
    profile_type: ProfileType = ProfileType.INDIVIDUAL
    capability_level: CapabilityLevel = CapabilityLevel.BASIC
    name: str = ""
    email: str = ""
    organization: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    preferences: UserPreferences = field(default_factory=UserPreferences)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    is_active: bool = True

    def update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self.updated_at = datetime.now(UTC)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "user_id": self.user_id,
            "profile_type": self.profile_type.value,
            "capability_level": self.capability_level.value,
            "name": self.name,
            "email": self.email,
            "organization": self.organization,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "preferences": {
                "preferred_models": self.preferences.preferred_models,
                "language": self.preferences.language,
                "timezone": self.preferences.timezone,
                "notification_settings": self.preferences.notification_settings,
                "privacy_settings": self.preferences.privacy_settings,
                "ui_preferences": self.preferences.ui_preferences,
                "custom_settings": self.preferences.custom_settings
            },
            "metadata": self.metadata,
            "tags": self.tags,
            "is_active": self.is_active
        }


@dataclass
class MetaProfileSnapshot:
    """Snapshot of meta-profile state for configuration management."""

    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    profile_id: Optional[str] = None
    configuration_data: Dict[str, Any] = field(default_factory=dict)
    environment_context: Dict[str, Any] = field(default_factory=dict)
    system_state: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    checksum: Optional[str] = None

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """Initialize from optional data dictionary."""
        if data:
            self.configuration_data = data.get("configuration", {})
            self.environment_context = data.get("environment", {})
            self.system_state = data.get("system_state", {})
            self.profile_id = data.get("profile_id")

    def calculate_checksum(self) -> str:
        """Calculate checksum for configuration integrity."""
        import hashlib

        config_json = json.dumps(self.configuration_data, sort_keys=True)
        env_json = json.dumps(self.environment_context, sort_keys=True)

        combined = f"{config_json}{env_json}{self.version}"
        self.checksum = hashlib.sha256(combined.encode()).hexdigest()[:16]

        return self.checksum

    def is_valid(self) -> bool:
        """Check if snapshot is valid and consistent."""
        if not self.configuration_data:
            return False

        calculated_checksum = self.calculate_checksum()
        return self.checksum == calculated_checksum

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp.isoformat(),
            "profile_id": self.profile_id,
            "configuration_data": self.configuration_data,
            "environment_context": self.environment_context,
            "system_state": self.system_state,
            "version": self.version,
            "checksum": self.checksum
        }


class MetaProfileManager:
    """Manages user profiles and meta-profile snapshots."""

    def __init__(self, max_profiles: int = 1000, max_snapshots: int = 5000):
        """
        Initialize meta-profile manager.

        Args:
            max_profiles: Maximum number of profiles to keep in memory
            max_snapshots: Maximum number of snapshots to keep in memory
        """
        self.profiles: Dict[str, UserProfile] = {}
        self.snapshots: List[MetaProfileSnapshot] = []
        self.max_profiles = max_profiles
        self.max_snapshots = max_snapshots

    def create_profile(
        self,
        user_id: str,
        profile_type: ProfileType = ProfileType.INDIVIDUAL,
        capability_level: CapabilityLevel = CapabilityLevel.BASIC,
        name: str = "",
        email: str = "",
        organization: Optional[str] = None,
        preferences: Optional[UserPreferences] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> UserProfile:
        """
        Create a new user profile.

        Args:
            user_id: Unique user identifier
            profile_type: Type of profile
            capability_level: User capability level
            name: User display name
            email: User email address
            organization: Organization affiliation
            preferences: User preferences
            metadata: Additional metadata
            tags: Profile tags

        Returns:
            Created user profile
        """
        if user_id in self.profiles:
            raise ValueError(f"Profile already exists for user: {user_id}")

        profile = UserProfile(
            user_id=user_id,
            profile_type=profile_type,
            capability_level=capability_level,
            name=name,
            email=email,
            organization=organization,
            preferences=preferences or UserPreferences(),
            metadata=metadata or {},
            tags=tags or []
        )

        self.profiles[user_id] = profile
        logger.info(f"Created profile for user: {user_id}")

        return profile

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID."""
        return self.profiles.get(user_id)

    def update_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Optional[UserProfile]:
        """
        Update user profile.

        Args:
            user_id: User identifier
            updates: Dictionary of updates to apply

        Returns:
            Updated profile or None if not found
        """
        if user_id not in self.profiles:
            logger.warning(f"Profile not found for user: {user_id}")
            return None

        profile = self.profiles[user_id]

        # Apply updates
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
            elif hasattr(profile.preferences, key):
                setattr(profile.preferences, key, value)

        profile.update_timestamp()
        logger.info(f"Updated profile for user: {user_id}")

        return profile

    def delete_profile(self, user_id: str) -> bool:
        """Delete user profile."""
        if user_id in self.profiles:
            del self.profiles[user_id]
            logger.info(f"Deleted profile for user: {user_id}")
            return True
        return False

    def create_snapshot(
        self,
        profile_id: Optional[str] = None,
        configuration_data: Optional[Dict[str, Any]] = None,
        environment_context: Optional[Dict[str, Any]] = None,
        system_state: Optional[Dict[str, Any]] = None
    ) -> MetaProfileSnapshot:
        """
        Create a meta-profile snapshot.

        Args:
            profile_id: Associated profile ID
            configuration_data: Configuration data
            environment_context: Environment context
            system_state: System state information

        Returns:
            Created snapshot
        """
        snapshot = MetaProfileSnapshot()
        snapshot.profile_id = profile_id
        snapshot.configuration_data = configuration_data or {}
        snapshot.environment_context = environment_context or {}
        snapshot.system_state = system_state or {}
        snapshot.calculate_checksum()

        self.snapshots.append(snapshot)

        # Maintain max size
        if len(self.snapshots) > self.max_snapshots:
            self.snapshots = self.snapshots[-int(self.max_snapshots * 0.8):]

        logger.info(f"Created snapshot: {snapshot.snapshot_id}")
        return snapshot

    def get_snapshots(
        self,
        profile_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[MetaProfileSnapshot]:
        """
        Get snapshots with optional filtering.

        Args:
            profile_id: Filter by profile ID
            limit: Maximum number of snapshots to return

        Returns:
            Filtered list of snapshots
        """
        filtered = self.snapshots

        if profile_id:
            filtered = [s for s in filtered if s.profile_id == profile_id]

        # Sort by timestamp (newest first)
        filtered.sort(key=lambda s: s.timestamp, reverse=True)

        if limit:
            filtered = filtered[:limit]

        return filtered

    def get_latest_snapshot(
        self,
        profile_id: Optional[str] = None
    ) -> Optional[MetaProfileSnapshot]:
        """Get the latest snapshot for a profile."""
        snapshots = self.get_snapshots(profile_id, limit=1)
        return snapshots[0] if snapshots else None

    def validate_snapshot(self, snapshot: MetaProfileSnapshot) -> bool:
        """Validate snapshot integrity."""
        return snapshot.is_valid()

    def get_statistics(self) -> Dict[str, Any]:
        """Get profile and snapshot statistics."""
        total_profiles = len(self.profiles)
        total_snapshots = len(self.snapshots)

        # Profile type distribution
        profile_types: dict[str, int] = {}
        for profile in self.profiles.values():
            profile_type = profile.profile_type.value
            profile_types[profile_type] = profile_types.get(profile_type, 0) + 1

        # Capability level distribution
        capability_levels: dict[str, int] = {}
        for profile in self.profiles.values():
            level = profile.capability_level.value
            capability_levels[level] = capability_levels.get(level, 0) + 1

        # Active profiles
        active_profiles = sum(1 for p in self.profiles.values() if p.is_active)

        return {
            "total_profiles": total_profiles,
            "active_profiles": active_profiles,
            "total_snapshots": total_snapshots,
            "profile_type_distribution": profile_types,
            "capability_level_distribution": capability_levels
        }


# Global meta-profile manager instance
_meta_profile_manager = MetaProfileManager()


def get_meta_profile_manager() -> MetaProfileManager:
    """Get the global meta-profile manager instance."""
    return _meta_profile_manager


def create_user_profile(
    user_id: str,
    profile_type: ProfileType = ProfileType.INDIVIDUAL,
    capability_level: CapabilityLevel = CapabilityLevel.BASIC,
    name: str = "",
    email: str = "",
    organization: Optional[str] = None,
    preferences: Optional[UserPreferences] = None,
    metadata: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None
) -> UserProfile:
    """Create a user profile using the global manager."""
    return _meta_profile_manager.create_profile(
        user_id=user_id,
        profile_type=profile_type,
        capability_level=capability_level,
        name=name,
        email=email,
        organization=organization,
        preferences=preferences,
        metadata=metadata,
        tags=tags
    )


def get_user_profile(user_id: str) -> Optional[UserProfile]:
    """Get user profile using the global manager."""
    return _meta_profile_manager.get_profile(user_id)


def update_user_profile(
    user_id: str,
    updates: Dict[str, Any]
) -> Optional[UserProfile]:
    """Update user profile using the global manager."""
    return _meta_profile_manager.update_profile(user_id, updates)


def create_configuration_snapshot(
    profile_id: Optional[str] = None,
    configuration_data: Optional[Dict[str, Any]] = None,
    environment_context: Optional[Dict[str, Any]] = None,
    system_state: Optional[Dict[str, Any]] = None
) -> MetaProfileSnapshot:
    """Create a configuration snapshot using the global manager."""
    return _meta_profile_manager.create_snapshot(
        profile_id=profile_id,
        configuration_data=configuration_data,
        environment_context=environment_context,
        system_state=system_state
    )


__all__ = [
    "ProfileType",
    "CapabilityLevel",
    "UserPreferences",
    "UserProfile",
    "MetaProfileSnapshot",
    "MetaProfileManager",
    "get_meta_profile_manager",
    "create_user_profile",
    "get_user_profile",
    "update_user_profile",
    "create_configuration_snapshot"
]





