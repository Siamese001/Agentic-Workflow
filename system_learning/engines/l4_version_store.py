"""L4 versioned ChangePackage store — write-once semantics with activation pointers.

Provides:
  - Content-addressed commit (SHA-256 of canonical_bytes → version_id)
  - Write-once / idempotent: same content → same version_id, no mutation
  - Parent existence enforcement (DAG, not free graph)
  - O(1) activation pointer update and rollback
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# =============================================================================
# Exceptions
# =============================================================================


class ParentVersionNotFound(Exception):
    """Raised when a specified parent version does not exist in the store."""


class VersionNotFound(Exception):
    """Raised when a requested version does not exist in the store."""


# =============================================================================
# VersionedPackage
# =============================================================================


@dataclass(frozen=True)
class VersionedPackage:
    """Immutable record of a committed ChangePackage."""

    version_id: str
    parent_version_id: str | None
    change_spec_hash: str
    committed_at_utc: int
    package_bytes: bytes


# =============================================================================
# L4VersionStore
# =============================================================================


class L4VersionStore:
    """Concrete in-memory L4 versioned store.

    Enforces:
      - Write-once / idempotent semantics (content-addressed by SHA-256)
      - Parent existence for non-genesis commits
      - O(1) activation pointer update and rollback
      - No deletion of historical versions
    """

    def __init__(self) -> None:
        self._versions: dict[str, VersionedPackage] = {}
        self._active_pointers: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Commit
    # ------------------------------------------------------------------

    def commit_change_package(
        self,
        package,
        parent_version_id: str | None,
        change_spec_hash: str,
        committed_at_utc: int,
    ) -> str:
        """Commit a ChangePackage and return its version_id.

        Parameters
        ----------
        package
            Any object implementing ``canonical_bytes() -> bytes``.
        parent_version_id : str | None
            Parent version or ``None`` for genesis.
        change_spec_hash : str
            Caller-supplied spec hash (stored but not used for version_id).
        committed_at_utc : int
            Commit timestamp.

        Returns
        -------
        str
            SHA-256 hex digest of ``package.canonical_bytes()``.

        Raises
        ------
        ParentVersionNotFound
            If ``parent_version_id`` is not ``None`` and not in the store.
        """
        raw = package.canonical_bytes()
        version_id = hashlib.sha256(raw).hexdigest()

        if version_id in self._versions:
            return version_id

        if parent_version_id is not None and parent_version_id not in self._versions:
            raise ParentVersionNotFound(
                f"PARENT_VERSION_NOT_FOUND: parent {parent_version_id!r} does not exist"
            )

        self._versions[version_id] = VersionedPackage(
            version_id=version_id,
            parent_version_id=parent_version_id,
            change_spec_hash=change_spec_hash,
            committed_at_utc=committed_at_utc,
            package_bytes=raw,
        )
        return version_id

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_change_package(self, version_id: str) -> VersionedPackage:
        """Retrieve a versioned package by ID.

        Raises
        ------
        VersionNotFound
            If the version_id is not in the store.
        """
        if version_id not in self._versions:
            raise VersionNotFound(f"VERSION_NOT_FOUND: {version_id!r}")
        return self._versions[version_id]

    def list_versions(self) -> list[str]:
        """Return a deterministic sorted list of all committed version_ids."""
        return sorted(self._versions.keys())

    # ------------------------------------------------------------------
    # Activation pointer
    # ------------------------------------------------------------------

    def update_activation_pointer(self, component: str, version_id: str) -> None:
        """Set the active version for a component.

        Raises
        ------
        VersionNotFound
            If the target version_id does not exist.
        """
        if version_id not in self._versions:
            raise VersionNotFound(f"ACTIVATION_TARGET_NOT_FOUND: {version_id!r}")
        self._active_pointers[component] = version_id

    def get_active_version(self, component: str) -> str | None:
        """Return the currently active version_id for a component, or None."""
        return self._active_pointers.get(component)

    def rollback(self, component: str, version_id: str) -> None:
        """Revert the activation pointer for a component to a prior version_id.

        Does NOT delete any historical versions.

        Raises
        ------
        VersionNotFound
            If the rollback target does not exist.
        """
        if version_id not in self._versions:
            raise VersionNotFound(
                f"VERSION_NOT_FOUND: rollback target {version_id!r} does not exist"
            )
        self._active_pointers[component] = version_id


__all__ = [
    "L4VersionStore",
    "VersionedPackage",
    "ParentVersionNotFound",
    "VersionNotFound",
]
