"""Semantic Versioning and Rollback for Prompts.

Phase 4 - Pillar 13: Prompt Governance (CMS)
Enables safe prompt tuning by non-engineers with version control and rollback.

Features:
- Semantic versioning (major.minor.patch)
- Environment tags (dev, staging, prod)
- Rollback capability
- Change tracking
- Deployment safety
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class VersionTag(Enum):
    """Version environment tags."""

    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


@dataclass
class PromptVersion:
    """Versioned prompt template."""

    version_id: str
    template_id: str
    version: str
    content: str
    tag: VersionTag
    created_at: float
    created_by: str
    change_notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version_id": self.version_id,
            "template_id": self.template_id,
            "version": self.version,
            "content": self.content,
            "tag": self.tag.value,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "change_notes": self.change_notes,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PromptVersion":
        """Create from dictionary."""
        return cls(
            version_id=data["version_id"],
            template_id=data["template_id"],
            version=data["version"],
            content=data["content"],
            tag=VersionTag(data["tag"]),
            created_at=data["created_at"],
            created_by=data["created_by"],
            change_notes=data.get("change_notes", ""),
            metadata=data.get("metadata", {}),
        )


class PromptVersionManager:
    """Manages prompt versions with semantic versioning.

    Features:
    - Semantic versioning (major.minor.patch)
    - Environment tagging
    - Version history
    - Rollback support
    - Safe deployment
    """

    def __init__(self, enable_logging: bool = True):
        """Initialize version manager.

        Args:
            enable_logging: Enable logging
        """
        self.enable_logging = enable_logging

        self._versions: dict[str, list[PromptVersion]] = {}
        self._tagged_versions: dict[str, dict[VersionTag, PromptVersion]] = {}

        if self.enable_logging:
            logger.info("prompt_version_manager_initialized")

    def create_version(
        self,
        template: PromptTemplate,
        created_by: str,
        change_notes: str = "",
        tag: VersionTag = VersionTag.DEV,
    ) -> PromptVersion:
        """Create a new version of a prompt.

        Args:
            template: Prompt template
            created_by: Creator identifier
            change_notes: Notes about changes
            tag: Environment tag

        Returns:
            PromptVersion
        """
        template_id = template.template_id

        # Get next version number
        next_version = self._get_next_version(template_id, template.version)

        # Create version
        version = PromptVersion(
            version_id=f"{template_id}_{next_version}_{int(time.time())}",
            template_id=template_id,
            version=next_version,
            content=template.content,
            tag=tag,
            created_at=time.time(),
            created_by=created_by,
            change_notes=change_notes,
            metadata=template.metadata.copy(),
        )

        # Store version
        if template_id not in self._versions:
            self._versions[template_id] = []
        self._versions[template_id].append(version)

        # Update tagged version
        if template_id not in self._tagged_versions:
            self._tagged_versions[template_id] = {}
        self._tagged_versions[template_id][tag] = version

        if self.enable_logging:
            logger.info(
                "version_created",
                extra={
                    "template_id": template_id,
                    "version": next_version,
                    "tag": tag.value,
                },
            )

        return version

    def promote_version(
        self,
        template_id: str,
        version: str,
        to_tag: VersionTag,
    ) -> PromptVersion | None:
        """Promote a version to a different environment.

        Args:
            template_id: Template identifier
            version: Version to promote
            to_tag: Target environment tag

        Returns:
            PromptVersion or None
        """
        # Find version
        versions = self._versions.get(template_id, [])
        target_version = None

        for v in versions:
            if v.version == version:
                target_version = v
                break

        if not target_version:
            return None

        # Update tag
        if template_id not in self._tagged_versions:
            self._tagged_versions[template_id] = {}

        self._tagged_versions[template_id][to_tag] = target_version

        if self.enable_logging:
            logger.info(
                "version_promoted",
                extra={
                    "template_id": template_id,
                    "version": version,
                    "to_tag": to_tag.value,
                },
            )

        return target_version

    def rollback(
        self,
        template_id: str,
        tag: VersionTag,
        to_version: str,
    ) -> PromptVersion | None:
        """Rollback to a previous version.

        Args:
            template_id: Template identifier
            tag: Environment tag
            to_version: Version to rollback to

        Returns:
            PromptVersion or None
        """
        # Find target version
        versions = self._versions.get(template_id, [])
        target_version = None

        for v in versions:
            if v.version == to_version:
                target_version = v
                break

        if not target_version:
            return None

        # Update tagged version
        if template_id not in self._tagged_versions:
            self._tagged_versions[template_id] = {}

        self._tagged_versions[template_id][tag] = target_version

        if self.enable_logging:
            logger.warning(
                "version_rolled_back",
                extra={
                    "template_id": template_id,
                    "tag": tag.value,
                    "to_version": to_version,
                },
            )

        return target_version

    def get_version(
        self,
        template_id: str,
        tag: VersionTag,
    ) -> PromptVersion | None:
        """Get current version for an environment.

        Args:
            template_id: Template identifier
            tag: Environment tag

        Returns:
            PromptVersion or None
        """
        tagged = self._tagged_versions.get(template_id, {})
        return tagged.get(tag)

    def get_version_history(
        self,
        template_id: str,
    ) -> list[PromptVersion]:
        """Get version history for a template.

        Args:
            template_id: Template identifier

        Returns:
            List of versions (newest first)
        """
        versions = self._versions.get(template_id, [])
        return sorted(versions, key=lambda v: v.created_at, reverse=True)

    def compare_versions(
        self,
        template_id: str,
        version1: str,
        version2: str,
    ) -> dict[str, Any] | None:
        """Compare two versions.

        Args:
            template_id: Template identifier
            version1: First version
            version2: Second version

        Returns:
            Comparison dict or None
        """
        versions = self._versions.get(template_id, [])

        v1 = None
        v2 = None

        for v in versions:
            if v.version == version1:
                v1 = v
            if v.version == version2:
                v2 = v

        if not v1 or not v2:
            return None

        return {
            "version1": v1.to_dict(),
            "version2": v2.to_dict(),
            "content_changed": v1.content != v2.content,
            "content_diff_length": abs(len(v1.content) - len(v2.content)),
        }

    def _get_next_version(
        self,
        template_id: str,
        current_version: str,
    ) -> str:
        """Get next semantic version.

        Args:
            template_id: Template identifier
            current_version: Current version string

        Returns:
            Next version string
        """
        versions = self._versions.get(template_id, [])

        if not versions:
            # First version
            return "1.0.0"

        # Parse current version
        try:
            parts = current_version.split(".")
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
        except (ValueError, IndexError):
            return "1.0.0"

        # Increment patch version
        patch += 1

        return f"{major}.{minor}.{patch}"

    def bump_minor(self, version: str) -> str:
        """Bump minor version.

        Args:
            version: Current version

        Returns:
            New version
        """
        try:
            parts = version.split(".")
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
        except (ValueError, IndexError):
            return "1.0.0"

        return f"{major}.{minor + 1}.0"

    def bump_major(self, version: str) -> str:
        """Bump major version.

        Args:
            version: Current version

        Returns:
            New version
        """
        try:
            parts = version.split(".")
            major = int(parts[0])
        except (ValueError, IndexError):
            return "1.0.0"

        return f"{major + 1}.0.0"


def create_version_manager() -> PromptVersionManager:
    """Factory function to create version manager.

    Returns:
        PromptVersionManager instance
    """
    return PromptVersionManager()
